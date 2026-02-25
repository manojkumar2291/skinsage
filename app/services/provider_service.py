import json
from typing import Optional, List
from decimal import Decimal
from fastapi import HTTPException
from app.database.mysql_conn import get_db_connection as get_connection
from app.schemas.provider import ProviderCreate , ProviderUpdate
from app.core.deps import get_current_user, Depends,role_required

class ProviderService:

    def create_provider(self, data: ProviderCreate):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)


        languages_json = json.dumps(data.languages)
        specialty_json = json.dumps(data.specialty)
        cur.execute("insert into users (full_name,email,phone,password_hash,role,dob,gender,language_pref,is_verified) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
         (data.name,data.email,data.phone,None,"provider",data.dob,data.gender,data.language_pref,True))
        user_id = cur.lastrowid
      
        sql = """
            INSERT INTO providers 
            (user_id,name,email, license_number, verification_status, specialty, 
             experience_years, languages, consultation_fee, bio, profile_photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
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
            data.bio, 
            data.profile_photo
        )

        cur.execute(sql, values)
        conn.commit()
        
        new_id = cur.lastrowid
        
        return {
            "id": new_id, 
            "verification_status": "pending",
            "languages": data.languages,
            **data.dict()
        }
    def get_provider_by_id(self, provider_id: int):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM providers WHERE id=%s", (provider_id,))
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

        return provider
    
    def list_providers(self, limit: int = 10, offset: int = 0, name: Optional[str] = None, 
                       specialty: Optional[str] = None, min_price: Optional[Decimal] = None, 
                       max_price: Optional[Decimal] = None, min_experience: Optional[int] = None,
                       availability: Optional[str] = None):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM providers WHERE 1=1"
        params = []
        
        if name:
            query += " AND name LIKE %s"
            params.append(f"%{name}%")
            
        if specialty:
            query += " AND specialty LIKE %s"
            params.append(f"%{specialty}%")
            
        if min_price:
            query += " AND consultation_fee >= %s"
            params.append(min_price)
            
        if max_price:
            query += " AND consultation_fee <= %s"
            params.append(max_price)
            
        if min_experience:
            query += " AND experience_years >= %s"
            params.append(min_experience)
            
        if availability == 'today':
            query += " AND id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND DATE(start_time) = CURDATE())"
        elif availability == 'tomorrow':
            query += " AND id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND DATE(start_time) = CURDATE() + INTERVAL 1 DAY)"
        elif availability == 'this_week':
            query += " AND id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND YEARWEEK(start_time, 1) = YEARWEEK(CURDATE(), 1))"
        elif availability == 'this_month':
            query += " AND id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND YEAR(start_time) = YEAR(CURDATE()) AND MONTH(start_time) = MONTH(CURDATE()))"
        elif availability:
            # Assume availability is a specific date string, e.g. 'YYYY-MM-DD'
            query += " AND id IN (SELECT provider_id FROM appointment_slots WHERE is_available=1 AND is_booked=0 AND DATE(start_time) = %s)"
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