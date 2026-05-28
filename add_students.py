import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.database.connection import get_connection

def add_more_students():
    conn = get_connection()
    cursor = conn.cursor()
    
    new_students = [
        ('Suraj Singh',      '306', 'suraj@gmail.com',  '9000000021', 'Mechanical Engineering', 2, None),
        ('Yash Patil',       '307', 'yash@gmail.com',   '9000000022', 'Mechanical Engineering', 2, None),
        ('Manoj Kumar',      '308', 'manoj@gmail.com',  '9000000023', 'Mechanical Engineering', 2, None),
        ('Deepika Padukone', '309', 'deepika@gmail.com','9000000024', 'Mechanical Engineering', 2, None),
        ('Anil Kapoor',      '310', 'anil@gmail.com',   '9000000025', 'Mechanical Engineering', 2, None)
    ]
    
    # Insert students
    cursor.executemany("""
        INSERT INTO students (full_name, roll_number, email, phone, department, year, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, new_students)
    
    # Fetch their IDs
    cursor.execute("SELECT student_id FROM students WHERE department = 'Mechanical Engineering' AND roll_number IN ('306','307','308','309','310')")
    new_ids = cursor.fetchall()
    
    # Enroll them in subjects 8 and 9
    enrollments = []
    for sid in new_ids:
        enrollments.append((sid[0], 8))
        enrollments.append((sid[0], 9))
    
    cursor.executemany("INSERT INTO enrollments (student_id, subject_id) VALUES (%s, %s)", enrollments)
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    add_more_students()
    print("5 new distinct Mechanical Engineering students successfully generated and enrolled!")
