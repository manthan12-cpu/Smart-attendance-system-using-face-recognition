import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.database.connection import get_connection

def check_db():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT e.subject_id, COUNT(e.student_id) as c
        FROM enrollments e 
        JOIN subjects sub ON e.subject_id=sub.subject_id 
        WHERE sub.professor_id=4
        GROUP BY e.subject_id
    """)
    print("Subject Counts:")
    print(cursor.fetchall())
    
    cursor.execute("""
        SELECT e.subject_id, s.roll_number, s.full_name 
        FROM enrollments e 
        JOIN students s ON e.student_id = s.student_id 
        JOIN subjects sub ON e.subject_id=sub.subject_id 
        WHERE sub.professor_id=4
        ORDER BY e.subject_id, s.roll_number
    """)
    print("All Enrollments:")
    for row in cursor.fetchall():
        print(f"Subject {row['subject_id']}: {row['roll_number']} - {row['full_name']}")

    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_db()
