# Megatron AI Desktop Assistant ⚡🤖

Megatron is an advanced desktop AI assistant built with **Python Eel**, **OpenCV**, and modern web technologies. Equipped with voice recognition, facial biometric authentication, computer vision, system automation, and generative AI reasoning.

---

## 🌟 Key Features

1. **Biometric Face Authentication**:
   - Real-time facial authentication using OpenCV Haar cascades and LBPH recognition.
   - Built-in fail-safe and instant bypass options so you never get locked out.

2. **Voice & Text Command Router**:
   - Continuous hotword listening ("Megatron", "Alexa").
   - Voice feedback using multi-threaded `pyttsx3` text-to-speech engine.
   - Global hotkey shortcut (`Win + J` or `Ctrl + J` or `Ctrl + Space`).

3. **Online AI Platforms Hub**:
   - One-click launcher and voice commands for top AI services:
     - **ChatGPT**: "Open ChatGPT", "Ask ChatGPT [prompt]" (auto-copies prompt to clipboard).
     - **Claude AI**: "Open Claude", "Ask Claude [prompt]".
     - **Google Gemini**: "Open Gemini".
     - **Perplexity AI**: "Open Perplexity", "Ask Perplexity [query]" (searches directly online).
     - **Microsoft Copilot**: "Open Copilot".
   - Interactive Quick Dock buttons on the desktop HUD and chat drawer chips.

4. **Real-Time Live Internet Data & Search**:
   - **Live Weather**: "Weather in [city]", "Temperature today" (live real-time report from wttr.in).
   - **Top News Headlines**: "Latest news", "News about [topic]" (real-time Google News RSS).
   - **Live Knowledge & Search**: "Search internet for [topic]", "Look up [query]" (DuckDuckGo + Wikipedia).

5. **System & Desktop Automation**:
   - **App Launcher**: Open Notepad, Calculator, Command Prompt, File Explorer, Task Manager, Control Panel, etc.
   - **Audio Controls**: "Volume up", "Volume down", "Mute / Unmute".
   - **Screen Actions**: "Take screenshot" (auto-saved to Pictures), "Lock screen", "Show desktop".

6. **Web & Media Streaming**:
   - **YouTube Playback**: "Play [song] on YouTube" or "Play [song]".
   - **Web Navigation**: Instant launch of Google, GitHub, ChatGPT, Wikipedia, Spotify, Netflix, etc.
   - **Google Web Search**: "Search [topic] on Google".

7. **Contacts & Communications**:
   - **WhatsApp Automation**: Send messages and initiate voice/video calls.
   - **Android Mobile Bridge**: SMS sending and phone dialer via wireless ADB.

8. **Dual-Core AI Reasoning**:
   - **Autonomous Built-in Engine**: Offline & online answers for identity, math evaluations, time, date, Wikipedia summaries, and system queries.
   - **Google Gemini Generative AI**: Optional integration with Gemini 1.5 Flash via REST API (configurable directly inside Assistant Settings in the GUI).

---

## 🚀 Getting Started

### 1. Installation

Ensure Python 3.10+ is installed on your Windows machine:

```powershell
pip install -r requirements.txt
```

### 2. Launching Megatron

To launch the full suite (Desktop GUI + Background Hotword Listener):

```powershell
python run.py
```

To run only the standalone Desktop GUI:

```powershell
python main.py
```

---

## ⚙️ Configuration & Settings

- **Settings Modal**: Click the gear icon `⚙️` in the Megatron HUD to:
  - View and edit your personal profile (Name, Designation, Phone, City).
  - Add or delete custom **System Commands** (e.g., custom `.exe` paths).
  - Add or delete custom **Web Commands** (e.g., favorite bookmarks and URLs).
  - Manage your **Phone Book** contacts.
  - Set or update your **Google Gemini API Key** under the **AI & Settings** tab.
- **Database**: All configuration and data is stored locally in `megatron.db` (SQLite3).

---

## 🔒 Biometric Training (Optional)

To train Megatron with your own face:

1. Capture samples:
   ```powershell
   python engine/auth/sample.py
   ```
2. Train the model:
   ```powershell
   python engine/auth/trainer.py
   ```

---

## 🛡️ Note on Version Control

> **Notice**: As per project guidelines, all commits and development remain strictly **local**. No code is pushed to remote GitHub repositories without explicit instruction.
