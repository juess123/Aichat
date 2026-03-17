from database.profile_db import load_user_profile
from profiles.profile_builder import build_profile_text

from database.personality_db import load_personality
from profiles.personality_builder import build_personality_text

from core.search import search_memory
from profiles.memory_builder import build_memory_text

from model.llama_client import call_llama_stream, warmup_model
from memory.generator import generate_memories

from core.search import load_memory_to_ram

from core.search import simplify_memories
def build_system_prompt(profile_text, personality_text):
    return f"""You are an AI companion.

User profile:
{profile_text}

User personality:
{personality_text}
"""

def should_inject_profile(user_input):
    keywords = ["goal", "learn", "work", "career", "interest"]
    return any(k in user_input.lower() for k in keywords)

def chat():

    # ===== 初始化 =====
    user_profile = load_user_profile()
    profile_text = build_profile_text(user_profile)
    # 🔥 你少了这两行
    user_personality = load_personality()
    personality_text = build_personality_text(user_personality)

    # 🔥 关键：构建 system_prompt
    system_prompt = build_system_prompt(profile_text, personality_text)
    print("""
    ========================
        AI Companion
    ========================
    """)

    session_history = []
    dialog_turn_counter = 0

    while True:
        user_input = input("\nYou: ")

        if user_input == "exit":
            break

        # ===== 手动触发记忆 =====
        if "remember" in user_input.lower():
            generate_memories("\n".join(session_history))
            dialog_turn_counter = 0
            continue

        # ===== 更新会话 =====
        session_history.append(f"User: {user_input}")

        # ===== 检索记忆 =====
        memory_candidates = search_memory(user_input)
        memory_candidates = simplify_memories(memory_candidates)
        memory_context = build_memory_text(memory_candidates)

        # ===== 构建 Prompt =====
        recent_history = session_history[-10:]   # ⚠️ 限制长度！
       
        prompt = f"""
            {system_prompt}

            Relevant memories:
            {memory_context}

            Recent conversation:
            {chr(10).join(recent_history)}

            User message:
            {user_input}

            Reply naturally.
            """

        # ===== 模型回复 =====
        ai_reply = call_llama_stream(prompt)

        session_history.append(f"AI: {ai_reply}")

        dialog_turn_counter += 1

        # ===== 自动记忆写入 =====
        if dialog_turn_counter >= 5:

            recent_block = session_history[-10:]
            history_text = "\n".join(recent_block)

            generate_memories(history_text)

            dialog_turn_counter = 0


if __name__ == "__main__":

    warmup_model()
    load_memory_to_ram()
    chat()