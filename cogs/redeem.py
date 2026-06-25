import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from datetime import datetime
from utils.data import load_sent_codes, save_sent_codes, get_channels_for_type
from cogs.settings import get_guild_settings

sent_codes = load_sent_codes()

GAME_SETTINGS = {
    "genshin": {"name": "원신", "emoji": "🌋", "hoyo_key": "genshin", "api_act_id": "e202102251931481"},
    "starrail": {"name": "붕괴: 스타레일", "emoji": "🚂", "hoyo_key": "starrail", "api_act_id": "e202304171044231"},
    "zzz": {"name": "젠레스 존 제로", "emoji": "📼", "hoyo_key": "zzz", "api_act_id": "e202407041710121"}
}

async def fetch_hoyolab_redeem_codes(api_act_id):
    """호요랩 공식 패키지/리딤 API를 통해 코드를 긁어옵니다."""
    url = f"https://sg-hk4e-api.hoyoverse.com/common/apicdkey/api/webShareCode?act_id={api_act_id}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                
                codes = []
                for entry in data.get("data", {}).get("code_list", []):
                    code = entry.get("code")
                    if code:
                        codes.append({
                            "code": code,
                            "reward": entry.get("title", "게임 내 보상"),
                            "time": entry.get("creat_time", "")
                        })
                return codes
    except Exception as e:
        print(f"[리딤] API 에러 ({api_act_id}): {e}")
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
        # 💡 한글 입력(원신, 스타레일, 젠레스)도 영어 키값으로 바꿔주는 맵핑
        channel_map = {
            "원신": "genshin", "genshin": "genshin",
            "스타레일": "starrail", "starrail": "starrail", "붕괴스타레일": "starrail",
            "젠레스": "zzz", "zzz": "zzz", "젠레스존제로": "zzz"
        }
        
        game_key = channel_map.get(game.lower())
        if not game_key:
            await ctx.send("❌ 가능한 게임: 원신(genshin), 스타레일(starrail), 젠레스(zzz)")
            return
            
        g_info = GAME_SETTINGS[game_key]
        async with ctx.typing():
            codes = await fetch_hoyolab_redeem_codes(g_info["api_act_id"])
            
        if not codes:
            await ctx.send(f"❌ {g_info['name']}의 최신 리딤코드를 가져오지 못했습니다. (API 응답 없음)")
            return
            
        # 캐싱 여부와 상관없이 현재 API에 존재하는 최신 코드를 무조건 보여줍니다.
        code_info = codes[0]
        await ctx.send(f"🧪 **[리딤 테스트] {g_info['emoji']} {g_info['name']}**\n코드: `{code_info['code']}`\n보상: {code_info['reward']}\n\n*※ 현재 정상적으로 호요랩에서 데이터를 당겨오고 있습니다!*")

    async def send_redeem_notification(self, game_key, code_data):
        global sent_codes
        code = code_data["code"]
        if code in sent_codes:
            return
            
        g_info = GAME_SETTINGS[game_key]
        guild_settings = get_guild_settings()
        discord_channels = get_channels_for_type(guild_settings, game_key)
        
        if not discord_channels:
            return
            
        embed = discord.Embed(
            title=f"{g_info['emoji']} {g_info['name']} 새로운 리딤코드 발급!",
            description=f"**코드:** `{code}`\n**보상:** {code_data['reward']}",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="호요버스 알림 서비스")
        
        for channel_id in discord_channels:
            channel = self.bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"리딤 전송 실패: {e}")
                    
        sent_codes.add(code)
        save_sent_codes(sent_codes)

    @tasks.loop(minutes=5)
    async def check_redeem_codes(self):
        for game_key, g_info in GAME_SETTINGS.items():
            codes = await fetch_hoyolab_redeem_codes(g_info["api_act_id"])
            for code_data in reversed(codes):
                await self.send_redeem_notification(game_key, code_data)
            await asyncio.sleep(2)

    @check_redeem_codes.before_loop
    async def before_check_redeem_codes(self):
        await self.bot.wait_until_ready()
        print("[리딤코드] 시스템 준비 완료.")

async def setup(bot):
    await bot.add_cog(Redeem(bot))
