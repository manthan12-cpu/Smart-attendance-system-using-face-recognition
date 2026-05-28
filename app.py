from flask import Flask, send_from_directory, jsonify, Response, request
from flask.json.provider import DefaultJSONProvider
import os
import time
import json
from datetime import datetime, timedelta, date
from decimal import Decimal

from src.database.connection import get_connection
from src.services.attendance_service import start_session, end_session
from src.services.face_recognition_service import generate_frames, stop_smart_camera
from src.services.student_service import list_students
from src.services.report_service import generate_monthly_report


class CustomJSONProvider(DefaultJSONProvider):
    """Handle MySQL types that aren't JSON-serializable by default."""
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, timedelta):
            return str(o)
        return super().default(o)


app = Flask(__name__)
app.json = CustomJSONProvider(app)

# Store session in memory for web API linkage
active_session_id = None

# ─── Static File Serving ──────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# ─── Auth API ─────────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def api_login():
    """Verify professor credentials against the database."""
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({"success": False, "message": "Please enter both email and password."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT professor_id, full_name, email FROM professors WHERE email = %s", (email,))
        professor = cursor.fetchone()
        cursor.close()
        conn.close()

        if professor:
            return jsonify({
                "success": True,
                "professor": {
                    "id": professor['professor_id'],
                    "name": professor['full_name'],
                    "email": professor['email']
                }
            })
        else:
            return jsonify({"success": False, "message": "Invalid email or password."}), 401
    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        return jsonify({"success": False, "message": "Server error during login."}), 500

# ─── Students API ─────────────────────────────────────────────

@app.route('/api/students')
def api_students():
    """Return students from the database for a specific professor or subject."""
    professor_id = request.args.get('professor_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if subject_id:
            cursor.execute("""
                SELECT s.student_id, s.roll_number, s.full_name, s.department, s.year
                FROM students s
                JOIN enrollments e ON s.student_id = e.student_id
                WHERE e.subject_id = %s
                ORDER BY CAST(s.roll_number AS UNSIGNED)
            """, (subject_id,))
        elif professor_id:
            cursor.execute("""
                SELECT DISTINCT s.student_id, s.roll_number, s.full_name, s.department, s.year
                FROM students s
                JOIN enrollments e ON s.student_id = e.student_id
                JOIN subjects sub ON e.subject_id = sub.subject_id
                WHERE sub.professor_id = %s
                ORDER BY CAST(s.roll_number AS UNSIGNED)
            """, (professor_id,))
        else:
            cursor.execute("SELECT student_id, roll_number, full_name, department, year FROM students ORDER BY CAST(roll_number AS UNSIGNED)")
        
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "students": students})
    except Exception as e:
        print(f"[STUDENTS ERROR] {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ─── Subjects API ─────────────────────────────────────────────

@app.route('/api/subjects')
def api_subjects():
    """Return subjects from the database for a specific professor."""
    professor_id = request.args.get('professor_id', type=int)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        if professor_id:
            cursor.execute("SELECT MIN(subject_id) as subject_id, subject_name, professor_id FROM subjects WHERE professor_id = %s GROUP BY subject_name, professor_id ORDER BY subject_name", (professor_id,))
        else:
            cursor.execute("SELECT MIN(subject_id) as subject_id, subject_name, professor_id FROM subjects GROUP BY subject_name, professor_id ORDER BY subject_name")
        subjects = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "subjects": subjects})
    except Exception as e:
        print(f"[SUBJECTS ERROR] {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ─── Dashboard Stats API ─────────────────────────────────────

@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """Return aggregate stats for the dashboard (total students, subjects, today's sessions)."""
    professor_id = request.args.get('professor_id', type=int)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if professor_id:
            cursor.execute("""
                SELECT COUNT(DISTINCT st.roll_number) as count
                FROM enrollments e
                JOIN subjects s ON e.subject_id = s.subject_id
                JOIN students st ON e.student_id = st.student_id
                WHERE s.professor_id = %s
            """, (professor_id,))
            total_students = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(DISTINCT subject_name) as count FROM subjects WHERE professor_id = %s", (professor_id,))
            total_subjects = cursor.fetchone()['count']

            cursor.execute("""
                SELECT COUNT(ls.session_id) as count 
                FROM lecture_sessions ls
                JOIN subjects s ON ls.subject_id = s.subject_id
                WHERE ls.session_date = CURDATE() AND s.professor_id = %s
            """, (professor_id,))
            sessions_today = cursor.fetchone()['count']
        else:
            cursor.execute("SELECT COUNT(DISTINCT roll_number) as count FROM students")
            total_students = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(DISTINCT subject_name) as count FROM subjects")
            total_subjects = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM lecture_sessions WHERE session_date = CURDATE()")
            sessions_today = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "stats": {
                "total_students": total_students,
                "total_subjects": total_subjects,
                "sessions_today": sessions_today
            }
        })
    except Exception as e:
        print(f"[STATS ERROR] {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ─── Reports API ──────────────────────────────────────────────

@app.route('/api/reports')
def api_reports():
    """Return monthly attendance report for a given subject, year, month."""
    subject_id = request.args.get('subject_id', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not subject_id or not year or not month:
        now = datetime.now()
        subject_id = subject_id or 1
        year = year or now.year
        month = month or now.month

    try:
        results = generate_monthly_report(subject_id, year, month)
        # Clean up results for JSON (convert any non-serializable types)
        clean_results = []
        for row in results:
            clean_results.append({
                "roll_number": row['roll_number'],
                "full_name": row['full_name'],
                "total_sessions": int(row['total_sessions']) if row['total_sessions'] else 0,
                "presents": (int(row['presents']) if row['presents'] else 0) + (int(row['lates']) if row['lates'] else 0),
                "absents": int(row['absents']) if row['absents'] else 0,
                "percentage": round((int(row['presents'] or 0) + int(row['lates'] or 0)) / int(row['total_sessions']) * 100, 1) if row['total_sessions'] else 0
            })

        return jsonify({"success": True, "report": clean_results, "subject_id": subject_id, "year": year, "month": month})
    except Exception as e:
        print(f"[REPORTS ERROR] {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/reports/sessions')
def api_reports_sessions():
    """Return per-session P/A matrix for all students for a given subject/year/month (for Excel export)."""
    subject_id = request.args.get('subject_id', type=int)
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if not subject_id or not year or not month:
        now = datetime.now()
        subject_id = subject_id or 1
        year = year or now.year
        month = month or now.month

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Get all sessions for this subject/month
        cursor.execute("""
            SELECT session_id, session_date, start_time
            FROM lecture_sessions
            WHERE subject_id = %s AND YEAR(session_date) = %s AND MONTH(session_date) = %s
            ORDER BY session_date, start_time
        """, (subject_id, year, month))
        sessions = cursor.fetchall()

        # Get all students enrolled in subject
        cursor.execute("""
            SELECT s.student_id, s.roll_number, s.full_name
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            WHERE e.subject_id = %s
            ORDER BY s.roll_number
        """, (subject_id,))
        students = cursor.fetchall()

        # Get all attendance logs for those sessions
        if sessions:
            session_ids = [s['session_id'] for s in sessions]
            format_strings = ','.join(['%s'] * len(session_ids))
            cursor.execute(f"""
                SELECT student_id, session_id, status
                FROM attendance_logs
                WHERE session_id IN ({format_strings})
            """, session_ids)
            logs = cursor.fetchall()
        else:
            logs = []

        cursor.close()
        conn.close()

        # Build lookup: {student_id: {session_id: status}}
        att_map = {}
        for log in logs:
            sid = log['student_id']
            sess = log['session_id']
            if sid not in att_map:
                att_map[sid] = {}
            att_map[sid][sess] = log['status']

        # Build result
        session_labels = [f"Session {i+1}\n{s['session_date'].strftime('%d-%b')}" for i, s in enumerate(sessions)]
        result_rows = []
        for student in students:
            row = {
                "roll_number": student['roll_number'],
                "full_name": student['full_name'],
            }
            for i, sess in enumerate(sessions):
                key = f"session_{i+1}"
                status = att_map.get(student['student_id'], {}).get(sess['session_id'])
                if status in ('Present', 'Late'):
                    row[key] = 'P'
                elif status == 'Absent':
                    row[key] = 'A'
                else:
                    row[key] = '-'
            result_rows.append(row)

        return jsonify({
            "success": True,
            "session_labels": session_labels,
            "rows": result_rows
        })
    except Exception as e:
        print(f"[SESSIONS REPORT ERROR] {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ─── Session Attendance (Live) API ────────────────────────────

@app.route('/api/attendance/mark', methods=['POST'])
def api_mark_attendance():
    """Manually mark/toggle attendance from the frontend."""
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    student_id = data.get('student_id')
    status = data.get('status')
    
    if not session_id or not student_id or not status:
        return jsonify({"success": False, "message": "Missing parameters."}), 400
        
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT log_id FROM attendance_logs WHERE session_id=%s AND student_id=%s", (session_id, student_id))
        if cursor.fetchone():
            cursor.execute("UPDATE attendance_logs SET status=%s WHERE session_id=%s AND student_id=%s", (status, session_id, student_id))
        else:
            cursor.execute("INSERT INTO attendance_logs (session_id, student_id, status) VALUES (%s, %s, %s)", (session_id, student_id, status))
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"[MARK ERROR] {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/attendance/session/<int:session_id>')
def api_session_attendance(session_id):
    """Return all attendance logs for an active/completed session."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT al.student_id, s.roll_number, s.full_name, al.status
            FROM attendance_logs al
            JOIN students s ON al.student_id = s.student_id
            WHERE al.session_id = %s
            ORDER BY s.roll_number
        """, (session_id,))
        logs = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "attendance": logs})
    except Exception as e:
        print(f"[SESSION ATT ERROR] {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ─── Camera / Session APIs ────────────────────────────────────

@app.route('/api/start_camera', methods=['POST'])
def api_start_camera():
    global active_session_id
    if active_session_id is not None:
        return jsonify({"status": "error", "message": "Session running"}), 400

    data = request.get_json(silent=True) or {}
    subject_id = data.get('subject_id', 1)

    active_session_id = start_session(subject_id)
    return jsonify({"status": "success", "session_id": active_session_id})

@app.route('/api/video_feed')
def video_feed():
    global active_session_id
    if active_session_id is None:
        return "No active session", 400
    return Response(generate_frames(active_session_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/end_camera', methods=['POST'])
def api_end_camera():
    global active_session_id
    if active_session_id is not None:
        stop_smart_camera()
        time.sleep(0.5)
        end_session(active_session_id)
        sid = active_session_id
        active_session_id = None
        return jsonify({"status": "success", "session_id": sid})

    return jsonify({"status": "success"})

@app.route('/api/active_session')
def api_active_session():
    """Return the currently active session ID if any."""
    return jsonify({"active_session_id": active_session_id})

if __name__ == '__main__':
    print("Starting Smart Attendance App on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True)
