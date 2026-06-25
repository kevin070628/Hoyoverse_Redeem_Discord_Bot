import os
import json

SENT_CODES_FILE = "data/sent_codes.json"
SENT_VIDEOS_FILE = "data/sent_videos.json"
GUILD_SETTINGS_FILE = "data/guild_settings.json"

def init_db():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(SENT_CODES_FILE):
        with open(SENT_CODES_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
    if not os.path.exists(SENT_VIDEOS_FILE):
        with open(SENT_VIDEOS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(GUILD_SETTINGS_FILE):
        with open(GUILD_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def load_sent_codes():
    try:
        with open(SENT_CODES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {k: set(v) for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_sent_codes(codes_dict):
    try:
        data = {k: list(v) for k, v in codes_dict.items()}
        with open(SENT_CODES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[데이터] 리딤코드 저장 실패: {e}")

def load_guild_settings():
    try:
        with open(GUILD_SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_guild_settings(settings):
    try:
        with open(GUILD_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[데이터] 길드 설정 저장 실패: {e}")

def load_sent_videos():
    try:
        with open(SENT_VIDEOS_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_sent_videos(sent_videos):
    try:
        with open(SENT_VIDEOS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(sent_videos), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[데이터] 유튜브 영상 기록 저장 실패: {e}")

def get_channels_for_type(guild_settings, notify_type):
    channels = []
    for guild_id, settings in guild_settings.items():
        if notify_type in settings:
            channels.append(settings[notify_type])
    return channels
