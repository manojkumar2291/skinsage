# app/database/mysql_conn.py
import mysql.connector
from mysql.connector import Error as MySQLDBError
import logging

logger = logging.getLogger(__name__)

from app.core.config import settings

def get_db_connection():
    """Returns a new MySQL connection."""
    try:
        conn = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        return conn
    except MySQLDBError as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        # Use a custom exception for connection failure
        raise ConnectionError("Failed to connect to the MySQL database. Check DB configuration and status.") from e





def insert_image_record(file_name: str, file_url: str):
    """Inserts a new image record (URL) into the database."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO uploaded_images (file_name, file_url, analysis_status) 
                VALUES (%s, %s, %s)
                """,
                (file_name, file_url, "")
            )
            conn.commit()
    except ConnectionError:
        logger.warning("Image record insertion skipped due to connection failure.")
    except Exception as e:
        logger.error(f"Error inserting record into MySQL: {e}")
        if conn and conn.is_connected():
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            conn.close()