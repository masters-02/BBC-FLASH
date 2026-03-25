import feedparser
import requests
import os

# BBC RSS Feed URL
RSS_FEED_URL = "http://feeds.bbci.co.uk/news/world/rss.xml"
WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')

def send_whatsapp_msg(title, link):
    url = "https://gate.whapi.cloud/messages/text"
    payload = {
        "typing_time": 0,
        "to": CHANNEL_ID,
        "body": f"🔴 *BBC Flash NEWS*\n\n{title}\n\n🔗 වැඩිදුර විස්තර: {link}"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {WHAPI_TOKEN}"
    }
    requests.post(url, json=payload, headers=headers)

# පුවත් කියවා අවසන් පුවත යැවීම
feed = feedparser.parse(RSS_FEED_URL)
if feed.entries:
    latest_news = feed.entries[0]
    send_whatsapp_msg(latest_news.title, latest_news.link)
