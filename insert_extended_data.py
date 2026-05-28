import mysql.connector

def main():
    db = mysql.connector.connect(host='127.0.0.1', user='root', password='root123', database='smart_attendance')
    cursor = db.cursor()

    # 1. Insert Professors
    cursor.execute("INSERT IGNORE INTO professors (full_name, email) VALUES (%s, %s)", ('Dr. Anjali Deshmukh', 'anjali.deshmukh@college.edu'))
    cursor.execute("INSERT IGNORE INTO professors (full_name, email) VALUES (%s, %s)", ('Dr. Vikram Singh', 'vikram.singh@college.edu'))

    cursor.execute("SELECT professor_id FROM professors WHERE email = 'anjali.deshmukh@college.edu'")
    prof1_id = cursor.fetchone()[0]
    cursor.execute("SELECT professor_id FROM professors WHERE email = 'vikram.singh@college.edu'")
    prof2_id = cursor.fetchone()[0]

    # 2. Insert Subjects
    subjects = [
        ('Web Development', prof1_id),
        ('Data Structures', prof1_id),
        ('Thermodynamics', prof2_id),
        ('Fluid Mechanics', prof2_id)
    ]
    cursor.executemany("INSERT IGNORE INTO subjects (subject_name, professor_id) VALUES (%s, %s)", subjects)
    
    cursor.execute("SELECT subject_id, subject_name FROM subjects WHERE professor_id IN (%s, %s)", (prof1_id, prof2_id))
    new_subject_ids = {row[1]: row[0] for row in cursor.fetchall()}

    # 3. Insert Students
    students = [
        ('Arjun Kapoor', '201', 'arjun@gmail.com', '9000000011', 'Information Technology', 2, None),
        ('Neha Sharma', '202', 'neha@gmail.com', '9000000012', 'Information Technology', 2, None),
        ('Rohan Das', '203', 'rohan@gmail.com', '9000000013', 'Information Technology', 2, None),
        ('Priya Singh', '204', 'priya@gmail.com', '9000000014', 'Information Technology', 2, None),
        ('Amit Patel', '205', 'amit@gmail.com', '9000000015', 'Information Technology', 2, None),
        ('Rahul Verma', '301', 'rahul@gmail.com', '9000000016', 'Mechanical Engineering', 2, None),
        ('Sneha Gupta', '302', 'sneha@gmail.com', '9000000017', 'Mechanical Engineering', 2, None),
        ('Vivek Kumar', '303', 'vivek@gmail.com', '9000000018', 'Mechanical Engineering', 2, None),
        ('Pooja Yadav', '304', 'pooja@gmail.com', '9000000019', 'Mechanical Engineering', 2, None),
        ('Karan Raj', '305', 'karan@gmail.com', '9000000020', 'Mechanical Engineering', 2, None)
    ]
    
    cursor.executemany("INSERT IGNORE INTO students (full_name, roll_number, email, phone, department, year, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s)", students)
    
    # 4. Enrollments
    cursor.execute("SELECT student_id, department FROM students WHERE roll_number IN ('201', '202', '203', '204', '205', '301', '302', '303', '304', '305')")
    new_students = cursor.fetchall()
    
    enrollments = []
    for s_id, dept in new_students:
        if dept == 'Information Technology':
            enrollments.append((s_id, new_subject_ids['Web Development']))
            enrollments.append((s_id, new_subject_ids['Data Structures']))
        else:
            enrollments.append((s_id, new_subject_ids['Thermodynamics']))
            enrollments.append((s_id, new_subject_ids['Fluid Mechanics']))
            
    # Try inserting individually with ignore
    for e in enrollments:
        cursor.execute("INSERT IGNORE INTO enrollments (student_id, subject_id) VALUES (%s, %s)", e)

    # 5. Lecture Sessions
    # Delete old sessions for these subjects just in case to avoid duplicates causing confusion
    for sid in new_subject_ids.values():
        cursor.execute("DELETE FROM lecture_sessions WHERE subject_id = %s", (sid,))

    sessions = [
        (new_subject_ids['Web Development'], '2025-08-01', '10:00:00', '11:00:00'),
        (new_subject_ids['Web Development'], '2025-08-02', '10:00:00', '11:00:00'),
        (new_subject_ids['Thermodynamics'], '2025-08-01', '12:00:00', '13:00:00'),
        (new_subject_ids['Thermodynamics'], '2025-08-03', '12:00:00', '13:00:00')
    ]
    cursor.executemany("INSERT INTO lecture_sessions (subject_id, session_date, start_time, end_time) VALUES (%s, %s, %s, %s)", sessions)
    
    cursor.execute("SELECT session_id, subject_id FROM lecture_sessions WHERE subject_id IN (%s, %s)", (new_subject_ids['Web Development'], new_subject_ids['Thermodynamics']))
    new_sessions = cursor.fetchall()
    
    web_dev_sessions = [s[0] for s in new_sessions if s[1] == new_subject_ids['Web Development']]
    thermo_sessions = [s[0] for s in new_sessions if s[1] == new_subject_ids['Thermodynamics']]
    
    # 6. Attendance Logs
    attendance = []
    it_students = [s[0] for s in new_students if s[1] == 'Information Technology']
    me_students = [s[0] for s in new_students if s[1] == 'Mechanical Engineering']
    
    if web_dev_sessions:
        for idx, s_id in enumerate(it_students):
            status = 'Present' if idx < 3 else 'Absent'
            attendance.append((web_dev_sessions[0], s_id, status))
            
    if thermo_sessions:
        for idx, s_id in enumerate(me_students):
            status = 'Present' if idx < 4 else 'Late'
            attendance.append((thermo_sessions[0], s_id, status))
            
    # clear old ones just in case
    for w in web_dev_sessions + thermo_sessions:
        cursor.execute("DELETE FROM attendance_logs WHERE session_id = %s", (w,))

    cursor.executemany("INSERT INTO attendance_logs (session_id, student_id, status) VALUES (%s, %s, %s)", attendance)
    
    db.commit()
    print("Insertion complete")

if __name__ == '__main__':
    main()
