import json
import re
from model.llama_client import call_llama


def extract_memories_with_llm(conversation_text):

    prompt = f"""
Extract long-term memories about the USER.

Conversation:
{conversation_text}

Return JSON array:

[
  {{
    "content": "...",
    "keywords": "a,b,c",
    "importance": 0.7,
    "emotion": "neutral",
    "type": "fact"
  }}
]

Rules:
- Only important memories
- Ignore small talk
- No explanation
- Output ONLY JSON
- importance must be between 0 and 1

If no memory found return []
"""

    result = call_llama(prompt)

    print("===== RAW LLM OUTPUT =====")
    print(result)

    try:
        match = re.search(r'\[.*\]', result, re.S)

        if not match:
            print("No JSON found")
            return []

        json_text = match.group()
        memories = json.loads(json_text)

        cleaned = []

        for m in memories:
            if not isinstance(m, dict):
                continue

            content = m.get("content", "").strip()
            if not content:
                continue

            # ===== 🔥 importance 处理（核心修改） =====
            try:
                importance = float(m.get("importance", 0.5))
            except:
                importance = 0.5

            # 限制范围
            importance = max(0.0, min(1.0, importance))

            # 类型加权（非常关键）
            mtype = m.get("type", "fact")

            if mtype == "goal":
                importance *= 1.2
            elif mtype == "belief":
                importance *= 1.1
            elif mtype == "emotion":
                importance *= 0.8

            # 再限制一次
            importance = min(1.0, importance)

            cleaned.append({
                "content": content,
                "keywords": m.get("keywords", ""),
                "importance": importance,
                "emotion": m.get("emotion", "neutral"),
                "type": mtype
            })

        return cleaned

    except Exception as e:
        print("Memory parse failed:", e)
        return []