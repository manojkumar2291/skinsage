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
        cur.execute("insert into users (full_name,email,phone,password_hash,role,dob,gender,language_pref,is_verfied,google_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
         (data.name,data.email,data.phone,None,"provider",data.dob,data.gender,data.language_pref,True,None))
        user_id = cur.lastrowid
      
        sql = """
            INSERT INTO providers 
            (name,email, license_number, verification_status, specialty, 
             experience_years, languages, consultation_fee, bio, profile_photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
        
        values = (
            user_id, 
            data.name,
            data.email,
            data.license_number, 
            "pending", 
            data.specialty, 
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

        return provider
    
    def list_providers(self, limit: int = 10, offset: int = 0, name: Optional[str] = None, 
                       specialty: Optional[str] = None, min_price: Optional[Decimal] = None, 
                       max_price: Optional[Decimal] = None, min_experience: Optional[int] = None):
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
            
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, tuple(params))
        providers = cur.fetchall()

       
        for p in providers:
            if isinstance(p['languages'], str):
                p['languages'] = json.loads(p['languages'])
                
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
        
        params = (
            provider_data.name,
            provider_data.specialty,
            provider_data.consultation_fee,
            provider_data.bio,
            provider_data.experience_years,
            provider_data.languages, # Pass list directly for Postgres
            current_user['id']
        )

        cursor.execute(query, params)
        db.commit()

        return {"msg": "Updated successfully", "status": "success"}