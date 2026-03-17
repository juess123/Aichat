def extract_keywords(text):
    words = text.lower().split()
    keywords = []
    for w in words:
        if len(w) > 3:
            keywords.append(w)

    return list(set(keywords))