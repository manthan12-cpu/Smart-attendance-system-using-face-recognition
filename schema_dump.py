import json
from src.database.connection import get_connection

def dump():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DESCRIBE attendance_logs")
    rows = cursor.fetchall()
    with open("schema.txt", "w") as f:
        f.write(json.dumps(rows, indent=2, default=str))

if __name__ == "__main__":
    dump()
