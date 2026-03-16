def build_personality_text(personality):

    text = ""

    if "BigFive" in personality:

        text += "Big Five Personality:\n"

        for trait, value in personality["BigFive"].items():
            text += f"{trait}: {value}\n"

        text += "\n"

    if "MBTI" in personality:

        text += "MBTI:\n"

        for trait, value in personality["MBTI"].items():
            text += f"{trait}: {value}\n"

        text += "\n"

    return text