import emoji

def lowercasing(text: str) -> str:
    return text.lower()

def change_emoji(text: str) -> str:
    return emoji.demojize(text)

