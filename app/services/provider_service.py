import json
from fastapi import HTTPException
from app.database.mysql_conn import get_db_connection as get_connection
from app.schemas.provider import ProviderCreate

class ProviderService:

    def create_provider(self, data: ProviderCreate):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # 1. Validate: Does this user exist?
        cur.execute("SELECT id, role FROM users WHERE id=%s", (data.user_id,))
        user = cur.fetchone()
        if not user:
            raise HTTPException(404, "User with this ID does not exist")

        # 2. Validate: Is this user already a provider?
        cur.execute("SELECT id FROM providers WHERE user_id=%s", (data.user_id,))
        if cur.fetchone():
            raise HTTPException(400, "This user is already a provider")

        # 3. Serialize languages list to JSON string
        languages_json = json.dumps(data.languages)

        # 4. Insert data
        sql = """
            INSERT INTO providers 
            (user_id,name, license_number, verification_status, specialty, 
             experience_years, languages, consultation_fee, bio, profile_photo)
            VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Since Admin is creating it, we can default to 'pending' or 'verified'. 
        # Usually, it starts as 'pending' until documents are double-checked, 
        # or 'verified' if the admin has already checked them offline. 
        # Let's stick to 'pending' as the default safety net.
        values = (
            data.user_id, 
            data.name,
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
        
        # MySQL connector might return JSON column as a string, we need to parse it back to a list
        if isinstance(provider['languages'], str):
             provider['languages'] = json.loads(provider['languages'])

        return provider
    
    def list_providers(self):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM providers")
        providers = cur.fetchall()

        # Parse JSON for all results
        for p in providers:
            if isinstance(p['languages'], str):
                p['languages'] = json.loads(p['languages'])
                
        return providers