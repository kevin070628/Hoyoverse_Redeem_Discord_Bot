import os
from dotenv import load_dotenv

# 로컬 테스트를 위해 .env 파일을 로드합니다 (Render는 서버 설정에서 가져옵니다)
load_dotenv()

# os.getenv를 사용하여 환경 변수를 불러옵니다.
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("⚠️ YOUTUBE_API_KEY가 설정되지 않았습니다! .env 또는 Render 설정을 확인하세요.")

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
