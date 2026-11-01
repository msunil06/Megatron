import os

ASSISTANT_NAME = "megatron"
LLM_KEY = os.environ.get("GEMINI_API_KEY", "")
DB_NAME = "megatron.db"

# Execution Modes: 'browser', 'windows_app', 'android_app'
APP_MODE = os.environ.get("MEGATRON_MODE", "browser")