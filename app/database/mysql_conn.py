# app/database/mysql_conn.py
import mysql.connector
from mysql.connector import Error as MySQLDBError

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
        print(f"Error connecting to MySQL database: {e}")
        # Use a custom exception for connection failure
        raise ConnectionError("Failed to connect to the MySQL database. Check DB configuration and status.") from e


def initialize_db():
    """Initializes the MySQL database and creates the table."""
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Table Creation Query
            # 1. USERS TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # 2. IMAGES TABLE
            cur.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_images (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    file_name VARCHAR(255) NOT NULL UNIQUE,
                    file_url VARCHAR(255) NOT NULL,
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            """)
            conn.commit()
            print("Database Tables Initialized (Users & Images)")
    except ConnectionError:
        print("Database initialization skipped due to connection failure.")
    except Exception as e:
        print(f"Error during MySQL database initialization: {e}")
        if conn and conn.is_connected():
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            conn.close()


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
        print("Image record insertion skipped due to connection failure.")
    except Exception as e:
        print(f"Error inserting record into MySQL: {e}")
        if conn and conn.is_connected():
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            conn.close()