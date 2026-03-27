import requests
import os
import time
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# --- Config & Keys ---
NEWS_API_KEY = "29c4923713d0493ab21959fca5d18184"
GEMINI_API_KEY = "AIzaSyD8nEhSKb1MzVuPSDK3dTV4qWsJP2merb4" 
WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')
DB_FILE = "sent_news.txt"

# Font එක කෙලින්ම file එකෙන් කියවයි
FONT_PATH = "PlayfairDisplay-Bold.ttf"

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def create_news_image(image_url, title_en, source_name):
    try:
        # 1. පින්තූරය ලබා ගැනීම
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        
        # 2. කළු පැහැති Gradient එකක් දැමීම (Text පෙනීමට)
        overlay = Image.new('RGBA', img.size, (0,0,0,0))
        draw_ov = ImageDraw.Draw(overlay)
        for y in range(720):
            if y > 400: # පින්තූරයේ පහළ කොටස පමණක් අඳුරු කරයි
                alpha = int(((y - 400) / 320) * 220)
                draw_ov.line([(0, y), (1280, y)], fill=(0, 0, 0, alpha))
        img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)
        f_title = get_font(52)
        f_src = get_font(24)

        # 3. Title එක පේළි වලට කැඩීම
        words = title_en.split()
        lines, cur_line = [], ""
        for w in words:
            if f_title.getlength(cur_line + w) <= 1100: cur_line += w + " "
            else:
                lines.append(cur_line)
                cur_line = w + " "
        lines.append(cur_line)

        # 4. මාතෘකාව පින්තූරයේ ඇඳීම
        y_pos = 600 - (len(lines) * 60)
        for line in lines:
            draw.text((70, y_pos), line.strip(), font=f_title, fill="white")
            y_pos += 65

        # 5. Credit line එක ඇඳීම
        draw.text((70, 660), f"SOURCE : {source_name.upper()} | BBC FLASH", font=f_src, fill="#FFD700") # රන්වන් පැහැයෙන්

        # 6. BBC FLASH Logo එක ඇඳීම
        if os.path.exists("logo.png"):
            logo = Image.open("logo.png").convert("RGBA")
            logo = logo.resize((140, 140), Image.Resampling.LANCZOS)
            img.paste(logo, (1080, 40), logo)

        # 7. අවසන් රූපය Output කිරීම
        img = img.convert("RGB")
        buff = BytesIO()
        img.save(buff, format="JPEG", quality=95)
        return f"data:image/jpeg;base64,{base64.b64encode(buff.getvalue()).decode()}"
    except Exception as e:
        print(f"Image Error: {e}")
        return image_url

# ඉතිරි සෙන්ඩ් කරන කේතය කලින් වගේමයි...
