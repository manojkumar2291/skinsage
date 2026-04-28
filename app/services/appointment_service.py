import asyncio
import json
from fastapi import HTTPException, BackgroundTasks
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo
import mysql.connector

from app.database.mysql_conn import get_db_connection as get_connection
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatus
from app.utils.email_templetes import booking_confirmation_template, appointment_reminder_template
from app.services.email_service import send_email_sync
from app.services.payment_service import PaymentService
from app.schemas.payment import OrderCreate

# --- BACKGROUND TASK FOR 7-MINUTE EXPIRATION ---
async def expire_pending_appointment(appointment_id: int, provider_id: int, formatted_slot: str):
    """Waits 7 minutes. If the appointment is still pending_payment, it cancels it and frees the slot."""
    await asyncio.sleep(420)  # Wait exactly 7 minutes (420 seconds)
    
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT status FROM appointments WHERE id=%s", (appointment_id,))
        appt = cur.fetchone()
        
        # If the user never paid, cancel the appointment and free the slot
        if appt and appt['status'] == 'pending_payment':
            print(f"Payment timeout! Cancelling appointment {appointment_id} and freeing slot.")
            
            # 1. Mark appointment as cancelled
            cur.execute("UPDATE appointments SET status='cancelled' WHERE id=%s", (appointment_id,))
            
            # 2. Free up the slot so someone else can book it
            cur.execute("""
                UPDATE appointment_slots 
                SET is_onhold=0, is_available=1 
                WHERE provider_id=%s AND start_time=%s
            """, (provider_id, formatted_slot))
            
            conn.commit()
    except Exception as e:
        print(f"Error in background expiration task: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


class AppointmentService:
    
    def create_pending_appointment(self, patient_id: int, data: AppointmentCreate, background_tasks: BackgroundTasks):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        try:
            # 1. Combine Date and Time
            slot_dt = datetime.combine(data.preferred_date, data.preferred_time)
            
            # 2. Strip any timezone info so 09:30 stays EXACTLY 09:30, and remove seconds
            normalized_slot = slot_dt.replace(tzinfo=None, second=0, microsecond=0)
            formatted_slot = normalized_slot.strftime('%Y-%m-%d %H:%M:%S')

            # --- BEGIN TRANSACTION LOGIC ---
            print(f"Attempting to secure slot for provider_id={data.provider_id} at {formatted_slot}")
            
            # 3. Check slot status first to provide specific error messages
            cur.execute("""
                SELECT is_available, is_onhold, is_booked 
                FROM appointment_slots 
                WHERE provider_id=%s AND start_time=%s
            """, (data.provider_id, formatted_slot))
            slot = cur.fetchone()

            if not slot:
                conn.rollback()
                raise HTTPException(status_code=404, detail="This slot does not exist.")
            
            if slot['is_booked']:
                conn.rollback()
                raise HTTPException(status_code=409, detail="This slot is already booked.")
            
            if slot['is_onhold']:
                conn.rollback()
                raise HTTPException(status_code=409, detail="This slot is temporarily locked for another payment. Please try again in a few minutes.")

            # 4. Update the slot FIRST to ensure it's available and lock it
            update_slot_sql = """
                UPDATE appointment_slots 
                SET is_onhold=1, is_available=0 
                WHERE provider_id=%s AND start_time=%s AND is_available=1 AND is_onhold=0
            """
            cur.execute(update_slot_sql, (data.provider_id, formatted_slot))
            
            # CRITICAL CHECK: Did we actually secure the slot?
            if cur.rowcount == 0:
                conn.rollback()
                raise HTTPException(status_code=409, detail="Failed to secure slot. It might have been recently locked or booked.")

            # 4. If slot is secured, insert the pending appointment
            insert_appt_sql = """
                INSERT INTO appointments
                (case_id, patient_id, provider_id, preferred_slot, status, created_at)
                VALUES (%s, %s, %s, %s, 'pending_payment', NOW())
            """
            cur.execute(insert_appt_sql, (data.case_id, patient_id, data.provider_id, formatted_slot))
            appointment_id = cur.lastrowid

            conn.commit()
            
            # 5. TRIGGER BACKGROUND TASK (7-minute countdown)
            background_tasks.add_task(
                expire_pending_appointment, 
                appointment_id=appointment_id, 
                provider_id=data.provider_id, 
                formatted_slot=formatted_slot
            )
            
            # --- CONSOLIDATED PAYMENT CREATION ---
            cur.execute("SELECT consultation_fee FROM providers WHERE id=%s", (data.provider_id,))
            provider_row = cur.fetchone()
            fee = provider_row['consultation_fee'] if provider_row else 0.0

            # Direct Call to Payment Service
            payment_svc = PaymentService() 
            order_data = OrderCreate(amount=float(fee), currency="INR", appointment_id=appointment_id)
            razorpay_order = payment_svc.create_order(patient_id, order_data)
            razorpay_order["appointment_id"] = appointment_id

            return razorpay_order

        except mysql.connector.Error as db_err:
            conn.rollback()
            print(f"Database Error: {db_err}")
            raise HTTPException(status_code=500, detail="Database error occurred.")
        except HTTPException:
            raise
        except Exception as e:
            conn.rollback()
            print(f"Unexpected Error: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
        finally:
            cur.close()
            conn.close()


    def list_appointments(self, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        print(f"Listing appointments for user_id={user_id}, role={role}")

        try:
            query = """
                SELECT a.*, p.name as provider_name, p.specialty as provider_specialty, p.experience_years as experience
                FROM appointments a
                LEFT JOIN providers p ON a.provider_id = p.id
                WHERE 1=1
            """
            params = []

            if role in ['provider', 'doctor']:
                # For providers, we first need to find their provider_id
                cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
                provider = cur.fetchone()
                if not provider:
                    return []
                query += " AND a.provider_id=%s ORDER BY a.preferred_slot ASC"
                params.append(provider['id'])
            elif role == 'admin':
                # Admins see everything
                query += " ORDER BY a.created_at DESC"
            else:
                # Patients see their own
                query += " AND a.patient_id=%s ORDER BY a.created_at DESC"
                params.append(user_id)

            cur.execute(query, tuple(params))
            result = cur.fetchall()

            for appt in result:
                if isinstance(appt.get('provider_specialty'), str):
                    try:
                        appt['provider_specialty'] = json.loads(appt['provider_specialty'])
                    except:
                        pass
                for field in ['preferred_slot', 'confirmed_slot', 'created_at']:
                    if appt.get(field) and isinstance(appt[field], datetime):
                        appt[field] = appt[field].replace(tzinfo=timezone.utc)
            return result
        finally:
            cur.close()
            conn.close()


    def get_appointment(self, appointment_id: int, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT a.*, p.name as provider_name, p.specialty as provider_specialty, p.experience_years as experience
                FROM appointments a
                LEFT JOIN providers p ON a.provider_id = p.id
                WHERE a.id = %s
            """
            cur.execute(query, (appointment_id,))
            appt = cur.fetchone()

            if not appt:
                raise HTTPException(404, "Appointment not found")

            # Parse specialty if it's a string
            if isinstance(appt.get('provider_specialty'), str):
                try:
                    appt['provider_specialty'] = json.loads(appt['provider_specialty'])
                except:
                    pass

            for field in ['preferred_slot', 'confirmed_slot', 'created_at']:
                if appt.get(field) and isinstance(appt[field], datetime):
                    appt[field] = appt[field].replace(tzinfo=timezone.utc)

            is_patient = appt['patient_id'] == user_id
            is_provider = False
            
            if role == 'doctor' or role == 'provider':
                cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
                provider = cur.fetchone()
                if provider and provider['id'] == appt['provider_id']:
                    is_provider = True

            if not (is_patient or is_provider or role == 'admin'):
                raise HTTPException(403, "Not authorized to view this appointment")

            return appt
        finally:
            cur.close()
            conn.close()


    def update_status(self, appointment_id: int, data: AppointmentUpdate, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        try:
            cur.execute("SELECT * FROM appointments WHERE id=%s", (appointment_id,))
            appt = cur.fetchone()
            if not appt:
                raise HTTPException(404, "Appointment not found")

            if role == 'provider':
                cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
                provider = cur.fetchone()
                if not provider or provider['id'] != appt['provider_id']:
                    raise HTTPException(403, "You are not the assigned provider for this appointment")
            elif role != 'admin':
                 if data.status == AppointmentStatus.CANCELLED and appt['patient_id'] == user_id:
                     pass 
                 else:
                     raise HTTPException(403, "Not authorized to update this appointment")

            confirmed_slot = data.confirmed_slot if data.confirmed_slot else appt['confirmed_slot']
            
            if data.status == AppointmentStatus.CONFIRMED and not confirmed_slot:
                confirmed_slot = appt['preferred_slot']

            sql = """
                UPDATE appointments 
                SET status=%s, confirmed_slot=%s
                WHERE id=%s
            """
            cur.execute(sql, (data.status, confirmed_slot, appointment_id))
            conn.commit()

            return {
                "id": appointment_id,
                "status": data.status,
                "confirmed_slot": confirmed_slot,
            }
        finally:
            cur.close()
            conn.close()


    def confirm_payment(self, appointment_id: int,case_id, background_tasks: BackgroundTasks):
        """Called by payment webhook/success route to finalize the appointment."""
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        print(f"Confirming payment for appointment: {appointment_id}")

        try:
            # 1. Fetch the existing pending appointment
            cur.execute("SELECT * FROM appointments WHERE id=%s AND status='pending_payment'", (appointment_id,))
            appt = cur.fetchone()

            if not appt:
                raise HTTPException(status_code=410, detail="Appointment not found or already processed/expired.")

            preferred_slot = appt['preferred_slot']
            provider_id = appt['provider_id']
            patient_id = appt['patient_id']

            # 2. Update Appointment to booked
            cur.execute("UPDATE appointments SET status='confirmed' WHERE id=%s", (appointment_id,))

            # 3. Permanently mark the slot as booked
            cur.execute("""
                UPDATE appointment_slots 
                SET is_booked=1, is_onhold=0, is_available=0 
                WHERE provider_id=%s AND start_time=%s
            """, (provider_id, preferred_slot))
            
            # 4. Fetch Emails for Notifications
            cur.execute("SELECT email, full_name FROM users WHERE id=%s", (patient_id,))
            patient = cur.fetchone()
            
            cur.execute("SELECT email, name FROM providers WHERE id=%s", (provider_id,))
            provider = cur.fetchone()

            conn.commit()

            # 5. Send Emails
            if patient and provider:
                patient_response = booking_confirmation_template(patient['full_name'], provider['name'], preferred_slot, appointment_id)
                provider_subject = f"New Appointment Request: {patient['full_name']}"
                provider_body = (
                    f"Hello Dr. {provider['name']},\n\n"
                    f"You have a new appointment request from {patient['full_name']}.\n"
                    f"Requested Slot: {preferred_slot}\n"
                    f"Please log in to your dashboard to Confirm this request."
                )

                background_tasks.add_task(send_email_sync, patient['email'], patient_response['subject'], patient_response['body'])
                background_tasks.add_task(send_email_sync, provider['email'], provider_subject, provider_body)

            return {"appointment_id": appointment_id, "status": "Booked"}
        except HTTPException:
            # Re-raise HTTP exceptions so FastAPI returns the correct 410, 404, etc.
            raise
        except Exception as e:
            conn.rollback()
            print(f"Failed to confirm payment: {e}")
            raise HTTPException(status_code=500, detail="Failed to process payment confirmation.")
        finally:
            cur.close()
            conn.close()


    def cancel_appointment(self, appointment_id: int, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        try:
            # 1. Fetch the appointment
            cur.execute("SELECT * FROM appointments WHERE id=%s", (appointment_id,))
            appt = cur.fetchone()

            if not appt:
                raise HTTPException(404, "Appointment not found")

            # 2. Authorization & Logic Checks
            if role == 'provider':
                cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
                provider = cur.fetchone()
                if not provider or provider['id'] != appt['provider_id']:
                    raise HTTPException(403, "You are not the assigned provider for this appointment")
            
            elif role == 'admin':
                pass # Admin can cancel anytime

            else: 
                # PATIENT LOGIC
                if appt['patient_id'] != user_id:
                    raise HTTPException(403, "Not authorized to cancel this appointment")
                
                # Check 2-Hour Window
                appointment_time = appt['preferred_slot']
                if isinstance(appointment_time, str):
                    appointment_time = datetime.strptime(appointment_time, '%Y-%m-%d %H:%M:%S')
                
                current_time = datetime.now(timezone.utc).replace(tzinfo=None)
                time_difference = appointment_time - current_time

                if time_difference < timedelta(hours=2):
                    raise HTTPException(
                        status_code=400, 
                        detail="Appointments cannot be cancelled less than 2 hours before the scheduled time."
                    )

            # 3. Execute Cancellation
            cur.execute("UPDATE appointments SET status='cancelled' WHERE id=%s", (appointment_id,))
            
            # 4. Free up the slot so someone else can book it!
            cur.execute("""
                UPDATE appointment_slots 
                SET is_booked=0, is_onhold=0, is_available=1 
                WHERE provider_id=%s AND start_time=%s
            """, (appt['provider_id'], appt['preferred_slot']))
            
            conn.commit()

            return {"id": appointment_id, "status": "cancelled"}

        finally:
            cur.close()
            conn.close()