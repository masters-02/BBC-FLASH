import requests
import os
import time
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import urllib.request

# --- API Keys ---
GNEWS_API_KEY = "86f195de5c480015cafdc7ea88a7fbbe"
NEWS_API_KEY = "29c4923713d0493ab21959fca5d18184"
GEMINI_API_KEY = "AIzaSyD8nEhSKb1MzVuPSDK3dTV4qWsJP2merb4" 
WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')
DB_FILE = "sent_news.txt"

# --- අකුරු විලාසය (Font) ඩවුන්ලෝඩ් කිරීම ---
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/static/PlayfairDisplay-Bold.ttf"
FONT_PATH = "PlayfairDisplay-Bold.ttf"
if not os.path.exists(FONT_PATH):
    urllib.request.urlretrieve(FONT_URL, FONT_PATH)

def get_sent_urls():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f: return f.read().splitlines()

def save_sent_url(url):
    with open(DB_FILE, "a") as f: f.write(url + "\n")

# --- 1. පින්තූරය Edit කිරීමේ පද්ධතිය ---
def create_news_image(image_url, title_en, source_name):
    try:
        # පින්තූරය අන්තර්ජාලයෙන් ලබා ගැනීම
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        
        # පින්තූරය 1280x720 (16:9) ප්‍රමාණයට සකස් කිරීම
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        
        # Black Gradient එකක් දැමීම (අකුරු පැහැදිලිව පෙනීමට)
        overlay = Image.new('RGBA', img.size, (0,0,0,0))
        draw = ImageDraw.Draw(overlay)
        for y in range(720):
            alpha = int((y / 720) * 200) if y > 360 else int(((150 - y) / 150) * 180) if y < 150 else 0
            alpha = max(0, min(255, alpha))
            draw.line([(0, y), (1280, y)], fill=(0, 0, 0, alpha))
        img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)
        font_title = ImageFont.truetype(FONT_PATH, 55)
        font_source = ImageFont.truetype(FONT_PATH, 25)

        # Title එක පේළි වලට කැඩීම (Text Wrapping)
        words = title_en.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font_title.getlength(test_line) <= 1100: current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        # Title එක පින්තූරයේ ලිවීම (English)
        y_text = 450
        for line in lines:
            draw.text((80, y_text), line, font=font_title, fill=(255, 255, 255, 255))
            y_text += 65

        # Source / Credit එක යටින් ලිවීම
        credit_text = f"SOURCE : {source_name.upper()} | BBC FLASH"
        draw.text((80, 650), credit_text, font=font_source, fill=(200, 200, 200, 255))

        # ලෝගෝ එක එකතු කිරීම (logo.png තිබේ නම්)
        if os.path.exists("logo.png"):
            logo = Image.open("logo.png").convert("RGBA")
            logo = logo.resize((150, 150), Image.Resampling.LANCZOS)
            img.paste(logo, (1080, 50), logo)

        # අවසන් පින්තූරය Save කිරීම
        img = img.convert("RGB")
        img.save("output.jpg", "JPEG", quality=90)
        
        # Base64 බවට පත් කිරීම (WhatsApp එකට යැවීමට)
        with open("output.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    except Exception as e:
        print(f"Image Edit Error: {e}")
        return image_url # Error ආවොත් මුල් පින්තූරයේ Link එක යවයි

# --- 2. Gemini AI පරිවර්තනය ---
def translate_to_sinhala(title, desc):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"පහත පුවතේ මාතෘකාව සහ සාරාංශය කියවා, එය සම්පූර්ණ හා සවිස්තරාත්මක පුවත් ලිපියක් ලෙස පිරිසිදු සිංහලෙන් ලියන්න. ඉංග්‍රීසි වචන භාවිතා නොකරන්න.\n\nTitle: {title}\nDescription: {desc}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, headers={'Content-Type': 'application/json'}, json=data).json()
        return res["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        return f"*{title}*\n\n{desc}"

# --- 3. WhatsApp වෙත යැවීම ---
def send_to_whatsapp(translated_text, b64_image, link):
    url = "https://gate.whapi.cloud/messages/image"
    caption = f"📢 *ලෝක පුවත් සේවය*\n\n{translated_text}\n\n🔗 *සම්පූර්ණ පුවත:* {link}"
    payload = {"media": b64_image, "to": CHANNEL_ID, "caption": caption}
    headers = {"authorization": f"Bearer {WHAPI_TOKEN}", "content-type": "application/json"}
    requests.post(url, json=payload, headers=headers)

# --- ප්‍රධාන ක්‍රියාවලිය ---
all_news = []
try:
    napi = requests.get(f"https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey={NEWS_API_KEY}").json()
    for art in napi.get('articles', []):
        all_news.append({'title': art.get('title'), 'desc': art.get('description'), 'url': art.get('url'), 'img': art.get('urlToImage'), 'source': art.get('source', {}).get('name', 'BBC News')})
except: pass

sent_list = get_sent_urls()
count = 0

for news in all_news:
    if news['url'] not in sent_list and count < 11 and news['img']:
        print(f"Processing: {news['title']}")
        
        # 1. පින්තූරය Edit කිරීම (අකුරු සහ ලෝගෝ එක සමග)
        final_image = create_news_image(news['img'], news['title'], news['source'])
        
        # 2. සම්පූර්ණ විස්තරය සිංහලට හැරවීම
        final_text = translate_to_sinhala(news['title'], news['desc'])
        
        # 3. WhatsApp එකට අප්ලෝඩ් කිරීම
        send_to_whatsapp(final_text, final_image, news['url'])
        
        save_sent_url(news['url'])
        count += 1
        time.sleep(15)

print(f"✅ Successfully created and uploaded {count} news updates.")
