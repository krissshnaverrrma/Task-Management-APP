import sqlite3
import os
DATABASE_FILE = 'database.db'
SQL_COMMANDS = [
    "ALTER TABLE user ADD COLUMN otp VARCHAR(6);",
    "ALTER TABLE user ADD COLUMN otp_expiration DATETIME;"
]
def run_db_migration():
    if not os.path.exists(DATABASE_FILE):
        print(f"Error: Database file '{DATABASE_FILE}' not found. Ensure you are in the correct directory.")
        return
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        print(f"Connected to {DATABASE_FILE}. Attempting to add new columns...")
        for command in SQL_COMMANDS:
            try:
                cursor.execute(command)
                print(f"-> Successfully executed: {command}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e) or "already exists" in str(e):
                    print(f"-> Skipped: Column already exists.")
                else:
                    raise e
        conn.commit()
        print("\n✅ Database migration successful! New OTP columns added.")
    except sqlite3.Error as e:
        print(f"\n❌ A database error occurred: {e}")    
    finally:
        if conn:
            conn.close()
if __name__ == '__main__':
    run_db_migration()