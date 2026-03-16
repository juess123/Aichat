def build_memory_text(memories):

    if not memories:
        return "No relevant memories."

    text = "Relevant memories:\n"

    for m in memories:
        text += f"- {m}\n"

    return text