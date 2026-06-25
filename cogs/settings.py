import discord
from discord import app_commands
from discord.ext import commands
from utils.config import NOTIFY_TYPES
from utils.data import load_guild_settings, save_guild_settings

class NotifyTypeSelect(discord.ui.Select):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        # ... (기존과 동일)
        options = []
        for key, info in NOTIFY_TYPES.items():
            if "_community" in key: continue
            options.append(discord.SelectOption(label=info["name"], value=key, emoji=info["emoji"]))
        super().__init__(placeholder="알림받을 항목 선택", min_values=1, max_values=len(options), options=options)
    
    async def callback(self, interaction: discord.Interaction):
        # 실시간 데이터 로드
        settings = load_guild_settings()
        guild_id = str(interaction.guild.id)
        
        if guild_id not in settings: settings[guild_id] = {}
        
        selected = list(self.values)
        # 커뮤니티 자동 추가 로직 유지
        yt_community_pairs = {"genshin_yt": "genshin_yt_community", "starrail_yt": "starrail_yt_community"} 
        
        for notify_type in selected:
            settings[guild_id][notify_type] = self.channel_id
            if notify_type in yt_community_pairs:
                settings[guild_id][yt_community_pairs[notify_type]] = self.channel_id
        
        save_guild_settings(settings)
        await interaction.response.send_message("✅ 설정 완료!", ephemeral=True)

# ... (NotifySelectView 등 나머지 클래스는 그대로 유지)

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # 💡 팁: 슬래시 명령어와 일반 명령어 이름을 구분하면 동기화 오류가 없습니다.
    @app_commands.command(name="알림설정", description="알림 설정 창을 엽니다")
    @app_commands.default_permissions(administrator=True)
    async def slash_notify_setup(self, interaction: discord.Interaction):
        view = NotifySelectView(interaction.channel.id)
        await interaction.response.send_message("알림을 선택하세요.", view=view, ephemeral=True)
    
    @commands.command(name="알림설정")
    @commands.has_permissions(administrator=True)
    async def notify_setup(self, ctx):
        view = NotifySelectView(ctx.channel.id)
        await ctx.send("알림을 선택하세요.", view=view)
        
    # (나머지 알림해제, 알림현황도 위와 같이 slash와 일반 명령어를 구분하여 유지)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Settings(bot))
