import sqlite3
from config import DB_PATH


def load_personality():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT model, trait, value, description FROM personality"
    )

    rows = cursor.fetchall()
    conn.close()

    personality = {}

    for model, trait, value, desc in rows:

        if model not in personality:
            personality[model] = {}

        if value is not None:
            personality[model][trait] = value
        else:
            personality[model][trait] = desc

    return personality