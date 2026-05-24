import asyncio
import os
import random
import string
import threading
from flask import Flask, render_template_string, jsonify, request
from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from pymongo import MongoClient

# ================= CONFIGURATION =================
BOT_TOKEN = "8445493171:AAFpi_rg_CSImfp0vjvtsxuxQ-k2Wsv3ds0" 
MONGO_URI = "mongodb+srv://shaurya59rt_db_user:admin123@cluster0.sw408wn.mongodb.net/?appName=Cluster0"
MINI_APP_URL = "https://monk-bot-sh8z.onrender.com" 

# ================= MONGODB SETUP =================
client = MongoClient(MONGO_URI)
db = client['telegram_bot_db']

users_col = db['users']      # Attributes: user_id, username, points, wager, team_code
history_col = db['history']  # System event logs
teams_col = db['teams']      # Attributes: code, name, creator_id

# ================= FLASK SERVER (MINI APP) =================
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monkxz Premium Mini App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg-dark: #090d16;
            --card-bg: rgba(30, 41, 59, 0.4);
            --neon-blue: #38bdf8;
            --neon-purple: #a855f7;
            --neon-green: #22c55e;
            --text-main: #f8fafc;
        }
        body { 
            background: var(--bg-dark); 
            color: var(--text-main); 
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            padding-bottom: 90px;
            overflow-x: hidden;
        }
        /* Top Cyber Bar */
        .header-bar {
            background: linear-gradient(90deg, var(--neon-blue), var(--neon-purple));
            height: 4px;
            width: 100%;
        }
        /* Premium Navigation Layout */
        .nav-bottom { 
            position: fixed; bottom: 0; left: 0; right: 0; 
            background: rgba(15, 23, 42, 0.95); 
            backdrop-filter: blur(10px);
            display: flex; padding: 12px 0; 
            border-top: 1px solid rgba(255, 255, 255, 0.1); 
            box-shadow: 0 -10px 25px rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }
        .nav-item { 
            color: #64748b; text-align: center; flex: 1; 
            font-size: 10px; font-weight: 700; cursor: pointer; 
            letter-spacing: 1px; transition: all 0.3s ease;
        }
        .nav-item.active { 
            color: var(--neon-blue); 
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.6);
            transform: translateY(-2px);
        }
        .app-page { display: none; padding: 20px; animation: fadeIn 0.4s ease-in-out; }
        .app-page.active { display: block; }
        
        /* Glassmorphic Neon Cards */
        .card-custom { 
            background: var(--card-bg); 
            backdrop-filter: blur(8px);
            border-radius: 16px; padding: 18px; margin-bottom: 15px; 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        .stat-val { font-size: 26px; font-weight: 800; margin-top: 5px; }
        
        /* Buttons Ecosystem */
        .btn-game { 
            width: 100%; margin-bottom: 12px; padding: 14px; 
            font-weight: 800; border-radius: 12px; border: none;
            text-transform: uppercase; letter-spacing: 1px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn-game:active { transform: scale(0.98); }
        .btn-dice { background: linear-gradient(135deg, #ef4444, #b91c1c); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }
        .btn-spin { background: linear-gradient(135deg, #f59e0b, #b45309); box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3); }
        .btn-flip { background: linear-gradient(135deg, #06b6d4, #0891b2); box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3); }
        
        /* Animations Mechanics */
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes diceShake {
            0% { transform: rotate(0deg) scale(1); }
            20% { transform: rotate(-15deg) scale(1.1); }
            40% { transform: rotate(15deg) scale(1.1); }
            60% { transform: rotate(-15deg) scale(1.1); }
            80% { transform: rotate(15deg) scale(1.1); }
            100% { transform: rotate(0deg) scale(1); }
        }
        @keyframes wheelSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(1440deg); }
        }
        
        .anim-dice { animation: diceShake 0.6s ease-in-out infinite; }
        .anim-wheel { animation: wheelSpin 1s cubic-bezier(0.1, 0.8, 0.3, 1) infinite; }
        
        .visual-container {
            height: 100px; display: flex; align-items: center; justify-content: center; margin-bottom: 15px;
        }
        .dice-element { font-size: 60px; }
        .wheel-element { font-size: 60px; transition: transform 2s ease-out; }
        .coin-element { font-size: 60px; transition: all 0.5s ease; }
        
        .form-control-cyber {
            background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1);
            color: white; border-radius: 10px; padding: 12px;
        }
        .form-control-cyber:focus {
            background: rgba(15, 23, 42, 0.8); border-color: var(--neon-blue); box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); color: white;
        }
    </style>
</head>
<body>
    <div class="header-bar"></div>

    <!-- 1. DASHBOARD PAGE -->
    <div id="page-dashboard" class="app-page active">
        <h4 class="mb-4">⚡ Welcome, <span id="user-name" class="text-info">Player</span></h4>
        <div class="row g-3 mb-3">
            <div class="col-6">
                <div class="card-custom text-center" style="border-bottom: 3px solid var(--neon-blue);">
                    <h6 class="text-muted small">Wallet Points</h6>
                    <div id="stat-points" class="stat-val text-info">0</div>
                </div>
            </div>
            <div class="col-6">
                <div class="card-custom text-center" style="border-bottom: 3px solid var(--neon-purple);">
                    <h6 class="text-muted small">Wager Points</h6>
                    <div id="stat-wager" class="stat-val text-purple" style="color: #a855f7;">0</div>
                </div>
            </div>
        </div>
        <div class="card-custom d-flex justify-content-between align-items-center">
            <span class="text-muted">Global Ranking Tier</span>
            <span id="stat-rank" class="badge bg-success fs-6">--</span>
        </div>
        <h6 class="mt-4 mb-2 text-muted uppercase tracking-wider small">Recent Performance History</h6>
        <div id="history-list" class="list-group"></div>
    </div>

    <!-- 2. LEADERBOARD PAGE -->
    <div id="page-leaderboard" class="app-page">
        <h4 class="mb-4">🏆 Hall of Fame</h4>
        <div class="btn-group w-100 mb-4 shadow">
            <button id="lbl-users" class="btn btn-sm btn-outline-info active" onclick="loadLB('users')">Top Hunters</button>
            <button id="lbl-teams" class="btn btn-sm btn-outline-info" onclick="loadLB('teams')">Top Squads</button>
        </div>
        <div id="lb-list" class="list-group shadow"></div>
    </div>

    <!-- 3. GAMES PAGE -->
    <div id="page-games" class="app-page text-center">
        <h4 class="mb-2">🎲 Nexus Arena</h4>
        <p class="small text-muted mb-4">Risk: 1 Point | Dynamic Reward: +2 Wager</p>
        
        <!-- Interactive Asset Render Base -->
        <div class="card-custom visual-container">
            <div id="visual-asset">🎯</div>
        </div>
        <div id="game-res" class="mb-4 fw-bold fs-5">Choose your game mode below</div>

        <button class="btn-game btn-dice text-white" onclick="triggerPlay('dice')">Roll Cyber Dice</button>
        <button class="btn-game btn-spin text-white" onclick="triggerPlay('spin')">Spin Quantum Wheel</button>
        <button class="btn-game btn-flip text-white" onclick="triggerPlay('flip')">Flip Neon Coin</button>
    </div>

    <!-- 4. TEAM PAGE -->
    <div id="page-team" class="app-page">
        <!-- Input Block UI -->
        <div id="team-join-ui">
            <h4 class="mb-4">🛡️ Faction System</h4>
            <div class="card-custom">
                <h6>Create New Faction</h6>
                <p class="small text-muted">Bina name ke team nahi banegi</p>
                <input type="text" id="t-name" class="form-control form-control-cyber mb-3" placeholder="Enter Unique Team Name">
                <button class="btn btn-info w-100 fw-bold" onclick="teamAct('create')">Initialize Faction</button>
            </div>
            <div class="text-center my-3 text-muted">OR</div>
            <div class="card-custom">
                <h6>Join via Secure Access Code</h6>
                <input type="text" id="t-code" class="form-control form-control-cyber mb-3" placeholder="Format: TEAM-XXXXXX">
                <button class="btn btn-purple w-100 text-white fw-bold" style="background:#a855f7;" onclick="teamAct('join')">Authenticate & Join</button>
            </div>
        </div>
        <!-- Profile Dashboard UI -->
        <div id="team-info-ui" style="display:none;">
            <div class="card-custom text-center" style="border: 1px solid var(--neon-blue);">
                <h3 id="cur-team-name" class="text-info fw-bold"></h3>
                <div class="badge bg-dark border border-warning text-warning my-2 p-2 fs-6">
                    🔑 Access Code: <span id="cur-team-code" class="fw-bold"></span>
                </div>
                <h5 id="cur-team-pts" class="text-success mt-2"></h5>
                <button class="btn btn-sm btn-outline-danger mt-3 px-4" onclick="teamAct('leave')">Leave Current Faction</button>
            </div>
            <h6 class="text-muted mt-4 mb-2">Squad Composition</h6>
            <div id="team-m-list" class="list-group"></div>
        </div>
    </div>

    <!-- PREMIUM BOTTOM NAVIGATION -->
    <div class="nav-bottom">
        <div id="nv-dashboard" class="nav-item active" onclick="showP('dashboard')">DASHBOARD</div>
        <div id="nv-leaderboard" class="nav-item" onclick="showP('leaderboard')">LEADERBOARD</div>
        <div id="nv-games" class="nav-item" onclick="showP('games')">GAMES</div>
        <div id="nv-team" class="nav-item" onclick="showP('team')">FACTION</div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        
        const uid = tg.initDataUnsafe?.user?.id || 99999;
        const uname = tg.initDataUnsafe?.user?.first_name || "Beta Tester";
        document.getElementById('user-name').innerText = uname;

        let lockGame = false;

        function showP(p) {
            document.querySelectorAll('.app-page').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            
            document.getElementById('page-'+p).classList.add('active');
            document.getElementById('nv-'+p).classList.add('active');
            
            if(p === 'dashboard') loadDash();
            if(p === 'leaderboard') loadLB('users');
            if(p === 'team') loadTeam();
        }

        function loadDash() {
            fetch(`/api/user?id=${uid}&name=${encodeURIComponent(uname)}`).then(r=>r.json()).then(d=>{
                document.getElementById('stat-points').innerText = d.points;
                document.getElementById('stat-wager').innerText = d.wager;
                document.getElementById('stat-rank').innerText = d.rank;
                let h = document.getElementById('history-list');
                if(!d.history || d.history.length === 0){
                    h.innerHTML = '<div class="text-center text-muted py-3 card-custom">No transaction records found</div>';
                } else {
                    h.innerHTML = d.history.map(x => {
                        let isLoss = x.pts < 0;
                        return `<div class="list-group-item bg-transparent text-white border-secondary d-flex justify-content-between align-items-center">
                            <span>${x.reason}</span>
                            <span class="${isLoss ? 'text-danger':'text-success'} fw-bold">${isLoss ? '':'+'}${x.pts}</span>
                        </div>`;
                    }).join('');
                }
            });
        }

        function loadLB(type) {
            document.getElementById('lbl-users').classList.toggle('active', type === 'users');
            document.getElementById('lbl-teams').classList.toggle('active', type === 'teams');
            
            fetch(`/api/lb?type=${type}`).then(r=>r.json()).then(d=>{
                let l = document.getElementById('lb-list');
                if(!d || d.length === 0){
                    l.innerHTML = '<div class="text-center text-muted py-3 card-custom">No ranks evaluated yet</div>';
                } else {
                    l.innerHTML = d.map((x,i) => `<div class="list-group-item bg-transparent text-white border-secondary d-flex justify-content-between">
                        <span>#${i+1} ${x.name}</span>
                        <span class="text-info fw-bold">${x.pts} Pts</span>
                    </div>`).join('');
                }
            });
        }

        function loadTeam() {
            fetch(`/api/team?id=${uid}`).then(r=>r.json()).then(d=>{
                if(d.has) {
                    document.getElementById('team-join-ui').style.display = 'none';
                    document.getElementById('team-info-ui').style.display = 'block';
                    document.getElementById('cur-team-name').innerText = d.name;
                    document.getElementById('cur-team-code').innerText = d.code;
                    document.getElementById('cur-team-pts').innerText = "Faction Total: " + d.total + " Points";
                    document.getElementById('team-m-list').innerHTML = d.m.map(x => `<div class="list-group-item bg-transparent text-white border-secondary d-flex justify-content-between">
                        <span>${x.name}</span><span class="text-warning">${x.pts} Pts</span>
                    </div>`).join('');
                } else {
                    document.getElementById('team-join-ui').style.display = 'block';
                    document.getElementById('team-info-ui').style.display = 'none';
                }
            });
        }

        function teamAct(act) {
            let n = document.getElementById('t-name').value.trim();
            let c = document.getElementById('t-code').value.trim();
            
            if(act === 'create' && !n) {
                alert("🔴 Faction initialization rejected: Team Name cannot be empty!");
                return;
            }
            if(act === 'join' && !c) {
                alert("🔴 Access code missing!");
                return;
            }
            
            fetch('/api/team_act', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({id:uid, name:uname, action:act, tname:n, tcode:c})
            }).then(r=>r.json()).then(res=>{ 
                alert(res.msg); 
                loadTeam(); 
            });
        }

        function triggerPlay(mode) {
            if(lockGame) return;
            lockGame = true;
            
            let asset = document.getElementById('visual-asset');
            let resDiv = document.getElementById('game-res');
            resDiv.innerText = "Processing transactional hash...";
            resDiv.className = "mb-4 text-warning fw-bold fs-5";

            // Inject Live Custom Animations
            if(mode === 'dice') {
                asset.className = "dice-element anim-dice";
                asset.innerText = "🎲";
            } else if(mode === 'spin') {
                asset.className = "wheel-element anim-wheel";
                asset.innerText = "🎡";
            } else if(mode === 'flip') {
                asset.className = "coin-element";
                asset.style.transform = "scaleX(0)";
                setTimeout(() => asset.style.transform = "scaleX(1)", 200);
                asset.innerText = "🪙";
            }

            setTimeout(() => {
                fetch('/api/play', {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({id:uid, game:mode})
                }).then(r=>r.json()).then(d=>{
                    asset.className = ""; 
                    lockGame = false;
                    
                    if(d.res === 'WIN') {
                        if(mode==='dice') asset.innerText = ["⚃","⚄","⚅"][Math.floor(Math.random()*3)];
                        if(mode==='spin') asset.innerText = "💎";
                        if(mode==='flip') asset.innerText = "👑";
                        resDiv.innerText = "🎉 TRANSACTION SUCCESS! +2 Wager Added";
                        resDiv.className = "mb-4 text-success fw-bold fs-5";
                    } else if(d.res === 'LOSE') {
                        if(mode==='dice') asset.innerText = ["⚀","⚁","⚂"][Math.floor(Math.random()*3)];
                        if(mode==='spin') asset.innerText = "💥";
                        if(mode==='flip') asset.innerText = "❌";
                        resDiv.innerText = "⚡ ANOMALY DETECTED! -1 Wallet Point";
                        resDiv.className = "mb-4 text-danger fw-bold fs-5";
                    } else {
                        asset.innerText = "🎯";
                        resDiv.innerText = "System status: Idle";
                        alert(d.msg);
                    }
                });
            }, 1200); // Animation window duration latency
        }
        
        loadDash();
    </script>
</body>
</html>
"""

# ================= API ENDPOINTS CONFIGURATION =================

@app.route('/')
def home(): 
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/user')
def get_user():
    uid = int(request.args.get('id'))
    name = request.args.get('name')
    u = users_col.find_one({"user_id": uid})
    if not u:
        u = {"user_id": uid, "username": name, "points": 0.0, "wager": 0.0, "team_code": None}
        users_col.insert_one(u)
    else:
        users_col.update_one({"user_id": uid}, {"$set": {"username": name}})
        
    all_u = list(users_col.find().sort("points", -1))
    rank = next((i + 1 for i, item in enumerate(all_u) if item["user_id"] == uid), "--")
    
    hist = list(history_col.find({"user_id": uid}).sort("_id", -1).limit(5))
    h_data = [{"reason": x['reason'], "pts": x['points']} for x in hist]
    return jsonify({"points": u['points'], "wager": u['wager'], "rank": rank, "history": h_data})

@app.route('/api/lb')
def get_lb():
    t = request.args.get('type')
    if t == 'users':
        data = users_col.find().sort("points", -1).limit(20)
        return jsonify([{"name": x['username'], "pts": x['points']} for x in data])
    else:
        pipeline = [
            {"$match": {"team_code": {"$ne": None}}},
            {"$group": {"_id": "$team_code", "total": {"$sum": "$points"}}},
            {"$sort": {"total": -1}}
        ]
        aggregated = list(users_col.aggregate(pipeline))
        lbs = []
        for x in aggregated:
            t_meta = teams_col.find_one({"code": x['_id']})
            t_display_name = t_meta['name'] if t_meta else f"Code: {x['_id']}"
            lbs.append({"name": t_display_name, "pts": x['total']})
        return jsonify(lbs)

@app.route('/api/team')
def get_team():
    uid = int(request.args.get('id'))
    u = users_col.find_one({"user_id": uid})
    if not u or not u.get('team_code'): 
        return jsonify({"has": False})
    
    tcode = u['team_code']
    t_meta = teams_col.find_one({"code": tcode})
    tname = t_meta['name'] if t_meta else "Unknown Faction"
    
    members = list(users_col.find({"team_code": tcode}))
    m_data = [{"name": x['username'], "pts": x['points']} for x in members]
    total = sum(x['points'] for x in members)
    return jsonify({"has": True, "name": tname, "code": tcode, "total": total, "m": m_data})

@app.route('/api/team_act', methods=['POST'])
def team_act():
    d = request.json
    uid, act, tname, tcode = d['id'], d['action'], d['tname'], d['tcode']
    u = users_col.find_one({"user_id": uid})
    
    if act == 'create':
        if not tname: return jsonify({"msg": "🔴 Error: Team Name mandatory hai!"})
        if u.get('team_code'): return jsonify({"msg": "🔴 Pehle apni current team leave karo!"})
        if teams_col.find_one({"name": tname}): return jsonify({"msg": "🔴 Yeh team name pehle se registered hai!"})
        
        # Unique Code Generator logic
        new_code = "TEAM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        teams_col.insert_one({"code": new_code, "name": tname, "creator": uid})
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": new_code}})
        return jsonify({"msg": f"🛡️ Faction Created! Code: {new_code}"})
        
    elif act == 'join':
        if u.get('team_code'): return jsonify({"msg": "🔴 Pehle old team leave karke aao!"})
        target_team = teams_col.find_one({"code": tcode})
        if not target_team: return jsonify({"msg": "🔴 System mismatch: Invalid Access Code!"})
        
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": tcode}})
        return jsonify({"msg": f"✅ Welcome to {target_team['name']}!"})
        
    elif act == 'leave':
        if not u.get('team_code'): return jsonify({"msg": "Aap pehle se kisi team me nahi ho!"})
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": None}})
        return jsonify({"msg": "🚪 Faction deployment abandoned successfully."})

@app.route('/api/play', methods=['POST'])
def play():
    data = request.json
    uid = int(data['id'])
    game_mode = data.get('game', 'arena')
    u = users_col.find_one({"user_id": uid})
    
    if not u or u['points'] < 1: 
        return jsonify({"res": "ERR", "msg": "Insufficient wallet balance to allocate stake!"})
    
    if random.random() < 0.40:
        # Wager points are strictly isolated and tracked separately here
        users_col.update_one({"user_id": uid}, {"$inc": {"wager": 2.0}})
        history_col.insert_one({"user_id": uid, "reason": f"Won {game_mode.upper()} match", "points": 2.0})
        res = "WIN"
    else:
        users_col.update_one({"user_id": uid}, {"$inc": {"points": -1.0}})
        history_col.insert_one({"user_id": uid, "reason": f"Lost {game_mode.upper()} stake", "points": -1.0})
        res = "LOSE"
    return jsonify({"res": res})

def run_f():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ================= TELEGRAM CORE BOT ENVIRONMENT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AdminAdd(StatesGroup):
    reason = State()
    payload = State()

@dp.message(CommandStart())
async def start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Open Premium Mini App ✨", web_app=WebAppInfo(url=MINI_APP_URL))]])
    await m.answer(f"🪐 **Welcome to the Arena, {html.bold(m.from_user.full_name)}!**\n\nApne premium interface ko toggle karne ke liye niche click karein.", reply_markup=kb, parse_mode="HTML")

@dp.message(Command("add"))
async def add_start(m: Message, state: FSMContext):
    await m.answer("📝 Enter event metadata / reference reason:")
    await state.set_state(AdminAdd.reason)

@dp.message(AdminAdd.reason)
async def add_reason(m: Message, state: FSMContext):
    await state.update_data(r=m.text)
    await m.answer("Send data payload in structure:\n`TARGET_ID POINTS` (e.g. `589632 25`)")
    await state.set_state(AdminAdd.payload)

@dp.message(AdminAdd.payload)
async def add_pay(m: Message, state: FSMContext):
    data = await state.get_data()
    reason = data['r']
    lines = m.text.strip().split('\n')
    success = 0
    
    for l in lines:
        parts = l.split()
        if len(parts) == 2:
            try:
                tid, pts = int(parts[0]), float(parts[1])
                users_col.update_one(
                    {"user_id": tid}, 
                    {"$inc": {"points": pts}, "$setOnInsert": {"username": "User", "wager": 0.0, "team_code": None}}, 
                    upsert=True
                )
                history_col.insert_one({"user_id": tid, "reason": reason, "points": pts})
                success += 1
                try: 
                    await bot.send_message(tid, f"🎁 **Wallet Update Notification!**\n\n💰 Added: +{pts} Points\n📌 Reason: {reason}")
                except: 
                    pass
            except ValueError:
                pass
                
    await m.answer(f"📊 Processed state updates: Successfully updated {success} entries.")
    await state.clear()

# ================= ORCHESTRATION ENGINE =================
if __name__ == '__main__':
    # Threading setup to resolve blocking constraints
    threading.Thread(target=run_f, daemon=True).start()
    
    print("🚀 Services Synchronized. Main engine online!")
    asyncio.run(dp.start_polling(bot))
