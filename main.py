from src.services.attendance_service import start_session, end_session, get_student_attendance
from src.services.report_service import generate_monthly_report
from src.services.face_recognition_service import run_smart_camera
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

    # --- Start a session and launch the Smart Camera ---
    subject_id = 1
    session_id = start_session(subject_id)

    print("\nStarting the Face Recognition Smart Camera for this session...")
    run_smart_camera(session_id)

    end_session(session_id)

    # --- Generate a report for the current month ---
    today = datetime.now()
    generate_monthly_report(subject_id, today.year, today.month)