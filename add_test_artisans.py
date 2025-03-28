# add_test_artisans.py
import sqlite3

def add_test_artisans():
    # Connect to the database
    conn = sqlite3.connect("gantt.db")
    cursor = conn.cursor()

    # Test artisans data with profile pictures
    test_artisans = [
        ("John Smith", "Carpenter", "Available", "resources/artisans/john_smith.png"),
        ("Aisha Khan", "Electrician", "Busy", "resources/artisans/aisha_khan.png"),
        ("Thabo Mokoena", "Plumber", "Available", "resources/artisans/thabo_mokoena.png"),
        ("Sarah Jones", "Painter", "On Leave", "resources/artisans/sarah_jones.png"),
        ("Michael Brown", "Mason", "Available", "resources/artisans/michael_brown.png"),
    ]

    # Insert test artisans
    for artisan in test_artisans:
        cursor.execute(
            "INSERT INTO artisans (name, skill, availability, profile_picture) VALUES (?, ?, ?, ?)",
            artisan
        )

    # Commit and close
    conn.commit()
    conn.close()
    print("Test artisans added successfully!")

if __name__ == "__main__":
    add_test_artisans()