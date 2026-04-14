"""
db_connector.py
Handles MySQL database connections, query execution, and automatic schema initialization.
"""
import mysql.connector
from mysql.connector import Error
import bcrypt
from config import DB_CONFIG

def get_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        raise Exception(f"Database connection error: {e}")

def execute_query(query: str, params: tuple = None, fetch: bool = False):
    """Executes INSERT, UPDATE, DELETE, or SELECT queries (if fetch=True)."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            return cursor.fetchall()

        conn.commit()
        return True
    except Error as e:
        print(f"Error executing query: {e}")
        return [] if fetch else False
    finally:
        cursor.close()
        conn.close()

def fetch_query(query: str, params: tuple = None, fetchone: bool = False):
    """Executes a SELECT query and fetches results."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetchone:
            return cursor.fetchone()
        else:
            return cursor.fetchall()
    except Error as e:
        print(f"Error fetching data: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def init_db():
    """
    Initializes the database structure.
    Creates the database, tables, and default content/admin if missing.
    """
    try:
        # 1. Connect to MySQL Server
        server_config = DB_CONFIG.copy()
        db_name = server_config.pop("database")

        server_conn = mysql.connector.connect(**server_config)
        cursor = server_conn.cursor()

        # 2. Create Database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        server_conn.commit()
        cursor.close()
        server_conn.close()

        # 3. Connect to the specific database
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # ── Create Tables ───────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                disease VARCHAR(100) NOT NULL,
                risk_level VARCHAR(50) NOT NULL,
                symptoms TEXT,
                ai_response TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255),
                action_type VARCHAR(100),
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_content (
                section_name VARCHAR(100) PRIMARY KEY,
                content TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diseases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                icon VARCHAR(10)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symptoms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                disease_id INT,
                symptom_name VARCHAR(255) NOT NULL,
                weight INT DEFAULT 1,
                FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE CASCADE
            )
        """)

        # ── Seed Default About Content ────────────────────────────────────────
        cursor.execute("""
            INSERT IGNORE INTO app_content (section_name, content) 
            VALUES ('about_purpose', 'MedPredict AI is an intelligent, user-friendly disease prediction system designed to bridge the gap between initial symptom onset and clinical consultation.')
        """)

        # ── Seed Default Admin Account ────────────────────────────────────────
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']

        if user_count == 0:
            # Create a default admin if the database is completely empty
            hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role) 
                VALUES (%s, %s, %s, %s)
            """, ("Super Admin", "admin@medpredict.com", hashed_pw, "admin"))

        conn.commit()
        cursor.close()
        conn.close()

    except Error as e:
        raise Exception(f"Failed to initialize database schema: {e}")