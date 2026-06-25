import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from cogs.keep_alive import keep_alive
from utils.data import init_db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 호요버스 3대장 알림 필수 기능만 로드
REQUIRED_COGS = [
    "cogs.settings",  # ⚙️ 채널 설정 명령어
    "cogs.redeem",    # 🎁 리딤코드 알림
    "cogs.youtube",   # 📺 유튜브 알림
    "cogs.events"     # 🌐 커뮤니티(호요랩 공지/이벤트) 알림
]

@bot.event
async def on_ready():
    print(f"========================================")
    print(f"🤖 [알림 봇 로그인 완료] {bot.user.name}")
    print(f"========================================")
    init_db()
    
    # 🧹 과거에 등록되었던 쓸모없는 슬래시 명령어들을 디스코드 서버에서 청소합니다.
    try:
        bot.tree.clear(guild=None)
        await bot.tree.sync()
        print("🧹 디스코드 서버의 과거 슬래시 명령어 목록 초기화 완료!")
    except Exception as e:
        print(f"⚠️ 명령어 초기화 중 오류 (무시 가능): {e}")
    
    for cog in REQUIRED_COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ {cog} 로드 완료")
        except Exception as e:
            print(f"❌ {cog} 로드 실패: {e}")
            
    print(f"========================================")
    print(f"🚀 호요버스 3대장 알림 서비스 시작!")
    print(f"========================================")

async def main():
    keep_alive()  # Render 24시간 유지 웹서버
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
