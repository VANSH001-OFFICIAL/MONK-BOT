import asyncio
import os
import random
import string
import threading
import time
import logging
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command, BaseFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from pymongo import MongoClient, DESCENDING

# ================= CONFIGURATION =================
BOT_TOKEN = "8445493171:AAFpi_rg_CSImfp0vjvtsxuxQ-k2Wsv3ds0" 
MONGO_URI = "mongodb+srv://shaurya59rt_db_user:admin123@cluster0.sw408wn.mongodb.net/?appName=Cluster0"
MINI_APP_URL = "https://monk-bot-sh8z.onrender.com" 
ADMIN_IDS = [6498723145, 123456789] # Add your Telegram ID here

# ================= MONGODB SETUP =================
client = MongoClient(MONGO_URI)
db = client['telegram_bot_db']
users_col = db['users']      
history_col = db['history']  
teams_col = db['teams']      
settings_col = db['settings']

# Ensure Indexes for performance
users_col.create_index([("user_id", 1)], unique=True)
history_col.create_index([("user_id", 1)])

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MonkBot")

# ================= FLASK SERVER (MINI APP) =================
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Monk Task Premium Arena</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Orbitron:wght@400;900&family=Inter:wght@300;600&display=swap');

        :root {
            --monk-gold: #FFD700;
            --monk-gold-glow: rgba(255, 215, 0, 0.4);
            --bg-obsidian: #080808;
            --bg-card: rgba(20, 20, 20, 0.95);
            --accent-gold: #C5A059;
            --text-gray: #A0A0A0;
            --glass: rgba(255, 255, 255, 0.03);
            --win-green: #4ADE80;
            --loss-red: #F87171;
        }

        /* BASE THEME FIXES */
        body { 
            background: var(--bg-obsidian); 
            color: #ffffff; 
            font-family: 'Inter', sans-serif;
            margin: 0; padding: 0;
            overflow: hidden;
            height: 100vh;
        }

        /* 1. ANIMATED SPLASH SCREEN */
        #splash-screen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #000; z-index: 10000; display: flex;
            flex-direction: column; align-items: center; justify-content: center;
        }
        .monk-logo-container { position: relative; width: 100px; height: 100px; }
        .monk-ring {
            position: absolute; width: 100%; height: 100%;
            border: 3px solid var(--monk-gold); border-radius: 50%;
            border-top-color: transparent; animation: spin 1s linear infinite;
        }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

        /* 2. NAVIGATION OVERHAUL */
        .premium-nav {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background: rgba(10, 10, 10, 0.98); backdrop-filter: blur(25px);
            border-top: 1px solid rgba(255, 215, 0, 0.15);
            display: flex; justify-content: space-around; padding: 15px 0 30px 0;
            z-index: 9000;
        }
        .nav-item {
            display: flex; flex-direction: column; align-items: center;
            color: var(--text-gray); text-decoration: none; font-size: 10px;
            font-family: 'Orbitron'; font-weight: 900; transition: 0.3s;
        }
        .nav-item.active { color: var(--monk-gold); text-shadow: 0 0 15px var(--monk-gold-glow); }

        /* 3. CARD SYSTEM */
        #app-viewport {
            height: 100vh; overflow-y: auto; padding: 20px 20px 140px 20px;
            display: none;
        }
        .gold-card {
            background: var(--bg-card); border: 1px solid rgba(255, 215, 0, 0.08);
            border-radius: 18px; padding: 20px; margin-bottom: 18px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.8);
        }
        .stat-header { font-family: 'Orbitron'; font-size: 10px; color: var(--accent-gold); letter-spacing: 1px; }
        .stat-value { font-family: 'Orbitron'; font-size: 24px; font-weight: 900; color: #fff; }

        /* 4. ARENA UI */
        .arena-box {
            height: 180px; background: rgba(0,0,0,0.4); border-radius: 20px;
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 20px; border: 1px solid rgba(255,215,0,0.1);
            position: relative;
        }
        .btn-monk-prime {
            background: linear-gradient(135deg, #FFD700, #B8860B);
            border: none; color: #000; font-family: 'Orbitron';
            font-weight: 900; padding: 16px; border-radius: 12px;
            width: 100%; margin-bottom: 12px; box-shadow: 0 5px 20px rgba(255,215,0,0.2);
        }

        /* 5. HISTORY LIST */
        .hist-item {
            display: flex; justify-content: space-between; padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }
        .hist-reason { font-size: 12px; color: #eee; }
        .hist-pts { font-family: 'Orbitron'; font-size: 12px; font-weight: 900; }
        
        .view-section { display: none; }
        .view-section.active { display: block; animation: fadeIn 0.4s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

    <div id="splash-screen">
        <div class="monk-logo-container"><div class="monk-ring"></div></div>
        <div style="margin-top:20px; font-family:'Orbitron'; color:var(--monk-gold); letter-spacing:5px;">MONK CORE</div>
    </div>

    <div id="app-viewport">
        <div id="view-task" class="view-section active">
            <div class="d-flex justify-content-between mb-4">
                <div>
                    <div class="stat-header">OPERATIVE</div>
                    <div id="ui-username" style="font-family:'Orbitron'; font-size:18px;">---</div>
                </div>
                <div class="text-end">
                    <div id="ui-rank" class="badge" style="background:rgba(255,215,0,0.1); border:1px solid var(--monk-gold); color:var(--monk-gold);">Rank --</div>
                </div>
            </div>

            <div class="gold-card">
                <div class="stat-header">TOTAL CREDITS</div>
                <div class="stat-value" id="ui-points">0.00</div>
                <div class="progress mt-3" style="height:4px; background:#111;">
                    <div id="ui-progress" class="progress-bar" style="background:var(--monk-gold); width:0%;"></div>
                </div>
            </div>

            <div class="row g-2 mb-4">
                <div class="col-6">
                    <div class="gold-card text-center p-3">
                        <div class="stat-header">WAGER</div>
                        <div id="ui-wager" style="font-family:'Orbitron'; font-weight:900;">0.0</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="gold-card text-center p-3">
                        <div class="stat-header">STATUS</div>
                        <div style="color:var(--win-green); font-family:'Orbitron'; font-weight:900;">ELITE</div>
                    </div>
                </div>
            </div>

            <div class="stat-header mb-3">SYSTEM LOGS</div>
            <div id="ui-history"></div>
        </div>

        <div id="view-arena" class="view-section">
            <div class="arena-box">
                <div id="arena-display" style="font-size: 50px;">⛩️</div>
            </div>
            <div id="arena-status" class="text-center small mb-4" style="color:var(--accent-gold); font-family:'Orbitron';">READY FOR ACTION</div>
            <button class="btn-monk-prime" onclick="playGame('dice')">ROLL MONK DICE</button>
            <button class="btn-monk-prime" onclick="playGame('flip')">COIN SANCTUARY</button>
            <button class="btn-monk-prime" style="background:transparent; border:1px solid var(--monk-gold); color:var(--monk-gold);" onclick="playGame('spin')">FORTUNE WHEEL</button>
        </div>

        <div id="view-ranks" class="view-section">
            <h4 class="mb-4" style="font-family:'Orbitron'; color:var(--monk-gold);">GLOBAL LEADERS</h4>
            <div id="ui-leaderboard"></div>
        </div>

        <div id="view-team" class="view-section">
            <div id="team-setup">
                <div class="gold-card">
                    <div class="stat-header">CREATE SQUAD</div>
                    <input type="text" id="t-name" class="form-control bg-dark text-white border-secondary mt-2 mb-3" placeholder="Squad Name">
                    <button class="btn-monk-prime btn-sm" onclick="teamAction('create')">INITIATE</button>
                </div>
                <div class="gold-card">
                    <div class="stat-header">JOIN SQUAD</div>
                    <input type="text" id="t-code" class="form-control bg-dark text-white border-secondary mt-2 mb-3" placeholder="MONK-XXXXXX">
                    <button class="btn-monk-prime btn-sm" onclick="teamAction('join')">AUTHENTICATE</button>
                </div>
            </div>
            <div id="team-info" style="display:none;">
                <div class="gold-card text-center">
                    <h3 id="ui-team-name" style="color:var(--monk-gold); font-family:'Orbitron';">---</h3>
                    <code id="ui-team-code" class="text-muted">---</code>
                </div>
                <div id="ui-team-members"></div>
            </div>
        </div>
    </div>

    <nav class="premium-nav">
        <a href="#" class="nav-item active" onclick="switchTab('task', this)"><span>DASH</span></a>
        <a href="#" class="nav-item" onclick="switchTab('arena', this)"><span>ARENA</span></a>
        <a href="#" class="nav-item" onclick="switchTab('ranks', this)"><span>RANKS</span></a>
        <a href="#" class="nav-item" onclick="switchTab('team', this)"><span>TEAM</span></a>
    </nav>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        const UID = tg.initDataUnsafe?.user?.id || 12345;
        const UNAME = tg.initDataUnsafe?.user?.first_name || "Guest";

        setTimeout(() => {
            document.getElementById('splash-screen').style.display = 'none';
            document.getElementById('app-viewport').style.display = 'block';
            refreshAll();
        }, 2500);

        function switchTab(id, el) {
            document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('view-'+id).classList.add('active');
            el.classList.add('active');
            refreshAll();
        }

        async function refreshAll() {
            const r = await fetch(`/api/sync?id=${UID}&name=${encodeURIComponent(UNAME)}`);
            const d = await r.json();
            
            document.getElementById('ui-username').innerText = UNAME;
            document.getElementById('ui-points').innerText = d.points.toFixed(2);
            document.getElementById('ui-wager').innerText = d.wager.toFixed(1);
            document.getElementById('ui-rank').innerText = "#" + d.rank;
            document.getElementById('ui-progress').style.width = Math.min(d.points, 100) + "%";

            // History Mapping
            document.getElementById('ui-history').innerHTML = d.history.map(h => `
                <div class="hist-item">
                    <span class="hist-reason">${h.msg}</span>
                    <span class="hist-pts" style="color:${h.val > 0 ? 'var(--win-green)':'var(--loss-red)'}">${h.val > 0 ? '+':''}${h.val}</span>
                </div>
            `).join('');

            // Leaderboard
            if(d.lb) {
                document.getElementById('ui-leaderboard').innerHTML = d.lb.map((u, i) => `
                    <div class="hist-item">
                        <span>#${i+1} ${u.name}</span>
                        <span class="hist-pts" style="color:var(--monk-gold)">${u.pts}</span>
                    </div>
                `).join('');
            }
        }

        async function playGame(type) {
            const btn = event.target;
            btn.disabled = true;
            document.getElementById('arena-display').innerHTML = '🌀';
            
            const r = await fetch('/api/play', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: UID, game: type})
            });
            const d = await r.json();
            
            setTimeout(() => {
                document.getElementById('arena-display').innerHTML = d.win ? '💎' : '💀';
                document.getElementById('arena-status').innerText = d.win ? "WIN: " + d.amt : "LOSS: " + d.amt;
                btn.disabled = false;
                refreshAll();
            }, 800);
        }
    </script>
</body>
</html>
"""

# ================= API ENDPOINTS =================

@app.route('/api/sync')
def sync_data():
    uid = int(request.args.get('id', 0))
    name = request.args.get('name', 'User')
    
    # User Fetch/Create
    u = users_col.find_one_and_update(
        {"user_id": uid},
        {"$set": {"username": name}, "$setOnInsert": {"points": 50.0, "wager": 0.0, "team_code": None}},
        upsert=True, return_document=True
    )

    # Rank Calculation
    all_users = list(users_col.find().sort("points", -1))
    rank = next((i + 1 for i, x in enumerate(all_users) if x['user_id'] == uid), 99)
    
    # History
    hist = list(history_col.find({"user_id": uid}).sort("_id", -1).limit(8))
    
    # Leaderboard
    lb = [{"name": x['username'], "pts": x['points']} for x in all_users[:10]]

    return jsonify({
        "points": u['points'],
        "wager": u['wager'],
        "rank": rank,
        "lb": lb,
        "history": [{"msg": x['reason'], "val": x['points']} for x in hist]
    })

@app.route('/api/play', methods=['POST'])
def play():
    data = request.json
    uid = int(data['id'])
    u = users_col.find_one({"user_id": uid})
    
    if u['points'] < 5:
        return jsonify({"win": False, "amt": "Insufficient Points (Min 5)"})

    win = random.random() < 0.3 # 30% Chance
    amt = 10.0 if win else -5.0
    reason = "Arena Victory" if win else "Arena Defeat"
    
    users_col.update_one({"user_id": uid}, {"$inc": {"points": amt, "wager": 1.0 if win else 0}})
    history_col.insert_one({"user_id": uid, "reason": reason, "points": amt, "ts": datetime.now()})
    
    return jsonify({"win": win, "amt": amt})

# ================= TELEGRAM BOT (AIOGRAM 3.x) =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AdminFilter(BaseFilter):
    async def __call__(self, m: Message) -> bool:
        return m.from_user.id in ADMIN_IDS

@dp.message(CommandStart())
async def cmd_start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⛩️ ENTER ARENA", web_app=WebAppInfo(url=MINI_APP_URL))
    ]])
    welcome = (
        f"<b>Welcome, Operative {m.from_user.first_name}</b>\n\n"
        "Status: <code>Connected to Monk-Net</code>\n"
        "Access Level: <code>Premium Tier</code>\n\n"
        "Use the Mini App below to manage your credits and participate in the Arena."
    )
    await m.answer(welcome, reply_markup=kb, parse_mode="HTML")

@dp.message(Command("add"), AdminFilter())
async def cmd_add(m: Message):
    """Usage: /add <user_id> <points> <reason>"""
    try:
        args = m.text.split(maxsplit=3)
        target_id = int(args[1])
        pts = float(args[2])
        reason = args[3] if len(args) > 3 else "Admin Adjustment"

        res = users_col.update_one(
            {"user_id": target_id}, 
            {"$inc": {"points": pts}}, 
            upsert=True
        )
        
        history_col.insert_one({
            "user_id": target_id,
            "reason": f"🎁 {reason}",
            "points": pts,
            "ts": datetime.now()
        })

        await m.reply(f"✅ <b>Successfully processed:</b>\nID: <code>{target_id}</code>\nAmt: <code>{pts}</code>")
        try:
            await bot.send_message(target_id, f"🎁 <b>Wallet Updated!</b>\nAmount: +{pts}\nReason: {reason}")
        except:
            pass
    except Exception as e:
        await m.reply(f"❌ Error: {e}\nFormat: `/add ID PTS REASON`")

# ================= SERVICE ORCHESTRATION =================
def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Web Services Hosted.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Offline.")
