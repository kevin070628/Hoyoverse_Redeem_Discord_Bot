import discord
from discord import app_commands
from discord.ext import commands
from utils.config import NOTIFY_TYPES
from utils.data import load_guild_settings, save_guild_settings

class NotifyTypeSelect(discord.ui.Select):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        options = []
        for key, info in NOTIFY_TYPES.items():
            if "_community" in key: continue
            options.append(discord.SelectOption(label=info["name"], value=key, emoji=info["emoji"]))
        super().__init__(placeholder="알림받을 항목을 선택하세요 (여러 개 가능)", min_values=1, max_values=len(options), options=options)
    
    async def callback(self, interaction: discord.Interaction):
        guild_settings = load_guild_settings()
        guild_id = str(interaction.guild.id)
        if guild_id not in guild_settings: guild_settings[guild_id] = {}
        
        selected = list(self.values)
        yt_community_pairs = {"genshin_yt": "genshin_yt_community", "starrail_yt": "starrail_yt_community", "zzz_yt": "zzz_yt_community"}
        
        for notify_type in selected:
            guild_settings[guild_id][notify_type] = self.channel_id
            if notify_type in yt_community_pairs:
                guild_settings[guild_id][yt_community_pairs[notify_type]] = self.channel_id
        
        save_guild_settings(guild_settings)
        await interaction.response.send_message("✅ 알림 설정이 저장되었습니다!", ephemeral=True)

class NotifySelectView(discord.ui.View):
    def __init__(self, channel_id):
        super().__init__(timeout=60)
        self.add_item(NotifyTypeSelect(channel_id))

class RemoveNotifySelect(discord.ui.Select):
    def __init__(self, guild_id, current_settings):
        self.guild_id = guild_id
        options = []
        for key in current_settings:
            if key in NOTIFY_TYPES:
                info = NOTIFY_TYPES[key]
                options.append(discord.SelectOption(label=info["name"], value=key, emoji=info["emoji"]))
        if not options: options.append(discord.SelectOption(label="설정된 알림 없음", value="none"))
        super().__init__(placeholder="해제할 알림을 선택하세요", min_values=1, max_values=len(options), options=options)
    
    async def callback(self, interaction: discord.Interaction):
        guild_settings = load_guild_settings()
        if "none" in self.values:
            await interaction.response.send_message("❌ 설정된 알림이 없습니다.", ephemeral=True)
            return
        for notify_type in self.values:
            if notify_type in guild_settings.get(self.guild_id, {}):
                del guild_settings[self.guild_id][notify_type]
        save_guild_settings(guild_settings)
        await interaction.response.send_message("🗑️ 알림이 해제되었습니다.", ephemeral=True)

class RemoveNotifyView(discord.ui.View):
    def __init__(self, guild_id, current_settings):
        super().__init__(timeout=60)
        self.add_item(RemoveNotifySelect(guild_id, current_settings))

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="알림설정", description="관리자: 이 채널에 알림을 설정합니다.")
    @app_commands.default_permissions(administrator=True)
    async def slash_notify_setup(self, interaction: discord.Interaction):
        view = NotifySelectView(interaction.channel.id)
        await interaction.response.send_message("받고 싶은 알림을 선택하세요.", view=view, ephemeral=True)
    
    @commands.command(name="알림설정")
    @commands.has_permissions(administrator=True)
    async def notify_setup(self, ctx):
        view = NotifySelectView(ctx.channel.id)
        await ctx.send("받고 싶은 알림을 선택하세요.", view=view)
        
    @app_commands.command(name="알림해제", description="관리자: 알림 설정을 해제합니다.")
    @app_commands.default_permissions(administrator=True)
    async def slash_notify_remove(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        current = load_guild_settings().get(guild_id, {})
        if not current:
            await interaction.response.send_message("❌ 설정된 알림이 없습니다.", ephemeral=True)
            return
        view = RemoveNotifyView(guild_id, current)
        await interaction.response.send_message("해제할 알림을 선택하세요.", view=view, ephemeral=True)

    @commands.command(name="알림해제")
    @commands.has_permissions(administrator=True)
    async def notify_remove(self, ctx):
        guild_id = str(ctx.guild.id)
        current = load_guild_settings().get(guild_id, {})
        view = RemoveNotifyView(guild_id, current)
        await ctx.send("해제할 알림을 선택하세요.", view=view)

    @app_commands.command(name="알림현황", description="현재 알림 설정 상태를 확인합니다.")
    async def slash_notify_status(self, interaction: discord.Interaction):
        await self._show_status(interaction)

    @commands.command(name="알림현황")
    async def notify_status(self, ctx):
        await self._show_status(ctx)

    async def _show_status(self, ctx_or_int):
        guild_id = str(ctx_or_int.guild.id)
        settings = load_guild_settings().get(guild_id, {})
        if not settings:
            msg = "📭 설정된 알림이 없습니다."
        else:
            msg = "📬 현재 설정된 알림 목록:\n" + "\n".join([f"- {NOTIFY_TYPES.get(k, {'name':k})['name']}: <#{v}>" for k,v in settings.items() if k in NOTIFY_TYPES])
        
        if isinstance(ctx_or_int, discord.Interaction):
            await ctx_or_int.response.send_message(msg, ephemeral=True)
        else:
            await ctx_or_int.send(msg)

async def setup(bot):
    await bot.add_cog(Settings(bot))
