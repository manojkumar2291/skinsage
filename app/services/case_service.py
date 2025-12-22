import json
from fastapi import HTTPException
from datetime import datetime
from app.database.mysql_conn import get_db_connection as get_connection
from app.schemas.case import CaseCreate

class CaseService:

    def create_case(self, user_id: int, data: CaseCreate):
        print(f"DEBUG: START create_case {data}")
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # 1. Validate AI Chat Ownership if provided
        if data.ai_chat_id:
            print(f"DEBUG: Checking Chat {data.ai_chat_id}")
            conn.commit() # Ensure we see latest data
            cur.execute("SELECT user_id FROM ai_chats WHERE id=%s", (data.ai_chat_id,))
            chat = cur.fetchone()
            print(f"DEBUG: Chat Found: {chat}")
            if not chat:
                 raise HTTPException(404, "Linked AI Chat not found")
            if chat['user_id'] != user_id:
                 raise HTTPException(403, "You cannot link an AI Chat that does not belong to you")
      

        # 2. Insert Query
        sql = """
            INSERT INTO cases 
            (user_id, ai_chat_id, title, symptoms,  status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Default status 'open' as per your schema default
        values = (
            user_id, 
            data.ai_chat_id, 
            data.title, 
            data.symptoms, 
            
            "open", 
            datetime.now()
        )

        cur.execute(sql, values)
        conn.commit()
        
        new_id = cur.lastrowid
        
        return {
            "id": new_id,
            "user_id": user_id,
            "ai_chat_id": data.ai_chat_id,
            "title": data.title,
            "symptoms": data.symptoms,
           
            "status": "open",
            "created_at": datetime.now()
        }

    def list_user_cases(self, user_id: int):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
      
        cur.execute("SELECT * FROM cases WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
        cases = cur.fetchall()

       
        return cases

    def get_case_details(self, case_id: int, user_id: int, user_role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("SELECT * FROM cases WHERE id=%s", (case_id,))
        case = cur.fetchone()
        
        if not case:
            raise HTTPException(404, "Case not found")

        # Security: Only owner or admin/doctor can view
        if case['user_id'] != user_id and user_role not in ['doctor', 'admin']:
            raise HTTPException(403, "Not authorized to view this case")
        
      
        return case

    def update_case_status(self, case_id: int, status: str, user_id: int, user_role: str):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Check existence and permissions
        cur.execute("SELECT id, user_id FROM cases WHERE id=%s", (case_id,))
        case = cur.fetchone()
        
        if not case:
            raise HTTPException(404, "Case not found")
        
       
        if case['user_id'] != user_id and user_role not in ['doctor', 'admin']:
            raise HTTPException(403, "Not authorized to update this case")

        cur.execute("UPDATE cases SET status=%s WHERE id=%s", (status, case_id))
        conn.commit()

        return {"status": status}