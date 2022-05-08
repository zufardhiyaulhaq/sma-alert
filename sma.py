import yfinance
import os
import sys
import yaml
import telegram
from datetime import date
from jinja2 import Environment, FileSystemLoader

STOCK_LISTS_FILEPATH = os.getenv('STOCK_LISTS_FILEPATH', "./stocks.yaml")
STOCK_RESISTANCE_TIMEFRAME= int(os.getenv('STOCK_RESISTANCE_TIMEFRAME'))
STOCK_RESISTANCE_SHIFT= int(os.getenv('STOCK_RESISTANCE_SHIFT'))
STOCK_PRICE_PERCENTAGE_FROM_SMA = float(os.getenv('STOCK_PRICE_PERCENTAGE_FROM_SMA'))
STOCK_PRICE_PERCENTAGE_FROM_RESISTANCE = float(os.getenv('STOCK_PRICE_PERCENTAGE_FROM_RESISTANCE'))
STOCK_PRICE_PERCENTAGE_FROM_SMA_TARGET_BUY = float(os.getenv('STOCK_PRICE_PERCENTAGE_FROM_SMA_TARGET_BUY'))
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

    # get closing price
    data = data['Close'].to_frame()

    # calculate resistance
    resistance_data = data['Close'].iloc[-abs(STOCK_RESISTANCE_TIMEFRAME+1):-1]
    resistance = resistance_data.max()
    is_resistance_valid = True

    for index in range(-abs(STOCK_RESISTANCE_TIMEFRAME+2), -abs(STOCK_RESISTANCE_TIMEFRAME+2)-abs(STOCK_RESISTANCE_SHIFT), -1):
        if resistance < data.iloc[index]["Close"]:
            is_resistance_valid = False
            break

    # calculate simple moving average
    data['SMA50'] = data['Close'].rolling(50).mean()
    data['SMA100'] = data['Close'].rolling(100).mean()
    data['SMA200'] = data['Close'].rolling(200).mean()

    # get data from the latest trading day
    close = data.iloc[-1]["Close"]
    sma50 = data.iloc[-1]["SMA50"]
    sma100 = data.iloc[-1]["SMA100"]
    sma200 = data.iloc[-1]["SMA200"]

    # check if resistance price in STOCK_PRICE_PERCENTAGE_FROM_RESISTANCE range
    if resistance < close+(close*STOCK_PRICE_PERCENTAGE_FROM_RESISTANCE/100):
        continue
    
    percentage_from_resistance = round((((resistance - close) / close) * 100), 5)

    if close > sma50:
        if sma50 > sma200:
            percentage_from_sma = round((((close - sma50) / sma50) * 100), 5)
            target_buy = round(sma50 + (sma50 * STOCK_PRICE_PERCENTAGE_FROM_SMA_TARGET_BUY / 100), 5)

            if percentage_from_sma <= STOCK_PRICE_PERCENTAGE_FROM_SMA:
                baseline_data["stocks"].append({
                    "code": issuer["code"],
                    "country": issuer["country"],
                    "sma": "SMA50",
                    "percentage_from_sma": percentage_from_sma,
                    "percentage_from_resistance": percentage_from_resistance,
                    "target_buy": target_buy,
                    "cutloss": sma50,
                })

    if close > sma200:
        percentage_from_sma = round((((close - sma200) / sma200) * 100), 5)
        target_buy = round(sma200 + (sma200 * STOCK_PRICE_PERCENTAGE_FROM_SMA_TARGET_BUY / 100), 5)

        if percentage_from_sma <= STOCK_PRICE_PERCENTAGE_FROM_SMA:
            baseline_data["stocks"].append({
                "code": issuer["code"],
                "country": issuer["country"],
                "sma": "SMA200",
                "percentage_from_sma": percentage_from_sma,
                "percentage_from_resistance": percentage_from_resistance,
                "target_buy": target_buy,
                "cutloss": sma200,
            })

message = baseline.render(baseline_data=baseline_data)
bot = telegram.Bot(token=TELEGRAM_TOKEN)
bot.send_message(chat_id=TELEGRAM_CHATID, text=message, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
