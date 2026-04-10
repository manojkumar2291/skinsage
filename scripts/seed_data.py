import os
import sys
from datetime import datetime, timedelta
import random
import json

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.mysql_conn import get_db_connection
from app.core.security import hash_password
from app.core.config import settings

def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Create a Test Patient if not exists
        cursor.execute("SELECT id FROM users WHERE email=%s", ("patient@example.com",))
        patient = cursor.fetchone()
        if not patient:
            pw_hash = hash_password("Test@123")
            cursor.execute("""
                INSERT INTO users (full_name, email, phone, password_hash, role, dob, gender, is_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, ("John Doe", "patient@example.com", "9876543210", pw_hash, "patient", "1990-01-01", "male", 1))
            patient_id = cursor.lastrowid
            print(f"Created patient John Doe (ID: {patient_id})")
        else:
            patient_id = patient['id']
            print(f"Using existing patient ID: {patient_id}")

        # 2. Doctor Profiles
        doctors = [
            {
                "name": "Dr. Rajesh Kumar",
                "email": "rajesh@skinsage.com",
                "specialty": ["Dermatologist"],
                "exp": 12,
                "bio": "Expert in clinical dermatology and acne treatment with over 12 years of experience at AIIMS.",
                "photo": "uploads/rajesh.png",
                "license": "MC-88721",
                "langs": ["English", "Hindi"]
            },
            {
                "name": "Dr. Sneha Reddy",
                "email": "sneha@skinsage.com",
                "specialty": ["Cosmetologist"],
                "exp": 8,
                "bio": "Specializes in laser treatments and anti-aging procedures. Passionate about skincare aesthetics.",
                "photo": "uploads/sneha.png",
                "license": "MC-45210",
                "langs": ["English", "Telugu"]
            },
            {
                "name": "Dr. Amit Shah",
                "email": "amit@skinsage.com",
                "specialty": ["Trichologist"],
                "exp": 10,
                "bio": "Dedicated to hair loss solutions and scalp health. Pioneer in hair transplant consultation.",
                "photo": "uploads/amit.png",
                "license": "MC-66321",
                "langs": ["English", "Gujarati"]
            },
            {
                "name": "Dr. Ananya Iyer",
                "email": "ananya@skinsage.com",
                "specialty": ["Dermatologist"],
                "exp": 15,
                "bio": "Focuses on pediatric dermatology and skin allergies. Dedicated to patient-centric care.",
                "photo": "uploads/ananya.png",
                "license": "MC-11200",
                "langs": ["English", "Tamil"]
            },
            {
                "name": "Dr. Vikram Singh",
                "email": "vikram@skinsage.com",
                "specialty": ["Skin Specialist"],
                "exp": 6,
                "bio": "Passionate about skin cancer screening and mole removal. Trained in advanced surgical dermatology.",
                "photo": "uploads/vikram.png",
                "license": "MC-55443",
                "langs": ["English", "Punjabi"]
            }
        ]

        pw_hash = hash_password("Test@123")
        
        provider_ids = []
        for doc in doctors:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE email=%s", (doc['email'],))
            user = cursor.fetchone()
            if not user:
                cursor.execute("""
                    INSERT INTO users (full_name, email, password_hash, role, is_verified)
                    VALUES (%s, %s, %s, %s, %s)
                """, (doc['name'], doc['email'], pw_hash, "provider", 1))
                user_id = cursor.lastrowid
            else:
                user_id = user['id']
            
            # Check if provider exists
            cursor.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
            prov = cursor.fetchone()
            
            # Convert specialty and languages to JSON strings
            specialty_json = json.dumps(doc['specialty'])
            langs_json = json.dumps(doc['langs'])

            if not prov:
                cursor.execute("""
                    INSERT INTO providers (email, name, license_number, verification_status, specialty, experience_years, bio, profile_photo, user_id, consultation_fee, languages)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (doc['email'], doc['name'], doc['license'], "verified", specialty_json, doc['exp'], doc['bio'], doc['photo'], user_id, 500.00, langs_json))
                provider_id = cursor.lastrowid
                print(f"Created provider {doc['name']} (ID: {provider_id})")
            else:
                provider_id = prov['id']
                # Update photo and specialty just in case
                cursor.execute("""
                    UPDATE providers 
                    SET profile_photo=%s, specialty=%s, languages=%s 
                    WHERE id=%s
                """, (doc['photo'], specialty_json, langs_json, provider_id))
                print(f"Updated/Using existing provider {doc['name']} (ID: {provider_id})")
            
            provider_ids.append(provider_id)

        # 3. Generate Slots for next 7 days
        print("Generating slots...")
        now = datetime.now()
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        for p_id in provider_ids:
            for day_offset in range(7):
                current_day = start_date + timedelta(days=day_offset)
                # Slots from 9 AM to 5 PM
                for hour in range(9, 17):
                    for minute in [0, 30]:
                        slot_start = current_day + timedelta(hours=hour, minutes=minute)
                        slot_end = slot_start + timedelta(minutes=30)
                        
                        # Insert slot, ignore if duplicate
                        cursor.execute("""
                            INSERT IGNORE INTO appointment_slots (provider_id, start_time, end_time, is_booked, is_available)
                            VALUES (%s, %s, %s, 0, 1)
                        """, (p_id, slot_start, slot_end))
        
        # 4. Book some sample appointments
        print("Booking sample appointments...")
        for p_id in provider_ids[:2]:  # Just for the first two doctors
            # Find an available slot
            cursor.execute("SELECT id, start_time FROM appointment_slots WHERE provider_id=%s AND is_booked=0 LIMIT 1", (p_id,))
            slot = cursor.fetchone()
            if slot:
                # Mark slot as booked
                cursor.execute("UPDATE appointment_slots SET is_booked=1 WHERE id=%s", (slot['id'],))
                
                # Create appointment
                cursor.execute("""
                    INSERT INTO appointments (patient_id, provider_id, preferred_slot, status)
                    VALUES (%s, %s, %s, %s)
                """, (patient_id, p_id, slot['start_time'], "confirmed"))
                print(f"Booked appointment for doctor {p_id} at {slot['start_time']}")

        conn.commit()
        print("Seeding completed successfully!")

    except Exception as e:
        print(f"Error during seeding: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_data()
