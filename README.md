<img width="1600" height="812" alt="image" src="https://github.com/user-attachments/assets/38633c43-8932-4cb8-a48a-a0737c16c248" />
<img width="1600" height="813" alt="image1" src="https://github.com/user-attachments/assets/be1bc449-be23-4be7-b237-78aa9ff0eb42" />
<img width="1600" height="803" alt="image 3" src="https://github.com/user-attachments/assets/5939b711-b4e4-40b5-93c7-b875197c6ffb" />
<img width="1600" height="812" alt="image 4" src="https://github.com/user-attachments/assets/05658b89-6121-4cd2-b987-f6a45774aa21" />

# SmartAttendance AI Face Recognition Attendance System

![Python](https://img.shields.io/badge/Python-3.10-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-4.8-green) ![Flask](https://img.shields.io/badge/Flask-2.3-lightgrey) ![License](https://img.shields.io/badge/License-MIT-brightgreen)

SmartAttend is a real-time face recognition attendance system for colleges and corporates. It detects faces via webcam, verifies liveness through blink detection, and marks attendance automatically no hardware required.

---

## Features
- Real-time face recognition via standard webcam (no special hardware)
- Liveness detection using Eye Aspect Ratio (EAR) blink verification
- Session-scoped enrollment only registered students recognized
- Web dashboard with List View, Grid View, and Reports
- Encoding cache for instant startup after first run
- MJPEG live stream embedded in browser via Flask

---

## Tech Stack
| Layer | Tech |
|-------|------|
| Backend | Python 3.10, Flask, face_recognition (dlib), OpenCV |
| Frontend | HTML/CSS/JS, MJPEG streaming |
| Database | MySQL |
| Recognition | 128-dim face encodings, Euclidean distance |

---

## Quick Start
```bash
git clone https://github.com/manthan12-cpu/SmartAttend
cd SmartAttend
pip install -r requirements.txt
cp .env.example .env
mysql -u root -p < database/schema.sql
python app.py
```
## Project Structure
```
SmartAttend/
├── src/
│   ├── services/
│   │   ├── face_recognition_service.py   # camera + recognition engine
│   │   └── attendance_service.py
│   └── database/
│       └── connection.py
├── templates/                            # Flask HTML pages
├── static/                               # CSS, JS
├── dataset/                              # add student photos here
├── database/
│   └── schema.sql
├── app.py
├── requirements.txt
└── README.md
```


## My Role
I built the camera and recognition engine (`face_recognition_service.py`) MJPEG streaming, face encoding pipeline, liveness detection, encoding cache, and session-scoped recognition.

## Authors
- **Manthan Masurkar** — Camera & recognition engine
- **Rishit Poojari** — Frontend & dashboard
- **Rutvik Mainkar** — Backend & database
- **Soham Salunke** — Debugging
