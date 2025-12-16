from fastapi import APIRouter, HTTPException, Depends
from app.database.mysql_conn import get_db_connection
from app.schemas.content import (
    PageUpsert, PageResponse, PageIDResponse,
    TestimonialCreate, TestimonialListResponse, TestimonialIDResponse
)
import mysql.connector

router = APIRouter()

# ==========================================
#  I. Content & CMS
# ==========================================

# ---------------------------------------------------------
# GET /content/:slug
# Summary: Get public page content
# ---------------------------------------------------------
@router.get("/content/{slug}", response_model=PageResponse)
def get_page_content(slug: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Only fetch if the page is active
        sql = "SELECT title, content, updated_at FROM pages WHERE slug = %s AND is_active = TRUE"
        cursor.execute(sql, (slug,))
        page = cursor.fetchone()
        
        if not page:
            raise HTTPException(status_code=404, detail="Page not found")
            
        return page

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()

# ---------------------------------------------------------
# POST /content
# Summary: Add OR Edit content (Upsert)
# ---------------------------------------------------------
@router.post("/content", response_model=PageIDResponse)
def upsert_content(data: PageUpsert):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        # We use "INSERT ... ON DUPLICATE KEY UPDATE"
        # This acts as a Create if slug is new, or Update if slug exists.
        sql = """
        INSERT INTO pages (slug, title, content, language, is_active, updated_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            content = VALUES(content),
            language = VALUES(language),
            is_active = VALUES(is_active),
            updated_by = VALUES(updated_by)
        """
        
        values = (
            data.slug, data.title, data.content, 
            data.language, data.is_active, data.updated_by
        )
        
        cursor.execute(sql, values)
        conn.commit()
        
        # Determine if it was an insert or update based on row count
        # 1 = Insert, 2 = Update, 0 = No change
        action = "updated" if cursor.rowcount == 2 else "created"
        
        # For updates, lastrowid might not return the correct ID in MySQL depending on driver version,
        # so we fetch the ID by slug to be safe.
        cursor.execute("SELECT id FROM pages WHERE slug = %s", (data.slug,))
        page_id = cursor.fetchone()[0]

        return {"page_id": page_id, "action": action}

    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()


# ==========================================
#  II. Testimonials
# ==========================================

# ---------------------------------------------------------
# GET /testimonials
# Summary: Get list of PUBLIC (Approved) testimonials
# ---------------------------------------------------------
@router.get("/testimonials", response_model=TestimonialListResponse)
def get_testimonials():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Only select APPROVED testimonials
        sql = """
        SELECT id, user_name, feedback, rating, created_at 
        FROM testimonials 
        WHERE approved = TRUE 
        ORDER BY created_at DESC
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        return {"list": rows}

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()

# ---------------------------------------------------------
# POST /testimonials
# Summary: Add new testimonial (Needs admin approval)
# ---------------------------------------------------------
@router.post("/testimonials", response_model=TestimonialIDResponse)
def add_testimonial(data: TestimonialCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor()
    try:
        # Default 'approved' is False (handled by DB default or explicit 0)
        sql = """
        INSERT INTO testimonials (user_name, feedback, rating, approved)
        VALUES (%s, %s, %s, 0)
        """
        
        values = (data.user_name, data.feedback, data.rating)
        
        cursor.execute(sql, values)
        conn.commit()
        
        return {"testimonial_id": cursor.lastrowid}

    except mysql.connector.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {err}")
    finally:
        cursor.close()
        conn.close()