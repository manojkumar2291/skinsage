import json
import re
import uuid
from typing import List, Tuple
from pathlib import Path
from datetime import datetime

# Added Request and Response for cookie handling
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, Request, Response 
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool
from app.core.deps import get_current_user
import requests
from app.schemas.analysis import AIChatResponse

from app.core.config import settings
from app.database.mysql_conn import get_db_connection as get_connection
from app.services import image_proc, llm_proc
from collections import namedtuple

# Define the helper class here
Credentials = namedtuple('Credentials', ['credentials'])

router = APIRouter()

def parse_summary_to_array(text):
    data_array = []
    text = text.replace(", Condition:", "\nCondition:")
    lines = text.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            data_array.append({
                "label": key.strip().title(), 
                "value": value.strip()
            })
    return data_array

def extract_category_and_path(messages_list: list) -> Tuple[str, str]:
    """
    Parses chat history.
    Returns a tuple: (subfolder_path, raw_category_type)
    Example: ('skin_issue/warts', 'Skin') or ('hair_issue/dandruff', 'Hair')
    """
    category = "uncategorized"
    condition = "general"
    raw_cat_type = "general" 

    pattern = r"Category:\s*(.*?),\s*Condition:\s*(.*)"

    for msg in messages_list:
        # Sometimes msg might be a string representation of a dict
        if isinstance(msg, str):
            try:
                msg = json.loads(msg)
            except:
                continue
                
        content = msg.get("content", "")
        if "Category:" in content and "Condition:" in content:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                raw_cat = match.group(1).strip()
                raw_cond = match.group(2).strip()
                
                raw_cat_type = raw_cat

                category = image_proc.sanitize_filename(raw_cat)
                condition = image_proc.sanitize_filename(raw_cond)
                break 
    
    return f"{category}/{condition}", raw_cat_type


@router.post("/chat")
async def analyze_endpoint(
    request: Request,   # <--- Added to access cookies/headers
    response: Response, # <--- Added to set cookies
    messages: str = Form(...),
    image_files: List[UploadFile] = File(...),
):
    user_id = None
    guest_id = None

    try:
        auth_header = request.headers.get("Authorization")
        print("Authorization header:", auth_header)

        if auth_header:
            token = auth_header.replace("Bearer ", "")
            token_obj = Credentials(credentials=token)
            curr_user = await run_in_threadpool(get_current_user, token_obj) 
            if curr_user:
                user_id = curr_user['id']
    except Exception as e:
        print("Error getting current user:", e)
        pass 

    if not user_id:
        guest_id = request.cookies.get("guest_id") 
        if not guest_id:
            guest_id = str(uuid.uuid4()) 
           
            response.set_cookie(key="guest_id", value=guest_id, httponly=True, max_age=2592000)
    

    try:
        messages_json = json.loads(messages)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in 'messages' field")

    if not (1 <= len(image_files) <= 3):
        raise HTTPException(status_code=400, detail="You must upload between 1 and 3 images.")

    subfolder_path, category_type = extract_category_and_path(messages_json)
    
    valid_images_payload = [] 

    for i, file in enumerate(image_files):
        try:
            image_bytes = await file.read()
        except Exception as e:
            print(f"ERROR: Failed reading file {file.filename}: {e}")
            raise HTTPException(status_code=400, detail=f"Failed reading file {file.filename}")
            
        # Very important: When form-data gets parsed, sometimes empty file inputs 
        # get sent by clients.
        if not image_bytes or len(image_bytes) == 0:
            print(f"WARNING: File {file.filename} is empty (0 bytes). Skipping.")
            continue
            
        print(f"DEBUG: Read {len(image_bytes)} bytes from {file.filename}")

        try:
            processed_image = image_proc.normalize_image_bytes(image_bytes)
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to normalize image {file.filename}: {e}")
            raise HTTPException(
                status_code=400, 
                detail=f"Uploaded file '{file.filename}' is not a valid or readable image."
            )

        is_valid, validation_msg = llm_proc.validate_image_is_dermatological(
            processed_image, 
            expected_category=category_type
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Image '{file.filename}' rejected: {validation_msg}"
            )
        
        valid_images_payload.append({
            "bytes": image_bytes,
            "filename": file.filename or f"upload_{i}.jpg",
            "processed": processed_image
        })

    if not valid_images_payload:
        raise HTTPException(status_code=400, detail="No valid images were provided in the upload.")

    print(f"📂 Validation passed. Saving {len(valid_images_payload)} images to: uploads/{subfolder_path}") 
    
    vision_model_content = []
    image_metadata = []

    for item in valid_images_payload:
        unique_filename, server_url_path = await image_proc.save_image_to_disk(
            item["bytes"], 
            item["filename"],
            subfolder=subfolder_path
        )
        
        image_metadata.append({
            "file_name": unique_filename,
            "server_url_path": server_url_path
        })
        
        image_data_uri = image_proc.encode_image_to_base64_datauri(
            item["processed"], 
            filename_hint=item["filename"]
        )
        vision_model_content.append({"type": "image_url", "image_url": {"url": image_data_uri}})

    def get_msg_role(m):
        if isinstance(m, str):
            try: m = json.loads(m)
            except: return ""
        return m.get('role', '')

    def get_msg_content(m):
        if isinstance(m, str):
            try: m = json.loads(m)
            except: return str(m)
        return m.get('content', '')

    user_prompt_text = (
        "=== USER'S COMPLETE SYMPTOM HISTORY ===\n"
        "The following is the structured conversation history containing the user's condition selection and diagnostic answers:\n\n"
        + "\n".join([f"- {get_msg_role(msg).upper()}: {get_msg_content(msg)}" for msg in messages_json if get_msg_role(msg) == 'user']) +
        "\n\n=== END OF HISTORY ===\n\n"
        "Now, analyze the images based on the provided history and the structured system prompt."
    )
    
    vision_model_content.insert(0, {"type": "text", "text": user_prompt_text})

    analysis_messages = [
        {"role": "system", "content": settings.ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": vision_model_content}
    ]

    try:
        response_llm = await run_in_threadpool(llm_proc.call_openrouter_model, analysis_messages) # Renamed var to avoid conflict
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"OpenRouter API request failed: {str(e)}")

    if response_llm.status_code != 200:
        error_detail = response_llm.text[:500] 
        raise HTTPException(status_code=400, detail=f"Model Provider API error: {response_llm.status_code} - {error_detail}")

    data = response_llm.json()
    raw_analysis = data.get('choices', [{}])[0].get('message', {}).get('content', "I couldn't complete the analysis.")
    
    recommendation_needed = False
    analysis_text = raw_analysis

    match = re.search(r"Recommendation_Required:\s*(Yes|No)", raw_analysis, re.IGNORECASE)
    if match:
        recommendation_status = match.group(1).lower()
        analysis_text = raw_analysis.replace(match.group(0), "").strip()
        if recommendation_status == 'yes':
            recommendation_needed = True

    new_id = None
    try:
        photo_urls = ",".join([item['server_url_path'] for item in image_metadata])
        summary_text = "Analysis completed by AI"
        
        red_flag = 1 if recommendation_needed else 0

        def db_insert_ai_chat():
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            
            cur.execute(
                """
                INSERT INTO ai_chats (
                    user_id, guest_id, input_text, ai_response, summary, 
                    red_flag, photo_url, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    user_id,    # Can be None now
                    guest_id,   # Can be None now
                    "\n".join([get_msg_content(msg) for msg in messages_json if get_msg_role(msg) == 'user']),
                    analysis_text,
                    summary_text,
                    red_flag,
                    photo_urls
                )
            )
            # ------------------------------------------------
            
            chat_id = cur.lastrowid
            conn.commit()
            chat_id = cur.lastrowid
            
            # --- AUTO-CREATE CASE ---
            if user_id:
                try:
                    case_sql = """
                        INSERT INTO cases 
                        (user_id, ai_chat_id, title, symptoms, status, created_at)
                        VALUES (%s, %s, %s, %s, 'open', NOW())
                    """
                    # Use a default title or derive from summary
                    case_title = f"AI Analysis - {datetime.now().strftime('%Y-%m-%d')}"
                    case_symptoms = "\n".join([get_msg_content(msg) for msg in messages_json if get_msg_role(msg) == 'user'])
                    
                    cur.execute(case_sql, (user_id, chat_id, case_title, case_symptoms))
                    conn.commit()
                    print(f"DEBUG: Auto-created Case for User {user_id}, Chat {chat_id}")
                except Exception as ex:
                    print(f"ERROR: Failed to auto-create case: {ex}")
            # ------------------------

            cur.close()
            conn.close()
            return chat_id

        new_id = await run_in_threadpool(db_insert_ai_chat)
        print(new_id)
    except Exception as e:
        print(f"Error inserting AI chat record: {e}")
        
    return JSONResponse({
        "reply": analysis_text, 
        "recommendation_needed": recommendation_needed,
        "images_processed": len(image_files),
        "chat_id": new_id,
        "guest_mode": (user_id is None) # <--- Added flag to tell frontend if user is guest
    })

@router.get("/{chat_id}", response_model=AIChatResponse)
def retrieve_ai_chat(
    chat_id: int, 
    current_user = Depends(get_current_user)
):
    db = get_connection()
    cursor = db.cursor()
    
    
    cursor.execute("""
        SELECT id, user_id, input_text, ai_response, summary, created_at, photo_url, red_flag
        FROM ai_chats WHERE id = %s
    """, (chat_id,))
    
    chat = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages_constructed = [
        {"role": "user", "content":parse_summary_to_array(chat[2]) },       
        {"role": "assistant", "content": chat[3]}   
    ]

    return {
        "id": chat[0],
        "user_id": chat[1],
        "summary": chat[4],     
        "messages": messages_constructed,
        "created_at": chat[5],  
        "photo_url": [chat[6]],   
        "red_flag": bool(chat[7]) 
    }

# @router.get("/health")
# def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "model": settings.MODEL_NAME,
#         "api_configured": bool(settings.OPENROUTER_API_KEY),
#         "validation_enabled": bool(settings.HUGGINGFACE_API_KEY)
#     }