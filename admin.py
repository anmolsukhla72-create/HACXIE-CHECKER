import json
import os
import random
import string
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

ADMIN_ID = [6469753987, 952847458]
ADMINS_ID = 6469753987
USERS_PATH = "Data/Users.json"
PLAN_PATH = "Data/plan.json"
KEYS_PATH = "Data/Keys.json"

# Ensure files exist
os.makedirs("Data", exist_ok=True)
for file in [USERS_PATH, PLAN_PATH, KEYS_PATH]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)

# Utility Functions


def is_admin(user_id):
    return int(user_id) in ADMIN_ID

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_keys(data):
    with open(KEYS_PATH, "w") as f:
        json.dump(data, f, indent=4)
        
def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def generate_key():
    return "-".join("".join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3))

# /stat
def stat_command(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    users = load_json(USERS_PATH)
    plans = load_json(PLAN_PATH)

    total_users = len(users)
    total_premium = sum(1 for uid, v in plans.items() if datetime.strpe.strptime(v["expiry"], "%Y-%m-%d %H:%M:%S") > datetime.today())

    msg = (
        "✦ 𝑨𝑫𝑴𝑰𝑵 𝑺𝑻𝑨𝑻𝑺 ✦\n\n"
        f"⟡ 𝗧𝗼𝘁𝗮𝗹 𝗨𝘀𝗲𝗿𝘀: {total_users}\n"
        f"⟡ 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗨𝘀𝗲𝗿𝘀: {total_premium}\n"
        "✦━━━━━━━━━━━━✦"
    )
    update.message.reply_text(msg)
    
# /broad
def broad_command(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    msg = " ".join(context.args)
    if not msg:
        update.message.reply_text("✦ Usage: /broad <your message>")
        return

    users = load_json(USERS_PATH)
    count = 0
    for uid in users:
        try:
            context.bot.send_message(chat_id=int(uid), text=msg)
            count += 1
        except:
            pass

    update.message.reply_text(f"✦ Broadcast sent to {count} users ✅")
    
# /broad
def broads_command(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    msg = " ".join(context.args)
    if not msg:
        update.message.reply_text("✦ Usage: /broad <your message>")
        return

    users = load_json(USERS_PATH)
    count = 0
    for uid in users:
        try:
            context.bot.send_message(chat_id=int(uid), text=msg)
            count += 1
        except:
            pass

    update.message.reply_text(f"✦ Broadcast sent to {count} users ✅")
    
    

# /premium
def premium_command(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    plans = load_json(PLAN_PATH)
    users = load_json(USERS_PATH)

    result = "✦ 𝑷𝑹𝑬𝑴𝑰𝑼𝑴 𝑼𝑺𝑬𝑹𝑺 ✦\n\n"
    count = 0
    for uid, v in plans.items():
        expiry = datetime.strptime(v["expiry"], "%Y-%m-%d %H:%M:%S")
        if expiry > datetime.today():
            username = users.get(uid, {}).get("username")
            username = f"@{username}" if username else "Unknown"
            result += f"⟡ {username} → {v['expiry']}\n"
            count += 1

    if count == 0:
        result += "⟡ No active premium users."
    update.message.reply_text(result)

def key_command(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) != 2 or not context.args[0].isdigit() or not context.args[1].isdigit():
        update.message.reply_text("✦ Usage: /key <days> <quantity>")
        return

    days = int(context.args[0])
    quantity = int(context.args[1])
    keys_data = load_json(KEYS_PATH)

    new_keys = []
    for _ in range(quantity):
        while True:
            k = generate_key()
            if k not in keys_data:
                keys_data[k] = {"days": days, "used": False}
                new_keys.append(k)
                break

    save_json(KEYS_PATH, keys_data)

    key_lines = "\n".join(f"{k}" for k in new_keys)
    msg = (
        "✦ 𝑲𝑬𝒀 𝑮𝑬𝑵𝑬𝑹𝑨𝑻𝑬𝑫 ✦\n\n"
        f"⟡ 𝑲𝑬𝒀 ↯ {key_lines}\n\n"
        f"⟡ 𝑽𝑨𝑳𝑰𝑫𝑰𝑻𝒀  ↯ {days} day(s)\n"
        f"⟡ 𝑸𝑼𝑨𝑵𝑻𝑰𝑻𝒀 ↯ {quantity} key(s)\n"
        f"⟡ 𝑼𝑺𝑨𝑮𝑬    ↯ /𝒓𝒆𝒅𝒆𝒆𝒎 𝒀𝑶𝑼𝑹 𝑲𝑬𝒀 𝑯𝑬𝑹𝑬\n\n"
        f"━━━━━━━━━━━━━━━━━━━━")
    update.message.reply_text(msg)



KEY_FILE = "Data/Keys.json"      



        
        
# Register all commands
def register_admin_commands(dispatcher):
    dispatcher.add_handler(CommandHandler("stat", stat_command))
    dispatcher.add_handler(CommandHandler("broad", broad_command, pass_args=True))
    dispatcher.add_handler(CommandHandler("premium", premium_command))
    dispatcher.add_handler(CommandHandler("key", key_command, pass_args=True))
