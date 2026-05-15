import discord
from discord.ext import commands
import os
import random
import asyncio

intents = discord.Intents.default()
intents.members = True          
intents.message_content = True  
bot = commands.Bot(command_prefix='!', intents=intents)

# 마지막 팀 정보 저장용
last_teams = {}

@bot.event
async def on_ready():
    print(f'--- {bot.user.name} 연결 완료! ---')

# 1. 팀나누기 (팀나)
@bot.command()
async def 팀나(ctx, num: int = 2):
    global last_teams
    if not ctx.author.voice:
        await ctx.send("⚠️ 음성 채널에 먼저 접속해주세요!")
        return

    members = [m for m in ctx.author.voice.channel.members if not m.bot]
    if len(members) < num:
        await ctx.send(f"⚠️ 인원이 부족합니다.")
        return

    random.shuffle(members)
    teams = [[] for _ in range(num)]
    for i, member in enumerate(members):
        teams[i % num].append(member)

    last_teams = {i+1: team for i, team in enumerate(teams)}

    res = "🎲 **팀 배정 결과**\n"
    for i, team in last_teams.items():
        names = [m.display_name for m in team]
        res += f"\n**{i}팀**: {', '.join(names)}"
    res += "\n\n💡 **!확정** 입력 시 자동 이동!"
    await ctx.send(res)

# 2. 팀 이동 확정 (확정)
@bot.command()
async def 확정(ctx):
    global last_teams
    if not last_teams:
        await ctx.send("⚠️ 먼저 `!팀나`를 해주세요.")
        return
    
    await ctx.send("🚀 이동 중...")
    for t_num, members in last_teams.items():
        keyword = f"0{t_num}" if t_num < 10 else str(t_num)
        target_ch = next((ch for ch in ctx.guild.voice_channels if keyword in ch.name), None)
        if target_ch:
            for m in members:
                try:
                    if m.voice: await m.move_to(target_ch)
                except: pass
    last_teams = {}
    await ctx.send("✅ 이동 완료!")

# 3. 전원 이동 (가자)
@bot.command()
async def 가자(ctx, target: str):
    if not ctx.author.voice:
        await ctx.send("⚠️ 음성 채널 접속 필수!")
        return
    to_ch = next((ch for ch in ctx.guild.voice_channels if target in ch.name), None)
    if not to_ch:
        await ctx.send("❓ 채널을 못 찾았습니다.")
        return
    for m in ctx.author.voice.channel.members:
        try: await m.move_to(to_ch)
        except: pass
    await ctx.send(f"🚀 {to_ch.name}로 전원 이동!")

# 4. 번호 골라 이동 (골라)
@bot.command()
async def 골라(ctx, target: str):
    if not ctx.author.voice: return
    members = [m for m in ctx.author.voice.channel.members if not m.bot]
    m_list = "\n".join([f"{i+1}. {m.display_name}" for i, m in enumerate(members)])
    await ctx.send(f"**[{target}]** 채널로 보낼 번호를 입력하세요 (예: 1 2)\n\n{m_list}")

    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg = await bot.wait_for('message', check=check, timeout=20.0)
        to_ch = next((ch for ch in ctx.guild.voice_channels if target in ch.name), None)
        for n in msg.content.split():
            if n.isdigit() and 0 < int(n) <= len(members):
                try: await members[int(n)-1].move_to(to_ch)
                except: pass
        await ctx.send("✅ 선택 인원 이동 완료!")
    except: pass

# 5. 기존 개별 이동 (이동)
@bot.command()
async def 이동(ctx, *args):
    if not ctx.message.mentions: return
    target_ch = args[-1]
    to_ch = next((ch for ch in ctx.guild.voice_channels if target_ch in ch.name), None)
    if to_ch:
        for m in ctx.message.mentions:
            try: await m.move_to(to_ch)
            except: pass
        await ctx.send(f"✅ {to_ch.name} 이동 완료!")

token = os.getenv('BOT_TOKEN')
bot.run(token)
