from models.llama_client import call_llama
def need_profile(user_input):
    prompt = f"""You are a classifier.

Decide if user basic profile and personality Analysis Report is needed.

Rules:
- YES → if question relates to user goals, learning, preferences, plans
- NO → if general knowledge, facts, or casual chat

User input:
{user_input}

Answer: YES or NO"""

    result = call_llama(prompt)

    result = result.strip().upper()

    # ===== 最稳解析 =====
    if result.startswith("Y"):
        return True
    if result.startswith("N"):
        return False

    # ===== fallback（极端情况）=====
    if "YES" in result:
        return True

    return False