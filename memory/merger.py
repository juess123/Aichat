def merge_content(old, new):

    if new in old:
        return old

    return old + " / " + new