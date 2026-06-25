import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from cogs.keep_alive import keep_alive
from utils.data import init_db

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# intents 설정에 message_content가 True인 것 확인 (필수!)
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
        # 기존 명령어 전체 제거 후 현재 코드에 있는 명령어들로 다시 싱크
        bot.tree.clear_commands(guild=None) 
        await bot.tree.sync()
        print("🧹 유령 슬래시 명령어 청소 및 명령어 동기화 완료!")
    except Exception as e:
        print(f"⚠️ 명령어 동기화 중 오류: {e}")
        
    print(f"🚀 호요버스 3대장 알림 서비스 정상 가동 중!")
    print(f"========================================\n")

async def main():
    # keep_alive를 비동기적으로 실행
    keep_alive() 
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # 봇 종료 시 정리 작업
        pass
