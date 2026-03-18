from database.profile_db import load_user_profile
from profiles.profile_builder import build_profile_text

from database.personality_db import load_personality
from profiles.personality_builder import build_personality_text

from core.search import search_memory, load_memory_to_ram, simplify_memories
from profiles.memory_builder import build_memory_text

from models.llama_client import call_llama_stream,warmup_model
from memory.generator import generate_memories
from memory.decay import decay_unused_memories

from core.context_router import need_profile


# ===== system prompt 构建 =====
def build_system_prompt(profile_text, personality_text):
    return f"""You are an AI companion.

User profile:
{profile_text}

User personality:
{personality_text}
"""


def chat():

    # ===== 初始化 =====
    user_profile = load_user_profile()
    profile_text = build_profile_text(user_profile)

    user_personality = load_personality()
    personality_text = build_personality_text(user_personality)

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
        if user_input.strip().lower() == "remember":
            generate_memories("\n".join(session_history))
            dialog_turn_counter = 0
            continue

        # ===== 更新会话 =====
        session_history.append(f"User: {user_input}")

        # ======================================
        # 🧠 核心：上下文决策（新增）
        # ======================================
        use_profile = need_profile(user_input)
        if use_profile:
            system_prompt = build_system_prompt(profile_text, personality_text)
        else:
            system_prompt = "You are an AI companion."

        # ===== 加载 memory =====
        
        memory_candidates = search_memory(user_input)
        memory_candidates = simplify_memories(memory_candidates)
        memory_context = build_memory_text(memory_candidates)

        # ===== 构建 Prompt =====
        recent_history = session_history[-10:]

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
    decay_unused_memories()
    load_memory_to_ram()
    chat()