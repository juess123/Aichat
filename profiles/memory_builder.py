import datetime
import random

phrases_recent = [
    "You recently mentioned:",
    "Lately you said:",
    "Not long ago you mentioned:",
]

phrases_past = [
    "You mentioned this before",
    "You talked about this earlier",
    "I remember you brought this up before",
]

phrases_again = [
    "and it came up again",
    "and it seems to have come up again",
    "and it’s been on your mind again",
]
def format_time(ts):
    if not ts:
        return ""

    now = datetime.datetime.now()
    diff = now - datetime.datetime.fromisoformat(ts)

    if diff.days < 1:
        return "today"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    elif diff.days < 30:
        return f"{diff.days // 7} weeks ago"
    else:
        return f"{diff.days // 30} months ago"
def build_memory_text(memories):

    if not memories:
        return ""

    text = """Relevant memories about the user:
Use them naturally if helpful.
"""

    for m in memories:
        created = m.get("created_at")
        last = m.get("last_accessed")

        created_str = format_time(created)
        last_str = format_time(last)

        content = m["content"]

        # ✅ 情况1：刚创建（最近）
        if created == last:
            if created_str:
                text += f"- {random.choice(phrases_recent)} {content}\n"
            else:
                text += f"- {content}\n"

        # ✅ 情况2：有时间跨度
        else:
            if created_str and last_str:
                text += (
                    f"- {random.choice(phrases_past)} ({created_str}), "
                    f"{random.choice(phrases_again)} {last_str}: {content}\n"
                )

            elif created_str:
                text += f"- {random.choice(phrases_past)} ({created_str}): {content}\n"

            elif last_str:
                text += f"- It came up again {last_str}: {content}\n"

            else:
                text += f"- {content}\n"

    return text