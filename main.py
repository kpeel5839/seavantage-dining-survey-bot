import discord
import holidays
import os
from discord.ext import commands
import datetime
import math

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="./", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
DINING_MESSAGE = """
[공지]  🍖 회식 참여 인원 조사
    > {}월 {}일 목요일 오후 6시~ 
오늘 퇴근 전 까지 1️⃣(참)  2️⃣(불참) 으로 참석여부 알려주세요.

(추가) 매월 2회 / 2,4주차 목요일에 진행하는 편안한(회식)자리입니다
각자 일정에 맞게 참석하시면 됩니다
"""


async def sendDiningSurveyMessage():
    # now = datetime.now()
    now = datetime.datetime(2025, 3, 6, 0, 0, 0)
    if isNotSendDiningMessageDate(now):
        return
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    diningMessage = createDiningMessage(now)

    if channel:
        createMessage = await channel.send(diningMessage)
        await createMessage.add_reaction("1️⃣")
        await createMessage.add_reaction("2️⃣")
    else:
        print(f"Cannot find channel with ID {str(CHANNEL_ID)}")


def isNotSendDiningMessageDate(now):
    thursdayOfNextWeek = getThursdayOfNextWeek(now)
    numberOfNextWeek = getNumberOfWeekOfMonth(thursdayOfNextWeek)
    koreaHolidays = holidays.KR(years=now.year)
    if (
        numberOfNextWeek != 2 and numberOfNextWeek != 4
    ) or thursdayOfNextWeek in koreaHolidays:
        return True

    sendDiningWeekDay = getSendDiningWeekDay(now)
    return sendDiningWeekDay != now.weekday()


def getThursdayOfNextWeek(now):
    currentWeekday = now.weekday()
    daysUntilNextThursday = 10 - currentWeekday
    return now + datetime.timedelta(days=daysUntilNextThursday)


def getNumberOfWeekOfMonth(now):
    firstDateTime = now.replace(day=1)
    firstDayWeekDay = firstDateTime.weekday()
    addition = 1 if firstDayWeekDay <= 3 else 0
    lastDateTimeOfFirstWeek = firstDateTime + datetime.timedelta(
        days=6 - firstDayWeekDay
    )
    return (math.ceil((now - lastDateTimeOfFirstWeek).days / 7)) + addition


def getSendDiningWeekDay(now):
    startOfWeekDateTime = now - datetime.timedelta(days=now.weekday())
    koreaHolidays = holidays.KR(years=now.year)

    weekDaysPriority = [3, 4, 2, 1, 0]
    for weekDay in weekDaysPriority:
        dateTime = startOfWeekDateTime + datetime.timedelta(days=weekDay)
        if dateTime.date() in koreaHolidays:
            continue
        return dateTime.weekday()


def createDiningMessage(now):
    thursDayOfNextWeek = getThursdayOfNextWeek(now)
    month = str(thursDayOfNextWeek.month)
    day = str(thursDayOfNextWeek.day)
    return DINING_MESSAGE.format(month, day)


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game("회식 수요 조사 봇 가동 중")
    )
    await sendDiningSurveyMessage()
    await client.close()


client.run(TOKEN)
