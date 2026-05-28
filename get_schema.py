import mysql.connector

with open('schema_output.txt', 'w') as f:
    db = mysql.connector.connect(host='127.0.0.1', user='root', password='root123', database='smart_attendance')
    cursor = db.cursor()
    for table in ['professors', 'subjects', 'students', 'enrollments', 'lecture_sessions', 'attendance_logs']:
        cursor.execute(f"DESCRIBE {table}")
        columns = [row[0] for row in cursor.fetchall()]
        f.write(f"{table}: {columns}\n")
