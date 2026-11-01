# Megatron AI — Android Mobile App Suite

This directory contains the complete Android Mobile Application for Megatron AI, configured with full mobile device system control permissions.

## Features with Full Mobile Device Control
- **Direct Phone Calling**: Place cellular calls using native Android telephony.
- **Direct SMS Messaging**: Dispatch SMS text messages through native `SmsManager`.
- **Torch / Flashlight Control**: Toggle phone hardware flashlight.
- **Haptic Feedback & Vibration**: Custom duration haptic pulses.
- **Battery Status Monitoring**: Read battery percentage and charging state in real time.
- **Camera Problem Solving**: Capture photos and screenshots for instant visual solution finding.
- **Speech Recognition & TTS**: Voice assistant input on the go.

## How to Install and Run

### Method 1: Instant PWA Install (Zero Compilation Needed)
1. Ensure your PC and Android phone are on the same Wi-Fi network.
2. Find your PC's IP address (e.g. `192.168.1.5`).
3. On your Android phone, open Chrome or Edge and navigate to: `http://<YOUR_PC_IP>:8000/index.html`.
4. Chrome will prompt **"Add Megatron to Home Screen"** or **"Install App"**.
5. Tap **Install** — Megatron will install as a native full-screen app on your Android home screen!

### Method 2: Compile & Install Native APK via Android Studio / Gradle
1. Open Android Studio -> Open an existing project -> Select this `android_app` directory.
2. Build -> Build Bundle(s) / APK(s) -> **Build APK(s)**.
3. Transfer the generated `app-debug.apk` to your Android device and install it.
4. When prompted, grant Call, SMS, and Camera permissions to enable full mobile controls!
