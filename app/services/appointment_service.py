from fastapi import HTTPException,BackgroundTasks
from datetime import datetime,timedelta
from app.database.mysql_conn import get_db_connection as get_connection
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatus
from typing import Optional
from zoneinfo import ZoneInfo
import mysql.connector
from app.utils.email_templetes import booking_confirmation_template, appointment_reminder_template

from app.services.email_service import send_email_sync

class AppointmentService:
    def reserve_appointment_slot(self, patient_id: int, data: AppointmentCreate):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        try:
            # 1. Convert preferred_slot to IST
            slot_dt = data.preferred_slot
            if slot_dt.tzinfo is None:
                slot_dt = slot_dt.replace(tzinfo=ZoneInfo("UTC"))
            
            # Convert timezone
            ist_slot_obj = slot_dt.astimezone(ZoneInfo("Asia/Kolkata"))

            # 2. Normalize: Remove Seconds & Microseconds (Crucial Step)
            # This matches the logic used in generate_slots
            ist_slot_normalized = ist_slot_obj.replace(second=0, microsecond=0)

            # 3. Format as String for SQL
            # This strips the "+05:30" offset from the query to match MySQL's format
            formatted_slot = ist_slot_normalized.strftime('%Y-%m-%d %H:%M:%S')

            # 4. Calculate Expiry
            expires_at = datetime.now() + timedelta(minutes=7)

            sql = """
                INSERT INTO appointment_reservations
                (patient_id, provider_id, preferred_slot, expires_at)
                VALUES (%s, %s, %s, %s)
            """

            try:
                # Insert using the formatted string
                cur.execute(sql, (patient_id, data.provider_id, formatted_slot, expires_at))
                reservation_id = cur.lastrowid
                print(cur.rowcount,cur.lastrowid)
                try:
                    # Update using the SAME formatted string
                    # Since generate_slots also used this format, they will now match perfectly.
                    cur.execute(
                        "UPDATE appointment_slots SET is_onhold=1 WHERE provider_id=%s AND start_time=%s", 
                        (data.provider_id, formatted_slot)
                    )

                    # Verification (Optional but recommended)
                    if cur.rowcount == 0:
                        print(f"WARNING: No slot found to hold at {formatted_slot}")
                        # You might want to rollback here if strict consistency is needed
                        # raise Exception("Slot not found")
                        
                except Exception as e:
                    print("Failed to hold the slot:", e)
                    conn.rollback() 
                    raise HTTPException(status_code=500, detail="Failed to hold the slot")
                    
            except mysql.connector.Error as e:
                if e.errno == 1062:  # Duplicate entry error code
                    raise HTTPException(status_code=409, detail="Slot already reserved by another patient")
                raise

            conn.commit()
            

            return {
                "reservation_id": reservation_id,
                "expires_at": expires_at,
                
            }

        finally:
            cur.close()
            conn.close()




    def list_appointments(self, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        print (role)

        if role == 'provider' or role == 'doctor':
            
            

            cur.execute("SELECT * FROM appointments WHERE provider_id=%s ORDER BY preferred_slot ASC", (user_id,))
        
        else:

            cur.execute("SELECT * FROM appointments WHERE patient_id=%s ORDER BY created_at DESC", (user_id,))

        return cur.fetchall()

    def get_appointment(self, appointment_id: int, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM appointments WHERE id=%s", (appointment_id,))
        appt = cur.fetchone()

        if not appt:
            raise HTTPException(404, "Appointment not found")


        is_patient = appt['patient_id'] == user_id
        
        is_provider = False
        if role == 'doctor':
            cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
            provider = cur.fetchone()
            if provider and provider['id'] == appt['provider_id']:
                is_provider = True

        if not (is_patient or is_provider or role == 'admin'):
            raise HTTPException(403, "Not authorized to view this appointment")

        return appt

    def update_status(self, appointment_id: int, data: AppointmentUpdate, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        
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
        print("gfytfytf")

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
    def confirm_payment(self, reservation_id: int, case_id: Optional[int], background_tasks: BackgroundTasks):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        try:
            cur.execute("""
                SELECT * FROM appointment_reservations
                WHERE id=%s AND expires_at > NOW()
            """, (reservation_id,))
            reservation = cur.fetchone()
           
            

            if not reservation:
                raise HTTPException(status_code=410, detail="Reservation expired")
            preferred_slot=reservation['preferred_slot']
            sql_insert = """
            INSERT INTO appointments
            (case_id, patient_id, provider_id, preferred_slot, status, created_at)
            VALUES (%s, %s, %s, %s, 'booked', NOW())
            """

            cur.execute(sql_insert, (
                case_id,
                reservation['patient_id'],
                reservation['provider_id'],
                reservation['preferred_slot']
            ))
            new_id = cur.lastrowid

            cur.execute("update appointment_slots set is_booked=1,is_onhold=0,is_available=0 where provider_id=%s and start_time=%s", (reservation['provider_id'], reservation['preferred_slot']))
            cur.execute("SELECT email, full_name FROM users WHERE id=%s", (reservation['patient_id'],))
            patient = cur.fetchone()
            patient_email = patient['email']
            patient_name = patient['full_name']

            cur.execute("SELECt email,name FROM providers WHERE id=%s", (reservation['provider_id'],))
            provider = cur.fetchone()
            provider_email = provider['email']
            provider_name = provider['name']

            cur.execute("DELETE FROM appointment_reservations WHERE id=%s", (reservation_id,))
            conn.commit()

            patient_response = booking_confirmation_template(patient_name, provider_name, preferred_slot, new_id)
            
            # --- Email for Provider ---
            # You can create a specific template function for this, but here is a basic text version
            provider_subject = f"New Appointment Request: {patient_name}"
            provider_body = (
                f"Hello Dr. {provider_name},\n\n"
                f"You have a new appointment request from {patient_name}.\n"
                f"Requested Slot: {preferred_slot}\n"
               
                f"Please log in to your dashboard to Confirm this request."
            )

            background_tasks.add_task(send_email_sync, patient_email, patient_response['subject'], patient_response['body'])
            background_tasks.add_task(send_email_sync, provider_email, provider_subject, provider_body)



            return {"appointment_id": new_id, "status": "Booked"}

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
                # Provider Check: Must be the assigned doctor
                cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
                provider = cur.fetchone()
                if not provider or provider['id'] != appt['provider_id']:
                    raise HTTPException(403, "You are not the assigned provider for this appointment")
            
            elif role == 'admin':
                # Admin can cancel anytime, so we pass
                pass

            else: 
                # PATIENT LOGIC (User)
                
                # A. Check Ownership
                if appt['patient_id'] != user_id:
                    raise HTTPException(403, "Not authorized to cancel this appointment")
                
                # B. Check 2-Hour Window (The new requirement)
                # Ensure appt['preferred_slot'] is a datetime object. 
                # If your DB returns a string, parse it: datetime.strptime(appt['preferred_slot'], "%Y-%m-%d %H:%M:%S")
                appointment_time = appt['preferred_slot']
                current_time = datetime.now()
                
                time_difference = appointment_time - current_time

                # If the appointment is in the past or less than 2 hours away
                if time_difference < timedelta(hours=2):
                    raise HTTPException(
                        status_code=400, 
                        detail="Appointments cannot be cancelled less than 2 hours before the scheduled time."
                    )

            # 3. Execute Cancellation
            cur.execute("UPDATE appointments SET status=%s WHERE id=%s", ("cancelled", appointment_id))
            conn.commit()

            return {"id": appointment_id, "status": "cancelled"}

        finally:
            cur.close()
            conn.close()