import urllib.request
import urllib.parse
import json
import time
import ssl
from datetime import datetime
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 🔐 SSL Security Bypass ---
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# --- ⚙️ MASTER CONFIG ---
TOKEN = "8628147889:AAESHyfeeJVzaijoxPAe_BhcC5CnzkhfjaQ"
MY_ID = "-1004311270361" 
API = "https://draw.ar-lottery01.com/TrxWinGo/TrxWinGo_1M/GetHistoryIssuePage.json"
X_MULTIPLIERS = [1, 3, 9, 27] 

# --- 🌐 ANTI-SLEEP WEB SERVER (KEEP-ALIVE ENGINE) ---
class KeepAliveServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running 24/7!")

def run_web_server():
    server_address = ('', 10000) # Render defaults to port 10000 or PORT env
    httpd = HTTPServer(server_address, KeepAliveServer)
    print("🌐 Anti-Sleep Web Server Started on Port 10000...")
    httpd.serve_forever()

class KyaltaryarBigSmallAssemblyV18:
    def __init__(self):
        self.last_period = None
        self.last_pred_side = None 
        self.last_pred_num = None  
        self.users = {str(MY_ID): 0} 
        self.last_update_id = 0
        
        self.random_key = "aafcd9c767bc482193c87a75cd3001f8"
        self.signature = "2DF68B95BC3AF3EC908203A582B19D68"
        self.timestamp = "1781328159"
        self.type_id = 13
        
        self.total_predictions = 0
        self.win_count = 0          
        self.lose_streak = 0       
        self.max_lose_streak = 0   
        self.round_count = 0 
        self.current_prob = "100%"
        self.last_failed_sides = [] 

        self.power_numbers = {
            1: 4, 2: 5, 3: 6, 4: 7, 5: 8,
            6: 9, 7: 0, 8: 1, 9: 2, 0: 3
        }

    def fetch_latest_results(self):
        try:
            url = f"{API}?pageNum=1&pageSize=30&typeId={self.type_id}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': 'application/json, text/plain, */*',
                'Random': self.random_key,
                'Signature': self.signature,
                'Timestamp': self.timestamp,
                'Content-Type': 'application/json'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
                res = json.loads(r.read().decode())
                data = res['data']['list']
                if not data: return None, []
                
                last_p = data[0]['issueNumber']
                raw_list = data[:30][::-1] 
                num_history = [int(x['number']) for x in raw_list]
                return last_p, num_history
        except Exception as e:
            print(f"📡 API Fetch Error: {e}")
            return None, []

    def chatgpt_brain(self, history):
        if len(history) >= 1:
            last = history[-1]
            if last in [3, 7]: return "Big", self.power_numbers.get(last, 7)
            if last in [4, 6]: return "Small", self.power_numbers.get(last, 2)
        scores = {i: 0 for i in range(10)}
        for index, num in enumerate(history):
            scores[num] += (index + 1) ** 1.9
        best_num = max(scores, key=scores.get)
        return "Big" if best_num >= 5 else "Small", best_num

    def deepseek_brain(self, history):
        if len(history) >= 2 and history[-1] == 0 and history[-2] == 0: return "Big", 8
        if len(history) < 2: return "Big", 5
        last_num = history[-1]
        transitions = []
        for i in range(len(history)-1):
            if history[i] == last_num: transitions.append(history[i+1])
        best_num = max(set(transitions), key=transitions.count) if transitions else (last_num + 1) % 10
        return "Big" if best_num >= 5 else "Small", best_num

    def gemini_brain(self, history):
        if history:
            last = history[-1]
            predicted_num = self.power_numbers.get(last, 5)
            return "Big" if predicted_num >= 5 else "Small", predicted_num
        return "Small", 3

    def claude_brain(self, history):
        if len(history) >= 2 and ((history[-2] == 1 and history[-1] == 7) or (history[-2] == 7 and history[-1] == 1)): return "Big", 7
        recent = history[-10:]
        big_count = sum(1 for x in recent if x >= 5)
        small_count = sum(1 for x in recent if x < 5)
        if big_count > small_count: return "Big", max([x for x in recent if x >= 5], default=7)
        else: return "Small", max([x for x in recent if x < 5], default=2)

    def grok_brain(self, history):
        if len(history) >= 1 and history[-1] in [9, 6]: return "Small", self.power_numbers.get(history[-1], 2)
        distances = {}
        for n in range(10):
            try:
                idx = list(reversed(history)).index(n)
                distances[n] = idx
            except ValueError: distances[n] = 30
        best_num = max(distances, key=distances.get)
        return "Big" if best_num >= 5 else "Small", best_num

    def llama_brain(self, history):
        if len(history) >= 2:
            if history[-2] == 3 and history[-1] == 8: return "Big", 9
            if history[-2] == 0 and history[-1] == 5: return "Small", 4
        avg = sum(history) / len(history) if history else 5
        best_num = int(avg) % 10
        return "Big" if best_num >= 5 else "Small", best_num

    def qwen_brain(self, history):
        if len(history) < 2: return "Big", 6
        gap = abs(history[-1] - history[-2])
        best_num = (history[-1] + gap) % 10
        return "Big" if best_num >= 5 else "Small", best_num

    def mistral_brain(self, history):
        if len(history) >= 1 and history[-1] == 3: return "Big", 6
        sorted_h = sorted(history) if history else [5]
        best_num = sorted_h[len(sorted_h)//2]
        return "Big" if best_num >= 5 else "Small", best_num

    def phi_brain(self, history):
        if not history: return "Big", 7
        best_num = (history[-1] * 3 + 7) % 10
        return "Big" if best_num >= 5 else "Small", best_num

    def execute_big_small_conference(self, num_history):
        if not num_history: return "Big", 5, "75%"
        ai_reports = [
            self.chatgpt_brain(num_history), self.deepseek_brain(num_history),
            self.gemini_brain(num_history), self.claude_brain(num_history),
            self.grok_brain(num_history), self.llama_brain(num_history),
            self.qwen_brain(num_history), self.mistral_brain(num_history),
            self.phi_brain(num_history)
        ]
        votes = {"Big": 0, "Small": 0}
        num_by_side = {"Big": [], "Small": []}
        for side, num in ai_reports:
            votes[side] += 1
            num_by_side[side].append(num)
        chosen_side = max(votes, key=votes.get)
        if self.lose_streak > 0 and chosen_side in self.last_failed_sides:
            chosen_side = "Small" if chosen_side == "Big" else "Big"
        nums_pool = num_by_side[chosen_side]
        chosen_num = max(set(nums_pool), key=nums_pool.count) if nums_pool else (7 if chosen_side == "Big" else 2)
        confidence = int((votes[chosen_side] / 9) * 100)
        if confidence > 98: confidence = 98
        if confidence < 50: confidence = 55
        return chosen_side, chosen_num, f"{confidence}%"

    def sync_users(self):
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={self.last_update_id + 1}&timeout=1"
            with urllib.request.urlopen(url, timeout=3, context=ctx) as r:
                res = json.loads(r.read().decode())
                if res['ok']:
                    for up in res['result']: self.last_update_id = up['update_id']
        except: pass

    def send_new_message(self, chat_id, text):
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={urllib.parse.quote(text)}&parse_mode=HTML"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8, context=ctx) as r: pass
        except Exception as e: print(f"❌ Telegram Send Error: {e}")

# --- 🚀 RUN ASSEMBLY MASTER V18 ---
bot = KyaltaryarBigSmallAssemblyV18()

# Start Web Server in a separate thread (Anti-Sleep)
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

print("⚡ Kyaltaryar v18 (Big/Small AI Image Strategy Bot) Online...")
bot.last_period, init_num = bot.fetch_latest_results()

while True:
    try:
        bot.sync_users()
        curr_p, num_history = bot.fetch_latest_results()

        if curr_p and curr_p != bot.last_period:
            bot.round_count += 1
            if bot.last_period:
                actual_num = num_history[-1] if num_history else 0
                actual_side = "Big" if actual_num >= 5 else "Small"
                
                if bot.last_pred_side is not None:
                    bot.total_predictions += 1
                    is_win = (actual_side == bot.last_pred_side)
                    
                    if is_win:
                        bot.win_count += 1; bot.lose_streak = 0; bot.last_failed_sides = [] 
                        win_streak_text = "⚡✨🔥===============🔥✨⚡\n\n" f"<b>=======✅ 🏆 WIN {bot.win_count} 🏆=====</b>\n\n" "⚡✨🔥===============🔥✨⚡"
                        for uid in list(bot.users.keys()): bot.send_new_message(uid, win_streak_text)
                        bot.users[str(MY_ID)] = 0
                    else:
                        bot.lose_streak += 1 
                        if bot.lose_streak > bot.max_lose_streak: bot.max_lose_streak = bot.lose_streak
                        bot.last_failed_sides.append(bot.last_pred_side)
                        if len(bot.last_failed_sides) > 2: bot.last_failed_sides.pop(0)
                        current_step = bot.users.get(str(MY_ID), 0)
                        bot.users[str(MY_ID)] = min(current_step + 1, len(X_MULTIPLIERS) - 1)

            p_side, p_num, p_conf = bot.execute_big_small_conference(num_history)
            bot.last_pred_side = p_side; bot.last_pred_num = p_num; bot.current_prob = p_conf
            bot.last_period = curr_p
            
            def build_custom_msg():
                next_period_num = int(curr_p) + 1
                current_step = bot.users.get(str(MY_ID), 0)
                display_multiplier = f"{X_MULTIPLIERS[current_step]}x" 
                return (
                    "=======================\n"
                    ":🎮 <b>GAME : GLOBAL TRX</b> 🎮:\n"
                    "=======================\n"
                    f"Period : {next_period_num}\n"
                    f"Predict : <b>{bot.last_pred_side} ({bot.last_pred_num})  -&gt; ({display_multiplier})</b>\n" 
                    f"Confidence : {bot.current_prob}\n" 
                    "=======================\n"
                    f"⚠️ MAX LOSE STREAK : {bot.max_lose_streak}"
                )

            for uid in list(bot.users.keys()): bot.send_new_message(uid, build_custom_msg())
                
        time.sleep(0.2) 
    except Exception as main_err: time.sleep(1)
