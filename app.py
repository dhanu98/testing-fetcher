from flask import Flask, render_template
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)

news_cache = []

def get_sentiment(title):
    bullish_words = ["rise", "surge", "gain", "growth", "increase"]
    bearish_words = ["fall", "drop", "crash", "war", "conflict"]

    title_lower = title.lower()

    if any(word in title_lower for word in bullish_words):
        return "Bullish 📈"
    elif any(word in title_lower for word in bearish_words):
        return "Bearish 📉"
    else:
        return "Neutral ⚖️"


def fetch_news():
    global news_cache

    query = """(
    geopolitics OR usa OR us OR trump OR war OR conflict OR military OR defense OR missile OR nuclear OR
    iran OR russia OR ukraine OR china OR taiwan OR israel OR gaza OR middle east OR
    oil OR crude oil OR brent OR opec OR energy crisis OR gas prices OR
    gold OR inflation OR recession OR central bank OR fed OR interest rates OR
    crypto OR bitcoin OR ethereum OR regulation OR sanctions OR economy OR global markets
    )"""
    url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"

    response = requests.get(url)
    root = ET.fromstring(response.content)

    temp_news = []

    for item in root.findall(".//item"):
        title = item.find("title").text
        link = item.find("link").text
        pub_date_raw = item.find("pubDate").text

        pub_date = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %Z")

        temp_news.append({
            "title": title,
            "link": link,
            "pub_date": pub_date,
            "sentiment": get_sentiment(title)
        })

    # sort latest first
    temp_news.sort(key=lambda x: x["pub_date"], reverse=True)

    news_cache = temp_news


# 🔁 Background updater (every 20 sec)
def updater():
    while True:
        fetch_news()
        time.sleep(20)


# start background thread
threading.Thread(target=updater, daemon=True).start()


@app.route("/")
def home():
    return render_template("index.html", news=news_cache)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
