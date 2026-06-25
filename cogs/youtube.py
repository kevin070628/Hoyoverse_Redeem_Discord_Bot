import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from datetime import datetime, timezone
from utils.config import YOUTUBE_CHANNELS, YOUTUBE_API_KEY
from utils.data import load_sent_videos, save_sent_videos, get_channels_for_type
from cogs.settings import get_guild_settings

# 전역 캐시 로드
sent_videos = load_sent_videos()
FIXED_MINUTES = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

async def get_latest_videos(channel_id, max_results=5):
    if not YOUTUBE_API_KEY or "방금_발급받은" in YOUTUBE_API_KEY:
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "order": "date",
        "maxResults": max_results,
        "type": "video"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=20) as resp:
                if resp.status != 200: return []
                data = await resp.json()
                return [{"video_id": item["id"]["videoId"], "title": item["snippet"]["title"]} 
                        for item in data.get("items", []) if "videoId" in item.get("id", {})]
    except Exception as e:
        print(f"[유튜브 API] 에러: {e}")
        return []

class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_youtube.start()
    
    def cog_unload(self):
        self.check_youtube.cancel()
    
    @commands.command(name="RSS테스트")
    @commands.has_permissions(administrator=True)
    async def rss_test(self, ctx, channel: str = "genshin"):
        channel_map = {"원신": "genshin_yt", "genshin": "genshin_yt", "스타레일": "starrail_yt", "starrail": "starrail_yt", "젠레스": "zzz_yt", "zzz": "zzz_yt"}
        yt_key = channel_map.get(channel.lower())
        if not yt_key:
            await ctx.send("❌ 가능한 채널: 원신, 스타레일, 젠레스")
            return
            
        yt_info = YOUTUBE_CHANNELS[yt_key]
        videos = await get_latest_videos(yt_info["channel_id"], max_results=1)
        if not videos:
            await ctx.send("❌ 영상을 가져올 수 없습니다.")
            return
        
        await ctx.send(f"🧪 **[{yt_info['name']}]** 최신 영상: {videos[0]['title']}\nhttps://www.youtube.com/watch?v={videos[0]['video_id']}")
    
    async def send_youtube_notification(self, video, yt_channel_key):
        global sent_videos
        video_id = video["video_id"]
        if video_id in sent_videos: return False
            
        yt_info = YOUTUBE_CHANNELS[yt_channel_key]
        guild_settings = get_guild_settings()
        discord_channels = get_channels_for_type(guild_settings, yt_channel_key)
        
        for channel_id in discord_channels:
            channel = self.bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(f"{yt_info['emoji']} **{yt_info['name']}** 새 영상 알림!\nhttps://www.youtube.com/watch?v={video_id}")
                except Exception as e:
                    print(f"알림 전송 실패: {e}")
                    
        sent_videos.add(video_id)
        save_sent_videos(sent_videos)
        return True
    
    @tasks.loop(minutes=1)
    async def check_youtube(self):
        # 현재 분 확인
        if datetime.now(timezone.utc).minute not in FIXED_MINUTES:
            return
            
        guild_settings = get_guild_settings()
        for yt_key, yt_info in YOUTUBE_CHANNELS.items():
            if not get_channels_for_type(guild_settings, yt_key): continue
                
            videos = await get_latest_videos(yt_info["channel_id"], max_results=5)
            for video in reversed(videos):
                await self.send_youtube_notification(video, yt_key)
            await asyncio.sleep(2) # 봇 부하 방지
            
    @check_youtube.before_loop
    async def before_check_youtube(self):
        global sent_videos
        await self.bot.wait_until_ready()
        print("[유튜브] 캐싱 시작...")
        for yt_key, yt_info in YOUTUBE_CHANNELS.items():
            videos = await get_latest_videos(yt_info["channel_id"], max_results=5)
            for video in videos:
                sent_videos.add(video["video_id"])
        save_sent_videos(sent_videos)
        print(f"[유튜브] 초기화 완료. {len(sent_videos)}개 캐시됨.")

async def setup(bot):
    await bot.add_cog(YouTube(bot))
