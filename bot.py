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
OWNER_USERNAME = 'shinelay1333' 

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

# --- 🛠️ HTML ထဲမှ JavaScript ကို Python အဖြစ်ပြောင်းလဲပြီး Run ပေးမည့် စနစ် 🛠️ ---
def convert_and_run_html(html_path, log_path, user_id, filename):
    """ HTML ထဲက script တွေကို Python ကနေ တိုက်ရိုက် Execute လုပ်နိုင်အောင် ကြားခံ ပတ်မောင်းပေးသည့် စနစ် """
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # HTML ထဲက <script> ... </script> ကြားထဲက JavaScript ကုဒ်ကို ရှာဖွေဆွဲထုတ်ခြင်း
        scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', html_content, re.DOTALL)
        js_code = "\n".join(scripts)

        # JavaScript ကုဒ်တွေကို Python ပေါ်မှာ တိုက်ရိုက် မောင်းနှင်ပေးနိုင်မည့် ကြားခံ Python Script အသစ်တစ်ခု ဆောက်ခြင်း
        bridge_py_path = html_path + "_runner.py"
        with open(bridge_py_path, "w", encoding="utf-8") as pf:
            pf.write(f"""import js2py
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

js_code = \"\"\"{js_code}\"\"\"

print("[+] HTML Engine: Executing JavaScript Code background...")
try:
    # js2py သုံးပြီး javascript ကုဒ်ကို Python ထဲမှာ တိုက်ရိုက် run စေခြင်း
    context = js2py.EvalJs()
    
    # HTML ထဲမှာပါတဲ့ fetch သို့မဟုတ် document တွေကို python requests နဲ့ သဟဇာတဖြစ်အောင် ကြားခံပေးခြင်း
    context.execute(\"\"\"
        // Browser Environment အချို့ကို ကြားခံ Simulate လုပ်ပေးခြင်း
        var console = {{ log: function(msg) {{ print(msg); }} }};
        var document = {{ getElementById: function() {{ return {{ style: {{}} }}; }} }};
        setTimeout = function(fn, delay) {{ }}
    \"\"\")
    
    # JavaScript ကို တိုက်ရိုက် run ပတ်မောင်းခြင်း
    js2py.eval_js(js_code)
except Exception as e:
    print("[-] Engine Error:", str(e))
""")

        # `.py` ဖိုင်တွေကို ပတ်မောင်းသလိုမျိုးပဲ Subprocess နဲ့ တိုက်ရိုက် Run စေခြင်း
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
        f"👋 Welcome, 🌟† ʀᴏ模ᴏ †🌟!\n"
        f"🆔 Your User ID: `{user_id}`\n"
        f"✳️ Username: @{message.from_user.username if message.from_user.username else 'None'}\n"
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
                # HTML ဖိုင်ဖြစ်ခဲ့ရင် စနစ်သစ်နဲ့ ပြောင်းလဲ Run ပေးခြင်း
                convert_and_run_html(file_path, log_path, user_id, filename)
                bot.answer_callback_query(call.id, f"🟢 HTML Script {filename} Started background!")
            else:
                # Python ဖိုင်ဆိုရင် ပုံမှန်အတိုင်း Run ပေးခြင်း
                log_file = open(log_path, "w")
                process = subprocess.Popen([sys.executable, file_path], stdout=log_file, stderr=subprocess.STDOUT, text=True)
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

def save_uploaded_file(message):
    if message.document and (message.document.file_name.endswith('.py') or message.document.file_name.endswith('.html')):
        user_id = message.from_user.id
        user_dir = get_user_folder(user_id)
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = os.path.join(user_dir, message.document.file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.reply_to(message, f"✅ `{message.document.file_name}` ကို လက်ခံရရှိပါပြီ။ `📁 Check Files` တွင် 🟢 Start နှိပ်ပြီး Run နိုင်ပါပြီဗျာ။", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ မှားယွင်းနေပါသည်။ `.py` သို့မဟုတ် `.html` ဖိုင်များကိုသာ ပို့ပေးရပါမယ်။")

if __name__ == '__main__':
    keep_alive()
    print("Bot & HTML Engine is running perfectly...")
    bot.infinity_polling()
