import discord
from discord.ext import commands
import asyncio
import sys
import io
from utils.config import DISCORD_TOKEN

# -------------------------------------------------------------
# [Render 24시간 유지를 위한 Flask 웹서버 설정]
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ Bot is alive and running!"

def run_web_server():
    # Render는 기본적으로 10000번 포트를 사용하거나 PORT 환경변수를 제공합니다.
    # 포트 충돌을 방지하기 위해 0.0.0.0:8080으로 설정합니다.
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True  # 메인 프로세스 종료 시 함께 종료되도록 설정
    t.start()
# -------------------------------------------------------------

# Windows 콘솔 인코딩 설정
# if sys.platform == 'win32':
#      sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
#      sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

COGS = [
    "cogs.fortune",
    "cogs.gacha",
    "cogs.settings",
    "cogs.redeem",
    "cogs.youtube",
    "cogs.community",
    "cogs.chatbot",
    "cogs.enka",
    "cogs.help",
    "cogs.gi_info",            # 원신 정보 (Honey Hunter World)
    "cogs.hsr_info",           # 스타레일 정보 (Prydwen.gg)
    "cogs.zzz_info",           # 젠존제 정보 (Prydwen.gg)
    "cogs.hoyo_info",          # 통합 검색 (!캐릭터/!무기/!성유물)
    "cogs.events",
]

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 로그인 완료!")
    print(f"📡 {len(bot.guilds)}개 서버에서 활동 중")
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)}개 슬래시 명령어 동기화 완료")
    except Exception as e:
        print(f"❌ 슬래시 명령어 동기화 실패: {e}")

async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"  ✅ {cog} 로드 완료")
        except Exception as e:
            print(f"  ❌ {cog} 로드 실패: {e}")

async def main():
    # 토큰 확인
    if not DISCORD_TOKEN:
        print("❌ 오류: DISCORD_TOKEN 환경 변수가 설정되지 않았습니다!")
        print("  PowerShell에서 다음 명령어를 실행하세요:")
        print('  $env:DISCORD_TOKEN="여기에_봇_토큰_입력"')
        return
    
    print("🔄 Cog 로딩 중...")
    await load_cogs()
    
    # 봇 시작 직전에 가짜 웹서버 구동
    print("🌐 웹 서버(Uptime 확인용) 시작 중...")
    keep_alive()
    
    print("🚀 봇 시작 중...")
    try:
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\n⏹️ 봇 종료 중...")
        await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 봇이 종료되었습니다.")
