SmartAttend — AI Face Recognition Attendance System
Python 3.10 OpenCV Flask License: MIT
SmartAttend is a real-time face recognition attendance system for colleges and corporates. It detects faces via webcam, verifies liveness through blink detection, and marks attendance automatically — no hardware required.

[demo.gif — screen recording goes here]
Features
Real-time face recognition via standard webcam (no special hardware)
Liveness detection using Eye Aspect Ratio (EAR) blink verification
Session-scoped enrollment — only registered students recognized
Web dashboard with List View, Grid View, and Reports
Encoding cache for instant startup after first run
MJPEG live stream embedded in browser via Flask
Tech stack
Backend: Python 3.10, Flask, face_recognition (dlib), OpenCV
Frontend: HTML/CSS/JS, MJPEG streaming
Database: MySQL
Recognition: 128-dim face encodings, Euclidean distance matching
Quick start
git clone https://github.com/YOUR_USERNAME/SmartAttend
cd SmartAttend
pip install -r requirements.txt
cp .env.example .env        # fill in your DB details
mysql -u root -p < database/schema.sql
python app.py
Project structure
SmartAttend/
├── src/services/face_recognition_service.py   # camera + recognition engine
├── src/services/attendance_service.py
├── src/database/connection.py
├── templates/          # Flask HTML pages
├── static/             # CSS, JS
├── dataset/            # add student photos here (see dataset/README.md)
└── database/schema.sql # DB setup
My role
I built the camera and recognition engine (face_recognition_service.py) — MJPEG streaming, face encoding pipeline, liveness detection, encoding cache, and session-scoped recognition.

Authors
Manthan Masurkar — Camera & recognition engine
Rishit poojari — Frontend & dashboard
Rutvik Mainkar — Backend & database
Soham salunke — Debugging
