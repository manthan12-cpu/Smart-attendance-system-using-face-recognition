import json
from src.database.connection import get_connection

def dump_all():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SHOW TABLES")
    tables = [list(r.values())[0] for r in cursor.fetchall()]
    
    schema = {}
    for t in tables:
        cursor.execute(f"DESCRIBE {t}")
        schema[t] = cursor.fetchall()
        
    with open("all_schema.json", "w") as f:
        json.dump(schema, f, indent=2, default=str)

if __name__ == "__main__":
    dump_all()
