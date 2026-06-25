import discord
from discord.ext import commands
import asyncio
import os
import threading
from dotenv import load_dotenv
from cogs.keep_alive import keep_alive
from utils.data import init_db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# intents 설정
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

REQUIRED_COGS = [
    "cogs.settings",
    "cogs.redeem",
    "cogs.youtube",
    "cogs.events"
]

@bot.event
async def on_ready():
    print(f"\n========================================")
    print(f"🤖 [알림 봇 로그인 완료] {bot.user.name}")
    print(f"========================================")
    
    # 1. 데이터베이스 초기화
    init_db()
    
    # 2. Cog 로드
    for cog in REQUIRED_COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ {cog} 로드 완료")
        except Exception as e:
            print(f"❌ {cog} 로드 실패: {e}")
            
    # 3. 슬래시 명령어 청소 및 동기화
    try:
        bot.tree.clear_commands(guild=None) 
        await bot.tree.sync()
        print("🧹 유령 슬래시 명령어 청소 및 명령어 동기화 완료!")
    except Exception as e:
        print(f"⚠️ 명령어 동기화 중 오류: {e}")
        
    print(f"🚀 호요버스 3대장 알림 서비스 정상 가동 중!")
    print(f"========================================\n")

def run_keep_alive():
    """Flask 웹 서버를 별도 스레드에서 실행"""
    keep_alive()

async def main():
    # 1. keep_alive를 백그라운드 스레드에서 시작 (봇 실행을 차단하지 않음)
    server_thread = threading.Thread(target=run_keep_alive)
    server_thread.daemon = True  # 메인 프로그램 종료 시 서버도 함께 종료되도록 설정
    server_thread.start()
    
    # 2. 봇 실행
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
