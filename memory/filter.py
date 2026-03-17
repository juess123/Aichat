bad_patterns = [
    "conversation began",
    "you asked me",
    "this conversation",
    "memory extraction system"
]


def is_valid_memory(content):

    if not content:
        return False

    content_lower = content.lower()

    for p in bad_patterns:
        if p in content_lower:
            return False

    return True