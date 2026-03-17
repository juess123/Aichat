import json

from model.embedding import encode
from database.memory_db import insert_memory, update_memory
from core.keyword import extract_keywords
from memory.extractor import extract_memories_with_llm
from memory.filter import is_valid_memory
from memory.scorer import search_similar_memories
from memory.merger import merge_content


def generate_memories(conversation_text):

    memories = extract_memories_with_llm(conversation_text)

    for m in memories:

        content = m.get("content", "").strip()

        if not is_valid_memory(content):
            continue

        importance = m.get("importance", 0.5)

        if importance < 0.5:
            continue

        keywords = m.get("keywords")
        if not keywords:
            keywords = ",".join(extract_keywords(content))

        embedding = encode(content)

        # ===== 🔥 Top-K 相似记忆 =====
        candidates = search_similar_memories(embedding, top_k=3)

        if candidates:
            best = candidates[0]
            similarity = best["similarity"]
        else:
            best = None
            similarity = 0

        # ===== 🔥 决策逻辑 =====

        if best and similarity > 0.9:

            print("Update memory (high similarity)")

            update_memory(
                memory_id=best["id"],
                content=merge_content(best["content"], content),
                importance=max(best["importance"], importance),
                emotion=m.get("emotion", "neutral")
            )

        elif best and similarity > 0.75:

            print("Moderate similarity → decide")

            # 👉 如果新信息更重要 → 更新
            if importance > best["importance"]:

                update_memory(
                    memory_id=best["id"],
                    content=merge_content(best["content"], content),
                    importance=importance,
                    emotion=m.get("emotion", "neutral")
                )

            else:
                print("Insert (new branch)")

                insert_memory(
                    content=content,
                    keywords=keywords,
                    importance=importance,
                    emotion=m.get("emotion", "neutral"),
                    mtype=m.get("type", "fact"),
                    embedding=json.dumps(embedding),
                    parent_id=best["id"]   # 🔥 建立关系
                )

        else:

            print("Insert (new memory)")

            insert_memory(
                content=content,
                keywords=keywords,
                importance=importance,
                emotion=m.get("emotion", "neutral"),
                mtype=m.get("type", "fact"),
                embedding=json.dumps(embedding),
                parent_id=None
            )