import urllib.request
import urllib.parse
import json
import time
import ssl
from datetime import datetime
from threading import Thread
from flask import Flask

# --- 🌐 FLASK WEB SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Kyaltaryar Formula Bot is Running Online!"

def run_flask():
    # Render သည် ပုံမှန်အားဖြင့် Port 10000 သို့မဟုတ် ၎င်းသတ်မှတ်ပေးသော Port ကို သုံးသည်
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 🔐 SSL Security Bypass ---
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# --- ⚙️ MASTER CONFIG ---
TOKEN = "8628147889:AAESHyfeeJVzaijoxPAe_BhcC5CnzkhfjaQ"
MY_ID = "-1004311270361" 
API = "https://draw.ar-lottery01.com/TrxWinGo/TrxWinGo_1M/GetHistoryIssuePage.json"
X_MULTIPLIERS = [1, 3, 9, 27, 81, 243, 729] 

# 📋 တောင်းဆိုထားသော ပုံသေ Formula ပတ်လမ်း (B = BIG, S = SMALL)
FORMULA_PATTERN = ["BIG", "BIG", "SMALL", "BIG", "SMALL", "SMALL", "SMALL", "BIG", "SMALL", "BIG"]

class KyaltaryarFormulaEngine:
    def __init__(self):
        self.last_period = None
        self.last_pred_val = None   
        self.users = {str(MY_ID): 0} 
        self.last_update_id = 0
        
        # --- 📊 Formula Settings ---
        self.formula_index = 0  # Formula ရဲ့ ဘယ်နေရာရောက်နေလဲ မှတ်ရန်
        
        # --- 📊 Stats Tracking ---
        self.total_predictions = 0
        self.win_count = 0          
        self.lose_streak = 0       
        self.max_lose_streak = 0   
        self.round_count = 0 

    def fetch_latest_results(self):
        try:
            url = f"{API}?pageNum=1&pageSize=5&typeId=13"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
                res = json.loads(r.read().decode())
                data = res['data']['list']
                if not data: return None, None
                
                last_p = data[0]['issueNumber']
                last_num = int(data[0]['number'])
                actual_bs = "BIG" if last_num >= 5 else "SMALL"
                
                return last_p, actual_bs
        except Exception as e:
            print(f"📡 API Fetch Error: {e}")
            return None, None

    def get_next_formula_prediction(self):
        # Formula အတိုင်း တစ်ခုချင်းစီ ထုတ်ပေးမည့် လုပ်ဆောင်ချက်
        pred = FORMULA_PATTERN[self.formula_index]
        # နောက်တစ်ကြိမ်အတွက် index တိုးမည်၊ အဆုံးရောက်ရင် ၀ ပြန်စမည်
        self.formula_index = (self.formula_index + 1) % len(FORMULA_PATTERN)
        return pred

    def sync_users(self):
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={self.last_update_id + 1}&timeout=2"
            with urllib.request.urlopen(url, timeout=5, context=ctx) as r:
                res = json.loads(r.read().decode())
                if res['ok']:
                    for up in res['result']:
                        self.last_update_id = up['update_id']
        except: pass

    def send_new_message(self, chat_id, text):
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={urllib.parse.quote(text)}&parse_mode=HTML"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
                pass
        except Exception as e:
            print(f"❌ Telegram Send Error: {e}")

# --- 🚀 BOT MAIN LOOP FUNCTION ---
def bot_main_loop():
    bot = KyaltaryarFormulaEngine()
    print("⚡ Kyaltaryar Formula Bot Engine Online...")
    bot.last_period, _ = bot.fetch_latest_results()

    # ပထမဆုံးအကြိမ် Predict တစ်ခုကို ကြိုထုတ်ထားမည်
    bot.last_pred_val = bot.get_next_formula_prediction()

    while True:
        try:
            bot.sync_users()
            curr_p, actual_bs = bot.fetch_latest_results()

            if curr_p and curr_p != bot.last_period:
                bot.round_count += 1
                
                if bot.last_period and bot.last_pred_val:
                    bot.total_predictions += 1
                    is_win = (actual_bs == bot.last_pred_val)
                    
                    if is_win:
                        bot.win_count += 1  
                        bot.lose_streak = 0  
                        
                        win_streak_text = (
                            "⚡✨🔥===============🔥✨⚡\n\n"
                            f"<b>=======✅ 🏆 WIN {bot.win_count} 🏆=====</b>\n\n"
                            "⚡✨🔥===============🔥✨⚡"
                        )
                        for uid in list(bot.users.keys()):
                            bot.send_new_message(uid, win_streak_text)
                            
                        for uid in list(bot.users.keys()):
                            bot.users[uid] = 0
                    else:
                        bot.lose_streak += 1 
                        if bot.lose_streak > bot.max_lose_streak:
                            bot.max_lose_streak = bot.lose_streak
                            
                        for uid in list(bot.users.keys()):
                            bot.users[uid] = min(bot.users[uid] + 1, len(X_MULTIPLIERS)-1)

                # နောက်ထပ် Period အတွက် Formula အတိုင်း Predict အသစ် ထုတ်ယူခြင်း
                bot.last_pred_val = bot.get_next_formula_prediction()
                bot.last_period = curr_p
                
                def build_custom_msg():
                    next_period_num = int(curr_p) + 1
                    current_step = bot.users.get(str(MY_ID), 0)
                    display_multiplier = f"<b>[ {X_MULTIPLIERS[current_step]}x ]</b>" 
                    
                    return (
                        "=======================\n"
                        "🎮 <b>GAME: GLOBAL TRX</b> 🎮\n"
                        "=======================\n"
                        f"Period : <code>{next_period_num}</code>\n"
                        f"Predict : <b>{bot.last_pred_val}</b> ➔  {display_multiplier}\n" 
                        f"Pattern : <code>FORMULA FIXED MODE</code>\n" 
                        "=======================\n"
                        f"⚠️ MAX LOSE STREAK : {bot.max_lose_streak}"
                    )

                for uid in list(bot.users.keys()):
                    bot.send_new_message(uid, build_custom_msg())
                    
            time.sleep(1) 

        except Exception as main_err: 
            print(f"⚠️ Main Loop Error: {main_err}")
            time.sleep(2)

# --- 🏁 START BOTH FLASK & BOT ---
if __name__ == "__main__":
    # Flask ကို Background Thread အဖြစ် Run ပါမည်
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Bot Main Engine ကို Run ပါမည်
    bot_main_loop()
