import asyncio
import os
import random
import re
import threading
from flask import Flask, render_template_string, jsonify, request
from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from pymongo import MongoClient
from datetime import datetime

# ================= CONFIGURATION =================
BOT_TOKEN = "8445493171:AAFpi_rg_CSImfp0vjvtsxuxQ-k2Wsv3ds0" 
# Agar local MongoDB hai to: "mongodb://localhost:27017/"
# Agar Atlas hai to waha ki connection string daalo
MONGO_URI = "mongodb+srv://shaurya59rt_db_user:admin123@cluster0.sw408wn.mongodb.net/?appName=Cluster0"

MINI_APP_URL = "https://monk-bot-sh8z.onrender.com" 

# ================= MONGODB SETUP =================
client = MongoClient(MONGO_URI)
db = client['telegram_bot_db']

users_col = db['users']      # User profile, points, team
history_col = db['history']  # Admin add logs, game logs
teams_col = db['teams']      # Team names and creators

# ================= FLASK SERVER (MINI APP) =================
app = Flask(__name__)

# HTML Template (Wahi interface jo pehle decide hua tha)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mini App Portal</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: sans-serif; padding-bottom: 80px; }
        .nav-bottom { position: fixed; bottom: 0; left: 0; right: 0; background: #1e293b; display: flex; padding: 10px 0; border-top: 1px solid #334155; }
        .nav-item { color: #94a3b8; text-align: center; flex: 1; font-size: 11px; cursor: pointer; text-decoration: none; }
        .nav-item.active { color: #38bdf8; font-weight: bold; }
        .app-page { display: none; padding: 20px; }
        .app-page.active { display: block; }
        .card-custom { background: #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid #334155; }
        .btn-game { width: 100%; margin-bottom: 10px; padding: 12px; font-weight: bold; border-radius: 8px; }
    </style>
</head>
<body>
    <div id="page-dashboard" class="app-page active">
        <h4>👋 <span id="user-name">User</span></h4>
        <div class="row g-2 mb-3">
            <div class="col-6"><div class="card-custom text-center"><h6>Points</h6><h3 id="stat-points" class="text-info">0</h3></div></div>
            <div class="col-6"><div class="card-custom text-center"><h6>Wager</h6><h3 id="stat-wager" class="text-warning">0</h3></div></div>
        </div>
        <div class="card-custom text-center"><h6>Global Rank: <span id="stat-rank" class="text-success">--</span></h6></div>
        <h6 class="mt-3">History</h6>
        <div id="history-list" class="list-group"></div>
    </div>

    <div id="page-leaderboard" class="app-page">
        <h4>🏆 Leaderboard</h4>
        <div class="btn-group w-100 mb-3">
            <button class="btn btn-sm btn-outline-info active" onclick="loadLB('users')">Users</button>
            <button class="btn btn-sm btn-outline-info" onclick="loadLB('teams')">Teams</button>
        </div>
        <div id="lb-list" class="list-group"></div>
    </div>

    <div id="page-games" class="app-page text-center">
        <h4>🎲 Games</h4>
        <p class="small text-muted">Win rate: 40% | Cost: 1 Point | Win: +2 Wager</p>
        <button class="btn btn-danger btn-game" onclick="play('dice')">Dice Roll</button>
        <button class="btn btn-warning btn-game" onclick="play('spin')">Spin Wheel</button>
        <button class="btn btn-primary btn-game" onclick="play('flip')">Coin Flip</button>
        <div id="game-res" class="mt-3 fw-bold"></div>
    </div>

    <div id="page-team" class="app-page">
        <div id="team-join-ui">
            <h4>🛡️ Team</h4>
            <input type="text" id="t-name" class="form-control mb-2" placeholder="Team Name">
            <button class="btn btn-success w-100 mb-2" onclick="teamAct('create')">Create Team</button>
            <button class="btn btn-primary w-100" onclick="teamAct('join')">Join Team</button>
        </div>
        <div id="team-info-ui" style="display:none;">
            <h3 id="cur-team-name" class="text-info"></h3>
            <h5 id="cur-team-pts"></h5>
            <button class="btn btn-sm btn-danger mb-3" onclick="teamAct('leave')">Leave Team</button>
            <h6>Members:</h6>
            <div id="team-m-list" class="list-group"></div>
        </div>
    </div>

    <div class="nav-bottom">
        <div class="nav-item active" onclick="showP('dashboard')">DASHBOARD</div>
        <div class="nav-item" onclick="showP('leaderboard')">LEADERBOARD</div>
        <div class="nav-item" onclick="showP('games')">GAMES</div>
        <div class="nav-item" onclick="showP('team')">TEAM</div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        const uid = tg.initDataUnsafe?.user?.id || 123;
        const uname = tg.initDataUnsafe?.user?.first_name || "Guest";

        function showP(p) {
            document.querySelectorAll('.app-page').forEach(el => el.classList.remove('active'));
            document.getElementById('page-'+p).classList.add('active');
            if(p === 'dashboard') loadDash();
            if(p === 'leaderboard') loadLB('users');
            if(p === 'team') loadTeam();
        }

        function loadDash() {
            fetch(`/api/user?id=${uid}&name=${uname}`).then(r=>r.json()).then(d=>{
                document.getElementById('stat-points').innerText = d.points;
                document.getElementById('stat-wager').innerText = d.wager;
                document.getElementById('stat-rank').innerText = d.rank;
                let h = document.getElementById('history-list');
                h.innerHTML = d.history.map(x => `<div class="list-group-item bg-dark text-white border-secondary">${x.reason}: +${x.pts}</div>`).join('');
            });
        }

        function loadLB(type) {
            fetch(`/api/lb?type=${type}`).then(r=>r.json()).then(d=>{
                let l = document.getElementById('lb-list');
                l.innerHTML = d.map((x,i) => `<div class="list-group-item bg-dark text-white border-secondary">#${i+1} ${x.name}: ${x.pts} pts</div>`).join('');
            });
        }

        function loadTeam() {
            fetch(`/api/team?id=${uid}`).then(r=>r.json()).then(d=>{
                if(d.has) {
                    document.getElementById('team-join-ui').style.display = 'none';
                    document.getElementById('team-info-ui').style.display = 'block';
                    document.getElementById('cur-team-name').innerText = d.name;
                    document.getElementById('cur-team-pts').innerText = "Total: " + d.total;
                    document.getElementById('team-m-list').innerHTML = d.m.map(x => `<div class="list-group-item bg-dark text-white border-secondary">${x.name}: ${x.pts}</div>`).join('');
                } else {
                    document.getElementById('team-join-ui').style.display = 'block';
                    document.getElementById('team-info-ui').style.display = 'none';
                }
            });
        }

        function teamAct(act) {
            let n = document.getElementById('t-name').value;
            fetch('/api/team_act', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({id:uid, name:uname, action:act, tname:n})
            }).then(r=>r.json()).then(res=>{ alert(res.msg); loadTeam(); });
        }

        function play(g) {
            fetch('/api/play', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({id:uid})
            }).then(r=>r.json()).then(d=>{
                let resDiv = document.getElementById('game-res');
                if(d.res === 'WIN') { resDiv.innerText = "WIN! +2 Wager"; resDiv.className="text-success mt-3"; }
                else if(d.res === 'LOSE') { resDiv.innerText = "LOSE! -1 Point"; resDiv.className="text-danger mt-3"; }
                else { alert(d.msg); }
                loadDash();
            });
        }
        loadDash();
    </script>
</body>
</html>
"""

# ================= API ROUTES (MONGODB) =================

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

@app.route('/api/user')
def get_user():
    uid = int(request.args.get('id'))
    name = request.args.get('name')
    u = users_col.find_one({"user_id": uid})
    if not u:
        u = {"user_id": uid, "username": name, "points": 0.0, "wager": 0.0, "team": None}
        users_col.insert_one(u)
    
    # Rank
    all_u = list(users_col.find().sort("points", -1))
    rank = next((i + 1 for i, item in enumerate(all_u) if item["user_id"] == uid), "--")
    
    # History
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
            {"$match": {"team": {"$ne": None}}},
            {"$group": {"_id": "$team", "total": {"$sum": "$points"}}},
            {"$sort": {"total": -1}}
        ]
        data = list(users_col.aggregate(pipeline))
        return jsonify([{"name": x['_id'], "pts": x['total']} for x in data])

@app.route('/api/team')
def get_team():
    uid = int(request.args.get('id'))
    u = users_col.find_one({"user_id": uid})
    if not u or not u.get('team'): return jsonify({"has": False})
    
    tname = u['team']
    members = list(users_col.find({"team": tname}))
    m_data = [{"name": x['username'], "pts": x['points']} for x in members]
    total = sum(x['points'] for x in members)
    return jsonify({"has": True, "name": tname, "total": total, "m": m_data})

@app.route('/api/team_act', methods=['POST'])
def team_act():
    d = request.json
    uid, act, tname = d['id'], d['action'], d['tname']
    u = users_col.find_one({"user_id": uid})
    
    if act == 'create':
        if teams_col.find_one({"name": tname}): return jsonify({"msg": "Team name exists!"})
        teams_col.insert_one({"name": tname, "creator": uid})
        users_col.update_one({"user_id": uid}, {"$set": {"team": tname}})
        return jsonify({"msg": "Team Created!"})
    elif act == 'join':
        if not teams_col.find_one({"name": tname}): return jsonify({"msg": "No such team!"})
        users_col.update_one({"user_id": uid}, {"$set": {"team": tname}})
        return jsonify({"msg": "Joined!"})
    elif act == 'leave':
        users_col.update_one({"user_id": uid}, {"$set": {"team": None}})
        return jsonify({"msg": "Left!"})

@app.route('/api/play', methods=['POST'])
def play():
    uid = int(request.json['id'])
    u = users_col.find_one({"user_id": uid})
    if u['points'] < 1: return jsonify({"res": "ERR", "msg": "No points!"})
    
    if random.random() < 0.4:
        users_col.update_one({"user_id": uid}, {"$inc": {"wager": 2.0}})
        res = "WIN"
    else:
        users_col.update_one({"user_id": uid}, {"$inc": {"points": -1.0}})
        res = "LOSE"
    return jsonify({"res": res})

# ================= 4. FLASK ROUTING & APIS =================
# ... (baki saare routes same rahenge)

# Isko update karo: Render ka dynamic port read karne ke liye
def run_f():
    # OS se PORT environment variable uthayega, nahi to default 5000 use karega
    port = int(os.environ.get("PORT", 5000))
    # Render par host '0.0.0.0' hona compulsory hai
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ================= 6. BOOTSTRAP EXECUTOR =================

# ================= TELEGRAM BOT (AIOGRAM) =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class AdminAdd(StatesGroup):
    reason = State()
    payload = State()

@dp.message(CommandStart())
async def start(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]])
    await m.answer("Welcome! Open Mini App:", reply_markup=kb)

@dp.message(Command("add"))
async def add_start(m: Message, state: FSMContext):
    await m.answer("Reason for adding points?")
    await state.set_state(AdminAdd.reason)

@dp.message(AdminAdd.reason)
async def add_reason(m: Message, state: FSMContext):
    await state.update_data(r=m.text)
    await m.answer("Send ID and Points (ID Points):")
    await state.set_state(AdminAdd.payload)

@dp.message(AdminAdd.payload)
async def add_pay(m: Message, state: FSMContext):
    data = await state.get_data()
    reason = data['r']
    lines = m.text.split('\n')
    for l in lines:
        parts = l.split()
        if len(parts) == 2:
            tid, pts = int(parts[0]), float(parts[1])
            users_col.update_one({"user_id": tid}, {"$inc": {"points": pts, "wager": pts*2}}, upsert=True)
            history_col.insert_one({"user_id": tid, "reason": reason, "points": pts})
            try: await bot.send_message(tid, f"Added {pts} points!")
            except: pass
    await m.answer("Done!")
    await state.clear()

async def main():
    threading.Thread(target=run_f, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Flask ko thread me start kiya
    threading.Thread(target=run_f, daemon=True).start()
    
    # Main loop me bot polling
    print("MongoDB Server ready & Bot Online!")
    asyncio.run(dp.start_polling(bot))
