import requests
from twilio.rest import Client
from datetime import datetime, timedelta
import project_config


TWILLIO_ACCOUNT_SID = project_config.TWILLIO_ACCOUNT_SID
TWILLIO_AUTH_TOKEN = project_config.TWILLIO_AUTH_TOKEN
ALPHAVANTAGE_API_KEY = project_config.ALPHAVANTAGE_API_KEY
NEWS_API_KEY = project_config.NEWS_API_KEY
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

## retrieving closing price for the last 2 business days and compare difference
param_alphavantage = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": ALPHAVANTAGE_API_KEY,
}

response = requests.get(url=STOCK_ENDPOINT, params=param_alphavantage)
data = response.json()["Time Series (Daily)"]
#putting the information associated with each date into a list,
# thus eliminating the need to check dated, simply grab the 2 most recent dates.
data_list = [value for (key, value) in data.items()]
# closing price for the previous 2 business days and their difference
closing_bd_1 = float(data_list[0]["4. close"])
closing_bd_2 = float(data_list[1]["4. close"])
difference_percent = round((closing_bd_1 - closing_bd_2) / closing_bd_2 * 100, 2)
print(difference_percent)

if difference_percent > 0:
    symbol = "🔺"
elif difference_percent < 0:
    symbol = "🔻"
else:
    symbol = "🔴"

##retrieve news
if abs(difference_percent) >= 5:
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    params_news = {
        "apiKey": NEWS_API_KEY,
        "q": COMPANY_NAME,
        "searchIn": "Title",
        "from": str(yesterday),
        "to": str(today),
        "language": "en",
        "sortBy": "relevancy"
    }
    response = requests.get(url=NEWS_ENDPOINT, params=params_news)
    #pick top 3 news and put in a list
    news_3 = response.json()["articles"][:3]
    print(response.json())
    for i in news_3:
        """send top 3 pieces of news if closing price difference >= 5%"""
        client = Client(TWILLIO_ACCOUNT_SID, TWILLIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=project_config.TWILLIO_SENDER,
            to=project_config.TWILLIO_RECIPIENT,
            body=f"{STOCK}:️ {symbol}{difference_percent}%\n"
                 f"Headline: {news_3[i]["title"]}\n"
                 f"Brief: {news_3[i]["description"]}\n",
        )


