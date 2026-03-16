def build_profile_text(profile):

    text = ""

    if "name" in profile:
        text += f"Name: {profile['name'][0]}\n"

    if "age" in profile:
        text += f"Age: {profile['age'][0]}\n"

    if "profession" in profile:
        text += f"Profession: {profile['profession'][0]}\n"

    if "field" in profile:
        text += f"Field: {profile['field'][0]}\n"

    if "skill" in profile:
        text += "Skills: " + ", ".join(profile["skill"]) + "\n"

    if "interest" in profile:
        text += "Interests: " + ", ".join(profile["interest"]) + "\n"

    if "learning" in profile:
        text += "Currently learning: " + ", ".join(profile["learning"]) + "\n"

    if "goal" in profile:
        text += "Goals: " + ", ".join(profile["goal"]) + "\n"

    return text