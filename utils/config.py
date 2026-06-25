import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = "AIzaSyDZp9u4RRrZaaeP3MmfPvMHNXLYFSuwPc4"

# 봇이 알림을 처리할 게임 타입 정의 (이게 없어서 에러가 발생한 것입니다!)
NOTIFY_TYPES = ["genshin_yt", "starrail_yt", "zzz_yt"]

YOUTUBE_CHANNELS = {
    "genshin_yt": {
        "channel_id": "UCi_-K67v255K7URW8S8Y4A",
        "name": "원신 공식 유튜브",
        "emoji": "🌋"
    },
    "starrail_yt": {
        "channel_id": "UC9jH99g_XW_bLsmfSstbIsg",
        "name": "붕괴: 스타레일 공식 유튜브",
        "emoji": "🚂"
    },
    "zzz_yt": {
        "channel_id": "UC6wTAsW49VccH3FvLgA_tSg",
        "name": "젠레스 존 제로 공식 유튜브",
        "emoji": "📼"
    }
}
