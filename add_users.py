# add_users.py
import sqlite3

def add_users():
    # Connect to the database
    try:
        conn = sqlite3.connect("gantt.db")
        cursor = conn.cursor()
        print("Connected to the database successfully.")
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return

    # List of users to insert (username, password, role)
    users = [
        ("cm_user", "pass123", "Construction Manager"),
        ("manager1", "managerpass1", "Construction Manager"),
        ("viewer1", "viewerpass1", "Viewer"),
        ("artisan1", "artisanpass1", "Artisan"),
        ("admin1", "adminpass1", "Admin"),
    ]

    # Insert users into the database
    for user in users:
        username, password, role = user
        try:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            print(f"Successfully added user: {username}")
        except sqlite3.IntegrityError as e:
            print(f"Error adding user {username}: {e} (Username likely already exists)")
        except sqlite3.Error as e:
            print(f"Error adding user {username}: {e}")

    # Commit the changes and close the connection
    conn.commit()
    print("All users have been processed.")
    cursor.close()
    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    add_users()
