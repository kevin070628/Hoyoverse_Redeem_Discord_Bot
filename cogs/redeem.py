import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from datetime import datetime, timezone
from utils.data import load_sent_codes, save_sent_codes, get_channels_for_type, load_guild_settings

sent_codes = load_sent_codes()

# 주의: 아래 API ID가 유효한지 확인이 필요합니다. 404가 뜬다면 ID가 만료된 것입니다.
GAME_SETTINGS = {
    "genshin": {"name": "원신", "emoji": "🌋", "hoyo_key": "genshin", "api_act_id": "e202102251931481"},
    "starrail": {"name": "붕괴: 스타레일", "emoji": "🚂", "hoyo_key": "starrail", "api_act_id": "e202304171044231"},
    "zzz": {"name": "젠레스 존 제로", "emoji": "📼", "hoyo_key": "zzz", "api_act_id": "e202407041710121"}
}

async def fetch_hoyolab_redeem_codes(api_act_id):
    # API 요청 시 필수적인 헤더 강화 (403/404 방지 목적)
    url = f"https://sg-hk4e-api.hoyoverse.com/common/apicdkey/api/webShareCode?act_id={api_act_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://act.hoyoverse.com/",
        "Origin": "https://act.hoyoverse.com/",
        "Accept": "application/json, text/plain, */*"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as resp:
                print(f"[디버그] {api_act_id} API 응답 상태코드: {resp.status}", flush=True)
                
                if resp.status != 200:
                    # 404가 뜬다면 URL 또는 ID 문제임
                    print(f"[디버그] {api_act_id} API 접속 불가 (상태코드: {resp.status})", flush=True)
                    return []
                
                data = await resp.json()
                
                # 데이터가 비어있는지 확인
                if "data" not in data or "code_list" not in data["data"]:
                    print(f"[디버그] 응답은 성공했으나 데이터 구조가 다름: {data}", flush=True)
                    return []
                
                codes = []
                for entry in data["data"]["code_list"]:
                    if entry.get("code"):
                        codes.append({
                            "code": entry["code"],
                            "reward": entry.get("title", "보상 정보 없음"),
                            "time": entry.get("creat_time", "")
                        })
                return codes
    except Exception as e:
        print(f"[디버그] 네트워크/API 연결 에러: {e}", flush=True)
        return []

class Redeem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_redeem_codes.start()
        
    def cog_unload(self):
        self.check_redeem_codes.cancel()

    @commands.command(name="코드테스트")
    @commands.has_permissions(administrator=True)
    async def code_test(self, ctx, game: str = "genshin"):
        game_map = {"원신": "genshin", "스타레일": "starrail", "젠레스": "zzz"}
        game_key = game_map.get(game, game.lower())
        
        if game_key not in GAME_SETTINGS:
            await ctx.send("❌ 지원하지 않는 게임입니다.")
            return
            
        g_info = GAME_SETTINGS[game_key]
        async with ctx.typing():
            codes = await fetch_hoyolab_redeem_codes(g_info["api_act_id"])
            
        if not codes:
            await ctx.send(f"❌ {g_info['name']} 코드를 가져올 수 없습니다. (API 주소가 만료되었을 수 있습니다.)")
            return
            
        await ctx.send(f"🧪 **[{g_info['name']} 테스트]**\n코드: `{codes[0]['code']}`\n보상: {codes[0]['reward']}")

    @tasks.loop(minutes=30) # 너무 자주 호출하면 IP 차단(403)당할 수 있으므로 30분으로 늘림
    async def check_redeem_codes(self):
        for game_key, g_info in GAME_SETTINGS.items():
            codes = await fetch_hoyolab_redeem_codes(g_info["api_act_id"])
            for code_data in reversed(codes):
                await self.send_redeem_notification(game_key, code_data)
            await asyncio.sleep(5) # 간격 추가

    async def send_redeem_notification(self, game_key, code_data):
        # ... (기존 send_redeem_notification 내용 유지) ...
        pass
