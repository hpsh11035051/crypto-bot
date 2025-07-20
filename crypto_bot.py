import discord
from discord.ext import tasks, commands
import requests
import datetime
import os

# ✅ TOKEN：雲端用環境變數，電腦本地用這裡的 Token
TOKEN = os.getenv("DISCORD_TOKEN", "在本地測試用的假TOKEN")  # ← 把這裡換成你自己的 Token

CHANNEL_ID = 1385225671185272922  # ← 換成你的頻道ID

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

previous_prices = {"BTC": None, "ETH": None}

def get_crypto_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin,ethereum", "vs_currencies": "usd"}
    r = requests.get(url, params=params).json()
    return {
        "BTC": r["bitcoin"]["usd"],
        "ETH": r["ethereum"]["usd"]
    }

def calc_percentage_change(old, new):
    if old is None:
        return 0
    return ((new - old) / old) * 100

@bot.event
async def on_ready():
    print(f"✅ 已登入為 {bot.user}")
    daily_price_update.start()

@bot.command()
async def test(ctx):
    await ctx.send("機器人正常運作！")

@tasks.loop(minutes=1)
async def daily_price_update():
    now = datetime.datetime.now()
    if now.hour == 12 and now.minute == 0:  # 每天12:00執行
        channel = bot.get_channel(CHANNEL_ID)
        prices = get_crypto_price()
        await channel.send(
            f"📢 **每日加密貨幣價格更新**\n"
            f"BTC: ${prices['BTC']}\n"
            f"ETH: ${prices['ETH']}"
        )
        check_price_fluctuation(prices, channel)

def check_price_fluctuation(current_prices, channel):
    for coin in current_prices:
        old_price = previous_prices[coin]
        change = calc_percentage_change(old_price, current_prices[coin])
        if abs(change) >= 1.5 and old_price is not None:
            msg = (
                f"🚨 **{coin} 價格波動警告**\n"
                f"漲跌幅: {change:.2f}%\n"
                f"最新價格: ${current_prices[coin]}"
            )
            bot.loop.create_task(channel.send(msg))
        previous_prices[coin] = current_prices[coin]

bot.run(TOKEN)
