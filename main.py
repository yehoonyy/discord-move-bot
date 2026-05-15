import discord
from discord.ext import commands
import os

# 1. 봇의 권한 및 접두사 설정
intents = discord.Intents.default()
intents.members = True          # 서버 멤버 목록 확인 권한
intents.message_content = True  # 메시지 내용 읽기 권한
bot = commands.Bot(command_prefix='!', intents=intents)

# 2. 봇 연결 확인 이벤트
@bot.event
async def on_ready():
    # Render 로그 시스템에서 확인할 수 있도록 출력
    print(f'--- 시스템 알림: {bot.user.name} 연결 완료! ---')

# 3. 인원 이동 명령어
@bot.command()
async def 이동(ctx, *args):
    # 1. 권한 확인
    if not ctx.author.guild_permissions.move_members:
        await ctx.send("❌ 권한이 없습니다.")
        return

    # 2. 인자 분석 (마지막 단어는 채널명, 나머지는 유저 언급)
    if len(args) < 2:
        await ctx.send("⚠️ 사용법: `!이동 @유저1 @유저2 채널이름` 형식으로 입력해주세요.")
        return

    destination_name = args[-1]  # 마지막 단어를 채널 이름으로 인식
    target_members = ctx.message.mentions # 메시지에서 언급(@)된 유저 목록 가져오기

    # 3. 도착 채널 찾기
   # 수정 전: to_channel = discord.utils.get(ctx.guild.voice_channels, name=destination_name)
    
    # 수정 후: 이름에 입력한 글자가 포함되어 있으면 채널을 선택함
    to_channel = next((channel for channel in ctx.guild.voice_channels if destination_name in channel.name), None)
    if not to_channel:
        await ctx.send(f"❓ '{destination_name}' 음성 채널을 찾을 수 없습니다.")
        return

    # 4. 이동 실행
    if not target_members:
        await ctx.send("⚠️ 이동시킬 유저를 @로 언급해주세요.")
        return

    moved_count = 0
    for member in target_members:
        if member.voice: # 음성 채널에 접속 중인 경우에만 이동 가능
            await member.move_to(to_channel)
            moved_count += 1
        else:
            await ctx.send(f"⚠️ {member.display_name}님이 음성 채널에 없습니다.")

    await ctx.send(f"✅ 언급된 {moved_count}명을 **{to_channel.name}** 채널로 이동시켰습니다!")

# 4. Render 환경 변수(BOT_TOKEN)를 사용하여 봇 실행
token = os.getenv('BOT_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ 에러: BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
