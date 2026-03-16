import sqlite3
from config import DB_PATH


def memory_exists(content):
    """
    检查数据库是否已经存在类似记忆
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM memories
        WHERE content LIKE ?
        LIMIT 1
    """, (f"%{content[:30]}%",))

    row = cursor.fetchone()

    conn.close()

    return row is not None


def extract_keywords(text):
    """
    从文本提取关键词
    """
    words = text.lower().split()

    keywords = []

    for w in words:
        if len(w) > 3:
            keywords.append(w)

    return keywords


def search_memories(user_input, limit=5):
    """
    根据用户输入搜索相关记忆
    """

    keywords = extract_keywords(user_input)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    memories = []

    for k in keywords:

        cursor.execute("""
            SELECT id, content
            FROM memories
            WHERE keywords LIKE ?
            ORDER BY importance DESC
            LIMIT ?
        """, (f"%{k}%", limit))

        rows = cursor.fetchall()

        for r in rows:

            memories.append(r[1])

            # 更新访问统计
            cursor.execute("""
                UPDATE memories
                SET access_count = access_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (r[0],))

    conn.commit()
    conn.close()

    return memories


def insert_memory(content, keywords=None, importance=0.5, emotion="neutral", mtype="fact"):
    """
    写入长期记忆
    """

    if memory_exists(content):
        print("Memory already exists, skip.")
        return

    if keywords is None:
        keywords = ",".join(extract_keywords(content))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO memories
        (type, content, keywords, importance, emotion)
        VALUES (?, ?, ?, ?, ?)
    """, (mtype, content, keywords, importance, emotion))

    conn.commit()
    conn.close()

    print("Memory stored:", content)