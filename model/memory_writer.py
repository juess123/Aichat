import json
import re
from model.llama_client import call_llama
from database.memory_db import insert_memory
from database.memory_db import memory_exists, extract_keywords

bad_patterns = [
    "conversation began",
    "the conversation started",
    "you asked me",
    "memory extraction system",
    "this conversation"
]


def generate_memories(conversation_text):
    prompt = f"""
    You are a memory extraction system.
    Your job is to extract long-term memories about the USER only.
    A good memory is a stable fact about the user such as:
    - interests
    - goals
    - preferences
    - emotional tendencies
    - important life facts
    DO NOT store:
    - system instructions
    - descriptions about the AI
    - conversation structure
    - statements like "the conversation started"
    - statements like "you asked me"

    Conversation:
    {conversation_text}

    Extract 1-3 meaningful long-term memories.

    Good examples:

    [
    {{
    "content": "Scout wants to improve English speaking skills.",
    "keywords": "english,learning,language",
    "importance": 0.8,
    "emotion": "motivated",
    "type": "goal"
    }},
    {{
    "content": "Scout enjoys discussing programming and intelligent systems.",
    "keywords": "programming,ai,technology",
    "importance": 0.7,
    "emotion": "neutral",
    "type": "interest"
    }}
    ]

    Bad examples (DO NOT output):

    [
    "I am a memory extraction system",
    "The conversation began with a question",
    "You asked me to help"
    ]

    Return ONLY valid JSON.

    Rules:
    - Output must be a JSON array
    - No explanations
    - No text before JSON
    - No text after JSON

    If no meaningful memory exists return [].

    Format:

    [
    {{
    "content": "...",
    "keywords": "keyword1,keyword2",
    "importance": 0.7,
    "emotion": "neutral",
    "type": "fact"
    }}
    ]
    """
    result = call_llama(prompt)

    print("===== MEMORY RAW OUTPUT =====")
    print(result)

    try:

        match = re.search(r'\[.*\]', result, re.S)

        if not match:
            print("No JSON found in LLM output")
            return

        json_text = match.group()

        memories = json.loads(json_text)

        for m in memories:

            content = m.get("content", "").strip()

            if not content:
                continue

            # 过滤垃圾记忆
            if any(p in content.lower() for p in bad_patterns):
                continue

            # 避免重复记忆
            if memory_exists(content):
                print("Skip duplicate memory")
                continue

            keywords = m.get("keywords")

            # 如果模型没给关键词，就自动生成
            if not keywords:
                keywords = ",".join(extract_keywords(content))

            insert_memory(
                content=content,
                keywords=keywords,
                importance=m.get("importance", 0.5),
                emotion=m.get("emotion", "neutral"),
                mtype=m.get("type", "fact")
            )

    except Exception as e:

        print("Memory parse failed:", e)