import discord
import holidays
import os
from discord.ext import commands
import datetime
import math

MONDAY_WEEKDAY = 0
TUESDAY_WEEKDAY = 1
WEDNESDAY_WEEKDAY = 2
THURSDAY_WEEKDAY = 3
FRIDAY_WEEKDAY = 4

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="./", intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
ATTEND_EMOJI_CODE = "<:attend:860867683088072734>"
NOT_ATTEND_EMOJI_CODE = "<:no_attend:860867683083354112>"
DINING_MESSAGE = """
[공지]  🍖 회식 참여 인원 조사
> {}월 {}일 목요일 오후 6시~ 
오늘 퇴근 전 까지 {}, {} 으로 참석여부 알려주세요.

(추가) 매월 2회 / 2,4주차 목요일에 진행하는 편안한(회식)자리입니다
각자 일정에 맞게 참석하시면 됩니다
"""


async def sendDiningSurveyMessage():
    now = datetime.datetime.now()
    if isNotSendDiningMessageDate(now):
        return
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    diningMessage = createDiningMessage(now)

    if channel:
        createMessage = await channel.send(diningMessage)
        await createMessage.add_reaction(ATTEND_EMOJI_CODE)
        await createMessage.add_reaction(NOT_ATTEND_EMOJI_CODE)
    else:
        print(f"Cannot find channel with ID {str(CHANNEL_ID)}")


def isNotSendDiningMessageDate(now):
    thursdayOfNextWeek = getThursdayOfNextWeek(now)
    numberOfWeekDayOfNextWeek = getNumberOfWeekOfMonth(thursdayOfNextWeek)
    koreaHolidays = holidays.KR(years=now.year)
    if (
        numberOfWeekDayOfNextWeek != 2 and numberOfWeekDayOfNextWeek != 4
    ) or thursdayOfNextWeek in koreaHolidays:
        return True

    sendDiningWeekDay = getSendDiningWeekDay(now)
    return sendDiningWeekDay != now.weekday()


def getThursdayOfNextWeek(now):
    THURSDAY_WEEKDAY_PERIOD = 10
    currentWeekday = now.weekday()
    daysUntilNextThursday = THURSDAY_WEEKDAY_PERIOD - currentWeekday
    return now + datetime.timedelta(days=daysUntilNextThursday)


def getNumberOfWeekOfMonth(now):
    FIRST_WEEK_PIVOT = 3
    firstDateTime = now.replace(day=1)
    firstDayWeekDay = firstDateTime.weekday()
    addition = 1 if firstDayWeekDay <= FIRST_WEEK_PIVOT else 0
    lastDateTimeOfFirstWeek = firstDateTime + datetime.timedelta(
        days=6 - firstDayWeekDay
    )
    return (math.ceil((now - lastDateTimeOfFirstWeek).days / 7)) + addition


def getSendDiningWeekDay(now):
    startOfWeekDateTime = now - datetime.timedelta(days=now.weekday())
    koreaHolidays = holidays.KR(years=now.year)

    weekDaysPriority = [
        THURSDAY_WEEKDAY,
        FRIDAY_WEEKDAY,
        WEDNESDAY_WEEKDAY,
        TUESDAY_WEEKDAY,
        MONDAY_WEEKDAY,
    ]

    for weekDay in weekDaysPriority:
        dateTime = startOfWeekDateTime + datetime.timedelta(days=weekDay)
        if dateTime.date() in koreaHolidays:
            continue
        return dateTime.weekday()


def createDiningMessage(now):
    thursDayOfNextWeek = getThursdayOfNextWeek(now)
    month = str(thursDayOfNextWeek.month)
    day = str(thursDayOfNextWeek.day)
    return DINING_MESSAGE.format(month, day, ATTEND_EMOJI_CODE, NOT_ATTEND_EMOJI_CODE)


@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game("회식 수요 조사")
    )
    await sendDiningSurveyMessage()
    await client.close()


client.run(TOKEN)
