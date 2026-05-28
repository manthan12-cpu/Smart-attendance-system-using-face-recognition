import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.database.connection import get_connection

def clean_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Remove attendance logs for generated students
    cursor.execute("DELETE FROM attendance_logs WHERE student_id > 20")
    # Remove enrollments for generated students
    cursor.execute("DELETE FROM enrollments WHERE student_id > 20")
    # Remove generated students
    cursor.execute("DELETE FROM students WHERE student_id > 20")
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    clean_db()
    print("Database deduplicated and restricted to initial 20 base students successfully.")
