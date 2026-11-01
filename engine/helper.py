import os
import re
import time
from bs4 import BeautifulSoup

def extract_yt_term(command):
    """Extract search term for YouTube, supporting 'play X on youtube' and 'play X'"""
    if not command:
        return ""
    clean = re.sub(r'\b(megatron|alexa|hey|please|can you)\b', '', command, flags=re.IGNORECASE).strip()
    
    # Check for 'play ... on youtube'
    pattern_yt = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern_yt, clean, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Check for 'play ...'
    pattern_play = r'play\s+(.*)'
    match = re.search(pattern_play, clean, re.IGNORECASE)
    if match:
        term = match.group(1).replace('on youtube', '').strip()
        return term
        
    return clean.replace('play', '').replace('on youtube', '').strip()

def remove_words(input_string, words_to_remove):
    if not input_string:
        return ""
    words = input_string.split()
    filtered_words = [word for word in words if word.lower() not in words_to_remove]
    return ' '.join(filtered_words)

# ADB / Android automation helpers
def keyEvent(key_code):
    try:
        command = f'adb shell input keyevent {key_code}'
        os.system(command)
        time.sleep(1)
    except Exception as e:
        print(f"ADB keyEvent error: {e}")

def tapEvents(x, y):
    try:
        command = f'adb shell input tap {x} {y}'
        os.system(command)
        time.sleep(1)
    except Exception as e:
        print(f"ADB tapEvents error: {e}")

def adbInput(message):
    try:
        command = f'adb shell input text "{message}"'
        os.system(command)
        time.sleep(1)
    except Exception as e:
        print(f"ADB adbInput error: {e}")

def goback(key_code=4):
    for _ in range(4):
        keyEvent(key_code)

def replace_spaces_with_percent_s(input_string):
    if not input_string:
        return ""
    return str(input_string).replace(' ', '%s')

def markdown_to_text(md):
    """Converts markdown to plain text without crashing if markdown2 is missing."""
    if not md:
        return ""
    try:
        import markdown2
        html = markdown2.markdown(md)
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text().strip()
    except Exception:
        # High quality regex markdown cleaner
        text = str(md)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'#+\s*', '', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n+', ' ', text)
        return text.strip()