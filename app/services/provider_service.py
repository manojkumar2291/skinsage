import json
from typing import Optional, List
from decimal import Decimal
from fastapi import HTTPException
from app.database.mysql_conn import get_db_connection as get_connection
from app.schemas.provider import ProviderCreate , ProviderUpdate
from app.core.deps import get_current_user, Depends,role_required
from app.services.email_service import send_email_sync
from app.utils.email_templetes import password_reset_template, provider_welcome_template
from app.core.config import settings
import secrets
from datetime import datetime, timedelta

class ProviderService:

    def create_provider(self, data: ProviderCreate):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)


        languages_json = json.dumps(data.languages)
        specialty_json = json.dumps(data.specialty)
        cur.execute("insert into users (full_name,email,phone,password_hash,role,dob,gender,language_pref,is_verified,profile_photo) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
         (data.name,data.email,data.phone,None,"provider",data.dob,data.gender,data.language_pref,True, data.profile_photo))
        user_id = cur.lastrowid
      
        sql = """
            INSERT INTO providers 
            (user_id,name,email, license_number, verification_status, specialty, 
             experience_years, languages, consultation_fee, bio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            user_id, 
            data.name,
            data.email,
            data.license_number, 
            "pending", 
            specialty_json, 
            data.experience_years, 
            languages_json, 
            data.consultation_fee, 
            data.bio
        )

        cur.execute(sql, values)
        conn.commit()
        
        new_id = cur.lastrowid
        
        # --- SEND WELCOME EMAIL WITH PASSWORD SETUP LINK ---
        token = secrets.token_urlsafe(32) 
        expires_at = datetime.now() + timedelta(days=7) # Link valid for 7 days
        
        # Save token
        cur.execute("""
            INSERT INTO password_resets (user_id, token, expires_at, used)
            VALUES (%s, %s, %s, 0)
        """, (user_id, token, expires_at))
        conn.commit()
        
        reset_link = f"{settings.FRONTENDURL}/reset-password?token={token}"
        
        # Generate email content using the dedicated template
        email_content = provider_welcome_template(data.name, reset_link)
        
        try:
            # Note: Provider is created by Admin synchronously during this request. 
            # In a real app we'd use BackgroundTasks, but since this is in the service layer
            # and we might not have BackgroundTasks readily injected, we send synchronously 
            # or could refactor to use it.
            send_email_sync(
                data.email, 
                email_content['subject'], 
                email_content['body']
            )
        except Exception as e:
            print(f"Failed to send welcome email to {data.email}: {e}")
        # --------------------------------------------------
        
        return {
            "id": new_id, 
            "verification_status": "pending",
            "languages": data.languages,
            **data.dict()
        }
    def get_provider_by_id(self, provider_id: int):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT p.*, u.profile_photo 
            FROM providers p 
            JOIN users u ON p.user_id = u.id 
            WHERE p.id=%s
        """, (provider_id,))
        provider = cur.fetchone()
        
        if not provider:
            raise HTTPException(404, "Provider not found")
        
        if isinstance(provider['languages'], str):
             provider['languages'] = json.loads(provider['languages'])
        if isinstance(provider['specialty'], str):
             try:
                 provider['specialty'] = json.loads(provider['specialty'])
             except:
                 pass

        if provider.get("profile_photo") and not provider["profile_photo"].startswith("http"):
             provider["profile_photo"] = f"{settings.BACKEND_URL}/{provider['profile_photo']}"

        return provider
    
    def list_providers(self, limit: int = 10, offset: int = 0, name: Optional[str] = None, 
                       specialty: Optional[str] = None, min_price: Optional[Decimal] = None, 
                       max_price: Optional[Decimal] = None, min_experience: Optional[int] = None,
                       availability: Optional[str] = None):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                u.id AS id,
                p.id AS provider_id,
                p.name,
                p.email,
                p.license_number,
                p.specialty,
                p.verification_status,
                p.experience_years,
                p.languages,
                p.consultation_fee,
                p.bio,
                u.profile_photo
            FROM providers p 
            JOIN users u ON p.user_id = u.id 
            WHERE 1=1
        """
        params = []
        
        if name:
            query += " AND p.name LIKE %s"
            params.append(f"%{name}%")
            
        if specialty:
            query += " AND p.specialty LIKE %s"
            params.append(f"%{specialty}%")
            
        if min_price:
            query += " AND p.consultation_fee >= %s"
            params.append(min_price)
            
        if max_price:
            query += " AND p.consultation_fee <= %s"
            params.append(max_price)
            
        if min_experience:
            query += " AND p.experience_years >= %s"
            params.append(min_experience)
            
        if availability == 'today':
            query += " AND p.id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND DATE(start_time) = CURDATE())"
        elif availability == 'tomorrow':
            query += " AND p.id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND DATE(start_time) = CURDATE() + INTERVAL 1 DAY)"
        elif availability == 'this_week':
            query += " AND p.id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND YEARWEEK(start_time, 1) = YEARWEEK(CURDATE(), 1))"
        elif availability == 'this_month':
            query += " AND p.id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND YEAR(start_time) = YEAR(CURDATE()) AND MONTH(start_time) = MONTH(CURDATE()))"
        elif availability:
            # Assume availability is a specific date string, e.g. 'YYYY-MM-DD'
            query += " AND p.id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND DATE(start_time) = %s)"
            params.append(availability)
            
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, tuple(params))
        providers = cur.fetchall()

        for p in providers:
            if isinstance(p['languages'], str):
                p['languages'] = json.loads(p['languages'])
            if isinstance(p['specialty'], str):
                try:
                    p['specialty'] = json.loads(p['specialty'])
                except:
                    pass

            if p.get("profile_photo") and not p["profile_photo"].startswith("http"):
                p["profile_photo"] = f"{settings.BACKEND_URL}/{p['profile_photo']}"

        return providers
    
    def update_provider_details(self,
        provider_data: ProviderUpdate,
        
       
        current_user: dict = Depends(role_required("admin","provider"))
        ):
        if current_user['role'] not in ["provider", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized")

        db = get_connection()
        cursor = db.cursor()
    
        # Find Provider ID linked to User ID
        cursor.execute("SELECT id FROM providers WHERE user_id = %s", (current_user['id'],))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Provider profile not found")
        
        # Static Query for Provider
        # Note: For 'languages' array, ensure your DB driver handles lists correctly (Psycopg2 does)
        query = """
            UPDATE providers
            SET 
                name = COALESCE(%s, name),
                specialty = COALESCE(%s, specialty),
                consultation_fee = COALESCE(%s, consultation_fee),
                bio = COALESCE(%s, bio),
                experience_years = COALESCE(%s, experience_years),
                languages = COALESCE(%s, languages)
            WHERE user_id = %s
        """
        
        specialty_val = json.dumps(provider_data.specialty) if provider_data.specialty is not None else None

        params = (
            provider_data.name,
            specialty_val,
            provider_data.consultation_fee,
            provider_data.bio,
            provider_data.experience_years,
            json.dumps(provider_data.languages) if provider_data.languages is not None else None, # Pass list directly for Postgres
            current_user['id']
        )

        cursor.execute(query, params)
        db.commit()

        return {"msg": "Updated successfully", "status": "success"}

    def generate_bulk_slots(self, provider_id: int, config: 'SlotGenerationRequest'):
        from app.schemas.provider import SlotGenerationRequest
        from datetime import datetime, timedelta, time
        from typing import List
        from fastapi import HTTPException

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        new_slots = []

        def normalize(dt: datetime):
            return dt.replace(second=0, microsecond=0)

        def is_excluded(current_dt: datetime, duration_minutes: int, excluded_intervals: List[List[time]]):
            if not excluded_intervals:
                return False
            
            slot_start_time = current_dt.time()
            slot_end_time = (current_dt + timedelta(minutes=duration_minutes)).time()
            
            for interval in excluded_intervals:
                ex_start, ex_end = interval
                # Overlap check for times within a day
                if slot_start_time < ex_end and slot_end_time > ex_start:
                    return True
            return False

        try:
            current_date = config.start_date
            while current_date <= config.end_date:
                start_dt_obj = datetime.combine(current_date, config.start_time)
                current_dt = normalize(start_dt_obj)
                end_dt_limit = normalize(datetime.combine(current_date, config.end_time))

                while current_dt + timedelta(minutes=config.duration_minutes) <= end_dt_limit:
                    if is_excluded(current_dt, config.duration_minutes, config.excluded_intervals):
                        current_dt += timedelta(minutes=config.duration_minutes)
                        continue

                    slot_end = normalize(current_dt + timedelta(minutes=config.duration_minutes))
                    fmt_start_time = current_dt.strftime('%Y-%m-%d %H:%M:%S')
                    fmt_end_time = slot_end.strftime('%Y-%m-%d %H:%M:%S')

                    # Check for overlaps or duplicates
                    cursor.execute("""
                        SELECT 1 FROM appointment_slots 
                        WHERE provider_id = %s 
                        AND start_time < %s 
                        AND end_time > %s
                    """, (provider_id, fmt_end_time, fmt_start_time))

                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO appointment_slots 
                            (provider_id, start_time, end_time, is_available, is_booked)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (provider_id, fmt_start_time, fmt_end_time, True, False))
                        
                        new_slots.append({
                            "id": cursor.lastrowid,
                            "provider_id": provider_id,
                            "start_time": fmt_start_time,
                            "end_time": fmt_end_time,
                            "is_available": True,
                            "is_booked": False
                        })

                    current_dt = slot_end
                current_date += timedelta(days=1)
            
            conn.commit()
            return new_slots
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to generate slots: {str(e)}")
        finally:
            cursor.close()
            conn.close()