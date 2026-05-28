from src.services.attendance_service import start_session, record_attendance, end_session, get_student_attendance
from src.services.report_service import generate_monthly_report
from datetime import datetime

if __name__ == "__main__":
    # --- Quick attendance lookup for a student ---
    student_id = input("Enter student ID to view attendance: ").strip()
    records = get_student_attendance(student_id)
    if records:
        for r in records:
            print(r)
    else:
        print("No attendance records found for this student.")

    # --- Manual test: start a session, mark a few students, end it ---
    subject_id = 1
    session_id = start_session(subject_id)

    record_attendance(session_id, 1)
    record_attendance(session_id, 2)
    record_attendance(session_id, 3)

    end_session(session_id)

    # --- Generate a report for the current month ---
    today = datetime.today()
    generate_monthly_report(subject_id, today.year, today.month)