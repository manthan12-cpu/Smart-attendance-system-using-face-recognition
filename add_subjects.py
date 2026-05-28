import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.database.connection import get_connection

conn = get_connection()
cursor = conn.cursor()

# Add 2 new unique ME subjects for Dr. Vikram Singh (professor_id=4)
cursor.execute("INSERT INTO subjects (subject_name, professor_id) VALUES ('Machine Design', 4)")
sid1 = cursor.lastrowid
cursor.execute("INSERT INTO subjects (subject_name, professor_id) VALUES ('Engineering Mechanics', 4)")
sid2 = cursor.lastrowid
print(f"Created subjects: Machine Design (ID {sid1}), Engineering Mechanics (ID {sid2})")

# Enroll his 5 ME students (rolls 301-305) into both new subjects
cursor.execute("SELECT student_id FROM students WHERE roll_number IN ('301','302','303','304','305')")
ids = [r[0] for r in cursor.fetchall()]
for sid in [sid1, sid2]:
    for student_id in ids:
        cursor.execute("INSERT INTO enrollments (student_id, subject_id) VALUES (%s, %s)", (student_id, sid))

conn.commit()
print(f"Enrolled {len(ids)} students into both new subjects. Done!")
cursor.close()
conn.close()
