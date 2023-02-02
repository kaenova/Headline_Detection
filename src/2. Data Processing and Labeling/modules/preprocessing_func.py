import emoji
import re

def lowercasing(text: str) -> str:
    return text.lower()

def change_emoji(text: str) -> str:
    return emoji.demojize(text)

def change_user(text:str) -> str:
    USER_TOKEN = "@USER"
    final_text = text
    results = re.findall(r"(@\S+)", final_text)
    results = set(results)
    results = sorted(results, reverse=True)
    for result in results:
        link = result
        final_text = re.sub(link, USER_TOKEN, final_text, count=0)
    return final_text

def change_web_url(text: str) -> str:
    URL_TOKEN = "HTTPURL"
    final_text = text
    results = re.findall(r"(http\S+)", final_text)
    results = set(results)
    results = sorted(results, reverse=True)
    for result in results:
        link = result
        final_text = re.sub(link, URL_TOKEN, final_text, count=0)
    return final_text

def remove_user(text:str) -> str:
    USER_TOKEN = ""
    final_text = text
    results = re.findall(r"(@\S+)", final_text)
    results = set(results)
    results = sorted(results, reverse=True)
    for result in results:
        link = result
        final_text = re.sub(link, USER_TOKEN, final_text, count=0)
    return final_text

def remove_url(text: str) -> str:
    URL_TOKEN = ""
    final_text = text
    results = re.findall(r"(http\S+)", final_text)
    results = set(results)
    results = sorted(results, reverse=True)
    for result in results:
        link = result
        final_text = re.sub(link, URL_TOKEN, final_text, count=0)
    return final_text