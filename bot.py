import feedparser
import requests
import os
from googletrans import Translator

# Config
RSS_FEED_URL = "http://feeds.bbci.co.uk/news/world/rss.xml"
WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')

translator = Translator()

def send_whatsapp_media(title_si, summary_si, link, image_url):
    url = "https://gate.whapi.cloud/messages/image"
    
    caption = f"🔴 *BBC Flash NEWS*\n\n📌 *{title_si}*\n\n📝 {summary_si}\n\n🔗 වැඩිදුර විස්තර: {link}"
    
    payload = {
        "media": image_url,
        "to": CHANNEL_ID,
        "caption": caption
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {WHAPI_TOKEN}"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code

# පුවත් කියවීම
feed = feedparser.parse(RSS_FEED_URL)

if feed.entries:
    # අලුත්ම පුවත තෝරා ගැනීම
    item = feed.entries[0]
    title_en = item.title
    summary_en = item.description
    link = item.link
    
    # පින්තූරය සොයා ගැනීම (BBC RSS වල media_thumbnail ලෙස ඇත)
    image_url = ""
    if 'media_thumbnail' in item:
        image_url = item.media_thumbnail[0]['url']
    else:
        # පින්තූරයක් නැත්නම් default එකක් (ඔයාට කැමති එකක් දාන්න පුළුවන්)
        image_url = "https://upload.wikimedia.org/wikipedia/commons/6/62/BBC_News_2019.svg"

    try:
        # සිංහලට පරිවර්තනය (Title සහ Summary)
        title_si = translator.translate(title_en, dest='si').text
        summary_si = translator.translate(summary_en, dest='si').text
        
        # WhatsApp යැවීම
        send_whatsapp_media(title_si, summary_si, link, image_url)
        print("Success: News sent in Sinhala with Image!")
    except Exception as e:
        print(f"Error in translation/sending: {e}")
