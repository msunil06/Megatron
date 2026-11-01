# 📁 Megatron AI — Folder and File Engineering Guide

This document is your comprehensive, file-by-file technical reference. Use this guide whenever you want to inspect, refactor, upgrade, or explain any file or folder in the Megatron AI codebase to an interviewer or collaborator.

---

## 🗂️ Complete Directory Layout

```
D:\J-238\Jarvis/ (or megatron/)
├── main.py                     # Primary entrypoint for Megatron Web Agent & Eel server
├── run.py                      # Multi-process launcher (Hotword background listener + UI)
├── megatron.db                 # SQLite database storing settings, history, and neural memory
├── requirements.txt            # Python dependencies (eel, pyautogui, requests, pyttsx3, etc.)
├── uninstall_megatron.bat      # 1-click complete uninstaller (self-purges all files from system)
├── rename_to_megatron.bat      # Folder rename utility (run when IDE is closed)
│
├── engine/                     # Python Core Intelligence & Operating System Engine
│   ├── command.py              # User query intake, speech synthesis (speak), PC hardware actions
│   ├── features.py             # Multi-Provider AI router, autonomous web search, weather, vision
│   ├── db.py                   # Database schema, continuous training, neural recall, security
│   ├── config.py               # Environment configuration, defaults, assistant name
│   ├── helper.py               # Text cleaning, regex extractors, ADB Android bridge utilities
│   └── auth/
│       └── recoganize.py       # Face authentication module using OpenCV / Haar cascade
│
├── www/                        # Frontend Presentation Layer (HTML5, Vanilla CSS3, JS)
│   ├── index.html              # Main Holographic HUD, Arc Core, Live Response Card, Modals
│   ├── style.css               # Marvel cyan-tech design system, animations, responsive grid
│   ├── main.js                 # Frontend event bus, API key switcher, training stats, vault auth
│   ├── controller.js           # Eel bridge receiver, Live Response renderer, Web Speech API
│   ├── script.js               # Equalizer spectrum visualizer & particle background
│   ├── manifest.json           # Web App Manifest for mobile installation
│   ├── service-worker.js       # PWA service worker for offline caching & Android installation
│   ├── downloads/              # Distribution Packages served directly in browser (Windows Suite .zip & Android .apk)
│   └── assets/                 # Graphics, logos, start audio chimes, vendor animations
│
├── windows_app/                # Windows Native Desktop Suite
│   ├── megatron_windows.py     # Native desktop client with full system hardware controls
│   ├── run_megatron_windows.bat# 1-click Windows Desktop Suite launcher
│   └── uninstall.bat           # Desktop suite uninstaller launcher
│
├── android_app/                # Android Mobile Application (Native & WebView Bridge)
│   ├── build.gradle            # Gradle build configuration
│   └── src/                    # Native Android Java/Kotlin source code & AndroidManifest
│
└── megatron_details/           # Complete Architecture & Interview Knowledge Repository
    ├── README.md               # Knowledge base index
    ├── ARCHITECTURE_DIAGRAMS.md# Mermaid system, sequence, and entity relationship diagrams
    ├── FOLDER_AND_FILE_GUIDE.md# This comprehensive engineering manual
    └── INTERVIEW_PREPARATION_GUIDE.md # Technical interview pitch & senior Q&A cheat sheet
```

---

## 🔍 Detailed Component & File Breakdown

### 1. Root Application Files

#### `main.py`
- **Role**: Primary application bootstrapper.
- **Key Functions**:
  - `start()`: Initializes Eel pointing to `www/`, plays startup chime, exposes `skipAuth()`, `init()`, and starts the Eel web server on `http://localhost:8000`.
  - `open_browser()`: Launches Microsoft Edge in `--app="http://localhost:8000/index.html"` mode or falls back to the default web browser.
  - `eel._detect_shutdown = lambda: None`: Prevents Eel from abruptly shutting down if a browser tab reloads or disconnects.
- **Future Improvements**:
  - To change the host or port, modify the `port=8000` argument in `eel.start()`.

#### `run.py`
- **Role**: Multi-processing launcher for voice hotword detection + GUI.
- **Key Functions**:
  - `startMegatron()`: Spawns the main UI process.
  - `listenHotword()`: Spawns the background hotword audio listener (`engine.features.hotword()`).
- **Future Improvements**:
  - To adjust process priority or run headless, configure the `multiprocessing.Process` parameters here.

#### `uninstall_megatron.bat`
- **Role**: Complete, zero-residual system uninstaller.
- **Workflow**:
  1. Requests confirmation from the user (can also be invoked silently with `--silent`).
  2. Terminates all active Megatron processes using `taskkill` and `wmic`.
  3. Deletes Desktop and Start Menu shortcuts (`Megatron AI.lnk`).
  4. Deploys a self-deleting script to `%TEMP%` that waits 2 seconds and recursively deletes the entire directory (`Remove-Item -Recurse -Force`) so nothing remains on the hard drive.

---

### 2. `engine/` — Intelligence & System Integration

#### `engine/command.py`
- **Role**: Query routing, input processing, and text-to-speech output.
- **Key Functions**:
  - `speak(text)`: Dual speech output:
    1. Sends text to the UI via `eel.DisplayMessage(text)`, `eel.receiverText(text)`, and `eel.showLiveResponse(text)` (which plays crisp browser audio via Web Speech API).
    2. Spawns a background thread with `pyttsx3.init('sapi5')` wrapped in `pythoncom.CoInitialize()` and `pythoncom.CoUninitialize()` for rock-solid Windows COM audio playback.
  - `takecommand()`: Uses `speech_recognition.Recognizer()` with microphone ambient noise adjustment to capture user voice.
  - `allCommands(message=1)`: Primary router. Handles voice (`message=1`) and text (`message="query"`):
    - PC controls (volume up/down/mute, screenshot, lock workstation, minimize windows).
    - Media streaming (YouTube music).
    - Contact communications (WhatsApp, phone calls, SMS via ADB).
    - Passes conversational queries to `engine.features.geminai(query)`.
- **How to Add New Voice Commands**:
  - Inside `allCommands()`, add an `elif "your keyword" in q:` block before the final `else:` fallback.

#### `engine/features.py`
- **Role**: Conversational AI brain, multi-provider router, and autonomous tool engine.
- **Key Functions**:
  - `geminai(query)`:
    1. Recalls prior knowledge using `find_learned_context(query)`.
    2. Calls active attached AI Provider via `call_llm_api(query, memory_instruction)`.
    3. If active API quota is ended, automatically switches to backup attached provider.
    4. If no external API key is attached, executes `handle_autonomous_query()` (live DuckDuckGo, weather, news, math).
    5. Saves and trains on every query/response using `save_search_record()`.
  - `call_llm_api(query, memory_instruction)`: Rotates through configured providers with automatic failover upon receiving HTTP 429 quota errors.
  - `_dispatch_single_provider(provider, query, memory_instruction, config)`: Handles HTTP payloads for:
    - **Gemini**: REST API (`models/gemini-1.5-flash:generateContent`).
    - **OpenAI**: Chat completions (`gpt-4o-mini`).
    - **Groq Cloud**: OpenAI-compatible REST API (`llama-3.3-70b-versatile`).
    - **OpenRouter**: Unified API (`meta-llama/llama-3.3-70b-instruct:free`).
    - **Custom LLM**: Configurable local endpoint (`http://localhost:11434/v1`).
  - `uploadImageSearch(...)`: Handles multimodal image uploads and routes to Gemini Vision, Google Lens, or Bing Visual Search.
  - `testApiConnection(provider, api_key, custom_url)`: Live ping verifying API key validity and active quota before saving.
  - `uninstallMegatronSystem()`: Spawns `uninstall_megatron.bat` for complete system uninstallation.
- **How to Add a New LLM Provider**:
  - Add an `elif p == "new_provider":` block in `_dispatch_single_provider()`, and add the provider name to `all_providers` in `call_llm_api()`.

#### `engine/db.py`
- **Role**: Database persistence, schema migrations, and continuous training engine.
- **Tables**:
  - `search_history`: Every query, generated answer, and category timestamped.
  - `learned_memory`: Normalized semantic knowledge nodes with `topic`, `summary`, `keywords`, `access_count`, and `confidence` (1.0 to 5.0).
  - `settings`: Active provider, API keys, quota exhaustion status, and admin master passcode.
  - `sys_command` / `web_command`: User-defined launch shortcuts.
  - `contacts` / `info`: Personal phonebook and user operator profile.
- **Key Continuous Training Functions**:
  - `save_search_record(query, response, category)`: Extracts non-stopword keywords, updates topic frequency, and dynamically adjusts neural confidence weights.
  - `find_learned_context(query)`: Queries semantic topics matching the terms in the query to provide ground truth context.
  - `get_training_stats()`: Returns total queries learned, synapse nodes, and average confidence.

#### `engine/config.py`
- **Role**: Environment variable bindings and default constant definitions (`ASSISTANT_NAME = 'Megatron'`, `DB_NAME = 'megatron.db'`).

---

### 3. `www/` — Frontend Interface & Holographic Design

#### `www/index.html`
- **Structure**:
  1. `<head>`: Outfitted with Google Fonts (*Orbitron*, *Outfit*, *Rajdhani*), Bootstrap 5, Bootstrap Icons, Animate.css.
  2. `#Oval`: Main active HUD containing:
     - Top Telemetry Bar (`#HudModePill`, `#HudTrainingPill`, `#HudAdminStatusPill`).
     - `#MegatronHood`: Holographic Marvel-inspired Arc Reactor Core with rotating azimuth brackets, scanner, and equalizer ring.
     - `#MegatronLiveResponseBox`: Holographic response card with readable answer text, voice replay button, and copy button.
     - `#TextInput`: Input field with Send, Voice Mic, API Integration, Image Search, Admin Vault, and Settings buttons.
     - `#AiQuickDock`: Direct quick launchers (ChatGPT, Claude, Gemini, Perplexity, Weather, News).
  3. `#exampleModal`: Full System Settings & Intelligence Hub modal with:
     - Tab 1: Operator Profile.
     - Tab 2: Custom System & Web Commands.
     - Tab 3: Comms Directory Phonebook.
     - **Tab 4: Multi-Provider API Integration & Continuous Model Training Hub**.
     - **Tab 5: Level 0 Classified Admin Neural Vault** (passcode-protected).
     - **Tab 6: Native Deployment Suites & Complete System Uninstaller**.
  4. `#ImageSearchModal`: Visual Solution Finder modal with drag & drop image upload and engine selector.

#### `www/style.css`
- **Design Tokens**:
  - `--megatron-cyan: #00f0ff;`
  - `--megatron-blue: #0066ff;`
  - `--megatron-dark: #030712;`
  - High-performance GPU-accelerated keyframe animations: `megatronAzimuthRotate`, `megatronTechInnerRotate`, `megatronArcCorePulse`, `megatronScannerSweep`.
  - Frosted glassmorphism (`backdrop-filter: blur(14px)`).

#### `www/main.js`
- **Role**: Frontend orchestrator.
- **Key Logic**:
  - `PlayAssistant(message)`: Calls `eel.allCommands(message)()` using proper double-parenthesis callback invocation.
  - `loadApiConfig()` / `applyProviderUI(provider)`: Populates API key inputs, active badges, and custom URL fields.
  - `#TestConnectionBtn`: Calls `eel.testApiConnection()` and displays green active status or red quota warning.
  - `#SaveApiConfigBtn`: Persists API configuration across providers.
  - `#SubmitTrainFactBtn`: Allows the user to manually teach Megatron new knowledge nodes.
  - `#TriggerSystemUninstallBtn`: Prompts for confirmation and triggers complete system purge.

#### `www/controller.js`
- **Role**: Eel bridge receiver methods exposed to Python.
- **Key Exposed Functions**:
  - `showLiveResponse(message)`: Fades in `#MegatronLiveResponseBox`, sets text, scrolls smoothly, and triggers `speakBrowserVoice(message)`.
  - `speakBrowserVoice(text)`: Utilizes browser `window.speechSynthesis` for clear, lag-free voice playback.
  - `DisplayMessage(text)`: Updates `.siri-message` textillate animation.
  - `receiverText(text)` & `senderText(text)`: Appends messages to the offcanvas chat history drawer.

---

### 4. `windows_app/` — Desktop Suite

#### `windows_app/megatron_windows.py`
- **Role**: Native Windows desktop automation client.
- **Unlocked Hardware Controls**:
  - `pyautogui.press('volumeup')`, `'volumedown'`, `'volumemute'`.
  - `os.system('rundll32.exe user32.dll,LockWorkStation')`.
  - `pyautogui.screenshot(...)` saved directly to the user's `Pictures` directory.
  - Global hotkey listener: Pressing `Win+J` from anywhere in Windows brings Megatron to the front and activates voice listening.

---

### 5. `android_app/` — Mobile Suite

- **Role**: Android smartphone native packaging.
- **Components**:
  - `MainActivity`: Fullscreen hardware-accelerated WebView rendering `http://<LAN_IP>:8000/index.html` or local PWA assets.
  - Native Javascript Bridge: Intercepts phone call and SMS commands to trigger native Android `android.intent.action.CALL` and `android.intent.action.SENDTO` without needing third-party servers.
  - Camera Intent: Captures photos on mobile and routes them directly to Megatron Visual Solution Finder.
