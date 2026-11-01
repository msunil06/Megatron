import datetime
import os
import re
import threading
import time

import eel
import pyautogui
import pyttsx3
import speech_recognition as sr

# Safe lock for text-to-speech with timeout to prevent SAPI5 concurrency deadlocks
tts_lock = threading.Lock()

def speak(text):
    """Speaks the text, updates web UI immediately, and triggers crisp browser speech."""
    if not text:
        return
    text = str(text).strip()
    print(f"[Megatron] {text}")

    # 1. Update web UI immediately (Live Response Box, Chat History, Siri text)
    try:
        eel.DisplayMessage(text)
        eel.receiverText(text)
        eel.showLiveResponse(text)
    except Exception as e:
        print(f"[UI Display Warning] {e}")

    # 2. Native Windows SAPI5 TTS execution with lock timeout so it NEVER deadlocks
    def _speak_worker(msg):
        acquired = tts_lock.acquire(timeout=2.0)
        if not acquired:
            print("[TTS Info] SAPI5 busy; browser Web Speech API is handling audio output.")
            return
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass
            engine = pyttsx3.init('sapi5')
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 174)
            engine.setProperty('volume', 1.0)
            engine.say(msg)
            engine.runAndWait()
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except Exception:
                pass
        except Exception as ex:
            print(f"[TTS Error] {ex}")
        finally:
            try:
                tts_lock.release()
            except Exception:
                pass

    threading.Thread(target=_speak_worker, args=(text,), daemon=True).start()


def takecommand():
    """Listens to user input via microphone with speech_recognition."""
    r = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("[Megatron] Listening for voice input...")
            try:
                eel.DisplayMessage("Listening...")
            except Exception:
                pass
            r.pause_threshold = 0.8
            r.adjust_for_ambient_noise(source, duration=0.4)
            audio = r.listen(source, timeout=4, phrase_time_limit=5)

        print("[Megatron] Recognizing speech...")
        try:
            eel.DisplayMessage("Recognizing...")
        except Exception:
            pass
        query = r.recognize_google(audio, language='en-in')
        print(f"[User Said] {query}")
        try:
            eel.DisplayMessage(query)
        except Exception:
            pass
        return query.lower().strip()

    except sr.WaitTimeoutError:
        print("[Megatron] Voice listening timed out.")
        return ""
    except sr.UnknownValueError:
        print("[Megatron] Could not understand audio.")
        return ""
    except Exception as e:
        print(f"[takecommand Error] {e}")
        return ""


@eel.expose
def allCommands(message=1):
    """
    Primary command router for Megatron, handling voice & text queries.
    Dispatches to background thread so Eel WebSocket event loop NEVER blocks,
    preventing UI freezes and keeping all buttons, scrolling, and controls responsive.
    """
    def _worker():
        if message == 1:
            query = takecommand()
            if not query:
                speak("I didn't catch that, Commander. You can ask me anything or type in the chat box.")
                try:
                    eel.ShowHood()
                except Exception:
                    pass
                return
            try:
                eel.senderText(query)
            except Exception:
                pass
        else:
            query = str(message).strip()
            if not query:
                try:
                    eel.ShowHood()
                except Exception:
                    pass
                return
            try:
                eel.senderText(query)
            except Exception:
                pass

        q = query.lower()

        try:
            # Check for PC hardware control commands
            is_pc_control = any(k in q for k in [
                "volume up", "increase volume", "volume down", "decrease volume", "mute", "unmute",
                "screenshot", "take screenshot", "lock screen", "lock pc", "lock system", "minimize all",
                "show desktop"
            ])

            if is_pc_control:
                from engine.config import APP_MODE
                current_mode = os.environ.get("MEGATRON_MODE", APP_MODE)
                if current_mode == "browser":
                    speak("PC hardware control is disabled in Browser Web Agent mode. Please launch or install the Megatron Windows Software for full system control.")
                    try:
                        eel.ShowHood()
                    except Exception:
                        pass
                    return

            # 1. System volume controls
            if "volume up" in q or "increase volume" in q:
                speak("Increasing volume")
                for _ in range(5):
                    pyautogui.press("volumeup")

            elif "volume down" in q or "decrease volume" in q:
                speak("Decreasing volume")
                for _ in range(5):
                    pyautogui.press("volumedown")

            elif "mute" in q or "unmute" in q:
                speak("Toggling volume mute")
                pyautogui.press("volumemute")

            # 2. Screenshot
            elif "screenshot" in q or "take screenshot" in q:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                pics_dir = os.path.join(os.path.expanduser("~"), "Pictures")
                if not os.path.exists(pics_dir):
                    pics_dir = os.path.expanduser("~")
                filepath = os.path.join(pics_dir, f"Megatron_Screenshot_{timestamp}.png")
                pyautogui.screenshot(filepath)
                speak(f"Screenshot captured and saved to Pictures.")

            # 3. Screen Lock / Desktop
            elif "lock screen" in q or "lock pc" in q or "lock system" in q:
                speak("Locking workstation, Commander.")
                os.system("rundll32.exe user32.dll,LockWorkStation")

            elif "minimize all" in q or "show desktop" in q:
                pyautogui.hotkey("win", "d")
                speak("Showing desktop.")

            # 4. Online AI Platforms (ChatGPT, Claude, Gemini, Perplexity, Copilot)
            elif any(ai in q for ai in ["chatgpt", "chat gpt", "claude", "gemini", "perplexity", "copilot", "huggingface"]):
                from engine.features import open_online_ai
                prompt = re.sub(r'^(open|launch|ask|consult)\s+(chatgpt|chat gpt|claude|gemini|perplexity|copilot|huggingface)\s*', '', q, flags=re.IGNORECASE).strip()
                target_ai = "chatgpt"
                for k in ["chatgpt", "chat gpt", "claude", "gemini", "perplexity", "copilot", "huggingface"]:
                    if k in q:
                        target_ai = k
                        break
                open_online_ai(target_ai, prompt)

            # 5. Live Real-Time Weather
            elif "weather" in q or "temperature" in q:
                from engine.features import fetch_live_weather
                city_match = re.search(r'\b(?:in|at|for|of)\s+([a-zA-Z\s]+)', q)
                city = city_match.group(1).strip() if city_match else ""
                fetch_live_weather(city)

            # 6. Live Top News Headlines
            elif "news" in q or "headline" in q:
                from engine.features import fetch_live_news
                topic_match = re.search(r'\b(?:about|on|regarding|for)\s+([a-zA-Z\s]+)', q)
                topic = topic_match.group(1).strip() if topic_match else ""
                fetch_live_news(topic)

            # 7. Real-time Live Internet Search
            elif "search internet" in q or "search online" in q or "look up" in q:
                from engine.features import search_internet_live
                search_internet_live(query)

            # 8. Open applications or websites
            elif q.startswith("open ") or " open " in q or q.startswith("launch "):
                from engine.features import openCommand
                openCommand(query)

            # 9. YouTube playback
            elif "on youtube" in q or q.startswith("play "):
                from engine.features import PlayYoutube
                from engine.db import save_search_record
                save_search_record(query, f"YouTube playback for {query}", category="media")
                PlayYoutube(query)

            # 10. Web Search
            elif q.startswith("search ") or q.startswith("google "):
                term = re.sub(r'^(search|google|search for)\s+', '', q).strip()
                if term:
                    import webbrowser
                    from urllib.parse import quote
                    from engine.db import save_search_record
                    save_search_record(term, f"Google search for {term}", category="web_search")
                    speak(f"Searching Google for {term}")
                    webbrowser.open(f"https://www.google.com/search?q={quote(term)}")
                else:
                    speak("What would you like me to search for?")

            # 11. WhatsApp / Phone / SMS
            elif any(phrase in q for phrase in ["send message", "phone call", "video call", "call to", "whatsapp"]):
                from engine.features import findContact, makeCall, sendMessage, whatsApp
                contact_no, name = findContact(query)
                if contact_no != 0:
                    speak("Which mode would you like to use: WhatsApp or Mobile?")
                    preference = takecommand()

                    if "mobile" in preference:
                        if "send message" in q or "send sms" in q:
                            speak("What message would you like to send?")
                            msg = takecommand()
                            sendMessage(msg, contact_no, name)
                        elif "phone call" in q or "call" in q:
                            makeCall(name, contact_no)
                        else:
                            speak("Instruction unclear. Please try again.")
                    elif "whatsapp" in preference or "whats app" in preference:
                        if "send message" in q:
                            speak("What message would you like to send?")
                            msg = takecommand()
                            whatsApp(contact_no, msg, 'message', name)
                        elif "phone call" in q:
                            whatsApp(contact_no, '', 'call', name)
                        else:
                            whatsApp(contact_no, '', 'video call', name)
                    else:
                        speak("Defaulting to WhatsApp.")
                        whatsApp(contact_no, '', 'call', name)

            # 12. Generative AI Conversational Brain & Continuous Learning
            else:
                from engine.features import geminai
                geminai(query)

        except Exception as e:
            print(f"[allCommands Exception] {e}")
            speak("An error occurred while processing your command.")

        finally:
            try:
                eel.ShowHood()
            except Exception:
                pass

    threading.Thread(target=_worker, daemon=True).start()
    return 1