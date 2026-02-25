from app.schemas.user import UserUpdate, UserResponse
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from app.core.deps import get_current_user
from app.database.mysql_conn import get_db_connection as get_db
import os
import shutil

router = APIRouter()

@router.put("/user/{user_id}", response_model=UserResponse)
def update_user_details(
    user_id: int, 
    user_data: UserUpdate, 
  
    current_user = Depends(get_current_user)
):
    db = get_db()
    cursor = db.cursor()
    
    # 1. Authorization
    if current_user['id'] != user_id and current_user['role'] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    # 2. Check if user exists
    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Static Update Query
    # COALESCE ensures we only update fields that are not None
    query = """
        UPDATE users
        SET 
            full_name = COALESCE(%s, full_name),
            phone = COALESCE(%s, phone),
            dob = COALESCE(%s, dob),
            gender = COALESCE(%s, gender),
            language_pref = COALESCE(%s, language_pref)
        WHERE id = %s
    """
    
    # We pass the values from the Pydantic model directly
    # If a value is None, SQL uses the existing column value
    params = (
        user_data.full_name,
        user_data.phone,
        user_data.dob,
        user_data.gender,
        user_data.language_pref,
        user_id
    )

    cursor.execute(query, params)
    db.commit()
    
    # Fetch updated user
    cursor.execute("SELECT id, full_name, email, phone, dob, gender, language_pref, profile_photo FROM users WHERE id = %s", (user_id,))
    updated_user = cursor.fetchone()
    return {
        "id": updated_user[0],
        "full_name": updated_user[1],
        "email": updated_user[2],
        "phone": updated_user[3],
        "dob": updated_user[4],
        "gender": updated_user[5],
        "language_pref": updated_user[6],
        "profile_photo": updated_user[7]
    }

@router.post("/user/{user_id}/profile-photo")
def upload_profile_photo(
    user_id: int, 
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    if current_user['id'] != user_id and current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Not authorized to upload photo for this user")
    
    upload_dir = "uploads/profile_photos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{user_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE users SET profile_photo=%s WHERE id=%s", (file_path, user_id))
    db.commit()
    
    return {"msg": "Profile photo uploaded successfully", "profile_photo": file_path}