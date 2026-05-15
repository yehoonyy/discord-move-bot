import discord
from discord.ext import commands

# 봇의 접두사 설정 (예: !이동)
intents = discord.Intents.default()
intents.members = True  
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
@bot.event
async def on_ready():
    print(f'{bot.user.name} 연결 완료!')

@bot.command()
async def 이동(ctx, from_channel_id: int, to_channel_id: int):
    # 관리자 권한 확인
    if not ctx.author.guild_permissions.move_members:
        await ctx.send("권한이 없습니다.")
        return

    from_channel = bot.get_channel(from_channel_id)
    to_channel = bot.get_channel(to_channel_id)

    if not isinstance(from_channel, discord.VoiceChannel) or not isinstance(to_channel, discord.VoiceChannel):
        await ctx.send("올바른 음성 채널 ID를 입력해주세요.")
        return

    moved_count = 0
    for member in from_channel.members:
        await member.move_to(to_channel)
        moved_count += 1

    await ctx.send(f"성공: {from_channel.name}에서 {to_channel.name}(으)로 {moved_count}명 이동 완료!")

import os
bot.run(os.getenv('BOT_TOKEN'))