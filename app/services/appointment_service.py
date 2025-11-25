from fastapi import HTTPException
from datetime import datetime
from app.database.mysql_conn import get_db_connection as get_connection
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentStatus

class AppointmentService:

    def request_appointment(self, patient_id: int, data: AppointmentCreate):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # 1. Validation: Ensure Case belongs to Patient
        cur.execute("SELECT id FROM cases WHERE id=%s AND user_id=%s", (data.case_id, patient_id))
        if not cur.fetchone():
            raise HTTPException(404, "Case not found or does not belong to you")

        # 2. Validation: Ensure Provider exists
        cur.execute("SELECT id FROM providers WHERE id=%s", (data.provider_id,))
        if not cur.fetchone():
            raise HTTPException(404, "Provider not found")

        # 3. Insert Appointment
        sql = """
            INSERT INTO appointments 
            (case_id, patient_id, provider_id, preferred_slot, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data.case_id,
            patient_id,
            data.provider_id,
            data.preferred_slot,
            "pending",
            datetime.now()
        )

        cur.execute(sql, values)
        conn.commit()
        new_id = cur.lastrowid

        return {
            "id": new_id,
            "case_id": data.case_id,
            "patient_id": patient_id,
            "provider_id": data.provider_id,
            "preferred_slot": data.preferred_slot,
            "confirmed_slot": None,
            "status": "pending",
            "video_link": None,
            "created_at": datetime.now()
        }

    def list_appointments(self, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        if role == 'doctor':
            # 1. Find the Provider ID linked to this User ID
            cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
            provider = cur.fetchone()
            if not provider:
                return [] # Or raise error: User is a doctor but not registered as provider
            
            # 2. Fetch appointments for this provider
            cur.execute("SELECT * FROM appointments WHERE provider_id=%s ORDER BY preferred_slot ASC", (provider['id'],))
        
        else:
            # Logic for Patient (and admin acting as patient viewing their own)
            cur.execute("SELECT * FROM appointments WHERE patient_id=%s ORDER BY created_at DESC", (user_id,))

        return cur.fetchall()

    def get_appointment(self, appointment_id: int, user_id: int, role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM appointments WHERE id=%s", (appointment_id,))
        appt = cur.fetchone()

        if not appt:
            raise HTTPException(404, "Appointment not found")

        # Authorization Check
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

        # 1. Fetch existing appointment
        cur.execute("SELECT * FROM appointments WHERE id=%s", (appointment_id,))
        appt = cur.fetchone()
        if not appt:
            raise HTTPException(404, "Appointment not found")

        # 2. Authorization: Only the assigned Provider (or admin) can confirm/update
        # Note: Patients might cancel, but here we focus on Provider Confirm flow
        if role == 'doctor':
            cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
            provider = cur.fetchone()
            if not provider or provider['id'] != appt['provider_id']:
                raise HTTPException(403, "You are not the assigned provider for this appointment")
        elif role != 'admin':
             # Allow patient to cancel only? (Logic can be expanded)
             if data.status == AppointmentStatus.CANCELLED and appt['patient_id'] == user_id:
                 pass # Allow
             else:
                 raise HTTPException(403, "Not authorized to update this appointment")

        # 3. Update fields
        # If confirming, ensure confirmed_slot is set (or default to preferred)
        confirmed_slot = data.confirmed_slot if data.confirmed_slot else appt['confirmed_slot']
        
        # If status is changing to CONFIRMED, confirmed_slot should be set. 
        # If user didn't send one, maybe use preferred? (Optional logic)
        if data.status == AppointmentStatus.CONFIRMED and not confirmed_slot:
            confirmed_slot = appt['preferred_slot']

        sql = """
            UPDATE appointments 
            SET status=%s, confirmed_slot=%s, video_link=%s 
            WHERE id=%s
        """
        cur.execute(sql, (data.status, confirmed_slot, data.video_link, appointment_id))
        conn.commit()

        return {
            "id": appointment_id,
            "status": data.status,
            "confirmed_slot": confirmed_slot,
            "video_link": data.video_link
        }