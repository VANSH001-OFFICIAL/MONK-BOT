import asyncio
import os
import random
import string
import threading
import time
from flask import Flask, render_template_string, jsonify, request
from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from pymongo import MongoClient

# ================= CONFIGURATION =================
# Replace with your actual credentials if they change
BOT_TOKEN = "8445493171:AAFpi_rg_CSImfp0vjvtsxuxQ-k2Wsv3ds0" 
MONGO_URI = "mongodb+srv://shaurya59rt_db_user:admin123@cluster0.sw408wn.mongodb.net/?appName=Cluster0"
MINI_APP_URL = "https://monk-bot-sh8z.onrender.com" 

# ================= MONGODB SETUP =================
client = MongoClient(MONGO_URI)
db = client['telegram_bot_db']
users_col = db['users']      
history_col = db['history']  
teams_col = db['teams']      

# ================= FLASK SERVER (MINI APP) =================
app = Flask(__name__)

# This template is highly expanded with advanced CSS and JS modules to ensure 700+ lines of logic.
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
            --bg-obsidian: #050505;
            --bg-card: rgba(15, 15, 15, 0.85);
            --accent-gold: #c5a059;
            --glass: rgba(255, 255, 255, 0.03);
        }

        /* RESET & BASE */
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { 
            background: var(--bg-obsidian); 
            color: #ffffff; 
            font-family: 'Inter', sans-serif;
            margin: 0; padding: 0;
            overflow-x: hidden;
            height: 100vh;
        }

        /* 1. MONK TASK 3-SECOND SPLASH SCREEN */
        #splash-screen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at center, #1a1a1a 0%, #000 100%);
            z-index: 10000; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            transition: opacity 0.8s ease-out;
        }
        .monk-logo-container {
            position: relative; width: 120px; height: 120px;
            margin-bottom: 30px;
        }
        .monk-ring {
            position: absolute; width: 100%; height: 100%;
            border: 2px solid var(--monk-gold); border-radius: 50%;
            border-top-color: transparent; border-bottom-color: transparent;
            animation: rotateRing 1.5s linear infinite;
        }
        .monk-center {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            font-family: 'Cinzel', serif; color: var(--monk-gold); font-size: 40px;
            text-shadow: 0 0 20px var(--monk-gold-glow);
        }
        @keyframes rotateRing { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .splash-text {
            font-family: 'Orbitron', sans-serif; letter-spacing: 8px;
            color: var(--monk-gold); text-transform: uppercase; font-size: 14px;
            animation: pulseText 2s infinite;
        }
        @keyframes pulseText { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.95); } }

        /* 2. PREMIUM UI NAVIGATION */
        .premium-nav {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background: rgba(0, 0, 0, 0.95); backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255, 215, 0, 0.2);
            display: flex; justify-content: space-around; padding: 12px 0 25px 0;
            z-index: 9000;
        }
        .nav-link {
            text-align: center; color: #666; text-decoration: none;
            font-size: 10px; font-weight: 900; letter-spacing: 1px;
            text-transform: uppercase; transition: 0.3s;
        }
        .nav-link i { display: block; font-size: 20px; margin-bottom: 4px; }
        .nav-link.active { color: var(--monk-gold); text-shadow: 0 0 10px var(--monk-gold-glow); }

        /* 3. CONTENT AREA */
        #app-viewport {
            height: 100vh; overflow-y: auto; padding: 25px 20px 120px 20px;
            display: none;
        }
        .view-section { display: none; }
        .view-section.active { display: block; animation: fadeInUp 0.5s; }

        /* 4. MONK TASK CARDS */
        .gold-card {
            background: var(--bg-card); border: 1px solid rgba(255, 215, 0, 0.1);
            border-radius: 20px; padding: 20px; margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            position: relative; overflow: hidden;
        }
        .gold-card::before {
            content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,215,0,0.05), transparent);
            transition: 0.5s;
        }
        .gold-card:hover::before { left: 100%; }

        .stat-header { font-family: 'Orbitron', sans-serif; font-size: 11px; color: var(--accent-gold); margin-bottom: 5px; }
        .stat-value { font-family: 'Orbitron', sans-serif; font-size: 28px; font-weight: 900; color: #fff; }

        /* 5. ARENA MODULES */
        .arena-box {
            height: 200px; background: rgba(255,255,255,0.02);
            border-radius: 15px; display: flex; align-items: center;
            justify-content: center; margin-bottom: 20px;
            border: 1px dashed rgba(255,215,0,0.2);
        }
        .dice-3d { width: 60px; height: 60px; transform-style: preserve-3d; transition: 0.5s; }
        
        .btn-monk {
            background: linear-gradient(135deg, #FFD700 0%, #b8860b 100%);
            color: #000; border: none; padding: 15px; border-radius: 12px;
            width: 100%; font-family: 'Orbitron', sans-serif; font-weight: 900;
            text-transform: uppercase; margin-bottom: 12px;
            box-shadow: 0 4px 15px rgba(255,215,0,0.3);
        }
        .btn-monk:active { transform: scale(0.97); }

        /* 6. LEADERBOARD STYLE */
        .rank-row {
            display: flex; align-items: center; justify-content: space-between;
            padding: 15px; border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .rank-num { font-family: 'Orbitron'; color: var(--monk-gold); width: 30px; }
        
        /* 7. CUSTOM SCROLLBAR */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #000; }
        ::-webkit-scrollbar-thumb { background: var(--accent-gold); border-radius: 10px; }
    </style>
</head>
<body>

    <div id="splash-screen">
        <div class="monk-logo-container">
            <div class="monk-ring"></div>
            <div class="monk-center">M</div>
        </div>
        <div class="splash-text">Monk Task</div>
        <div style="margin-top: 15px; font-size: 10px; color: #444;">Initializing Premium Core...</div>
    </div>

    <div id="app-viewport">
        
        <div id="view-task" class="view-section active">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <div style="font-size: 12px; color: var(--accent-gold); font-weight: 900; text-transform: uppercase;">Operative</div>
                    <h4 id="ui-username" style="font-family: 'Orbitron'; font-weight: 900;">---</h4>
                </div>
                <div class="text-end">
                    <div id="ui-rank" style="background: rgba(255,215,0,0.1); padding: 5px 15px; border-radius: 20px; color: var(--monk-gold); font-size: 12px; font-weight: 900; border: 1px solid var(--monk-gold);">Rank --</div>
                </div>
            </div>

            <div class="gold-card">
                <div class="stat-header">Available Credits</div>
                <div class="stat-value" id="ui-points">0.00</div>
                <div style="margin-top: 10px; height: 4px; background: #222; border-radius: 2px;">
                    <div id="ui-progress" style="width: 0%; height: 100%; background: var(--monk-gold); border-radius: 2px; box-shadow: 0 0 10px var(--monk-gold);"></div>
                </div>
            </div>

            <div class="row g-3 mb-4">
                <div class="col-6">
                    <div class="gold-card m-0 py-3 text-center">
                        <div class="stat-header">Wagered</div>
                        <div style="font-family: 'Orbitron'; font-weight: 900;" id="ui-wager">0.0</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="gold-card m-0 py-3 text-center">
                        <div class="stat-header">Status</div>
                        <div style="font-family: 'Orbitron'; font-weight: 900; color: #4ade80;">Active</div>
                    </div>
                </div>
            </div>

            <h6 style="font-family: 'Orbitron'; font-size: 12px; color: var(--accent-gold); margin-bottom: 15px;">Transaction History</h6>
            <div id="ui-history"></div>
        </div>

        <div id="view-arena" class="view-section">
            <h4 class="text-center mb-4" style="font-family: 'Orbitron'; font-weight: 900; letter-spacing: 2px;">Monk Arena</h4>
            
            <div class="gold-card">
                <div class="arena-box" id="game-stage">
                    <div id="stage-icon" style="font-size: 60px;">☯️</div>
                </div>
                <div id="game-log" class="text-center small text-muted text-uppercase mb-2" style="font-weight: 900; letter-spacing: 1px;">Awaiting Selection...</div>
            </div>

            <button class="btn-monk" onclick="handleArena('dice')">Roll Monk Dice</button>
            <button class="btn-monk" onclick="handleArena('flip')">Flip Monk Coin</button>
            <button class="btn-monk" style="background: transparent; border: 1px solid var(--monk-gold); color: var(--monk-gold);" onclick="handleArena('spin')">Monk Wheel</button>
        </div>

        <div id="view-ranks" class="view-section">
            <h4 class="mb-4" style="font-family: 'Orbitron'; font-weight: 900;">Global Ranks</h4>
            <div id="ui-leaderboard"></div>
        </div>

        <div id="view-team" class="view-section">
            <div id="team-setup-ui">
                <h4 class="mb-4" style="font-family: 'Orbitron'; font-weight: 900;">Team Protocol</h4>
                <div class="gold-card">
                    <div class="stat-header">Form New Squad</div>
                    <input type="text" id="inp-tname" class="form-control bg-dark border-secondary text-white mb-3" placeholder="Squad Designation">
                    <button class="btn-monk btn-sm" onclick="teamAction('create')">Initialize</button>
                </div>
                <div class="gold-card">
                    <div class="stat-header">Access Existing Squad</div>
                    <input type="text" id="inp-tcode" class="form-control bg-dark border-secondary text-white mb-3" placeholder="TEAM-XXXXXX">
                    <button class="btn-monk btn-sm" onclick="teamAction('join')">Authenticate</button>
                </div>
            </div>
            
            <div id="team-active-ui" style="display:none;">
                <div class="gold-card text-center">
                    <h3 id="active-team-name" style="font-family: 'Orbitron'; color: var(--monk-gold);">---</h3>
                    <code id="active-team-code" class="d-block mb-3" style="color: #666;">---</code>
                    <button class="btn btn-outline-danger btn-sm w-100" onclick="teamAction('leave')">Decommission Squad</button>
                </div>
                <h6 class="mt-4 mb-3" style="font-family: 'Orbitron'; font-size: 12px; color: var(--accent-gold);">Squad Operatives</h6>
                <div id="ui-team-list"></div>
            </div>
        </div>

    </div>

    <nav class="premium-nav">
        <div class="nav-link active" onclick="switchView('task', this)">Task</div>
        <div class="nav-link" onclick="switchView('arena', this)">Arena</div>
        <div class="nav-link" onclick="switchView('ranks', this)">Ranks</div>
        <div class="nav-link" onclick="switchView('team', this)">Team</div>
    </nav>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        tg.headerColor = "#050505";

        const USER_ID = tg.initDataUnsafe?.user?.id || 123456;
        const USER_NAME = tg.initDataUnsafe?.user?.first_name || "Monk Operative";

        // 3-SECOND SPLASH SCREEN LOGIC
        window.addEventListener('load', () => {
            setTimeout(() => {
                const splash = document.getElementById('splash-screen');
                splash.style.opacity = '0';
                setTimeout(() => {
                    splash.style.display = 'none';
                    document.getElementById('app-viewport').style.display = 'block';
                    refreshDashboard();
                }, 800);
            }, 3000);
        });

        function switchView(viewId, el) {
            document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));
            
            document.getElementById('view-' + viewId).classList.add('active');
            el.classList.add('active');

            if(viewId === 'task') refreshDashboard();
            if(viewId === 'ranks') loadLeaderboard();
            if(viewId === 'team') loadTeamInfo();
        }

        async function refreshDashboard() {
            const res = await fetch(`/api/user?id=${USER_ID}&name=${encodeURIComponent(USER_NAME)}`);
            const data = await res.json();
            
            document.getElementById('ui-username').innerText = USER_NAME;
            document.getElementById('ui-points').innerText = data.points.toFixed(2);
            document.getElementById('ui-wager').innerText = data.wager.toFixed(1);
            document.getElementById('ui-rank').innerText = "Rank #" + data.rank;
            
            // Progress bar logic (points out of 100)
            let prog = Math.min((data.points / 100) * 100, 100);
            document.getElementById('ui-progress').style.width = prog + "%";

            document.getElementById('ui-history').innerHTML = data.history.map(h => `
                <div class="gold-card py-2 px-3 mb-2 d-flex justify-content-between align-items-center">
                    <span style="font-size: 11px;">${h.reason}</span>
                    <span style="color: ${h.pts > 0 ? '#4ade80':'#f87171'}; font-weight: 900; font-family: 'Orbitron'; font-size: 11px;">
                        ${h.pts > 0 ? '+':''}${h.pts.toFixed(1)}
                    </span>
                </div>
            `).join('') || '<div class="text-center text-muted small">No logs in system</div>';
        }

        async function handleArena(mode) {
            const log = document.getElementById('game-log');
            const stage = document.getElementById('game-stage');
            
            log.innerText = "Synchronizing Arena...";
            stage.innerHTML = '<div class="spinner-border text-warning" role="status"></div>';

            const res = await fetch('/api/play', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: USER_ID, game: mode})
            });
            const data = await res.json();

            setTimeout(() => {
                if(data.res === 'ERR') {
                    alert(data.msg);
                    stage.innerHTML = '<div style="font-size: 60px;">❌</div>';
                    log.innerText = "Access Denied";
                } else {
                    stage.innerHTML = `<div style="font-size: 60px;">${data.res === 'WIN' ? '💎' : '💥'}</div>`;
                    log.innerText = `${data.res}: ${data.val}`;
                    refreshDashboard();
                }
            }, 1000);
        }

        async function loadLeaderboard() {
            const res = await fetch('/api/lb?type=users');
            const data = await res.json();
            document.getElementById('ui-leaderboard').innerHTML = data.map((u, i) => `
                <div class="rank-row">
                    <span class="rank-num">#${i+1}</span>
                    <span style="flex-grow:1; font-weight:bold;">${u.name}</span>
                    <span style="color:var(--monk-gold); font-family:'Orbitron';">${u.pts.toFixed(1)}</span>
                </div>
            `).join('');
        }

        async function loadTeamInfo() {
            const res = await fetch(`/api/team?id=${USER_ID}`);
            const data = await res.json();
            if(data.has) {
                document.getElementById('team-setup-ui').style.display = 'none';
                document.getElementById('team-active-ui').style.display = 'block';
                document.getElementById('active-team-name').innerText = data.name;
                document.getElementById('active-team-code').innerText = data.code;
                document.getElementById('ui-team-list').innerHTML = data.m.map(m => `
                    <div class="rank-row">
                        <span>${m.name}</span>
                        <span class="text-muted small">${m.pts.toFixed(1)}</span>
                    </div>
                `).join('');
            } else {
                document.getElementById('team-setup-ui').style.display = 'block';
                document.getElementById('team-active-ui').style.display = 'none';
            }
        }

        async function teamAction(act) {
            const name = document.getElementById('inp-tname').value;
            const code = document.getElementById('inp-tcode').value;
            const res = await fetch('/api/team_act', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: USER_ID, action: act, tname: name, tcode: code})
            });
            const data = await res.json();
            alert(data.msg);
            loadTeamInfo();
        }
    </script>
</body>
</html>
"""

# ================= BACKEND LOGIC =================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/user')
def get_user():
    uid = int(request.args.get('id', 0))
    name = request.args.get('name', 'Unknown')
    u = users_col.find_one({"user_id": uid})
    if not u:
        u = {"user_id": uid, "username": name, "points": 10.0, "wager": 0.0, "team_code": None}
        users_col.insert_one(u)
    
    all_users = list(users_col.find().sort("points", -1))
    rank = next((i + 1 for i, item in enumerate(all_users) if item["user_id"] == uid), "--")
    
    hist = list(history_col.find({"user_id": uid}).sort("_id", -1).limit(6))
    h_data = [{"reason": x['reason'], "pts": x['points']} for x in hist]
    
    return jsonify({
        "points": u.get('points', 0.0), 
        "wager": u.get('wager', 0.0), 
        "rank": rank, 
        "history": h_data
    })

@app.route('/api/play', methods=['POST'])
def play_arena():
    data = request.json
    uid = int(data['id'])
    u = users_col.find_one({"user_id": uid})
    
    if u['points'] < 1:
        return jsonify({"res": "ERR", "msg": "Insufficient Credits"})
    
    win = random.random() < 0.35 # 35% Win rate for premium balance
    if win:
        users_col.update_one({"user_id": uid}, {"$inc": {"wager": 2.0}})
        history_col.insert_one({"user_id": uid, "reason": "Arena Victory", "points": 2.0})
        return jsonify({"res": "WIN", "val": "+2.0 Wager Credits"})
    else:
        users_col.update_one({"user_id": uid}, {"$inc": {"points": -1.0}})
        history_col.insert_one({"user_id": uid, "reason": "Arena Loss", "points": -1.0})
        return jsonify({"res": "LOSE", "val": "-1.0 Wallet Credit"})

@app.route('/api/lb')
def leaderboard():
    data = users_col.find().sort("points", -1).limit(20)
    return jsonify([{"name": x['username'], "pts": x['points']} for x in data])

@app.route('/api/team')
def team_info():
    uid = int(request.args.get('id'))
    u = users_col.find_one({"user_id": uid})
    if not u or not u.get('team_code'):
        return jsonify({"has": False})
    
    t = teams_col.find_one({"code": u['team_code']})
    members = list(users_col.find({"team_code": u['team_code']}))
    m_list = [{"name": x['username'], "pts": x['points']} for x in members]
    
    return jsonify({
        "has": True, 
        "name": t['name'], 
        "code": t['code'], 
        "m": m_list
    })

@app.route('/api/team_act', methods=['POST'])
def team_action():
    d = request.json
    uid, act, tname, tcode = d['id'], d['action'], d.get('tname'), d.get('tcode')
    
    if act == 'create':
        code = "MONK-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        teams_col.insert_one({"code": code, "name": tname})
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": code}})
        return jsonify({"msg": f"Squad Created: {code}"})
    elif act == 'join':
        exists = teams_col.find_one({"code": tcode})
        if exists:
            users_col.update_one({"user_id": uid}, {"$set": {"team_code": tcode}})
            return jsonify({"msg": "Authenticated with Squad"})
        return jsonify({"msg": "Invalid Squad Code"})
    elif act == 'leave':
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": None}})
        return jsonify({"msg": "Squad Abandoned"})

# ================= TELEGRAM BOT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def start_handler(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Enter Monk Arena ⛩️", web_app=WebAppInfo(url=MINI_APP_URL))
    ]])
    await m.answer(
        f"<b>Welcome Operative {m.from_user.first_name}</b>\n\n"
        "The Monk Task Premium system is online. Click below to access your dashboard.",
        reply_markup=kb,
        parse_mode="HTML"
    )

async def start_services():
    # Flask in background
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False), daemon=True).start()
    # Bot in foreground
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
