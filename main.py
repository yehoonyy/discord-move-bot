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
async def 이동(ctx, from_channel_id: int, to_channel_id: int):
    # 멤버 이동 권한이 있는지 확인
    if not ctx.author.guild_permissions.move_members:
        await ctx.send("❌ 이 명령어를 사용할 권한(멤버 이동)이 없습니다.")
        return

    # 채널 객체 가져오기
    from_channel = bot.get_channel(from_channel_id)
    to_channel = bot.get_channel(to_channel_id)

    # 유효한 음성 채널인지 확인
    if not isinstance(from_channel, discord.VoiceChannel) or not isinstance(to_channel, discord.VoiceChannel):
        await ctx.send("⚠️ 올바른 음성 채널 ID를 입력해주세요.")
        return

    # 이동 작업 시작
    moved_count = 0
    members = from_channel.members

    if not members:
        await ctx.send(f"ℹ️ {from_channel.name} 채널에 접속 중인 유저가 없습니다.")
        return

    for member in members:
        try:
            await member.move_to(to_channel)
            moved_count += 1
        except Exception as e:
            print(f"이동 실패 ({member.display_name}): {e}")

    await ctx.send(f"✅ **성공:** {from_channel.name} ➡️ {to_channel.name} ({moved_count}명 이동 완료)")

# 4. Render 환경 변수(BOT_TOKEN)를 사용하여 봇 실행
token = os.getenv('BOT_TOKEN')
if token:
    bot.run(token)
else:
    print("❌ 에러: BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
