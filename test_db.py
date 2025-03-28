# test_db.py
from db.database import Database

def test_db_creation():
    db = Database(db_path="gantt.db")
    db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = db.cursor.fetchall()
    print("Tables in database:", tables)
    db.close()

if __name__ == "__main__":
    test_db_creation()
