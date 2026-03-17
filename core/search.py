import sqlite3
import json
import datetime
from config import DB_PATH
from model.embedding import encode
from database.memory_db import record_memory_access
import numpy as np
ALL_CONTENTS = []
ALL_IDS = []
ALL_IMPORTANCE = []
ALL_EMBS = []
ALL_TIME = []
ALL_CREATED = []
ALL_PARENT = []
ALL_UPDATED = []
def load_memory_to_ram():
    global ALL_CONTENTS, ALL_EMBS, ALL_IDS, ALL_IMPORTANCE, ALL_TIME, ALL_CREATED

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, content, embedding, importance, last_accessed, created_at, parent_id, last_updated
        FROM memory_nodes
    """)
    rows = cursor.fetchall()
    conn.close()

    ids = []
    contents = []
    embs = []
    importances = []
    last_accesseds = []
    created_ats = []
    parents = []
    updateds = []
    for mid, content, emb_json, importance, last_accessed, created_at, parent_id, last_updated in rows:
        emb = np.array(json.loads(emb_json), dtype=np.float32)
        emb = emb / (np.linalg.norm(emb) + 1e-8)

        ids.append(mid)
        contents.append(content)
        embs.append(emb)
        importances.append(importance)
        last_accesseds.append(last_accessed)
        created_ats.append(created_at)
        parents.append(parent_id)
        updateds.append(last_updated)

    ALL_IDS = ids
    ALL_CONTENTS = contents
    ALL_EMBS = np.vstack(embs) if embs else None
    ALL_IMPORTANCE = importances
    ALL_TIME = last_accesseds
    ALL_CREATED = created_ats
    ALL_PARENT = parents
    ALL_UPDATED = updateds

def keyword_score(query, content):
    q_words = set(query.lower().split())
    c_words = set(content.lower().split())
    overlap = len(q_words & c_words)
    return overlap / (len(q_words) + 1e-6)


def normalize(v):
    return v / (np.linalg.norm(v) + 1e-8)

def simplify_memories(memories):
    return [
        {
            "content": m["content"],
            "created_at": m.get("created_at"),
            "last_accessed": m.get("last_accessed")
        }
        for m in memories
    ]


def compute_recency(last_accessed, created_at, last_updated):

    now = datetime.datetime.now()

    def safe_parse(t):
        if not t:
            return None
        try:
            return datetime.datetime.fromisoformat(t)
        except:
            return None

    times = [
        safe_parse(last_accessed),
        safe_parse(last_updated),
        safe_parse(created_at)
    ]

    times = [t for t in times if t]

    if not times:
        return 1.0

    latest = max(times)

    delta = (now - latest).total_seconds()

    # 半衰：1天衰减
    return 1 / (1 + delta / 86400)


def get_depth(idx):

    depth = 0
    current_parent = ALL_PARENT[idx]

    while current_parent:
        try:
            parent_idx = ALL_IDS.index(current_parent)
        except:
            break

        depth += 1
        current_parent = ALL_PARENT[parent_idx]

    return depth



def search_memory(query, top_k=5, threshold=0.5):
    if ALL_EMBS is None or len(ALL_EMBS) == 0:
        return []

    # 1️⃣ 编码 + 归一化
    query_vec = np.array(encode(query), dtype=np.float32)
    query_vec = normalize(query_vec)

    # 2️⃣ cosine similarity（数据库已归一化）
    scores = ALL_EMBS @ query_vec

    # 3️⃣ 取 top_k
    top_indices = np.argsort(scores)[::-1][:top_k * 3]

    results = []

    for idx in top_indices:
        sim = scores[idx]

        if sim < threshold:
            continue

        content = ALL_CONTENTS[idx]
        mid = ALL_IDS[idx]
        importance = ALL_IMPORTANCE[idx]
        last_accessed = ALL_TIME[idx]
        created_at = ALL_CREATED[idx]
        recency = compute_recency(last_accessed, created_at, ALL_UPDATED[idx])
        k_score = keyword_score(query, content)
        depth = get_depth(idx)
        final_score = (
            sim * 0.6 +
            importance * 0.2 +
            recency * 0.15 +
            depth * 0.05 +
            k_score * 0.1
        )
        record_memory_access(mid, increase_importance=(final_score > 0.6))
        results.append({
            "id": mid,
            "content": content,
            "score": float(final_score),
            "similarity": float(sim),
            "keyword": float(k_score),
            "importance": float(importance),
            "last_accessed": last_accessed,
            "created_at": created_at
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]