import sqlite3
from config import DB_PATH
def load_user_profile():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT key,value FROM user_profile")

    rows = cursor.fetchall()

    conn.close()

    profile = {}

    for key,value in rows:

        if key not in profile:
            profile[key] = []

        profile[key].append(value)

    return profile