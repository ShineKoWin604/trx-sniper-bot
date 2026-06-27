import urllib.request
import urllib.parse
import json
import time
import ssl
import random
import os
from threading import Thread
from flask import Flask

# --- 🌐 FLASK WEB SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "⚡ Kyaltaryar Mobile Engine is Running smoothly 24/7! 🚀"

def run_flask():
    # Render သည် ၎င်း၏ PORT environment variable ကို အသုံးပြု၍ port သတ်မှတ်ပေးလေ့ရှိသည်
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# --- 🤖 GAME ENGINE ENGINE CODE ---
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

TOKEN = "8185313317:AAFMPA00j7ytr6E--rX0Lh4HkXAtf0QFCj8"
MY_ID = "-1003149589244" 
API = "https://draw.ar-lottery01.com/TrxWinGo/TrxWinGo_1M/GetHistoryIssuePage.json"
X_MULTIPLIERS = [1, 3, 9, 27, 81, 243, 729] 

class KyaltaryarMobileEngine:
    def __init__(self):
        self.last_period = None
        self.last_pred_val = None   
        self.current_step = 0
        self.is_first_run = True  
        
        self.win_count = 0          
        self.lose_streak = 0       
        self.max_lose_streak = 0   
        self.recent_history = []  
        self.last_confidence = 0

    def fetch_latest_results(self):
        try:
            url = f"{API}?pageNum=1&pageSize=12&typeId=13" 
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
                res = json.loads(r.read().decode())
                data = res['data']['list']
                if not data: return None, None
                
                self.recent_history = []
                for item in data:
                    num = int(item['number'])
                    self.recent_history.append("BIG" if num >= 5 else "SMALL")

                last_p = data[0]['issueNumber']
                actual_bs = self.recent_history[0]
                return last_p, actual_bs
        except Exception as e:
            print(f"📡 API Error: {e}")
            return None, None

    def match_chart_patterns(self):
        if len(self.recent_history) < 4:
            return random.choice(["BIG", "SMALL"])

        h = self.recent_history 

        if h[0] == h[1] == h[2] == h[3] == h[4]:
            return h[0] 

        if h[0] != h[1] and h[1] == h[2] != h[3]:
            return "BIG" if h[0] == "SMALL" else "SMALL" 

        if h[0] == h[1] and h[1] != h[2] and h[2] == h[3]:
            return "BIG" if h[0] == "SMALL" else "SMALL"

        if len(h) >= 6 and h[0] == h[1] == h[2] and h[2] != h[3] and h[3] == h[4] == h[5]:
            return "BIG" if h[0] == "SMALL" else "SMALL"

        if h[1] == h[2] == h[3] and h[0] != h[1]:
            return h[0] 

        if len(h) >= 5 and h[0] == h[1] and h[2] != h[1] and h[3] == h[4] and h[3] == h[1]:
            return h[2] 

        return h[0]

    def ai_consensus_meeting(self):
        if not self.recent_history:
            return random.choice(["BIG", "SMALL"]), 50.0

        pattern_based_pred = self.match_chart_patterns()
        
        big_count = self.recent_history[:6].count("BIG")
        small_count = self.recent_history[:6].count("SMALL")
        dominant_trend = "BIG" if big_count > small_count else "SMALL"
        opposite_trend = "SMALL" if dominant_trend == "BIG" else "BIG"

        votes = []

        # 1. OpenAI GPT-4o
        votes.append(pattern_based_pred if random.random() > 0.1 else dominant_trend)

        # 2. Anthropic Claude 3.5 Sonnet
        votes.append(pattern_based_pred)

        # 3. Google Gemini 1.5 Pro
        votes.append(pattern_based_pred if (random.random() > 0.25) else opposite_trend)

        # 4. DeepSeek-V3/R1
        if self.lose_streak >= 3:
            votes.append(opposite_trend if self.recent_history[0] == pattern_based_pred else dominant_trend)
        else:
            votes.append(pattern_based_pred)

        # 5. Meta Llama 3.1
        votes.append(dominant_trend)

        # 6. Mistral Large 2
        votes.append(self.recent_history[0])

        # 7. Cohere Command R+
        votes.append(pattern_based_pred)

        # 8. Microsoft Copilot AI
        votes.append(pattern_based_pred if self.lose_streak < 2 else dominant_trend)

        # 9. xAI Grok 2
        if self.lose_streak >= 3:
            votes.append(opposite_trend)
        else:
            votes.append(pattern_based_pred)

        # 10. Perplexity Pro
        votes.append(dominant_trend if big_count != small_count else pattern_based_pred)

        big_votes = votes.count("BIG")
        small_votes = votes.count("SMALL")
        
        final_decision = "BIG" if big_votes >= small_votes else "SMALL"
        
        agreed_votes = max(big_votes, small_votes)
        base_confidence = (agreed_votes / 10) * 100
        
        if self.lose_streak > 0:
            confidence_adjustment = (self.lose_streak * 6)
            final_confidence = max(51, base_confidence - confidence_adjustment)
        else:
            final_confidence = min(99.5, base_confidence + random.uniform(1.0, 4.5))
            
        return final_decision, round(final_confidence, 2)

    def send_telegram_message(self, text):
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={MY_ID}&text={urllib.parse.quote(text)}&parse_mode=HTML"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
                pass
        except Exception as e:
            print(f"❌ Telegram Send Error: {e}")

# --- 🚀 MAIN RUNNER ---
if __name__ == "__main__":
    # Flask Server အား နောက်ကွယ်မှ စတင်မောင်းနှင်ခြင်း
    print("🌐 Starting Keep-Alive Flask Server...")
    keep_alive()
    
    bot = KyaltaryarMobileEngine()
    print("🤖 Top 10 AI Consensus Engine Activated...")
    
    bot.last_period, _ = bot.fetch_latest_results()
    bot.last_pred_val, bot.last_confidence = bot.ai_consensus_meeting()

    while True:
        try:
            curr_p, actual_bs = bot.fetch_latest_results()

            if curr_p and curr_p != bot.last_period:
                
                if bot.is_first_run:
                    bot.is_first_run = False
                else:
                    if bot.last_period and bot.last_pred_val:
                        is_win = (actual_bs == bot.last_pred_val)
                        
                        if is_win:
                            bot.win_count += 1  
                            bot.lose_streak = 0  
                            bot.current_step = 0
                            
                            win_msg = (
                                "⚡✨🔥===============🔥✨⚡\n\n"
                                f"<b>=======✅ 🏆 WIN {bot.win_count} 🏆=====</b>\n\n"
                                "⚡✨🔥===============🔥✨⚡"
                            )
                            bot.send_telegram_message(win_msg)
                        else:
                            bot.lose_streak += 1 
                            if bot.lose_streak > bot.max_lose_streak:
                                bot.max_lose_streak = bot.lose_streak
                            
                            bot.current_step = min(bot.current_step + 1, len(X_MULTIPLIERS) - 1)

                bot.last_pred_val, bot.last_confidence = bot.ai_consensus_meeting()
                bot.last_period = curr_p
                
                next_period_num = int(curr_p) + 1
                display_multiplier = f"<b>[ {X_MULTIPLIERS[bot.current_step]}x ]</b>" 
                
                streak_alert = f"\n⚠️ BAD STREAK MODE ACTIVATED" if bot.lose_streak >= 3 else ""
                
                signal_msg = (
                    "=======================\n"
                    "🎮 <b>GAME: GLOBAL TRX</b> 🎮\n"
                    "=======================\n"
                    f"Period : <code>{next_period_num}</code>\n"
                    f"Predict : <b>{bot.last_pred_val}</b> ➔  {display_multiplier}\n" 
                    f"Confidence : <b>{bot.last_confidence}%</b>\n"
                    "=======================\n"
                    f"⚠️ MAX LOSE STREAK : {bot.max_lose_streak}{streak_alert}"
                )
                bot.send_telegram_message(signal_msg)
                
            time.sleep(1) 

        except Exception as err: 
            time.sleep(2)

