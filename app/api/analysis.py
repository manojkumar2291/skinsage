import json
import re
from typing import List
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool
import requests

from app.core.config import settings
from app.database.mysql_conn import get_db_connection as get_connection
from app.services import image_proc, llm_proc

router = APIRouter()

def extract_folder_path_from_messages(messages_list: list) -> str:
    """
    Parses chat history to find 'Category: X, Condition: Y'.
    Returns a path string like 'skin_issue/warts' or 'uncategorized/general'.
    """
    category = "uncategorized"
    condition = "general"

    # Regex to capture "Category: [Group 1], Condition: [Group 2]"
    # (?i) makes it case insensitive
    pattern = r"Category:\s*(.*?),\s*Condition:\s*(.*)"

    for msg in messages_list:
        content = msg.get("content", "")
        # Check if this message line has the classification data
        if "Category:" in content and "Condition:" in content:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                raw_cat = match.group(1).strip()
                raw_cond = match.group(2).strip()
                
                # Sanitize the names to be folder-safe
                category = image_proc.sanitize_filename(raw_cat)
                condition = image_proc.sanitize_filename(raw_cond)
                break # Stop after finding the classification message
    
    # Return path format: skin_issue/warts
    return f"{category}/{condition}"




@router.post("/analyze")
async def analyze_endpoint(
    messages: str = Form(...),
    image_files: List[UploadFile] = File(...)
):
    # 1. Parse conversation history
    try:
        messages_json = json.loads(messages)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in 'messages' field")

    if not (1 <= len(image_files) <= 3):
        raise HTTPException(status_code=400, detail="You must upload between 1 and 3 images.")

    # --- Determine Subfolder Path ---
    subfolder_path = extract_folder_path_from_messages(messages_json)
    print(f"📂 Saving images to: uploads/{subfolder_path}") 

    vision_model_content = []
    image_metadata = [] 

    # 2. Image Processing Loop
    for i, file in enumerate(image_files):
        image_bytes = await file.read()
        await file.seek(0)

        # Save Image to Disk
        unique_filename, server_url_path = await image_proc.save_image_to_disk(
            image_bytes, 
            file.filename or f"upload_{i}.jpg",
            subfolder=subfolder_path
        )
        
        image_metadata.append({
            "file_name": unique_filename,
            "server_url_path": server_url_path
        })
        
        # Process image for LLM
        processed_image = image_proc.normalize_image_bytes(image_bytes)

        is_valid, validation_msg = llm_proc.validate_image_is_dermatological(processed_image)
        if not is_valid:
            print(f"Validation failed for file {i+1}: {validation_msg}. Proceeding anyway.")

        image_data_uri = image_proc.encode_image_to_base64_datauri(processed_image, filename_hint=file.filename or f"upload_{i}.jpg")
        vision_model_content.append({"type": "image_url", "image_url": {"url": image_data_uri}})

    # 3. Build final message for vision model
    user_prompt_text = (
        "=== USER'S COMPLETE SYMPTOM HISTORY ===\n"
        "The following is the structured conversation history containing the user's condition selection and diagnostic answers:\n\n"
        + "\n".join([f"- {msg['role'].upper()}: {msg['content']}" for msg in messages_json if msg['role'] == 'user']) +
        "\n\n=== END OF HISTORY ===\n\n"
        "Now, analyze the images based on the provided history and the structured system prompt."
    )
    vision_model_content.insert(0, {"type": "text", "text": user_prompt_text})

    analysis_messages = [
        {"role": "system", "content": settings.ANALYSIS_SYSTEM_PROMPT},
        {"role": "user", "content": vision_model_content}
    ]

    # 4. Call vision model
    try:
        response = await run_in_threadpool(llm_proc.call_openrouter_model, analysis_messages)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"API request failed: {str(e)}")

    if response.status_code != 200:
        error_detail = response.text[:500] 
        raise HTTPException(status_code=502, detail=f"Model API error: {response.status_code} - {error_detail}")

    # 5. Extract AI analysis
    data = response.json()
    raw_analysis = data.get('choices', [{}])[0].get('message', {}).get('content', "I couldn't complete the analysis.")
    
    recommendation_needed = False
    analysis_text = raw_analysis

    match = re.search(r"Recommendation_Required:\s*(Yes|No)", raw_analysis, re.IGNORECASE)
    if match:
        recommendation_status = match.group(1).lower()
        analysis_text = raw_analysis.replace(match.group(0), "").strip()
        if recommendation_status == 'yes':
            recommendation_needed = True

    # 6. Insert AI chat record into ai_chats (single insertion)
    try:
        photo_urls = ",".join([item['server_url_path'] for item in image_metadata])
        summary_text = "Analysis completed by AI"
        red_flag = 1 if recommendation_needed else 0

        def db_insert_ai_chat():
            conn = get_connection()
       
            cur = conn.cursor(dictionary=True)
            print (summary_text)
            cur.execute(
                """
                INSERT INTO ai_chats (
                    user_id,
                    input_text,
                    ai_response,
                    summary,
                    red_flag,
                    photo_url,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    1,  # Replace with actual user_id if dynamic
                    "\n".join([msg['content'] for msg in messages_json if msg['role'] == 'user']),
                    analysis_text,
                    summary_text,
                    red_flag,
                    photo_urls
                )
            )
            conn.commit()

        await run_in_threadpool(db_insert_ai_chat)

    except Exception as e:
        print(f"Error inserting AI chat record: {e}")

    # 7. Return structured JSON

    return JSONResponse({"reply": analysis_text, "recommendation_needed": recommendation_needed})






@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": settings.MODEL_NAME,
        "api_configured": bool(settings.OPENROUTER_API_KEY),
        "validation_enabled": bool(settings.HUGGINGFACE_API_KEY)
    }