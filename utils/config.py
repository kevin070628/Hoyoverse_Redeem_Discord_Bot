import os
from dotenv import load_dotenv

load_dotenv()

# 💡 [필독] 이전에 구글 콘솔에서 발급받은 API 키를 아래 변수에 직접 넣어주세요!
YOUTUBE_API_KEY = "방금_발급받은_AIzaSy_시작하는_API_키"

# 3대장 게임 데이터 고정
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
