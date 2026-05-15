import discord
from discord.ext import commands
import os
import random
import asyncio

intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
bot = commands.Bot(command_prefix='!', intents=intents)

last_teams = {}

@bot.event
async def on_ready():
    print(f'--- {bot.user.name} 차원 이동 준비 완료! ---')

# 1. 팀 나누기
@bot.command()
async def 팀나(ctx, num: int = 2):
    global last_teams
    if not ctx.author.voice:
        await ctx.send("⚠️ 음성 채널에 접속해주세요!")
        return
    members = [m for m in ctx.author.voice.channel.members if not m.bot]
    if len(members) < num:
        await ctx.send("⚠️ 인원이 부족합니다.")
        return
    random.shuffle(members)
    teams = [[] for _ in range(num)]
    for i, member in enumerate(members):
        teams[i % num].append(member)
    last_teams = {i+1: team for i, team in enumerate(teams)}
    res = "🎲 **랜덤 팀 배정**\n"
    for i, team in last_teams.items():
        res += f"\n**{i}팀**: {', '.join([m.display_name for m in team])}"
    res += "\n\n💡 **!확정** 입력 시 자동 이동!"
    await ctx.send(res)

# 2. 팀 이동 확정
@bot.command()
async def 확정(ctx):
    global last_teams
    if not last_teams:
        await ctx.send("⚠️ 팀을 먼저 나눠주세요.")
        return
    await ctx.send("🚀 팀별로 이동합니다!")
    for t_num, members in last_teams.items():
        keyword = f"0{t_num}" if t_num < 10 else str(t_num)
        target_ch = next((ch for ch in ctx.guild.voice_channels if keyword in ch.name), None)
        if target_ch:
            for m in members:
                try:
                    if m.voice: await m.move_to(target_ch)
                except: pass
    last_teams = {}

# 3. 전원 이동 (나랑 같이 가자)
@bot.command()
async def 가자(ctx, target: str):
    if not ctx.author.voice: return
    to_ch = next((ch for ch in ctx.guild.voice_channels if target in ch.name), None)
    if to_ch:
        for m in ctx.author.voice.channel.members:
            try: await m.move_to(to_ch)
            except: pass
        await ctx.send(f"🚀 {to_ch.name}로 모두 이동!")

# 4. [신규] 모든 채널 인원 소집
@bot.command()
async def 소집(ctx):
    if not ctx.author.voice:
        await ctx.send("⚠️ 먼저 음성 채널에 들어가 있어야 합니다!")
        return
    my_ch = ctx.author.voice.channel
    await ctx.send(f"📢 모든 인원을 **{my_ch.name}** 채널로 소집합니다!")
    for vc in ctx.guild.voice_channels:
        for m in vc.members:
            if m != bot.user:
                try: await m.move_to(my_ch)
                except: pass
    await ctx.send("✅ 소집 완료!")

# 5. [신규] 채팅방 청소
@bot.command()
async def 청소(ctx, amount: int = 10):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("❌ 메시지 관리 권한이 없습니다.")
        return
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 {amount}개의 메시지를 삭제했습니다!")
    await asyncio.sleep(3) # 3초 뒤 안내 메시지 삭제
    await msg.delete()

# 6. 번호 골라 이동
@bot.command()
async def 골라(ctx, target: str):
    if not ctx.author.voice: return
    members = [m for m in ctx.author.voice.channel.members if not m.bot]
    m_list = "\n".join([f"{i+1}. {m.display_name}" for i, m in enumerate(members)])
    await ctx.send(f"**[{target}]** 채널로 보낼 번호를 입력하세요!\n\n{m_list}")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=20.0)
        to_ch = next((ch for ch in ctx.guild.voice_channels if target in ch.name), None)
        for n in msg.content.split():
            if n.isdigit() and 0 < int(n) <= len(members):
                try: await members[int(n)-1].move_to(to_ch)
                except: pass
        await ctx.send("✅ 이동 완료!")
    except: pass

# 7. 개별 이동
@bot.command()
async def 이동(ctx, *args):
    if not ctx.message.mentions: return
    to_ch = next((ch for ch in ctx.guild.voice_channels if args[-1] in ch.name), None)
    if to_ch:
        for m in ctx.message.mentions:
            try: await m.move_to(to_ch)
            except: pass

token = os.getenv('BOT_TOKEN')
bot.run(token)
