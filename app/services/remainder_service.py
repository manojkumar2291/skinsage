from datetime import datetime, timedelta
import mysql.connector
import os
from app.database.mysql_conn import get_db_connection as get_db
from app.services.email_service import send_email_sync as send_email
from app.utils.email_templetes import appointment_reminder_template, booking_confirmation_template  


    

def send_reminder_emails():
    print('--- Running Reminder Email Service ---')
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    now = datetime.utcnow()

    cursor.execute("""
        SELECT 
            a.id, 
            a.preferred_slot, 
            u.email, 
            u.full_name,
            p.name as provider_name  -- Fetch Provider Name
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        JOIN providers p ON a.provider_id = p.id  -- Join Providers Table
        WHERE a.preferred_slot BETWEEN %s AND %s
        AND a.reminder_1_sent = 0;
    """, (now, now + timedelta(days=1)))

    for appt in cursor.fetchall():
        response = appointment_reminder_template(
            user_name=appt['full_name'], 
            doctor_name=appt['provider_name'],
            appointment_time=appt['preferred_slot'],
            booking_id=appt['id']
        )
        
        subject, message = response['subject'], response['body']
        
        
        send_email(to_email=appt["email"], subject=subject, body=message)
        
        update_cursor = conn.cursor() 
        update_cursor.execute("UPDATE appointments SET reminder_1_sent = 1 WHERE id = %s", (appt["id"],))
        update_cursor.close()
        conn.commit()

    cursor.execute("""
        SELECT 
            a.id, 
            a.preferred_slot, 
            u.email, 
            u.full_name,
            p.name as provider_name  -- Fetch Provider Name
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        JOIN providers p ON a.provider_id = p.id  -- Join Providers Table
        WHERE a.preferred_slot BETWEEN %s AND %s
        AND a.reminder_2_sent = 0;
    """, (now, now + timedelta(hours=2)))

    for appt in cursor.fetchall():
        response = appointment_reminder_template(
            patient_name=appt['full_name'], 
            provider_name=appt['provider_name'],
            slot=appt['preferred_slot'],
            appointment_id=appt['id']
        )

        send_email(to_email=appt["email"], subject=response['subject'], body=response['body'])
        
        update_cursor = conn.cursor()
        update_cursor.execute("UPDATE appointments SET reminder_2_sent = 1 WHERE id = %s", (appt["id"],))
        update_cursor.close()
        conn.commit()

    cursor.close()
    conn.close()