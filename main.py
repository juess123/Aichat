from database.profile_db import load_user_profile
from profiles.profile_builder import build_profile_text

from database.personality_db import load_personality
from profiles.personality_builder import build_personality_text

from database.memory_db import search_memories
from profiles.memory_builder import build_memory_text

from model.llama_client import call_llama_stream, warmup_model
from model.memory_writer import generate_memories


def chat():
    
    profile = load_user_profile()
    profile_text = build_profile_text(profile)

    personality = load_personality()
    personality_text = build_personality_text(personality)

    print("""
        ========================
        AI Companion
        ========================
        """)
    global_conversation_history = []
    turn_count = 0
    while True:
        user_input = input("\nYou: ")
        if user_input == "exit":
            break
        if "remember" in user_input.lower():    
            generate_memories("\n".join(global_conversation_history))
            turn_count=0

        global_conversation_history.append(f"User: {user_input}")

        memories = search_memories(user_input)
        memory_text = build_memory_text(memories)

        prompt = f"""
                You are an AI companion.

                User profile:
                {profile_text}

                User personality:
                {personality_text}

                {memory_text}

                User message:
                {user_input}

                Reply naturally.
                """

        ai_reply = call_llama_stream(prompt)

        global_conversation_history.append(f"AI: {ai_reply}")

        turn_count += 1

        if turn_count >= 5:

            last_10_messages = global_conversation_history[-10:]

            history_text = "\n".join(last_10_messages)

            generate_memories(history_text)

            turn_count = 0


if __name__ == "__main__":

    warmup_model()

    chat()