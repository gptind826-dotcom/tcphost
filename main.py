import telebot
import os
import shutil
import zipfile
import subprocess
import signal
import json
import uuid
import psutil
import time
from telebot import types

# ==========================================
# ⚙️ 𝐂𝐎𝐍𝐅𝐈𝐆𝐔𝐑𝐀𝐓𝐈𝐎𝐍 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒 ⚙️
# ==========================================
API_TOKEN = '8529750722:AAFE8bXKEimv8hcT0Iyj2x2ITuJmZreb1Q8'  # Insert Telegram Bot Token
ADMIN_ID = 8379062893  # Insert your numeric Telegram ID

# HIDDEN CHANNEL REQUIREMENT
REQUIRED_CHANNEL = "@exucodex" 
SUPPORT_LINK = "https://t.me/exucodex"

TEMPLATES_DIR = "templates"
INSTANCES_DIR = "instances"
DB_FILE = "orchestrator_db.json"

bot = telebot.TeleBot(API_TOKEN)

# Initialize Root Directories
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(INSTANCES_DIR, exist_ok=True)

# ==========================================
# 🗄️ 𝐃𝐀𝐓𝐀𝐁𝐀𝐒𝐄 & 𝐒𝐘𝐒𝐓𝐄𝐌 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓 🗄️
# ==========================================
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"users":[], "instances": {}}

def save_db(data):
    with open(DB_FILE, "w") as f: 
        json.dump(data, f, indent=4)

def is_subscribed(user_id):
    if user_id == ADMIN_ID: return True
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        if member.status in ['left', 'kicked', 'restricted']:
            return False
        return True
    except:
        return False 

# ==========================================
# ⌨️ 𝐊𝐄𝐘𝐁𝐎𝐀𝐑𝐃 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐎𝐑𝐒 ⌨️
# ==========================================
def sub_keyboard():
    markup = types.InlineKeyboardMarkup()
    # Hidden link embedded in the join button
    markup.add(types.InlineKeyboardButton("📢 𝐉𝐨𝐢𝐧 𝐂𝐡𝐚𝐧𝐧𝐞𝐥", url=SUPPORT_LINK))
    markup.add(types.InlineKeyboardButton("🔄 𝐕𝐞𝐫𝐢𝐟𝐲 𝐉𝐨𝐢𝐧", callback_data="check_sub"))
    return markup

def main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚀 𝐃𝐞𝐩𝐥𝐨𝐲 𝐁𝐨𝐭", "🤖 𝐌𝐲 𝐁𝐨𝐭𝐬")
    markup.row("📊 𝐒𝐲𝐬𝐭𝐞𝐦 𝐒𝐭𝐚𝐭𝐮𝐬", "📜 𝐈𝐧𝐬𝐭𝐫𝐮𝐜𝐭𝐢𝐨𝐧𝐬")
    markup.row("📞 𝐒𝐮𝐩𝐩𝐨𝐫𝐭")
    if user_id == ADMIN_ID:
        markup.row("👑 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋")
    return markup

def admin_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📤 𝐔𝐩𝐥𝐨𝐚𝐝 𝐙𝐢𝐩", callback_data="adm_upload"),
        types.InlineKeyboardButton("🗑 𝐃𝐞𝐥𝐞𝐭𝐞 𝐙𝐢𝐩", callback_data="adm_deltpl")
    )
    markup.add(
        types.InlineKeyboardButton("📈 𝐆𝐥𝐨𝐛𝐚𝐥 𝐒𝐭𝐚𝐭𝐬", callback_data="adm_stats"),
        types.InlineKeyboardButton("🚫 𝐆𝐥𝐨𝐛𝐚𝐥 𝐒𝐭𝐨𝐩", callback_data="adm_stopall")
    )
    return markup

# ==========================================
# 📄 𝐈𝐍𝐒𝐓𝐑𝐔𝐂𝐓𝐈𝐎𝐍 𝐓𝐄𝐗𝐓 📄
# ==========================================
INSTRUCTIONS = """
📖 **𝐌𝐚𝐢𝐧 𝐇𝐨𝐬𝐭𝐢𝐧𝐠 𝐈𝐧𝐬𝐭𝐫𝐮𝐜𝐭𝐢𝐨𝐧𝐬**

𝟏. **𝐂𝐥𝐨𝐧𝐞**: 𝐒𝐞𝐥𝐞𝐜𝐭 𝐚 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐙𝐈𝐏 𝐭𝐨 𝐬𝐭𝐚𝐫𝐭.
𝟐. **𝐒𝐚𝐧𝐝𝐛𝐨𝐱**: 𝐄𝐚𝐜𝐡 𝐛𝐨𝐭 𝐫𝐮𝐧𝐬 𝐢𝐧 𝐚 𝐩𝐫𝐢𝐯𝐚𝐭𝐞 𝐢𝐬𝐨𝐥𝐚𝐭𝐞𝐝 𝐟𝐨𝐥𝐝𝐞𝐫.
𝟑. **𝐂𝐨𝐧𝐟𝐢𝐠**: 𝐘𝐨𝐮𝐫 𝐔𝐈𝐃 & 𝐏𝐚𝐬𝐬𝐰𝐨𝐫𝐝 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐰𝐫𝐢𝐭𝐭𝐞𝐧 𝐭𝐨 𝐁𝐨𝐭.𝐭𝐱𝐭.
𝟒. **𝐑𝐮𝐧𝐭𝐢𝐦𝐞**: 𝐓𝐡𝐞 𝐬𝐲𝐬𝐭𝐞𝐦 𝐬𝐩𝐚𝐰𝐧𝐬 𝐚 𝐛𝐚𝐜𝐤𝐠𝐫𝐨𝐮𝐧𝐝 𝐩𝐫𝐨𝐜𝐞𝐬𝐬 𝐟𝐨𝐫 𝐲𝐨𝐮.
𝟓. **𝐋𝐨𝐠𝐬**: 𝐀𝐥𝐥 𝐨𝐮𝐭𝐩𝐮𝐭 𝐢𝐬 𝐬𝐚𝐯𝐞𝐝 𝐭𝐨 𝐛𝐨𝐭.𝐥𝐨𝐠 𝐢𝐧𝐬𝐢𝐝𝐞 𝐲𝐨𝐮𝐫 𝐧𝐨𝐝𝐞.
𝟔. **𝐄𝐱𝐢𝐭**: 𝐔𝐬𝐞 '𝐌𝐲 𝐁𝐨𝐭𝐬' 𝐭𝐨 𝐭𝐞𝐫𝐦𝐢𝐧𝐚𝐭𝐞 𝐭𝐡𝐞 𝐩𝐫𝐨𝐜𝐞𝐬𝐬 𝐚𝐧𝐝 𝐰𝐢𝐩𝐞 𝐝𝐚𝐭𝐚.

⚠️ **𝐍𝐞𝐯𝐞𝐫 𝐬𝐡𝐚𝐫𝐞 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐨𝐮𝐧𝐭 𝐜𝐫𝐞𝐝𝐞𝐧𝐭𝐢𝐚𝐥𝐬 𝐰𝐢𝐭𝐡 𝐚𝐧𝐲𝐨𝐧𝐞.**
"""

# ==========================================
# 🚀 𝐁𝐎𝐓 𝐇𝐀𝐍𝐃𝐋𝐄𝐑𝐒 & 𝐋𝐎𝐆𝐈𝐂 🚀
# ==========================================
@bot.message_handler(commands=['start'])
def start_msg(message):
    if not is_subscribed(message.chat.id):
        return bot.send_message(message.chat.id, "🚫 **𝐀𝐜𝐜𝐞𝐬𝐬 𝐃𝐞𝐧𝐢𝐞𝐝!**\n\n𝐘𝐨𝐮 𝐦𝐮𝐬𝐭 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐞 𝐡𝐨𝐬𝐭𝐢𝐧𝐠 𝐬𝐞𝐫𝐯𝐢𝐜𝐞𝐬.", reply_markup=sub_keyboard())
    
    db = load_db()
    if message.chat.id not in db["users"]:
        db["users"].append(message.chat.id)
        save_db(db)
    
    bot.send_message(message.chat.id, "✨ **𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 𝐓𝐂𝐏 𝐇𝐨𝐬𝐭𝐢𝐧𝐠 𝐁𝐨𝐭**\n\n𝐒𝐲𝐬𝐭𝐞𝐦 𝐢𝐬 𝐑𝐞𝐚𝐝𝐲. 𝐂𝐡𝐨𝐨𝐬𝐞 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐛𝐞𝐥𝐨𝐰:", reply_markup=main_keyboard(message.chat.id))

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def verify_subscription(call):
    if is_subscribed(call.message.chat.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ **𝐀𝐜𝐜𝐞𝐬𝐬 𝐆𝐫𝐚𝐧𝐭𝐞𝐝!**\n\n𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐛𝐞𝐥𝐨𝐰:", reply_markup=main_keyboard(call.message.chat.id))
    else:
        bot.answer_callback_query(call.id, "❌ 𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐧𝐨𝐭 𝐣𝐨𝐢𝐧𝐞𝐝 𝐲𝐞𝐭!", show_alert=True)

@bot.message_handler(func=lambda m: m.text == "📞 𝐒𝐮𝐩𝐩𝐨𝐫𝐭")
def contact_support(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🌐 𝐉𝐨𝐢𝐧 𝐂𝐨𝐦𝐦𝐮𝐧𝐢𝐭𝐲", url=SUPPORT_LINK))
    bot.send_message(message.chat.id, "📩 **𝐅𝐨𝐫 𝐚𝐧𝐲 𝐢𝐬𝐬𝐮𝐞𝐬 𝐨𝐫 𝐪𝐮𝐞𝐫𝐢𝐞𝐬:**", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📜 𝐈𝐧𝐬𝐭𝐫𝐮𝐜𝐭𝐢𝐨𝐧𝐬")
def tutorial(message):
    if not is_subscribed(message.chat.id): return
    bot.reply_to(message, INSTRUCTIONS)

@bot.message_handler(func=lambda m: m.text == "📊 𝐒𝐲𝐬𝐭𝐞𝐦 𝐒𝐭𝐚𝐭𝐮𝐬")
def status_info(message):
    if not is_subscribed(message.chat.id): return
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    bot.reply_to(message, f"📊 **𝐒𝐲𝐬𝐭𝐞𝐦 𝐇𝐞𝐚𝐥𝐭𝐡**\n\n⚙️ 𝐂𝐏𝐔 𝐔𝐬𝐚𝐠𝐞: {cpu}%\n💾 𝐑𝐀𝐌 𝐔𝐬𝐚𝐠𝐞: {ram}%")

@bot.message_handler(func=lambda m: m.text == "🚀 𝐃𝐞𝐩𝐥𝐨𝐲 𝐁𝐨𝐭")
def prepare_deployment(message):
    if not is_subscribed(message.chat.id): return
    templates =[f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.zip')]
    if not templates: return bot.reply_to(message, "❌ **𝐍𝐨 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞𝐬 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 𝐟𝐨𝐫 𝐀𝐝𝐦𝐢𝐧.**")
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for t in templates:
        markup.add(types.InlineKeyboardButton(f"📦 {t}", callback_data=f"sel_{t}"))
    bot.send_message(message.chat.id, "𝐂𝐡𝐨𝐨𝐬𝐞 𝐚 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐟𝐫𝐨𝐦 𝐭𝐡𝐞 𝐥𝐢𝐬𝐭:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("sel_"))
def process_selection(call):
    template = call.data.replace("sel_", "")
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"📂 **𝐒𝐞𝐥𝐞𝐜𝐭𝐞𝐝 𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞**: {template}\n\n𝟏️⃣ **𝐄𝐧𝐭𝐞𝐫 𝐲𝐨𝐮𝐫 𝐅𝐫𝐞𝐞 𝐅𝐢𝐫𝐞 𝐔𝐈𝐃:**")
    bot.register_next_step_handler(msg, collect_uid, template)

def collect_uid(message, template):
    uid = message.text.strip()
    msg = bot.send_message(message.chat.id, "𝟐️⃣ **𝐄𝐧𝐭𝐞𝐫 𝐲𝐨𝐮𝐫 𝐏𝐚𝐬𝐬𝐰𝐨𝐫𝐝:**")
    bot.register_next_step_handler(msg, collect_password_and_launch, template, uid)

def collect_password_and_launch(message, template, uid):
    password = message.text.strip()
    chat_id = message.chat.id
    instance_id = f"ffbot_{uuid.uuid4().hex[:5]}"
    instance_path = os.path.join(INSTANCES_DIR, instance_id)

    bot.send_message(chat_id, "⏳ **𝐒𝐩𝐢𝐧𝐧𝐢𝐧𝐠 𝐮𝐩 𝐲𝐨𝐮𝐫 𝐩𝐫𝐨𝐜𝐞𝐬𝐬. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭...**")

    try:
        os.makedirs(instance_path, exist_ok=True)
        template_path = os.path.join(TEMPLATES_DIR, template)
        
        with zipfile.ZipFile(template_path, 'r') as zip_ref:
            zip_ref.extractall(instance_path)
        
        # Free Fire BOT Credential Injection
        config_path = os.path.join(instance_path, "Bot.txt")
        with open(config_path, "w") as f:
            f.write(f"uid={uid}\npassword={password}\n")

        log_path = os.path.join(instance_path, "bot.log")
        log_file = open(log_path, "a")
        
        # Starts the free fire `main.py` found INSIDE the Extracted ZIP Sandbox
        proc = subprocess.Popen(["python3", "main.py"], cwd=instance_path, stdout=log_file, stderr=log_file)

        db = load_db()
        db["instances"][instance_id] = {
            "owner": chat_id, 
            "pid": proc.pid, 
            "uid": uid, 
            "template": template,
            "deployed_on": time.strftime("%Y-%m-%d %H:%M")
        }
        save_db(db)

        success_text = f"✅ **𝐃𝐞𝐩𝐥𝐨𝐲𝐦𝐞𝐧𝐭 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥!**\n\n🆔 **𝐈𝐧𝐬𝐭𝐚𝐧𝐜𝐞 𝐈𝐃**: `{instance_id}`\n👤 **𝐓𝐚𝐫𝐠𝐞𝐭 𝐔𝐈𝐃**: `{uid}`\n🚀 **𝐒𝐭𝐚𝐭𝐮𝐬**: 𝐑𝐮𝐧𝐧𝐢𝐧𝐠 𝐢𝐧 𝐁𝐚𝐜𝐤𝐠𝐫𝐨𝐮𝐧𝐝."
        bot.send_message(chat_id, success_text)

    except Exception as e:
        bot.send_message(chat_id, f"❌ **𝐅𝐚𝐭𝐚𝐥 𝐄𝐫𝐫𝐨𝐫**: {e}")
        if os.path.exists(instance_path): shutil.rmtree(instance_path)

@bot.message_handler(func=lambda m: m.text == "🤖 𝐌𝐲 𝐁𝐨𝐭𝐬")
def overview_running_nodes(message):
    if not is_subscribed(message.chat.id): return
    db = load_db()
    
    my_bots = {k: v for k, v in db["instances"].items() if v["owner"] == message.chat.id}
    if not my_bots: 
        return bot.reply_to(message, "❗️ **𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐧𝐨 𝐚𝐜𝐭𝐢𝐯𝐞 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐞𝐬 𝐫𝐮𝐧𝐧𝐢𝐧𝐠.**")

    for bid, info in my_bots.items():
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛑 𝐒𝐭𝐨𝐩 & 𝐃𝐞𝐥𝐞𝐭𝐞", callback_data=f"stop_{bid}"))
        
        detail_panel = (
            f"🤖 **𝐈𝐧𝐬𝐭𝐚𝐧𝐜𝐞 𝐈𝐃**: `{bid}`\n"
            f"🆔 **𝐂𝐫𝐞𝐝 𝐔𝐈𝐃**: `{info['uid']}`\n"
            f"📦 **𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞**: `{info['template']}`\n"
            f"📅 **𝐁𝐨𝐨𝐭𝐞𝐝**: {info.get('deployed_on', 'Unknown')}"
        )
        bot.send_message(message.chat.id, detail_panel, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("stop_"))
def shutdown_system(call):
    bid = call.data.replace("stop_", "")
    db = load_db()
    
    if bid in db["instances"]:
        pid = db["instances"][bid]["pid"]
        try:
            os.kill(pid, signal.SIGTERM) 
        except Exception: pass
            
        try:
            node_dir = os.path.join(INSTANCES_DIR, bid)
            if os.path.exists(node_dir): shutil.rmtree(node_dir)
            del db["instances"][bid]
            save_db(db)
            bot.edit_message_text("✅ **𝐁𝐨𝐭 𝐓𝐞𝐫𝐦𝐢𝐧𝐚𝐭𝐞𝐝 𝐚𝐧𝐝 𝐖𝐢𝐩𝐞𝐝.**", call.message.chat.id, call.message.message_id)
        except Exception:
            bot.answer_callback_query(call.id, "𝐈𝐧𝐭𝐞𝐫𝐧𝐚𝐥 𝐅𝐢𝐥𝐞 𝐄𝐫𝐫𝐨𝐫", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "❌ 𝐏𝐫𝐨𝐜𝐞𝐬𝐬 𝐧𝐨 𝐥𝐨𝐧𝐠𝐞𝐫 𝐢𝐧 𝐫𝐞𝐠𝐢𝐬𝐭𝐫𝐲.")

# ==========================================
# 👑 𝐀𝐃𝐌𝐈𝐍𝐈𝐒𝐓𝐑𝐀𝐓𝐈𝐎𝐍 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 𝐏𝐀𝐍𝐄𝐋 👑
# ==========================================
@bot.message_handler(func=lambda m: m.text == "👑 𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋" and m.chat.id == ADMIN_ID)
def launch_superpanel(message):
    bot.send_message(message.chat.id, "👑 **𝐖𝐞𝐥𝐜𝐨𝐦𝐞, 𝐀𝐝𝐦𝐢𝐧! 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭 𝐂𝐨𝐧𝐬𝐨𝐥𝐞:**", reply_markup=admin_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "adm_upload")
def prepare_upload_payload(call):
    msg = bot.send_message(call.message.chat.id, "📤 **𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐩𝐥𝐨𝐚𝐝 𝐲𝐨𝐮𝐫 .𝐳𝐢𝐩 𝐦𝐚𝐬𝐭𝐞𝐫 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞.**")
    bot.register_next_step_handler(msg, process_zip_payload)

def process_zip_payload(message):
    if message.document and message.document.file_name.endswith('.zip'):
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            with open(os.path.join(TEMPLATES_DIR, message.document.file_name), 'wb') as f:
                f.write(downloaded)
            bot.reply_to(message, "✅ **𝐌𝐚𝐬𝐭𝐞𝐫 𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐀𝐩𝐩𝐞𝐧𝐝𝐞𝐝 𝐭𝐨 𝐒𝐞𝐫𝐯𝐞𝐫 𝐋𝐢𝐛𝐫𝐚𝐫𝐲.**")
        except Exception as e:
            bot.reply_to(message, f"❌ **𝐓𝐫𝐚𝐧𝐬𝐦𝐢𝐬𝐬𝐢𝐨𝐧 𝐅𝐚𝐢𝐥𝐮𝐫𝐞**: {e}")
    else:
        bot.reply_to(message, "❌ **𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐅𝐢𝐥𝐞. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐨𝐧𝐥𝐲 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐙𝐈𝐏.**")

@bot.callback_query_handler(func=lambda call: call.data == "adm_deltpl")
def del_tpl_command(call):
    templates =[f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.zip')]
    if not templates: return bot.answer_callback_query(call.id, "No Templates in server", show_alert=True)

    markup = types.InlineKeyboardMarkup(row_width=1)
    for t in templates: markup.add(types.InlineKeyboardButton(f"🗑 {t}", callback_data=f"killtpl_{t}"))
    bot.edit_message_text("☢️ **𝐒𝐞𝐥𝐞𝐜𝐭 𝐚 𝐭𝐞𝐦𝐩𝐥𝐚𝐭𝐞 𝐭𝐨 𝐝𝐞𝐥𝐞𝐭𝐞:**", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("killtpl_"))
def exe_del_tpl(call):
    template = call.data.replace("killtpl_", "")
    target = os.path.join(TEMPLATES_DIR, template)
    if os.path.exists(target): os.remove(target)
    bot.edit_message_text(f"✅ **𝐓𝐞𝐦𝐩𝐥𝐚𝐭𝐞 '{template}' 𝐞𝐫𝐚𝐝𝐢𝐜𝐚𝐭𝐞𝐝.**", call.message.chat.id, call.message.message_id, reply_markup=admin_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "adm_stats")
def display_server_info(call):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    db = load_db()
    stat = f"📊 **𝐌𝐀𝐒𝐓𝐄𝐑 𝐓𝐄𝐋𝐄𝐌𝐄𝐓𝐑𝐘**\n\n🖥 **𝐂𝐏𝐔**: {cpu}%\n🔋 **𝐑𝐀𝐌**: {ram.percent}%\n🌍 **𝐔𝐬𝐞𝐫𝐬**: {len(db['users'])}\n🔥 **𝐁𝐨𝐭𝐬 𝐑𝐮𝐧𝐧𝐢𝐧𝐠**: {len(db['instances'])}"
    bot.edit_message_text(stat, call.message.chat.id, call.message.message_id, reply_markup=admin_keyboard())

@bot.callback_query_handler(func=lambda call: call.data == "adm_stopall")
def armageddon_switch(call):
    db = load_db()
    kill_count = 0
    for inst_id, data in list(db["instances"].items()):
        try: os.kill(data["pid"], signal.SIGTERM)
        except: pass
        if os.path.exists(os.path.join(INSTANCES_DIR, inst_id)): shutil.rmtree(os.path.join(INSTANCES_DIR, inst_id))
        kill_count += 1
    db["instances"] = {}
    save_db(db)
    bot.edit_message_text(f"💀 **𝐎𝐦𝐞𝐠𝐚 𝐏𝐮𝐫𝐠𝐞 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞.**\n{kill_count} 𝐁𝐨𝐭𝐬 𝐭𝐞𝐫𝐦𝐢𝐧𝐚𝐭𝐞𝐝.", call.message.chat.id, call.message.message_id, reply_markup=admin_keyboard())

# ==========================================
# 🔥 𝐒𝐓𝐀𝐑𝐓𝐔𝐏 𝐑𝐎𝐔𝐓𝐈𝐍𝐄 🔥
# ==========================================
if __name__ == '__main__':
    print("🚀[𝐓𝐂𝐏 𝐇𝐨𝐬𝐭𝐢𝐧𝐠 𝐎𝐫𝐜𝐡𝐞𝐬𝐭𝐫𝐚𝐭𝐨𝐫 𝐨𝐧𝐥𝐢𝐧𝐞! 𝐋𝐢𝐬𝐭𝐞𝐧𝐢𝐧𝐠...]")
    bot.infinity_polling()
