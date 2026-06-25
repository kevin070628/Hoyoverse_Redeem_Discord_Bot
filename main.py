import discord
from discord.ext import commands
import asyncio
import os
import threading
from dotenv import load_dotenv
from cogs.keep_alive import keep_alive
from utils.data import init_db

# 1. 환경 변수 로드
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# 2. 인텐트 설정 (메시지 읽기 권한)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 3. 로드할 Cog 목록
REQUIRED_COGS = [
    "cogs.settings",
    "cogs.redeem",
    "cogs.youtube",
    "cogs.events"
]

@bot.event
async def on_ready():
    print(f"\n" + "="*50, flush=True)
    print(f"🤖 [알림 봇 로그인 완료] {bot.user.name}", flush=True)
    print("="*50, flush=True)
    
    # DB 초기화
    try:
        init_db()
        print("✅ 데이터베이스 초기화 완료", flush=True)
    except Exception as e:
        print(f"❌ DB 초기화 실패: {e}", flush=True)
    
    # Cog 로드 (실패 시 정확한 에러 확인 가능)
    for cog in REQUIRED_COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ {cog} 로드 완료", flush=True)
        except Exception as e:
            # 여기서 에러 내용을 출력하여 범인을 잡습니다.
            print(f"❌ {cog} 로드 실패: {e}", flush=True)
            
    # 슬래시 명령어 동기화
    try:
        bot.tree.clear_commands(guild=None) 
        await bot.tree.sync()
        print("🧹 유령 슬래시 명령어 청소 및 동기화 완료!", flush=True)
    except Exception as e:
        print(f"⚠️ 명령어 동기화 중 오류: {e}", flush=True)
        
    print(f"🚀 호요버스 3대장 알림 서비스 정상 가동 중!", flush=True)
    print("="*50 + "\n", flush=True)

def run_keep_alive():
    """Flask 웹 서버를 별도 스레드에서 실행"""
    keep_alive()

async def main():
    # 1. keep_alive를 백그라운드 스레드에서 시작
    server_thread = threading.Thread(target=run_keep_alive)
    server_thread.daemon = True
    server_thread.start()
    
    # 2. 토큰 확인
    if not TOKEN:
        print("❌ 에러: DISCORD_TOKEN이 환경 변수에 없습니다!", flush=True)
        return

    # 3. 봇 실행
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
