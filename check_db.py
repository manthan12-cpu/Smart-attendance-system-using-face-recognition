import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.database.connection import get_connection

def check_db():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT st.roll_number, st.full_name, st.student_id 
        FROM enrollments e 
        JOIN subjects s ON e.subject_id = s.subject_id 
        JOIN students st ON e.student_id = st.student_id 
        WHERE s.professor_id = 4
    """)
    rows = cursor.fetchall()
    
    # We want to keep exactly 10 distinct students (2 enrollments each probably = 20 rows, but 10 unique roll numbers)
    # The user says "now it showing 15 do what delete 5 students and change the number to 10"
    unique_rolls = set()
    unique_students = []
    
    to_delete = []
    
    for r in rows:
        if r['roll_number'] not in unique_rolls:
            unique_rolls.add(r['roll_number'])
            unique_students.append(r)
        
    print(f"Total Unique Students Enrolled for Prof 4: {len(unique_students)}")
    for u in unique_students:
        print(f"  {u['roll_number']} - {u['full_name']} (ID: {u['student_id']})")
        
    # If len > 10, let's delete the excess from the database
    if len(unique_students) > 10:
        excess = unique_students[10:]
        excess_ids = [u['student_id'] for u in excess]
        print(f"Deleting {len(excess_ids)} excess students: {excess_ids}")
        for eid in excess_ids:
            cursor.execute("DELETE FROM attendance_logs WHERE student_id = %s", (eid,))
            cursor.execute("DELETE FROM enrollments WHERE student_id = %s", (eid,))
            cursor.execute("DELETE FROM students WHERE student_id = %s", (eid,))
        conn.commit()
        print("Excess deleted. Now there are 10.")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    check_db()
