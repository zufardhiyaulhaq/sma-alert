import yfinance
import os
import sys
import yaml
import telegram
from datetime import date
from jinja2 import Environment, FileSystemLoader

STOCK_LISTS_FILEPATH = os.getenv('STOCK_LISTS_FILEPATH')
STOCK_PRICE_PERCENTAGE_FROM_SMA = float(os.getenv('STOCK_PRICE_PERCENTAGE_FROM_SMA'))

TELEGRAM_CHATID = os.getenv('TELEGRAM_CHATID')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

ENV = Environment(loader=FileSystemLoader('.'))
TEMPLATE_PATH = './templates/template_message.j2'
baseline = ENV.get_template(TEMPLATE_PATH)

baseline_data = {}
baseline_data["stocks"] = []
baseline_data["percentage"] = STOCK_PRICE_PERCENTAGE_FROM_SMA
baseline_data["date"] = date.today().strftime("%B %d, %Y")

with open(STOCK_LISTS_FILEPATH, 'r') as stream:
    try:
        config=yaml.safe_load(stream)
    except yaml.YAMLError as exception:
        sys.exit(exception)

for issuer in config["issuers"]:
    data = yfinance.download(
        tickers = issuer["code"] + "." + issuer["country"],
        period = "1y",
        interval = "1d",
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None
    )

    data = data['Close'].to_frame()
    data['SMA50'] = data['Close'].rolling(50).mean()
    data['SMA100'] = data['Close'].rolling(100).mean()
    data['SMA200'] = data['Close'].rolling(200).mean()

    close = data.iloc[-1]["Close"]
    sma50 = data.iloc[-1]["SMA50"]
    sma100 = data.iloc[-1]["SMA100"]
    sma200 = data.iloc[-1]["SMA200"]

    if close > sma50:
        if (((close - sma50) / sma50) * 100) <= STOCK_PRICE_PERCENTAGE_FROM_SMA:
            baseline_data["stocks"].append({
                "code": issuer["code"],
                "country": issuer["country"],
                "sma": "SMA50",
            })

    if close > sma100:
        if (((close - sma100) / sma100) * 100) <= STOCK_PRICE_PERCENTAGE_FROM_SMA:
            baseline_data["stocks"].append({
                "code": issuer["code"],
                "country": issuer["country"],
                "sma": "SMA100",
            })

    if close > sma200:
        if (((close - sma200) / sma200) * 100) <= STOCK_PRICE_PERCENTAGE_FROM_SMA:
            baseline_data["stocks"].append({
                "code": issuer["code"],
                "country": issuer["country"],
                "sma": "SMA200",
            })

message = baseline.render(baseline_data=baseline_data)
bot = telegram.Bot(TELEGRAM_TOKEN)
bot.send_message(chat_id=TELEGRAM_CHATID, text=message, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)