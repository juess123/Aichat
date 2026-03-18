import sqlite3
import datetime
from config import DB_PATH


def decay_unused_memories(days=7, decay=0.1, min_importance=0.1):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    now = datetime.datetime.now()

    cursor.execute("""
        SELECT id, importance, last_accessed, created_at, last_decay_check
        FROM memory_nodes
    """)

    rows = cursor.fetchall()

    for mid, importance, last_accessed, created_at, last_decay_check in rows:

        # ===== 1️⃣ 上次使用时间 =====
        base_time = last_accessed or created_at

        try:
            base_time = datetime.datetime.fromisoformat(base_time)
        except:
            continue

        # ===== 2️⃣ 是否真的长期未使用 =====
        delta_since_access = (now - base_time).days

        if delta_since_access < days:
            continue   # ❌ 最近用过，不衰减

        # ===== 3️⃣ 上次衰减时间（防重复）=====
        if last_decay_check:
            try:
                last_check = datetime.datetime.fromisoformat(last_decay_check)
            except:
                last_check = base_time
        else:
            last_check = base_time

        # ===== 4️⃣ 只计算“新增时间” =====
        delta_since_decay = (now - last_check).days

        periods = delta_since_decay // days

        if periods <= 0:
            continue

        # ===== 5️⃣ 执行衰减 =====
        total_decay = periods * decay

        new_importance = max(min_importance, importance - total_decay)

        cursor.execute("""
            UPDATE memory_nodes
            SET importance = ?, last_decay_check = ?
            WHERE id = ?
        """, (new_importance, now.isoformat(), mid))

    conn.commit()
    conn.close()