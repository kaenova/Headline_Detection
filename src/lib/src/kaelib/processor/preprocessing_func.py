import emoji
import re

def lowercasing(text: str) -> str:
    return text.lower()

def change_emoji(text: str) -> str:
    return emoji.demojize(text)

def remove_html_tags(text:str) -> str:
    return re.sub('<.*?>', '', text)

def remove_punctuation(text: str) -> str:
    return re.sub(r'[^\w\s]', '', text)

def change_user(text:str) -> str:
    """
    Change a username with '@' at the begining with @USER
    """
    TOKEN = "@USER"
    final_text = text
    results = re.findall(r"(@\S+)", final_text)
    results = set(results)
    results = sorted(results, reverse=True)
    for result in results:
        link = result
        final_text = re.sub(link, TOKEN, final_text, count=0)
    return final_text

def change_web_url(text: str) -> str:
    """
    Change a username with 'http' at the begining with HTTPURL
    """
    TOKEN = "HTTPURL"
    final_text = text
    results = re.findall(r"(http\S+)", final_text)
    results = set(results)
    results = sorted(results, reverse=True)
    for result in results:
        link = result
        final_text = re.sub(link, TOKEN, final_text, count=0)
    return final_text

def remove_username(text:str) -> str:
    """
    Remove username with an @ at front of the username
    """
    return re.sub(r"(@\S+)", "", text)


def remove_url(text: str) -> str:
    """
    Remove an url with a 'http' at front of the url
    """
    return re.sub(r"(http\S+)", "", text)