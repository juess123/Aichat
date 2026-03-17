import sqlite3
import datetime
import json
from config import DB_PATH


# ===== 查询 =====
def load_all_memories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""SELECT id, content, embedding, importance FROM memory_nodes""")

    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "content": r[1],
            "embedding": json.loads(r[2]),
            "importance": r[3]
        })

    return result


# ===== 插入 =====
def insert_memory(content, keywords, importance, emotion, mtype, embedding, parent_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.datetime.now()

    cursor.execute("""
        INSERT INTO memory_nodes
        (content, keywords, importance, emotion, type, embedding, parent_id, created_at, last_accessed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (content, keywords, importance, emotion, mtype, embedding, now, now))

    conn.commit()
    conn.close()


# ===== 🔴 认知更新（你要加的） =====
def update_memory(memory_id, content, importance, emotion):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.datetime.now()

    cursor.execute("""
        UPDATE memory_nodes
        SET 
            content = ?,
            importance = ?,
            emotion = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (content, importance, emotion, now, memory_id))

    conn.commit()
    conn.close()


# ===== 🟡 使用强化 =====
def record_memory_access(memory_id, increase_importance=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.datetime.now()

    if increase_importance:
        cursor.execute("""
            UPDATE memory_nodes
            SET 
                access_count = access_count + 1,
                last_accessed = ?,
                importance = MIN(importance + 0.05, 1.0)
            WHERE id = ?
        """, (now, memory_id))
    else:
        cursor.execute("""
            UPDATE memory_nodes
            SET 
                access_count = access_count + 1,
                last_accessed = ?
            WHERE id = ?
        """, (now, memory_id))

    conn.commit()
    conn.close()