import os
import subprocess
import sys
from threading import Thread
from flask import Flask
from telebot import TeleBot, types

# --- FLASK WEB SERVER SETTING ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running online perfectly!"

def run_flask():
    # Render က ပေးမယ့် PORT ကို ဖတ်မယ်၊ မရှိရင် 8080 ကို သုံးမယ်
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    # Flask server ကို background thread အနေနဲ့ လှမ်း run တာဖြစ်ပါတယ်
    t = Thread(target=run_flask)
    t.start()

# --- TELEGRAM BOT CONFIGURATION ---
BOT_TOKEN = '8938971304:AAG_YGMBDMJjwjF7Yuny_qiaqM7zgWP_qP8'
CHANNEL_URL = 'https://t.me/ck6lotterysg1132' 
OWNER_USERNAME = 'shinelay1333' 

bot = TeleBot(BOT_TOKEN)

# ဖိုင်တွေသိမ်းမယ့် Folder လမ်းကြောင်း
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_files")
os.makedirs(BASE_DIR, exist_ok=True)

running_processes = {}

def get_user_folder(user_id):
    user_dir = os.path.join(BASE_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

# --- Keyboards ---
def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_channel = types.KeyboardButton("📢 Updates Channel")
    btn_upload = types.KeyboardButton("📤 Upload File")
    btn_check = types.KeyboardButton("📁 Check Files")
    markup.add(btn_channel)
    markup.add(btn_upload, btn_check)
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
    files = [f for f in os.listdir(user_dir) if f.endswith('.py')]
    
    welcome_text = (
        f"👋 Welcome, 🌟† ʀᴏᴍᴇᴏ †🌟!\n"
        f"🆔 Your User ID: `{user_id}`\n"
        f"✳️ Username: @{message.from_user.username if message.from_user.username else 'None'}\n"
        f"ℹ️ Your Status: 🆓 Free User\n"
        f"📁 Files Uploaded: {len(files)} / 6\n\n"
        f"🤖 Host & run Python (.py) scripts. Upload single scripts.\n\n"
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
        msg = bot.send_message(chat_id, "📥 Send your Python (.py) file.", reply_markup=markup)
        bot.register_next_step_handler(msg, save_uploaded_file)

    elif message.text == "📁 Check Files":
        files = [f for f in os.listdir(user_dir) if f.endswith('.py')]
        if not files:
            bot.send_message(chat_id, "📂 သင့်ထံတွင် တင်ထားသော ဖိုင်မရှိသေးပါ။")
            return
            
        markup = types.InlineKeyboardMarkup(row_width=1)
        for f in files:
            is_run = user_id in running_processes and f in running_processes[user_id]
            status_icon = "🟢" if is_run else "🔴"
            markup.add(types.InlineKeyboardButton(f"{status_icon} {f}", callback_data=f"manage_{f}"))
        
        bot.send_message(chat_id, "🗂️ Your files:\nClick to manage.", reply_markup=markup)

    elif message.text == "📢 Updates Channel":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Join Channel 📢", url=CHANNEL_URL))
        bot.send_message(chat_id, "📣 ကျွန်ုပ်တို့၏ Channel ကို အောက်ကခလုတ်နှိပ်ပြီး Join ထားနိုင်ပါတယ်-", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    user_dir = get_user_folder(user_id)
    
    if call.data == "menu_check":
        files = [f for f in os.listdir(user_dir) if f.endswith('.py')]
        if not files:
            bot.edit_message_text("📂 သင့်ထံတွင် တင်ထားသော ဖိုင်မရှိသေးပါ။", chat_id, call.message.message_id)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for f in files:
            is_run = user_id in running_processes and f in running_processes[user_id]
            status_icon = "🟢" if is_run else "🔴"
            markup.add(types.InlineKeyboardButton(f"{status_icon} {f}", callback_data=f"manage_{f}"))
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
            try:
                log_file = open(log_path, "w")
                process = subprocess.Popen([sys.executable, file_path], stdout=log_file, stderr=subprocess.STDOUT, text=True)
                running_processes[user_id][filename] = process
                bot.answer_callback_query(call.id, f"🟢 {filename} started!")
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ Error: {str(e)}")
        
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
            if not logs.strip():
                logs = "(Log empty)"
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
    if message.document and message.document.file_name.endswith('.py'):
        user_id = message.from_user.id
        user_dir = get_user_folder(user_id)
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = os.path.join(user_dir, message.document.file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        bot.reply_to(message, f"✅ `{message.document.file_name}` ကို အောင်မြင်စွာ လက်ခံရရှိပါပြီ။ `📁 Check Files` ကိုနှိပ်ပြီး စစ်ဆေးနိုင်ပါတယ်။", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ မှားယွင်းနေပါသည်။ `.py` ဖိုင်ကိုသာ ပို့ပေးရပါမယ်။")

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # ၁။ Flask Server ကို Background မှာ အရင်ဦးဆုံး စမောင်းမည်
    keep_alive()
    print("Web Server is alive!")
    
    # ၂။ Telegram Bot ကို စတင်ပတ်မောင်းမည်
    print("Bot is running perfectly...")
    bot.infinity_polling()
