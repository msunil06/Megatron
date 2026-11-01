import os
import sqlite3
from engine.config import DB_NAME, ASSISTANT_NAME, LLM_KEY

def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), DB_NAME)
    con = sqlite3.connect(db_path, check_same_thread=False)
    return con

def init_db():
    con = get_connection()
    cursor = con.cursor()

    # 1. System Commands Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sys_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE,
            path VARCHAR(1000)
        )
    ''')

    # 2. Web Commands Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_command (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) UNIQUE,
            url VARCHAR(1000)
        )
    ''')

    # 3. Contacts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200),
            mobile_no VARCHAR(255),
            email VARCHAR(255),
            address VARCHAR(255)
        )
    ''')

    # 4. Personal Info Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100),
            designation VARCHAR(50),
            mobileno VARCHAR(40),
            email VARCHAR(200),
            city VARCHAR(300)
        )
    ''')

    # 5. App Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key VARCHAR(100) PRIMARY KEY,
            value TEXT
        )
    ''')

    # 6. Search History Table (persistent memory for training/recall)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            response TEXT,
            category VARCHAR(50) DEFAULT 'general',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 7. Learned Memory & Knowledge Table (AI Continuous Training Synapses)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learned_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic VARCHAR(250) UNIQUE,
            summary TEXT,
            keywords TEXT,
            category VARCHAR(50) DEFAULT 'general',
            access_count INTEGER DEFAULT 1,
            confidence REAL DEFAULT 1.0,
            last_queried DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Gracefully upgrade table schema if existing
    for col_def in [
        ("keywords", "TEXT DEFAULT ''"),
        ("category", "VARCHAR(50) DEFAULT 'general'"),
        ("confidence", "REAL DEFAULT 1.0"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE learned_memory ADD COLUMN {col_def[0]} {col_def[1]}")
        except Exception:
            pass

    # Seed System Commands
    default_sys_commands = [
        ('notepad', 'notepad.exe'),
        ('calculator', 'calc.exe'),
        ('calc', 'calc.exe'),
        ('paint', 'mspaint.exe'),
        ('command prompt', 'cmd.exe'),
        ('cmd', 'cmd.exe'),
        ('powershell', 'powershell.exe'),
        ('task manager', 'taskmgr.exe'),
        ('taskmgr', 'taskmgr.exe'),
        ('file explorer', 'explorer.exe'),
        ('explorer', 'explorer.exe'),
        ('wordpad', 'write.exe'),
        ('control panel', 'control.exe'),
        ('settings', 'ms-settings:'),
        ('edge', 'msedge.exe'),
        ('browser', 'msedge.exe'),
    ]
    for name, path in default_sys_commands:
        cursor.execute('INSERT OR IGNORE INTO sys_command (name, path) VALUES (?, ?)', (name, path))

    # Seed Web Commands (including Online AI tools)
    default_web_commands = [
        ('google', 'https://www.google.com'),
        ('youtube', 'https://www.youtube.com'),
        ('github', 'https://www.github.com'),
        ('gmail', 'https://mail.google.com'),
        ('chatgpt', 'https://chatgpt.com'),
        ('claude', 'https://claude.ai'),
        ('gemini', 'https://gemini.google.com'),
        ('perplexity', 'https://www.perplexity.ai'),
        ('copilot', 'https://copilot.microsoft.com'),
        ('huggingface', 'https://huggingface.co/chat'),
        ('wikipedia', 'https://www.wikipedia.org'),
        ('whatsapp', 'https://web.whatsapp.com'),
        ('netflix', 'https://www.netflix.com'),
        ('spotify', 'https://open.spotify.com'),
        ('twitter', 'https://twitter.com'),
        ('x', 'https://x.com'),
        ('linkedin', 'https://www.linkedin.com'),
        ('amazon', 'https://www.amazon.com'),
        ('reddit', 'https://www.reddit.com'),
    ]
    for name, url in default_web_commands:
        cursor.execute('INSERT OR IGNORE INTO web_command (name, url) VALUES (?, ?)', (name, url))

    # Seed Personal Info if empty
    cursor.execute('SELECT COUNT(*) FROM info')
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            '''INSERT INTO info (name, designation, mobileno, email, city)
               VALUES (?, ?, ?, ?, ?)''',
            ('Commander', 'Lead Engineer', '+91 9876543210', 'commander@megatron.ai', 'Cybertron')
        )

    # Seed Contacts if empty
    cursor.execute('SELECT COUNT(*) FROM contacts')
    if cursor.fetchone()[0] == 0:
        default_contacts = [
            ('Emergency', '+91 112', 'emergency@sos.org', 'Control Room'),
            ('Support', '+91 1800112233', 'support@megatron.ai', 'Global HQ'),
        ]
        for name, phone, email, addr in default_contacts:
            cursor.execute('INSERT INTO contacts (name, mobile_no, email, address) VALUES (?, ?, ?, ?)',
                           (name, phone, email, addr))

    # Seed App Settings & Multi-Provider AI API Integrations
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('assistant_name', ASSISTANT_NAME))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('llm_key', LLM_KEY))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('admin_passcode', 'admin123'))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('active_ai_provider', 'gemini'))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('gemini_api_key', LLM_KEY))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('openai_api_key', os.environ.get("OPENAI_API_KEY", "")))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('groq_api_key', os.environ.get("GROQ_API_KEY", "")))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('openrouter_api_key', os.environ.get("OPENROUTER_API_KEY", "")))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('custom_api_url', 'http://localhost:11434/v1'))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('custom_api_key', ''))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('auto_failover', '1'))
    cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('quota_exhausted_providers', ''))

    con.commit()
    con.close()

# Stopwords for semantic keyword filtering
_STOPWORDS = {
    'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'in', 'of', 'for', 'to',
    'what', 'who', 'how', 'when', 'where', 'why', 'can', 'you', 'please', 'tell', 'me',
    'about', 'this', 'that', 'with', 'by', 'from', 'up', 'down', 'out', 'my', 'your',
    'search', 'online', 'find', 'megatron', 'hey', 'hello', 'hi', 'it', 'its', 'be',
    'do', 'does', 'did', 'have', 'has', 'had', 'will', 'would', 'should', 'give'
}

def _extract_keywords(text):
    """Extract semantic keywords for neural memory training."""
    if not text:
        return ""
    words = [w.strip(".,!?:;\"'()[]{}") for w in text.lower().split()]
    meaningful = [w for w in words if len(w) > 2 and w not in _STOPWORDS]
    return " ".join(list(dict.fromkeys(meaningful))[:12])

# Memory and Search History Helpers (Continuous Model Training)
def save_search_record(query, response="", category="general"):
    """
    Persists and trains Megatron's continuous neural model on EVERY search and response.
    1. Records complete query and answer in persistent search history.
    2. Dynamically indexes keywords, semantic topics, access counts, and confidence weights.
    """
    if not query or not query.strip():
        return
    q_clean = query.strip()
    r_clean = response.strip() if response else ""
    keywords = _extract_keywords(f"{q_clean} {r_clean}")
    topic = q_clean.lower()[:200]

    con = get_connection()
    cursor = con.cursor()
    try:
        # 1. Append to search history log
        cursor.execute(
            '''INSERT INTO search_history (query, response, category) VALUES (?, ?, ?)''',
            (q_clean, r_clean, category)
        )

        # 2. Train continuous learned memory
        cursor.execute(
            '''INSERT INTO learned_memory (topic, summary, keywords, category, access_count, confidence, last_queried)
               VALUES (?, ?, ?, ?, 1, 1.0, CURRENT_TIMESTAMP)
               ON CONFLICT(topic) DO UPDATE SET
                   access_count = access_count + 1,
                   confidence = MIN(5.0, confidence + 0.2),
                   summary = CASE WHEN ? != '' THEN ? ELSE summary END,
                   keywords = CASE WHEN ? != '' THEN ? ELSE keywords END,
                   category = ?,
                   last_queried = CURRENT_TIMESTAMP''',
            (topic, r_clean[:500], keywords, category,
             r_clean[:500], r_clean[:500],
             keywords, keywords, category)
        )
        con.commit()
    except Exception as e:
        print(f"[Continuous Training Save Error] {e}")
    finally:
        con.close()

def get_recent_searches(limit=60):
    """Retrieve recent queries and learned answers."""
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute(
            '''SELECT id, query, response, category, datetime(created_at, 'localtime')
               FROM search_history ORDER BY id DESC LIMIT ?''', (limit,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[Memory Fetch Error] {e}")
        return []
    finally:
        con.close()

def clear_search_history():
    """Clear all stored search records and learned memory."""
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM search_history")
        cursor.execute("DELETE FROM learned_memory")
        con.commit()
        return True
    except Exception as e:
        print(f"[Memory Clear Error] {e}")
        return False
    finally:
        con.close()

def find_learned_context(query):
    """
    Semantic Neural Recall: looks up previously learned knowledge, verified facts,
    and prior search answers to inject directly into Megatron's reasoning core.
    """
    if not query or not query.strip():
        return None
    con = get_connection()
    cursor = con.cursor()
    try:
        kw = _extract_keywords(query)
        search_terms = kw.split() if kw else query.lower().split()

        # Step 1: Exact / subtopic match in learned memory
        for term in search_terms:
            if len(term) < 3:
                continue
            cursor.execute(
                '''SELECT topic, summary, confidence FROM learned_memory
                   WHERE (topic LIKE ? OR keywords LIKE ?) AND summary != ''
                   ORDER BY access_count DESC, confidence DESC LIMIT 2''',
                (f"%{term}%", f"%{term}%")
            )
            rows = cursor.fetchall()
            if rows:
                snippets = [f"Topic: {r[0]} -> {r[1]}" for r in rows if r[1]]
                if snippets:
                    return "; ".join(snippets)

        # Step 2: Recent search history fallback match
        for term in search_terms[:3]:
            cursor.execute(
                '''SELECT query, response FROM search_history
                   WHERE query LIKE ? AND response != '' AND response NOT LIKE '%failed%'
                   ORDER BY id DESC LIMIT 1''',
                (f"%{term}%",)
            )
            hist = cursor.fetchone()
            if hist and hist[1]:
                return f"Prior Q: {hist[0]} -> Ans: {hist[1][:250]}"

        return None
    except Exception as e:
        print(f"[Learned Context Lookup Error] {e}")
        return None
    finally:
        con.close()

def get_training_stats():
    """Returns training metrics on how much knowledge Megatron has acquired."""
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM search_history")
        searches_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM learned_memory")
        topics_count = cursor.fetchone()[0]
        cursor.execute("SELECT IFNULL(ROUND(AVG(confidence), 2), 1.0) FROM learned_memory")
        avg_conf = cursor.fetchone()[0]
        return {
            "searches": searches_count,
            "topics": topics_count,
            "confidence": avg_conf,
            "trained_nodes": topics_count + searches_count
        }
    except Exception:
        return {"searches": 0, "topics": 0, "confidence": 1.0, "trained_nodes": 0}
    finally:
        con.close()

# Multi-Provider API Integration & Quota Management Helpers
def get_api_config():
    """Returns active AI provider and all configured keys."""
    con = get_connection()
    cursor = con.cursor()
    cfg = {
        "active_provider": "gemini",
        "gemini_api_key": "",
        "openai_api_key": "",
        "groq_api_key": "",
        "openrouter_api_key": "",
        "custom_api_url": "http://localhost:11434/v1",
        "custom_api_key": "",
        "auto_failover": "1",
        "quota_exhausted_providers": ""
    }
    try:
        cursor.execute("SELECT key, value FROM settings WHERE key IN ("
                       "'active_ai_provider', 'gemini_api_key', 'openai_api_key', "
                       "'groq_api_key', 'openrouter_api_key', 'custom_api_url', "
                       "'custom_api_key', 'auto_failover', 'quota_exhausted_providers', 'llm_key')")
        for k, v in cursor.fetchall():
            if k == "active_ai_provider": cfg["active_provider"] = v or "gemini"
            elif k in ("gemini_api_key", "llm_key") and v: cfg["gemini_api_key"] = v
            elif k in cfg: cfg[k] = v or ""
        # If gemini key empty, check environment
        if not cfg["gemini_api_key"]:
            cfg["gemini_api_key"] = os.environ.get("GEMINI_API_KEY", "")
        if not cfg["openai_api_key"]:
            cfg["openai_api_key"] = os.environ.get("OPENAI_API_KEY", "")
        if not cfg["groq_api_key"]:
            cfg["groq_api_key"] = os.environ.get("GROQ_API_KEY", "")
        if not cfg["openrouter_api_key"]:
            cfg["openrouter_api_key"] = os.environ.get("OPENROUTER_API_KEY", "")
    except Exception as e:
        print(f"[API Config Fetch Error] {e}")
    finally:
        con.close()
    return cfg

def save_api_config(data):
    """Saves updated AI provider keys and active provider selection."""
    if not isinstance(data, dict):
        return False
    con = get_connection()
    cursor = con.cursor()
    try:
        keys_map = {
            "active_provider": "active_ai_provider",
            "gemini_api_key": "gemini_api_key",
            "openai_api_key": "openai_api_key",
            "groq_api_key": "groq_api_key",
            "openrouter_api_key": "openrouter_api_key",
            "custom_api_url": "custom_api_url",
            "custom_api_key": "custom_api_key",
            "auto_failover": "auto_failover"
        }
        for client_k, db_k in keys_map.items():
            if client_k in data:
                val = str(data[client_k]).strip()
                cursor.execute(
                    "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?",
                    (db_k, val, val)
                )
                if db_k == "gemini_api_key":
                    # Keep llm_key synchronized
                    cursor.execute(
                        "INSERT INTO settings (key, value) VALUES ('llm_key', ?) ON CONFLICT(key) DO UPDATE SET value = ?",
                        (val, val)
                    )
        con.commit()
        return True
    except Exception as e:
        print(f"[API Config Save Error] {e}")
        return False
    finally:
        con.close()

def mark_provider_quota_exhausted(provider, is_exhausted=True):
    """Tracks if an API provider's package/quota has ended."""
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT value FROM settings WHERE key = 'quota_exhausted_providers'")
        row = cursor.fetchone()
        current_set = set(row[0].split(",")) if row and row[0] else set()
        p = provider.lower().strip()
        if is_exhausted:
            current_set.add(p)
        else:
            current_set.discard(p)
        new_val = ",".join(current_set)
        cursor.execute(
            "INSERT INTO settings (key, value) VALUES ('quota_exhausted_providers', ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            (new_val, new_val)
        )
        con.commit()
    except Exception as e:
        print(f"[Quota Tracking Error] {e}")
    finally:
        con.close()

def delete_search_record(record_id):
    """Delete a specific search record by ID."""
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("DELETE FROM search_history WHERE id = ?", (record_id,))
        con.commit()
        return True
    except Exception as e:
        print(f"[Delete Search Error] {e}")
        return False
    finally:
        con.close()

def search_memory_by_keyword(keyword):
    """Search history records matching a keyword."""
    con = get_connection()
    cursor = con.cursor()
    try:
        kw = f"%{keyword.strip()}%"
        cursor.execute(
            '''SELECT id, query, response, category, datetime(created_at, 'localtime')
               FROM search_history WHERE query LIKE ? OR response LIKE ?
               ORDER BY id DESC LIMIT 50''',
            (kw, kw)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"[Search Memory Error] {e}")
        return []
    finally:
        con.close()

def get_memory_stats():
    """Get count of searches and learned topics."""
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM search_history")
        searches_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM learned_memory")
        topics_count = cursor.fetchone()[0]
        return {"searches": searches_count, "topics": topics_count}
    except Exception:
        return {"searches": 0, "topics": 0}
    finally:
        con.close()

# Admin Security & Passcode Helpers
def get_admin_passcode():
    """Retrieve the main admin passcode from settings."""
    con = get_connection()
    cursor = con.cursor()
    try:
        cursor.execute("SELECT value FROM settings WHERE key = 'admin_passcode'")
        row = cursor.fetchone()
        if row and row[0]:
            return str(row[0]).strip()
        return "admin123"
    except Exception:
        return "admin123"
    finally:
        con.close()

def verify_admin_passcode(passcode):
    """Verify if the provided passcode matches the main admin passcode."""
    if not passcode:
        return False
    expected = get_admin_passcode()
    return str(passcode).strip() == str(expected).strip()

def update_admin_passcode(new_passcode):
    """Update the main admin passcode in settings."""
    if not new_passcode or not str(new_passcode).strip():
        return False
    con = get_connection()
    cursor = con.cursor()
    try:
        val = str(new_passcode).strip()
        cursor.execute(
            "INSERT INTO settings (key, value) VALUES ('admin_passcode', ?) ON CONFLICT(key) DO UPDATE SET value = ?",
            (val, val)
        )
        con.commit()
        return True
    except Exception as e:
        print(f"[Admin Passcode Update Error] {e}")
        return False
    finally:
        con.close()

# Auto-initialize on module load
init_db()

con = get_connection()
cursor = con.cursor()

