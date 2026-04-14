"""
admin_tools.py
Command-line backend controller for MedPredict AI.
Run this directly in your terminal: python admin_tools.py
"""
import sys
import io
# Force UTF-8 output so emoji characters print correctly on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import bcrypt
import mysql.connector
from config import DB_CONFIG
from db_connector import init_db  # Imports your main database builder

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def full_database_setup():
    """Builds base tables and adds role/status columns."""
    print("\n⚙️ Running full database setup & upgrade...")
    try:
        # 1. Build core tables using your existing db_connector logic
        print("📦 Initializing core tables...")
        init_db()
        print("✅ Core tables verified.")

        # 2. Add extra columns specifically needed for Admin tools
        conn = get_db()
        cursor = conn.cursor()

        # Add role column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'")
            print("✅ Added 'role' column.")
        except mysql.connector.Error as e:
            if e.errno == 1060: # Duplicate column error
                print("⚡ 'role' column already exists.")
            else: raise e

        # Add status column
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active'")
            print("✅ Added 'status' column.")
        except mysql.connector.Error as e:
            if e.errno == 1060:
                print("⚡ 'status' column already exists.")
            else: raise e

        conn.commit()
        print("🎉 Database setup and upgrade complete!")
    except Exception as e:
        print(f"❌ Error during setup: {e}")

def create_admin():
    print("\n👑 Create Admin Account")
    name = input("Enter Admin Name: ")
    email = input("Enter Admin Email: ")
    password = input("Enter Password: ")

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, status) VALUES (%s, %s, %s, 'admin', 'active')",
            (name, email, hashed)
        )
        conn.commit()
        print(f"✅ Admin account '{email}' created successfully!")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")

def list_users():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, role, status FROM users")
        users = cursor.fetchall()
        print("\n📊 Current Platform Users:")
        print("-" * 75)
        print(f"{'ID':<5} | {'Name':<15} | {'Email':<25} | {'Role':<8} | {'Status'}")
        print("-" * 75)
        for u in users:
            print(f"{u['id']:<5} | {u['name']:<15} | {u['email']:<25} | {u['role']:<8} | {u['status']}")
        print("-" * 75)
    except Exception as e:
        print(f"❌ Error fetching users: {e}")

def change_user_status():
    print("\n🛑 Manage a User")
    email = input("Enter the user's email: ")
    action = input("Enter action (suspend/activate/delete): ").lower()

    try:
        conn = get_db()
        cursor = conn.cursor()
        if action == "delete":
            cursor.execute("DELETE FROM users WHERE email = %s", (email,))
            print(f"🗑️ User {email} completely deleted.")
        elif action in ["suspend", "activate"]:
            status = 'suspended' if action == 'suspend' else 'active'
            cursor.execute("UPDATE users SET status = %s WHERE email = %s", (status, email))
            print(f"✅ User {email} has been {status}.")
        else:
            print("❌ Invalid action.")
        conn.commit()
    except Exception as e:
        print(f"❌ Error updating user: {e}")

def reset_user_password():
    print("\n🔑 Force Password Reset")
    email = input("Enter the user's email: ")
    new_password = input("Enter new password: ")

    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed, email))
        if cursor.rowcount > 0:
            print(f"✅ Password for {email} has been updated successfully!")
        else:
            print(f"❌ User with email {email} not found.")
        conn.commit()
    except Exception as e:
        print(f"❌ Error resetting password: {e}")

def view_system_stats():
    print("\n📈 System Statistics")
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as c FROM users")
        users = cursor.fetchone()['c']

        cursor.execute("SELECT COUNT(*) as c FROM history")
        history = cursor.fetchone()['c']

        cursor.execute("SELECT COUNT(*) as c FROM diseases")
        diseases = cursor.fetchone()['c']

        print("-" * 40)
        print(f"👥 Total Registered Users:  {users}")
        print(f"📋 Total AI Predictions:    {history}")
        print(f"🔬 Total Disease Profiles:  {diseases}")
        print("-" * 40)
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")

def seed_default_data():
    """Injects sample disease data into the DB for testing."""
    print("\n🌱 Seeding Database with Sample Diseases...")
    try:
        conn = get_db()
        cursor = conn.cursor()

        # Seed Disease
        cursor.execute("INSERT IGNORE INTO diseases (name, description, icon) VALUES ('Diabetes', 'Chronic condition affecting blood sugar.', '🩸')")
        cursor.execute("SELECT id FROM diseases WHERE name = 'Diabetes'")
        disease_id = cursor.fetchone()[0]

        # Seed Symptoms
        symptoms = [('Frequent urination', 2), ('Increased thirst', 2), ('Fatigue', 1), ('Blurred vision', 2)]
        for sym, weight in symptoms:
            cursor.execute("INSERT IGNORE INTO symptoms (disease_id, symptom_name, weight) VALUES (%s, %s, %s)", (disease_id, sym, weight))

        conn.commit()
        print("✅ Sample disease 'Diabetes' and symptoms added!")
    except Exception as e:
        print(f"❌ Error seeding data: {e}")

def wipe_history():
    print("\n⚠️ WARNING: This will permanently delete ALL prediction history in the database.")
    confirm = input("Type 'DELETE' to confirm: ")
    if confirm == "DELETE":
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history")
            conn.commit()
            print("🗑️ All prediction history has been wiped clean.")
        except Exception as e:
            print(f"❌ Error wiping history: {e}")
    else:
        print("🛑 Action cancelled.")

if __name__ == "__main__":
    while True:
        print("""
    🏥 MedPredict AI — Backend Admin Terminal
    -----------------------------------------
    1. Full Database Setup (Fixes missing tables & columns!)
    2. Create an Admin Account
    3. View All Users
    4. Manage a User (Suspend/Activate/Delete)
    5. Reset a User's Password
    6. View System Statistics
    7. Seed Sample Diseases & Symptoms
    8. Wipe All Prediction History
    9. Exit
        """)
        choice = input("Select an option (1-9): ")
        if choice == '1': full_database_setup()
        elif choice == '2': create_admin()
        elif choice == '3': list_users()
        elif choice == '4': change_user_status()
        elif choice == '5': reset_user_password()
        elif choice == '6': view_system_stats()
        elif choice == '7': seed_default_data()
        elif choice == '8': wipe_history()
        elif choice == '9':
            print("\nExiting Admin Tools. Goodbye! 👋")
            sys.exit()
        else: print("❌ Invalid choice. Please select 1-9.")