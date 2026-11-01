import datetime
import json
import os
import re
import struct
import subprocess
import threading
import time
import webbrowser
import xml.etree.ElementTree as ET
from urllib.parse import quote

import eel
import pyaudio
import pyautogui
from playsound import playsound
import pywhatkit as kit
import requests
import wikipedia

try:
    import pyperclip
except ImportError:
    pyperclip = None

from engine.command import speak
from engine.config import ASSISTANT_NAME, DB_NAME, LLM_KEY
from engine.db import (
    clear_search_history,
    delete_search_record,
    find_learned_context,
    get_api_config,
    get_connection,
    get_memory_stats,
    get_recent_searches,
    get_training_stats,
    init_db,
    mark_provider_quota_exhausted,
    save_api_config,
    save_search_record,
    search_memory_by_keyword,
    update_admin_passcode,
    verify_admin_passcode,
)

from engine.helper import (
    adbInput,
    extract_yt_term,
    goback,
    keyEvent,
    markdown_to_text,
    remove_words,
    replace_spaces_with_percent_s,
    tapEvents,
)

# Ensure DB is initialized
init_db()

# Global assistant name and key tracking
CURRENT_ASSISTANT_NAME = ASSISTANT_NAME
CURRENT_LLM_KEY = LLM_KEY


@eel.expose
def playAssistantSound():
    """Play startup chime asynchronously without blocking the UI."""
    def _play():
        try:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            music_dir = os.path.join(base, "www", "assets", "audio", "start_sound.mp3")
            if os.path.exists(music_dir):
                playsound(music_dir)
        except Exception as e:
            print(f"[Sound Error] {e}")

    threading.Thread(target=_play, daemon=True).start()


# --- Online AI & Internet Search Features ---

@eel.expose
def openOnlineAI(service, prompt=""):
    """Launch online AI platforms (ChatGPT, Claude, Gemini, Perplexity, Copilot)."""
    return open_online_ai(service, prompt)


def open_online_ai(service, prompt=""):
    """Opens online AI services in browser with optional prompt auto-fill/clipboard."""
    service_clean = service.lower().strip()
    ai_urls = {
        "chatgpt": ("https://chatgpt.com", "ChatGPT"),
        "chat gpt": ("https://chatgpt.com", "ChatGPT"),
        "claude": ("https://claude.ai", "Claude AI"),
        "claude ai": ("https://claude.ai", "Claude AI"),
        "gemini": ("https://gemini.google.com/app", "Google Gemini"),
        "google gemini": ("https://gemini.google.com/app", "Google Gemini"),
        "perplexity": ("https://www.perplexity.ai", "Perplexity AI"),
        "perplexity ai": ("https://www.perplexity.ai", "Perplexity AI"),
        "copilot": ("https://copilot.microsoft.com", "Microsoft Copilot"),
        "microsoft copilot": ("https://copilot.microsoft.com", "Microsoft Copilot"),
        "huggingface": ("https://huggingface.co/chat", "HuggingFace Chat"),
        "hugging face": ("https://huggingface.co/chat", "HuggingFace Chat"),
    }

    matched_key = None
    for k in ai_urls:
        if k in service_clean:
            matched_key = k
            break

    if not matched_key:
        matched_key = "chatgpt"

    base_url, display_name = ai_urls[matched_key]

    if prompt and prompt.strip():
        p_text = prompt.strip()
        save_search_record(f"AI Query ({display_name}): {p_text}", f"Opened in {display_name}", category="ai_hub")
        if "perplexity" in matched_key:
            target_url = f"https://www.perplexity.ai/search?q={quote(p_text)}"
            speak(f"Searching on Perplexity AI for: {p_text}")
            webbrowser.open(target_url)
            return target_url
        else:
            if pyperclip:
                try:
                    pyperclip.copy(p_text)
                    speak(f"Opening {display_name}. Your query has been copied to your clipboard—press Ctrl+V to paste.")
                except Exception:
                    speak(f"Opening {display_name} for you.")
            else:
                speak(f"Opening {display_name} for you.")
            webbrowser.open(base_url)
            return base_url
    else:
        save_search_record(f"Open {display_name}", f"Opened {display_name} in browser", category="ai_hub")
        speak(f"Opening {display_name} in your browser.")
        webbrowser.open(base_url)
        return base_url


@eel.expose
def getLiveWeather(city=""):
    """Retrieve real-time live weather report."""
    return fetch_live_weather(city)


def fetch_live_weather(city="", do_speak=True):
    """Fetch live real-time weather from wttr.in without requiring an API key."""
    if not city or city.strip() == "":
        con = get_connection()
        cursor = con.cursor()
        try:
            cursor.execute("SELECT city FROM info LIMIT 1")
            row = cursor.fetchone()
            if row and row[0] and row[0].lower() != "cybertron":
                city = row[0].strip()
        except Exception:
            pass
        finally:
            con.close()

    city_param = quote(city.strip()) if city and city.strip() else ""
    url = f"https://wttr.in/{city_param}?format=%C,+%t+(feels+like+%f),+humidity+%h"
    try:
        resp = requests.get(url, headers={"User-Agent": "curl/7.68.0"}, timeout=6)
        if resp.status_code == 200 and resp.text.strip():
            raw_text = resp.text.strip()
            spoken_text = raw_text.replace("°C", " degrees Celsius").replace("°", " degrees ").replace("+", "")
            spoken_text = re.sub(r'\s+', ' ', spoken_text).strip()
            loc_str = f" in {city.title()}" if city else ""
            report = f"The current weather{loc_str} is {spoken_text}."
            save_search_record(f"Weather for {city or 'Current Location'}", report, category="weather")
            if do_speak:
                speak(report)
            return report
    except Exception as e:
        print(f"[Weather Error] {e}")

    fallback = "Unable to fetch live weather at this moment. Please check your internet connection."
    if do_speak:
        speak(fallback)
    return fallback


@eel.expose
def getLiveNews(topic=""):
    """Retrieve real-time top headlines from Google News RSS."""
    return fetch_live_news(topic, do_speak=True)


def fetch_live_news(topic="", do_speak=True):
    """Fetch latest top news headlines from Google News RSS feed."""
    try:
        if topic and topic.strip():
            url = f"https://news.google.com/rss/search?q={quote(topic.strip())}&hl=en-IN&gl=IN&ceid=IN:en"
            topic_str = f" regarding {topic.title()}"
        else:
            url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
            topic_str = ""

        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=7)
        if resp.status_code == 200:
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")[:3]
            if items:
                headlines = []
                for item in items:
                    title_elem = item.find("title")
                    if title_elem is not None and title_elem.text:
                        cleaned_title = re.sub(r' - [^-]+$', '', title_elem.text).strip()
                        headlines.append(cleaned_title)

                full_report = f"Top News{topic_str}:\n"
                for idx, h in enumerate(headlines, 1):
                    full_report += f"{idx}. {h}\n"

                save_search_record(f"News Headlines: {topic or 'Top Stories'}", full_report.strip(), category="news")
                if do_speak:
                    speech_text = f"Here are the top news headlines{topic_str}: " + ". ".join(headlines[:2])
                    speak(speech_text)
                return full_report
    except Exception as e:
        print(f"[News Error] {e}")

    fallback = "Unable to fetch live news at this time."
    if do_speak:
        speak(fallback)
    return fallback


@eel.expose
def searchOnline(query):
    """Search live internet for query and speak synthesized response."""
    return search_internet_live(query)


def search_internet_live(query, do_speak=True):
    """
    Search internet in real-time using DuckDuckGo Instant Answer API and Wikipedia.
    Synthesizes a voice-friendly factual summary without opening unwanted popup tabs.
    """
    clean_q = re.sub(r'\b(search internet for|search online for|search for|look up|what is|who is|tell me about)\b', '', query, flags=re.IGNORECASE).strip()
    if not clean_q:
        fallback = "What would you like me to look up on the internet, Commander?"
        if do_speak:
            speak(fallback)
        return fallback

    # 1. Try DuckDuckGo Instant Answer API
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={quote(clean_q)}&format=json&no_html=1&skip_disambig=1"
        resp = requests.get(ddg_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            abstract = data.get("AbstractText", "")
            if abstract and len(abstract) > 20:
                save_search_record(clean_q, abstract, category="web_search")
                if do_speak:
                    speak(abstract)
                return abstract
            answer = data.get("Answer", "")
            if answer:
                save_search_record(clean_q, answer, category="web_search")
                if do_speak:
                    speak(answer)
                return answer
    except Exception as e:
        print(f"[DuckDuckGo Error] {e}")

    # 2. Try Wikipedia summary with proper custom User-Agent and Disambiguation handling
    try:
        wikipedia.set_user_agent("MegatronAI/2.0 (contact@megatron.ai)")
        wikipedia.set_lang("en")
        try:
            summary = wikipedia.summary(clean_q, sentences=2, auto_suggest=False)
        except wikipedia.DisambiguationError as de:
            first_opt = de.options[0] if de.options else clean_q
            try:
                summary = wikipedia.summary(first_opt, sentences=2, auto_suggest=False)
            except Exception:
                summary = ""
        except Exception:
            summary = ""

        if summary and len(summary) > 20:
            clean_summary = re.sub(r'\s+', ' ', summary).strip()
            save_search_record(clean_q, clean_summary, category="web_search")
            if do_speak:
                speak(clean_summary)
            return clean_summary
    except Exception as e:
        print(f"[Wikipedia Live Search Error] {e}")

    # 3. Clean Synthesized Summary Fallback
    result_text = f"I gathered intelligence on '{clean_q}'. You can also consult external online models like ChatGPT, Claude, or Gemini from the Megatron dock."
    save_search_record(clean_q, result_text, category="web_search")
    if do_speak:
        speak(result_text)
    return result_text


# --- Command Execution Helpers ---

def openCommand(query):
    """Open desktop applications, online AI tools, or websites with intelligent fallback."""
    global CURRENT_ASSISTANT_NAME
    query_clean = query.lower()
    for word in [CURRENT_ASSISTANT_NAME.lower(), "open", "launch", "start", "please"]:
        query_clean = query_clean.replace(word, "")
    app_name = query_clean.strip()

    if not app_name:
        speak("What would you like me to open?")
        return

    # 1. Check for Online AI platforms
    for ai_keyword in ["chatgpt", "chat gpt", "claude", "gemini", "perplexity", "copilot", "huggingface"]:
        if ai_keyword in app_name:
            prompt = re.sub(rf'\b(open|launch|ask)\s+{ai_keyword}\b', '', query, flags=re.IGNORECASE).strip()
            return open_online_ai(ai_keyword, prompt)

    con = get_connection()
    cursor = con.cursor()

    try:
        current_mode = os.environ.get("MEGATRON_MODE", "browser")

        # 2. Check web_command table first
        cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ? OR LOWER(name) LIKE ?', (app_name, f"%{app_name}%"))
        results = cursor.fetchall()
        if results:
            target_url = results[0][0]
            speak(f"Opening {app_name}")
            webbrowser.open(target_url)
            return

        # 3. If in Browser Web Agent mode, restrict desktop local program launching
        if current_mode == "browser":
            speak(f"Opening desktop program {app_name} is disabled in Browser Web Agent mode. Please launch or install the Megatron Windows Software for full system control.")
            return

        # 4. Search sys_command table (Windows Desktop software mode)
        cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ? OR LOWER(name) LIKE ?', (app_name, f"%{app_name}%"))
        results = cursor.fetchall()
        if results:
            target_path = results[0][0]
            speak(f"Opening {app_name}")
            try:
                os.startfile(target_path)
            except Exception:
                subprocess.Popen(target_path, shell=True)
            return

        # 5. Built-in system shortcuts (Windows Desktop software mode)
        builtins = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "paint": "mspaint.exe",
            "cmd": "cmd.exe",
            "terminal": "wt.exe",
            "explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "settings": "ms-settings:",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
        }
        for key, cmd in builtins.items():
            if key in app_name:
                speak(f"Opening {key}")
                try:
                    os.system(f'start {cmd}')
                    return
                except Exception:
                    pass

        # 5. Fallback to start command or browser search
        speak(f"Opening {app_name}")
        try:
            os.system(f'start {app_name}')
        except Exception:
            webbrowser.open(f"https://www.google.com/search?q={quote(app_name)}")
    except Exception as e:
        print(f"[openCommand Error] {e}")
        speak("Unable to open the requested application.")
    finally:
        con.close()


def PlayYoutube(query):
    """Search and play a video or song directly on YouTube."""
    search_term = extract_yt_term(query)
    if not search_term:
        speak("What song or video should I play on YouTube?")
        return
    speak(f"Playing {search_term} on YouTube")
    try:
        kit.playonyt(search_term)
    except Exception as e:
        print(f"[YouTube Error] {e}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote(search_term)}")


def hotword():
    """Background listener for wake words ('megatron', 'alexa')."""
    porcupine = None
    paud = None
    audio_stream = None

    try:
        import pvporcupine
        porcupine = pvporcupine.create(keywords=["alexa"])
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        while True:
            keyword = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)
            if keyword_index >= 0:
                print("[Hotword] Wake word detected via Porcupine!")
                triggerWake()
    except Exception as e:
        print(f"[Hotword Porcupine fallback] {e}")
    finally:
        if audio_stream is not None:
            try:
                audio_stream.close()
            except Exception:
                pass
        if porcupine is not None:
            try:
                porcupine.delete()
            except Exception:
                pass
        if paud is not None:
            try:
                paud.terminate()
            except Exception:
                pass

    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True

        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            print("[Hotword Listener] Actively listening for 'Megatron'...")
            while True:
                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=3)
                    text = r.recognize_google(audio).lower()
                    if "megatron" in text or "wake up" in text:
                        print(f"[Hotword Detected] User said: {text}")
                        triggerWake()
                except (sr.WaitTimeoutError, sr.UnknownValueError):
                    continue
                except Exception as ex:
                    time.sleep(1)
    except Exception as e:
        print(f"[Hotword SpeechRecognizer Error] {e}")


def triggerWake():
    """Simulate keypress Win+J to bring Megatron to focus and start voice intake."""
    try:
        pyautogui.keyDown("win")
        pyautogui.press("j")
        time.sleep(0.5)
        pyautogui.keyUp("win")
    except Exception as e:
        print(f"[TriggerWake Error] {e}")


def findContact(query):
    """Find contact mobile number by matching name against contacts table."""
    global CURRENT_ASSISTANT_NAME
    words_to_remove = [CURRENT_ASSISTANT_NAME.lower(), 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    clean_query = remove_words(query, words_to_remove).strip().lower()

    if not clean_query:
        speak("Whom would you like to contact?")
        return 0, 0

    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT mobile_no, name FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
                       ('%' + clean_query + '%', clean_query + '%'))
        results = cursor.fetchall()
        if results:
            mobile_number_str = str(results[0][0]).strip()
            contact_name = results[0][1]
            if not mobile_number_str.startswith('+'):
                mobile_number_str = '+91' + mobile_number_str
            return mobile_number_str, contact_name
        else:
            speak("That person does not exist in your contacts.")
            return 0, 0
    except Exception as e:
        print(f"[findContact Error] {e}")
        speak("Unable to search contacts.")
        return 0, 0
    finally:
        con.close()


def whatsApp(mobile_no, message, flag, name):
    """Automate sending WhatsApp messages or placing WhatsApp calls."""
    if flag == 'message':
        target_tab = 12
        feedback = f"Message sent successfully to {name}"
    elif flag == 'call':
        target_tab = 7
        message = ''
        feedback = f"Calling {name} on WhatsApp"
    else:
        target_tab = 6
        message = ''
        feedback = f"Starting video call with {name}"

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
    full_command = f'start "" "{whatsapp_url}"'

    try:
        subprocess.run(full_command, shell=True)
        time.sleep(5)
        subprocess.run(full_command, shell=True)
        pyautogui.hotkey('ctrl', 'f')
        for _ in range(1, target_tab):
            pyautogui.hotkey('tab')
        pyautogui.hotkey('enter')
        speak(feedback)
    except Exception as e:
        print(f"[WhatsApp Error] {e}")
        speak("Failed to connect to WhatsApp desktop application.")


def makeCall(name, mobileNo):
    """Place phone call via ADB Android bridge."""
    clean_no = mobileNo.replace(" ", "")
    speak(f"Calling {name}")
    command = f'adb shell am start -a android.intent.action.CALL -d tel:{clean_no}'
    os.system(command)


def sendMessage(message, mobileNo, name):
    """Send SMS via ADB Android bridge."""
    msg_formatted = replace_spaces_with_percent_s(message)
    no_formatted = replace_spaces_with_percent_s(mobileNo)
    speak(f"Sending message to {name}")
    try:
        goback(4)
        time.sleep(1)
        keyEvent(3)
        tapEvents(136, 2220)
        tapEvents(819, 2192)
        adbInput(no_formatted)
        tapEvents(601, 574)
        tapEvents(390, 2270)
        adbInput(msg_formatted)
        tapEvents(957, 1397)
        speak(f"Message sent successfully to {name}")
    except Exception as e:
        print(f"[ADB SMS Error] {e}")
        speak("Could not send SMS through connected device.")


def get_stored_llm_key():
    """Retrieve saved Gemini API Key from database or environment."""
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT value FROM settings WHERE key = 'llm_key'")
        row = cursor.fetchone()
        if row and row[0]:
            return row[0].strip()
    except Exception:
        pass
    finally:
        con.close()
    return os.environ.get("GEMINI_API_KEY", CURRENT_LLM_KEY)


def _dispatch_single_provider(provider, query, memory_instruction, config):
    """
    Dispatches prompt to a specific provider.
    Returns (response_text, is_quota_ended, error_msg).
    """
    p = provider.lower().strip()
    system_prompt = (
        "You are Megatron, a powerful, polite, highly capable AI desktop assistant. "
        "Provide concise, informative, voice-friendly answers (under 3 sentences unless asked for detail). "
        f"{memory_instruction}"
    )

    if p == "gemini":
        key = config.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
        if not key:
            return None, False, "No Gemini API Key attached."
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\nUser query: {query}"}
                    ]
                }
            ]
        }
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text, False, ""
            err_text = resp.text
            if resp.status_code == 429 or "RESOURCE_EXHAUSTED" in err_text or "quota" in err_text.lower():
                return None, True, f"Gemini API Quota Exceeded (429): {err_text[:200]}"
            return None, False, f"Gemini HTTP {resp.status_code}: {err_text[:200]}"
        except Exception as e:
            return None, False, str(e)

    elif p == "openai":
        key = config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")
        if not key:
            return None, False, "No OpenAI API Key attached."
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "max_tokens": 400
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return text, False, ""
            err_text = resp.text
            if resp.status_code == 429 or "insufficient_quota" in err_text.lower() or "quota" in err_text.lower():
                return None, True, f"OpenAI API Quota Exceeded (429): {err_text[:200]}"
            return None, False, f"OpenAI HTTP {resp.status_code}: {err_text[:200]}"
        except Exception as e:
            return None, False, str(e)

    elif p == "groq":
        key = config.get("groq_api_key") or os.environ.get("GROQ_API_KEY", "")
        if not key:
            return None, False, "No Groq API Key attached."
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "max_tokens": 400
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return text, False, ""
            err_text = resp.text
            if resp.status_code == 429 or "rate_limit" in err_text.lower() or "quota" in err_text.lower():
                return None, True, f"Groq Rate/Quota Exceeded (429): {err_text[:200]}"
            return None, False, f"Groq HTTP {resp.status_code}: {err_text[:200]}"
        except Exception as e:
            return None, False, str(e)

    elif p == "openrouter":
        key = config.get("openrouter_api_key") or os.environ.get("OPENROUTER_API_KEY", "")
        if not key:
            return None, False, "No OpenRouter API Key attached."
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "max_tokens": 400
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return text, False, ""
            err_text = resp.text
            if resp.status_code in (402, 429) or "credits" in err_text.lower() or "quota" in err_text.lower():
                return None, True, f"OpenRouter Credits/Quota Exhausted: {err_text[:200]}"
            return None, False, f"OpenRouter HTTP {resp.status_code}: {err_text[:200]}"
        except Exception as e:
            return None, False, str(e)

    elif p == "custom":
        custom_url = config.get("custom_api_url", "http://localhost:11434/v1").rstrip("/")
        custom_key = config.get("custom_api_key", "")
        url = f"{custom_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if custom_key:
            headers["Authorization"] = f"Bearer {custom_key}"
        payload = {
            "model": "llama3",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "max_tokens": 400
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return text, False, ""
            return None, False, f"Custom LLM HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            return None, False, str(e)

    return None, False, f"Unknown AI Provider: {p}"


def call_llm_api(query, memory_instruction=""):
    """
    Intelligent Multi-Provider Router with Automatic Quota-Exhaustion Failover.
    Attempts active attached provider first; if package/quota ended, switches to secondary attached provider!
    """
    config = get_api_config()
    active = config.get("active_provider", "gemini").lower()
    auto_failover = str(config.get("auto_failover", "1")) == "1"

    all_providers = ["gemini", "openai", "groq", "openrouter", "custom"]
    order = [active] + [p for p in all_providers if p != active] if auto_failover else [active]

    for provider in order:
        resp_text, is_quota_ended, err_msg = _dispatch_single_provider(provider, query, memory_instruction, config)
        if resp_text:
            if is_quota_ended:
                mark_provider_quota_exhausted(provider, False)
            return resp_text, provider, False
        if is_quota_ended:
            mark_provider_quota_exhausted(provider, True)
            print(f"[Megatron API Quota Alert] Provider '{provider}' package/quota exhausted: {err_msg}")
            if not auto_failover:
                return None, provider, True

    return None, active, True


def geminai(query):
    """
    Intelligent Conversational Brain for Megatron.
    1. First retrieves trained continuous neural memory from prior searches.
    2. Calls active attached AI Provider (Gemini, OpenAI, Groq, OpenRouter, Custom).
    3. If active API package/quota is ended, automatically switches to backup attached provider!
    4. If no external API available, falls back to Megatron's autonomous live search engine.
    5. CONTINUOUS MODEL TRAINING: Automatically trains on every single search and response!
    """
    global CURRENT_ASSISTANT_NAME
    raw_query = query
    clean_query = query.lower()
    for word in [CURRENT_ASSISTANT_NAME.lower(), "search", "please", "can you", "tell me"]:
        clean_query = clean_query.replace(word, "").strip()

    # Step 1: Neural Memory Recall (Ground Truth from prior interactions)
    learned_context = find_learned_context(raw_query)
    memory_instruction = ""
    if learned_context:
        memory_instruction = f"\n[Continuous Learned Memory from prior searches]: '{learned_context}'. Use this ground truth knowledge to inform your response."

    # Step 2: Call Attached AI Provider with automatic failover
    ai_text, used_provider, quota_ended = call_llm_api(raw_query, memory_instruction)

    if ai_text:
        filtered_text = markdown_to_text(ai_text)
        # Train continuous model on this query & response
        save_search_record(raw_query, filtered_text, category=f"ai_{used_provider}")
        speak(filtered_text)
        return filtered_text

    # Step 3: If API package ended or not configured, fallback to Megatron's Autonomous Live Search
    offline_response = handle_autonomous_query(clean_query, raw_query)
    if quota_ended:
        quota_notice = f" [Note: Your {used_provider.capitalize()} API package quota ended. Switched to Megatron Live Intelligence. You can attach a new API key in the browser.]"
        speak(offline_response)
        full_resp = offline_response + quota_notice
        save_search_record(raw_query, full_resp, category="web_fallback")
        return full_resp

    save_search_record(raw_query, offline_response, category="general")
    speak(offline_response)
    return offline_response


def handle_autonomous_query(clean_query, raw_query):
    """Autonomous live online search, tool & rule engine for Megatron."""
    q = clean_query.lower()

    # 1. Online AI Platforms (ChatGPT, Claude, Gemini, Perplexity, Copilot)
    for ai in ["chatgpt", "chat gpt", "claude", "gemini", "perplexity", "copilot", "huggingface"]:
        if ai in q:
            prompt = re.sub(rf'\b(open|ask|launch|check|consult)\s+{ai}\b', '', raw_query, flags=re.IGNORECASE).strip()
            return open_online_ai(ai, prompt)

    # 2. Live Real-Time Weather
    if "weather" in q or "temperature" in q:
        city_match = re.search(r'\b(?:in|at|for|of)\s+([a-zA-Z\s]+)', q)
        city = city_match.group(1).strip() if city_match else ""
        return fetch_live_weather(city, do_speak=False)

    # 3. Live Real-Time News
    if "news" in q or "headline" in q:
        topic_match = re.search(r'\b(?:about|on|regarding|for)\s+([a-zA-Z\s]+)', q)
        topic = topic_match.group(1).strip() if topic_match else ""
        return fetch_live_news(topic, do_speak=False)

    # 4. Identity & Name
    if any(phrase in q for phrase in ["who are you", "what is your name", "what are you", "introduce yourself"]):
        return "I am Megatron, your advanced AI assistant with real-time internet search and continuous neural learning."

    # 5. Greetings
    if any(phrase in q for phrase in ["hello", "hi", "hey there", "greetings"]):
        return "Greetings, Commander. Megatron is online, connected to live web feeds, and at your service."

    # 6. Status
    if any(phrase in q for phrase in ["how are you", "system status", "status"]):
        return "All systems, continuous memory, and online search channels are operating at peak efficiency, Commander."

    # 7. Time & Date
    if "time" in q:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}."

    if "date" in q or "today" in q:
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."

    # 8. Capabilities & Help
    if any(phrase in q for phrase in ["what can you do", "help", "features", "commands"]):
        return (
            "I can fetch live news, check real-time weather, open online AIs like ChatGPT and Claude, "
            "perform internet web searches, stream YouTube music, manage contacts, and execute system controls."
        )

    # 9. Math & Calculation
    if any(op in q for op in ["+", "-", "*", "/", "plus", "minus", "multiply", "divided by", "times"]):
        try:
            expr = (
                q.replace("plus", "+")
                .replace("minus", "-")
                .replace("multiplied by", "*")
                .replace("times", "*")
                .replace("divided by", "/")
                .replace("x", "*")
            )
            cleaned_math = re.sub(r'[^0-9\+\-\*\/\.\(\)\s]', '', expr)
            if cleaned_math.strip():
                result = eval(cleaned_math)
                return f"The result is {result}."
        except Exception:
            pass

    # 10. Live Internet Search / Facts
    if any(k in q for k in ["search internet", "search online", "look up", "who is", "what is", "tell me about"]):
        return search_internet_live(raw_query, do_speak=False)

    # 11. Jokes
    if "joke" in q:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why was the JavaScript developer sad? Because he didn't know how to 'null' his feelings.",
            "There are only 10 types of people in the world: those who understand binary, and those who don't.",
            "Why did the computer keep freezing? It left its Windows open!",
        ]
        import random
        return random.choice(jokes)

    # 12. Final Web Search Fallback
    return search_internet_live(raw_query, do_speak=False)


# --- Eel Expositions for UI Interaction ---

@eel.expose
def assistantName():
    con = get_connection()
    cursor = con.cursor()
    name = "megatron"
    try:
        cursor.execute("SELECT value FROM settings WHERE key = 'assistant_name'")
        row = cursor.fetchone()
        if row and row[0]:
            name = row[0]
    except Exception:
        pass
    finally:
        con.close()
    return name


@eel.expose
def personalInfo():
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT name, designation, mobileno, email, city FROM info LIMIT 1")
        row = cursor.fetchone()
        if row:
            jsonArr = json.dumps(list(row))
            eel.getData(jsonArr)
            return 1
        return 0
    except Exception as e:
        print(f"[personalInfo Error] {e}")
        return 0
    finally:
        con.close()


@eel.expose
def updatePersonalInfo(name, designation, mobileno, email, city):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM info")
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute(
                '''UPDATE info SET name=?, designation=?, mobileno=?, email=?, city=?''',
                (name, designation, mobileno, email, city)
            )
        else:
            cursor.execute(
                '''INSERT INTO info (name, designation, mobileno, email, city) VALUES (?, ?, ?, ?, ?)''',
                (name, designation, mobileno, email, city)
            )
        con.commit()
        personalInfo()
        return 1
    except Exception as e:
        print(f"[updatePersonalInfo Error] {e}")
        return 0
    finally:
        con.close()


@eel.expose
def displaySysCommand():
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, name, path FROM sys_command ORDER BY id DESC")
        results = cursor.fetchall()
        jsonArr = json.dumps(results)
        eel.displaySysCommand(jsonArr)
        return 1
    except Exception as e:
        print(f"[displaySysCommand Error] {e}")
        eel.displaySysCommand("[]")
        return 0
    finally:
        con.close()


@eel.expose
def addSysCommand(key, value):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute('''INSERT OR REPLACE INTO sys_command (name, path) VALUES (?, ?)''', (key.strip().lower(), value.strip()))
        con.commit()
    except Exception as e:
        print(f"[addSysCommand Error] {e}")
    finally:
        con.close()


@eel.expose
def deleteSysCommand(id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM sys_command WHERE id = ?", (id,))
        con.commit()
    except Exception as e:
        print(f"[deleteSysCommand Error] {e}")
    finally:
        con.close()


@eel.expose
def displayWebCommand():
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, name, url FROM web_command ORDER BY id DESC")
        results = cursor.fetchall()
        jsonArr = json.dumps(results)
        eel.displayWebCommand(jsonArr)
        return 1
    except Exception as e:
        print(f"[displayWebCommand Error] {e}")
        eel.displayWebCommand("[]")
        return 0
    finally:
        con.close()


@eel.expose
def addWebCommand(key, value):
    con = get_connection()
    cursor = con.cursor()
    try:
        url = value.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        cursor.execute('''INSERT OR REPLACE INTO web_command (name, url) VALUES (?, ?)''', (key.strip().lower(), url))
        con.commit()
    except Exception as e:
        print(f"[addWebCommand Error] {e}")
    finally:
        con.close()


@eel.expose
def deleteWebCommand(id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM web_command WHERE id = ?", (id,))
        con.commit()
    except Exception as e:
        print(f"[deleteWebCommand Error] {e}")
    finally:
        con.close()


@eel.expose
def displayPhoneBookCommand():
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT id, name, mobile_no, email, address FROM contacts ORDER BY id DESC")
        results = cursor.fetchall()
        jsonArr = json.dumps(results)
        eel.displayPhoneBookCommand(jsonArr)
        return 1
    except Exception as e:
        print(f"[displayPhoneBookCommand Error] {e}")
        eel.displayPhoneBookCommand("[]")
        return 0
    finally:
        con.close()


@eel.expose
def InsertContacts(Name, MobileNo, Email, City):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute(
            '''INSERT INTO contacts (name, mobile_no, email, address) VALUES (?, ?, ?, ?)''',
            (Name.strip(), MobileNo.strip(), Email.strip(), City.strip())
        )
        con.commit()
    except Exception as e:
        print(f"[InsertContacts Error] {e}")
    finally:
        con.close()


@eel.expose
def deletePhoneBookCommand(id):
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM contacts WHERE id = ?", (id,))
        con.commit()
    except Exception as e:
        print(f"[deletePhoneBookCommand Error] {e}")
    finally:
        con.close()


@eel.expose
def getApiKey():
    """Retrieve Gemini API Key for the Settings Modal."""
    key = get_stored_llm_key()
    return key or ""


@eel.expose
def updateApiKey(new_key):
    """Save Gemini API Key from the Settings Modal."""
    global CURRENT_LLM_KEY
    CURRENT_LLM_KEY = new_key.strip()
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('llm_key', ?)", (CURRENT_LLM_KEY,))
        con.commit()
        return 1
    except Exception as e:
        print(f"[updateApiKey Error] {e}")
        return 0
    finally:
        con.close()


# --- Search History, Memory & Visual Image Solution Eel Expositions ---

@eel.expose
def verifyAdminAccess(passcode):
    """Verifies main admin master passcode."""
    if verify_admin_passcode(passcode):
        return json.dumps({"success": True, "message": "CLEARANCE GRANTED: Main Admin Authenticated."})
    return json.dumps({"success": False, "message": "ACCESS DENIED: Invalid Admin Master Passcode."})


@eel.expose
def changeAdminPasscode(current_code, new_code):
    """Allows main admin to change the master passcode."""
    if not verify_admin_passcode(current_code):
        return json.dumps({"success": False, "message": "Verification failed: Current passcode incorrect."})
    if not new_code or len(str(new_code).strip()) < 4:
        return json.dumps({"success": False, "message": "New passcode must be at least 4 characters long."})
    ok = update_admin_passcode(str(new_code).strip())
    if ok:
        return json.dumps({"success": True, "message": "Admin Master Passcode updated successfully."})
    return json.dumps({"success": False, "message": "Database error while updating passcode."})


@eel.expose
def getSearchHistory(limit=60, admin_passcode=""):
    """
    Retrieve search history records for UI display.
    STRICTLY RESTRICTED: Trained data is accessible only by the Main Admin.
    """
    if not verify_admin_passcode(admin_passcode):
        return json.dumps({
            "error": "ACCESS_DENIED",
            "message": "CLASSIFIED: Main Admin Clearance Required. Trained neural data is restricted."
        })
    records = get_recent_searches(limit)
    return json.dumps(records)


@eel.expose
def clearSearchMemory(admin_passcode=""):
    """Clear all stored search memory - strictly main admin only."""
    if not verify_admin_passcode(admin_passcode):
        return 0
    res = clear_search_history()
    return 1 if res else 0


@eel.expose
def deleteSearchItem(record_id, admin_passcode=""):
    """Delete a single search record - strictly main admin only."""
    if not verify_admin_passcode(admin_passcode):
        return 0
    try:
        res = delete_search_record(int(record_id))
        return 1 if res else 0
    except Exception:
        return 0


@eel.expose
def searchLearnedData(keyword, admin_passcode=""):
    """Search stored memories by keyword - strictly main admin only."""
    if not verify_admin_passcode(admin_passcode):
        return json.dumps([])
    records = search_memory_by_keyword(keyword)
    return json.dumps(records)


@eel.expose
def getMemoryStats(admin_passcode=""):
    """
    Retrieve memory statistics.
    Locked by default unless main admin passcode is verified.
    """
    if not verify_admin_passcode(admin_passcode):
        return json.dumps({"searches": 0, "topics": 0, "locked": True})
    stats = get_memory_stats()
    stats["locked"] = False
    return json.dumps(stats)


@eel.expose
def uploadImageSearch(imageDataBase64, filename, engine_choice, prompt=""):
    """
    Handles image uploads and routes to Google Lens, Bing Visual Search,
    or Megatron Vision AI (Gemini 1.5 Flash multimodal) for solution finding.
    """
    import base64
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_dir, "www", "assets", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    # 1. Decode and save image locally
    mime_type = "image/png"
    pure_b64 = imageDataBase64
    if "," in imageDataBase64:
        header, pure_b64 = imageDataBase64.split(",", 1)
        if "image/jpeg" in header or "image/jpg" in header:
            mime_type = "image/jpeg"
        elif "image/webp" in header:
            mime_type = "image/webp"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = "jpg" if "jpeg" in mime_type or "jpg" in mime_type else "png"
    safe_name = f"solution_query_{timestamp}.{ext}"
    local_file_path = os.path.join(upload_dir, safe_name)

    try:
        with open(local_file_path, "wb") as f:
            f.write(base64.b64decode(pure_b64))
    except Exception as e:
        print(f"[Image Save Error] {e}")

    prompt_clean = prompt.strip() if prompt else "Analyze this image and find the step-by-step solution, answer, or technical explanation."

    # 2. Routing based on engine choice
    if engine_choice == "google_lens":
        speak("Opening Google Lens for visual solution search.")
        webbrowser.open("https://lens.google.com/")
        save_search_record(f"Image Solution (Google Lens): {filename or safe_name} - {prompt_clean}", "Opened Google Lens for web solution search", category="image_search")
        return {"status": "opened", "engine": "Google Lens", "message": "Google Lens opened in browser. Drop or select your saved image to view solutions across the web."}

    elif engine_choice == "bing":
        speak("Opening Bing Visual Search for web solutions.")
        webbrowser.open("https://www.bing.com/visualsearch")
        save_search_record(f"Image Solution (Bing Visual): {filename or safe_name} - {prompt_clean}", "Opened Bing Visual Search for web solutions", category="image_search")
        return {"status": "opened", "engine": "Bing Visual Search", "message": "Bing Visual Search opened in browser."}

    elif engine_choice == "yandex":
        speak("Opening Yandex Visual Search.")
        webbrowser.open("https://yandex.com/images/search?rpt=imageview")
        save_search_record(f"Image Solution (Yandex): {filename or safe_name} - {prompt_clean}", "Opened Yandex Visual Search", category="image_search")
        return {"status": "opened", "engine": "Yandex", "message": "Yandex Visual Search opened in browser."}

    else:
        # Default: Megatron Vision AI (multimodal Gemini 1.5 Flash solution finder)
        api_key = get_stored_llm_key()
        if api_key:
            speak("Megatron Vision AI is analyzing the image to find the solution.")
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": (
                                        "You are Megatron Vision AI, an expert multimodal problem solver. "
                                        "Analyze this image thoroughly. Identify the problem, equation, diagram, code error, or object shown. "
                                        "Provide a clear, comprehensive, step-by-step solution, answer, and practical explanation. "
                                        f"User instruction: {prompt_clean}"
                                    )
                                },
                                {
                                    "inline_data": {
                                        "mime_type": mime_type,
                                        "data": pure_b64
                                    }
                                }
                            ]
                        }
                    ]
                }
                headers = {"Content-Type": "application/json"}
                resp = requests.post(url, json=payload, headers=headers, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    full_solution = data["candidates"][0]["content"]["parts"][0]["text"]
                    clean_spoken = markdown_to_text(full_solution)
                    sentences = [s.strip() for s in clean_spoken.split(".") if s.strip()]
                    short_speech = ". ".join(sentences[:2]) + "." if sentences else "Solution generated successfully."
                    speak(short_speech)
                    save_search_record(f"Image AI Solution: {filename or safe_name} - {prompt_clean}", full_solution, category="image_ai")
                    return {"status": "success", "engine": "Megatron Vision AI", "solution": full_solution}
                else:
                    print(f"[Gemini Vision Error {resp.status_code}] {resp.text}")
            except Exception as e:
                print(f"[Vision Exception] {e}")

        # Fallback if no API key or vision error
        speak("Opening Google Lens and Bing Visual Search to find the solution online.")
        webbrowser.open("https://lens.google.com/")
        save_search_record(f"Image Solution: {filename or safe_name} - {prompt_clean}", "Google Lens opened (Gemini API key optional)", category="image_search")
        return {
            "status": "fallback",
            "engine": "Google Lens",
            "message": "Google Lens opened in browser. To enable direct Megatron Vision AI solving, add your Gemini API Key in Settings."
        }


@eel.expose
def getAppMode():
    """Retrieve current execution mode ('browser', 'windows_app', 'android_app')."""
    from engine.config import APP_MODE
    return os.environ.get("MEGATRON_MODE", APP_MODE)


@eel.expose
def setAppMode(mode):
    """Set execution mode dynamically from frontend or launcher."""
    global CURRENT_APP_MODE
    if mode in ["browser", "windows_app", "android_app"]:
        os.environ["MEGATRON_MODE"] = mode
        return 1
    return 0


# ========================================================
# MULTI-PROVIDER AI API INTEGRATION & CONTINUOUS TRAINING
# ========================================================

@eel.expose
def getApiConfig():
    """Retrieve multi-provider API configuration for browser UI."""
    return json.dumps(get_api_config())


@eel.expose
def saveApiConfig(config_json):
    """Save updated API keys and active provider selection."""
    try:
        data = json.loads(config_json) if isinstance(config_json, str) else config_json
        success = save_api_config(data)
        return json.dumps({"success": success, "message": "API configuration updated successfully."})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e)})


@eel.expose
def testApiConnection(provider, api_key, custom_url=""):
    """
    Live test ping to verify whether an attached API key has active quota
    and valid connection before user saves it.
    """
    p = (provider or "").lower().strip()
    key = (api_key or "").strip()
    c_url = (custom_url or "").strip().rstrip("/")

    if not key and p != "custom":
        return json.dumps({"success": False, "message": f"Please provide an API key for {provider.capitalize()}."})

    test_prompt = "Say 'OK' in one word."

    try:
        if p == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
            payload = {"contents": [{"parts": [{"text": test_prompt}]}]}
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
            if resp.status_code == 200:
                mark_provider_quota_exhausted("gemini", False)
                return json.dumps({"success": True, "message": "🟢 Gemini API connection verified! Quota is active."})
            if resp.status_code == 429 or "RESOURCE_EXHAUSTED" in resp.text:
                mark_provider_quota_exhausted("gemini", True)
                return json.dumps({"success": False, "message": "🔴 Gemini Quota Exhausted (429). Please attach a new key."})
            return json.dumps({"success": False, "message": f"Gemini Error ({resp.status_code}): {resp.text[:180]}"})

        elif p == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": test_prompt}], "max_tokens": 10}
            resp = requests.post(url, json=payload, headers=headers, timeout=8)
            if resp.status_code == 200:
                mark_provider_quota_exhausted("openai", False)
                return json.dumps({"success": True, "message": "🟢 OpenAI API connection verified! Quota is active."})
            if resp.status_code == 429 or "insufficient_quota" in resp.text:
                mark_provider_quota_exhausted("openai", True)
                return json.dumps({"success": False, "message": "🔴 OpenAI Quota Exhausted (429). Please attach a new key or check billing."})
            return json.dumps({"success": False, "message": f"OpenAI Error ({resp.status_code}): {resp.text[:180]}"})

        elif p == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": test_prompt}], "max_tokens": 10}
            resp = requests.post(url, json=payload, headers=headers, timeout=8)
            if resp.status_code == 200:
                mark_provider_quota_exhausted("groq", False)
                return json.dumps({"success": True, "message": "🟢 Groq API connection verified! Lightning-fast response."})
            if resp.status_code == 429:
                mark_provider_quota_exhausted("groq", True)
                return json.dumps({"success": False, "message": "🔴 Groq Rate/Quota Limit reached. Please attach a new key."})
            return json.dumps({"success": False, "message": f"Groq Error ({resp.status_code}): {resp.text[:180]}"})

        elif p == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
            payload = {"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": [{"role": "user", "content": test_prompt}], "max_tokens": 10}
            resp = requests.post(url, json=payload, headers=headers, timeout=8)
            if resp.status_code == 200:
                mark_provider_quota_exhausted("openrouter", False)
                return json.dumps({"success": True, "message": "🟢 OpenRouter connection verified! Credits are active."})
            if resp.status_code in (402, 429):
                mark_provider_quota_exhausted("openrouter", True)
                return json.dumps({"success": False, "message": "🔴 OpenRouter Credits/Quota Exhausted. Please attach a funded key."})
            return json.dumps({"success": False, "message": f"OpenRouter Error ({resp.status_code}): {resp.text[:180]}"})

        elif p == "custom":
            target_url = (c_url or "http://localhost:11434/v1") + "/chat/completions"
            headers = {"Content-Type": "application/json"}
            if key: headers["Authorization"] = f"Bearer {key}"
            payload = {"model": "llama3", "messages": [{"role": "user", "content": test_prompt}], "max_tokens": 10}
            resp = requests.post(target_url, json=payload, headers=headers, timeout=8)
            if resp.status_code == 200:
                return json.dumps({"success": True, "message": f"🟢 Custom Endpoint ({c_url}) connected successfully!"})
            return json.dumps({"success": False, "message": f"Custom Endpoint HTTP {resp.status_code}: {resp.text[:180]}"})

        return json.dumps({"success": False, "message": f"Unknown provider: {provider}"})
    except Exception as ex:
        return json.dumps({"success": False, "message": f"Connection Exception: {str(ex)}"})


@eel.expose
def getTrainingStats():
    """Retrieve real-time continuous model training metrics for HUD and Vault."""
    stats = get_training_stats()
    return json.dumps(stats)


@eel.expose
def forceTrainEntry(topic, summary, category="operator_train"):
    """Manually train a new knowledge node or fact into Megatron's memory."""
    try:
        save_search_record(topic, summary, category=category)
        return json.dumps({"success": True, "message": "Knowledge node trained into Megatron neural memory."})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e)})


@eel.expose
def uninstallMegatronSystem():
    """
    Initiates complete system uninstallation of Megatron.
    Stops processes, cleans up shortcuts, purges database and deletes all project files completely.
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        uninstaller_bat = os.path.join(base_dir, "uninstall_megatron.bat")
        if os.path.exists(uninstaller_bat):
            subprocess.Popen(["cmd.exe", "/c", "start", "", uninstaller_bat], shell=True)
            return json.dumps({"success": True, "message": "Uninstallation initiated. Megatron will now close and delete all files."})
        return json.dumps({"success": False, "message": "Uninstaller script not found."})
    except Exception as e:
        return json.dumps({"success": False, "message": str(e)})