import numpy as np
from database.memory_db import load_all_memories
import datetime

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


import datetime


def compute_recency(memory):

    if not memory.get("last_accessed"):
        return 1.0

    last_time = datetime.datetime.fromisoformat(memory["last_accessed"])
    delta = (datetime.datetime.now() - last_time).total_seconds()

    # 简单衰减（你可以以后优化）
    return 1 / (1 + delta / 3600)   # 1小时衰减


def search_similar_memories(query_embedding, top_k=5):

    memories = load_all_memories()

    scored = []

    for m in memories:

        emb = np.array(m["embedding"])
        similarity = cosine_similarity(query_embedding, emb)

        importance = m.get("importance", 0.5)
        recency = compute_recency(m)

        final_score = similarity * importance * recency

        m_copy = m.copy()
        m_copy["similarity"] = similarity
        m_copy["score"] = final_score

        scored.append(m_copy)

    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:top_k]