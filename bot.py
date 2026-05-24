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
BOT_TOKEN = "8445493171:AAFpi_rg_CSImfp0vjvtsxuxQ-k2Wsv3ds0" 
MONGO_URI = "mongodb+srv://shaurya59rt_db_user:admin123@cluster0.sw408wn.mongodb.net/?appName=Cluster0"
MINI_APP_URL = "https://monk-bot-sh8z.onrender.com" 

# ================= MONGODB SETUP =================
client = MongoClient(MONGO_URI)
db = client['telegram_bot_db']
users_col = db['users']      
history_col = db['history']  
teams_col = db['teams']      

# ================= AIOGRAM STATES SYSTEM =================
class AdminAddStates(StatesGroup):
    waiting_for_reason = State()
    waiting_for_data = State()

# ================= FLASK SERVER (MINI APP UI) =================
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
            --bg-obsidian: #050505;
            --bg-card: rgba(22, 22, 22, 0.95);
            --accent-gold: #c5a059;
            --glass: rgba(255, 255, 255, 0.05);
            --text-main: #ffffff;
            --text-muted: #b0b0b0;
        }

        * { 
            box-sizing: border-box; 
            -webkit-tap-highlight-color: transparent; 
            user-select: none;
        }
        
        /* Input handling fix for mobile view typing bugs */
        input, textarea {
            user-select: text !important;
            -webkit-user-select: text !important;
        }

        body { 
            background: var(--bg-obsidian); 
            color: var(--text-main); 
            font-family: 'Inter', sans-serif;
            margin: 0; padding: 0;
            overflow-x: hidden;
            height: 100vh;
        }

        /* 1. MONK TASK 3-SECOND SPLASH SCREEN */
        #splash-screen {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at center, #111111 0%, #000000 100%);
            z-index: 10000; display: flex; flex-direction: column;
            align-items: center; justify-content: center;
            transition: opacity 0.6s ease-out;
        }
        .monk-logo-container {
            position: relative; width: 120px; height: 120px;
            margin-bottom: 30px;
        }
        .monk-ring {
            position: absolute; width: 100%; height: 100%;
            border: 3px solid var(--monk-gold); border-radius: 50%;
            border-top-color: transparent; border-bottom-color: transparent;
            animation: rotateRing 1.2s linear infinite;
        }
        .monk-center {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            font-family: 'Cinzel', serif; color: var(--monk-gold); font-size: 44px;
            text-shadow: 0 0 25px var(--monk-gold-glow);
        }
        @keyframes rotateRing { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .splash-text {
            font-family: 'Orbitron', sans-serif; letter-spacing: 8px;
            color: var(--monk-gold); text-transform: uppercase; font-size: 16px;
            animation: pulseText 2s infinite;
        }
        @keyframes pulseText { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.6; transform: scale(0.96); } }

        /* 2. PREMIUM UI NAVIGATION */
        .premium-nav {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background: #0a0a0a; backdrop-filter: blur(25px);
            border-top: 2px solid rgba(255, 215, 0, 0.25);
            display: flex; justify-content: space-around; padding: 12px 0 28px 0;
            z-index: 9000;
        }
        .nav-link-btn {
            text-align: center; color: #777777; text-decoration: none;
            font-size: 11px; font-weight: 900; letter-spacing: 1.5px;
            text-transform: uppercase; transition: 0.25s ease;
            background: none; border: none; padding: 5px 10px; cursor: pointer;
        }
        .nav-link-btn.active { color: var(--monk-gold); text-shadow: 0 0 15px var(--monk-gold-glow); }

        /* 3. CONTENT AREA */
        #app-viewport {
            height: 100vh; overflow-y: auto; padding: 25px 20px 130px 20px;
            display: none;
        }
        .view-section { display: none; }
        .view-section.active { display: block; animation: fadeInUp 0.4s ease-out; }

        /* 4. MONK TASK HIGH CONTRAST CARDS */
        .gold-card {
            background: var(--bg-card); 
            border: 1.5px solid rgba(255, 215, 0, 0.25);
            border-radius: 20px; padding: 22px; margin-bottom: 20px;
            box-shadow: 0 12px 35px rgba(0,0,0,0.7);
            position: relative; overflow: hidden;
        }
        .gold-card::before {
            content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,215,0,0.08), transparent);
            transition: 0.6s;
        }
        .gold-card:hover::before { left: 100%; }

        .stat-header { font-family: 'Orbitron', sans-serif; font-size: 12px; color: var(--accent-gold); margin-bottom: 6px; font-weight: 900; }
        .stat-value { font-family: 'Orbitron', sans-serif; font-size: 32px; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }

        /* 5. ARENA MODULES */
        .arena-box {
            height: 200px; background: rgba(0, 0, 0, 0.4);
            border-radius: 15px; display: flex; align-items: center;
            justify-content: center; margin-bottom: 20px;
            border: 2px dashed rgba(255,215,0,0.35);
        }
        
        .btn-monk {
            background: linear-gradient(135deg, #FFD700 0%, #b8860b 100%);
            color: #000000; border: none; padding: 16px; border-radius: 14px;
            width: 100%; font-family: 'Orbitron', sans-serif; font-weight: 900;
            text-transform: uppercase; margin-bottom: 14px;
            box-shadow: 0 5px 20px rgba(255,215,0,0.35);
            transition: transform 0.1s ease;
        }
        .btn-monk:active { transform: scale(0.96); }

        /* INPUT FIELD OVERRIDES FOR WHITE COLOR AND PERFECT INTERACTION */
        .monk-input {
            background-color: #151515 !important;
            border: 2px solid rgba(255, 215, 0, 0.4) !important;
            color: #ffffff !important;
            border-radius: 10px;
            padding: 12px;
            font-size: 15px;
            font-weight: 600;
            margin-bottom: 15px;
            width: 100%;
        }
        .monk-input::placeholder {
            color: #888888 !important;
        }
        .monk-input:focus {
            outline: none !important;
            border-color: var(--monk-gold) !important;
            box-shadow: 0 0 10px var(--monk-gold-glow) !important;
        }

        /* 6. LEADERBOARD STYLE */
        .tab-btn-group {
            display: flex; gap: 10px; margin-bottom: 20px;
        }
        .tab-btn {
            flex: 1; padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255, 215, 0, 0.2); color: #aaaaaa; font-family: 'Orbitron';
            font-weight: 900; text-transform: uppercase; font-size: 12px;
        }
        .tab-btn.active {
            background: var(--monk-gold); color: #000000; border-color: var(--monk-gold);
        }

        .rank-row {
            display: flex; align-items: center; justify-content: space-between;
            padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.01); margin-bottom: 5px; border-radius: 8px;
        }
        .rank-num { font-family: 'Orbitron'; color: var(--monk-gold); width: 40px; font-weight: 900; }
        .rank-name { flex-grow: 1; font-weight: 600; color: #ffffff; }
        .rank-pts { color: var(--monk-gold); font-family: 'Orbitron'; font-weight: 900; }
        
        /* 7. CUSTOM WHITE LEVEL HISTORY LOGGER */
        .history-card {
            background: rgba(30, 30, 30, 0.85);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px; padding: 12px 18px; margin-bottom: 10px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .history-reason { font-size: 13px; color: #ffffff; font-weight: 600; }

        ::-webkit-scrollbar { width: 5px; }
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
        <div style="margin-top: 15px; font-size: 11px; color: #666; font-family: 'Orbitron';">Initializing Premium Core v3.0...</div>
    </div>

    <div id="app-viewport">
        
        <!-- VIEW: DASHBOARD/TASK -->
        <div id="view-task" class="view-section active">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <div style="font-size: 11px; color: var(--accent-gold); font-weight: 900; text-transform: uppercase; letter-spacing: 1px;">Operative Profile</div>
                    <h4 id="ui-username" style="font-family: 'Orbitron'; font-weight: 900; color: #ffffff;">---</h4>
                </div>
                <div class="text-end">
                    <div id="ui-rank" style="background: rgba(255,215,0,0.1); padding: 6px 16px; border-radius: 20px; color: var(--monk-gold); font-size: 12px; font-weight: 900; border: 1.5px solid var(--monk-gold);">Rank --</div>
                </div>
            </div>

            <div class="gold-card">
                <div class="stat-header">Available Main Credits</div>
                <div class="stat-value" id="ui-points">0.00</div>
                <div style="margin-top: 12px; height: 6px; background: #222; border-radius: 3px;">
                    <div id="ui-progress" style="width: 0%; height: 100%; background: var(--monk-gold); border-radius: 3px; box-shadow: 0 0 12px var(--monk-gold);"></div>
                </div>
            </div>

            <div class="row g-3 mb-4">
                <div class="col-6">
                    <div class="gold-card m-0 py-3 text-center">
                        <div class="stat-header">Wagered Vault</div>
                        <div style="font-family: 'Orbitron'; font-weight: 900; font-size: 20px; color: #ffd700;" id="ui-wager">0.0</div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="gold-card m-0 py-3 text-center">
                        <div class="stat-header">System Node</div>
                        <div style="font-family: 'Orbitron'; font-weight: 900; font-size: 20px; color: #4ade80;">Premium</div>
                    </div>
                </div>
            </div>

            <h6 style="font-family: 'Orbitron'; font-size: 13px; color: var(--accent-gold); margin-bottom: 15px; font-weight: 900; text-transform: uppercase;">System Ledger History</h6>
            <div id="ui-history"></div>
        </div>

        <!-- VIEW: ARENA GAMES -->
        <div id="view-arena" class="view-section">
            <h4 class="text-center mb-4" style="font-family: 'Orbitron'; font-weight: 900; letter-spacing: 2px;">Monk Arena</h4>
            
            <div class="gold-card">
                <div class="arena-box" id="game-stage">
                    <div id="stage-icon" style="font-size: 65px;">☯️</div>
                </div>
                <div id="game-log" class="text-center small text-uppercase mb-2" style="font-weight: 900; letter-spacing: 1px; color: #b0b0b0;">Choose Your Protocol Strategy</div>
            </div>

            <p class="text-center text-muted small px-2" style="margin-bottom: 20px;">Rule Matrix: Every roll/action consumes exactly 1 Wallet Credit. Victory grants +2.0 Wager Credits instantly!</p>

            <button class="btn-monk" onclick="handleArena('dice')">Roll Premium Dice</button>
            <button class="btn-monk" onclick="handleArena('flip')">Flip Phoenix Coin</button>
            <button class="btn-monk" style="background: transparent; border: 2px solid var(--monk-gold); color: var(--monk-gold);" onclick="handleArena('spin')">Spin Oracle Wheel</button>
        </div>

        <!-- VIEW: LEADERBOARD SYSTEM -->
        <div id="view-ranks" class="view-section">
            <h4 class="mb-4" style="font-family: 'Orbitron'; font-weight: 900; text-transform: uppercase;">Global Database</h4>
            
            <div class="tab-btn-group">
                <button id="tab-users" class="tab-btn active" onclick="switchLeaderboardTab('users')">Top Users</button>
                <button id="tab-teams" class="tab-btn" onclick="switchLeaderboardTab('teams')">Top Squads</button>
            </div>

            <div id="ui-leaderboard"></div>
        </div>

        <!-- VIEW: SQUAD STRATEGY MANAGEMENT -->
        <div id="view-team" class="view-section">
            <div id="team-setup-ui">
                <h4 class="mb-4" style="font-family: 'Orbitron'; font-weight: 900;">SQUAD SYNDICATE</h4>
                <div class="gold-card">
                    <div class="stat-header">Create Custom Squad</div>
                    <input type="text" id="inp-tname" class="monk-input" placeholder="Enter Squad Name Designation">
                    <button class="btn-monk" style="padding: 10px; margin: 0;" onclick="teamAction('create')">Establish Squad</button>
                </div>
                <div class="gold-card">
                    <div class="stat-header">Join Authorized Squad</div>
                    <input type="text" id="inp-tcode" class="monk-input" placeholder="Format: MONK-XXXXXX">
                    <button class="btn-monk" style="padding: 10px; margin: 0; background: linear-gradient(135deg, #a0a0a0, #444);" onclick="teamAction('join')">Verify Code Join</button>
                </div>
            </div>
            
            <div id="team-active-ui" style="display:none;">
                <div class="gold-card text-center">
                    <h3 id="active-team-name" style="font-family: 'Orbitron'; color: var(--monk-gold); font-weight: 900;">---</h3>
                    <code id="active-team-code" class="d-block mb-3" style="color: #ffffff; background: #222; padding: 8px; border-radius: 6px; font-size: 14px; letter-spacing: 1px;">---</code>
                    <button class="btn btn-outline-danger btn-sm w-100 py-2 style-leav-btn" style="font-weight: 900; font-family:'Orbitron';" onclick="teamAction('leave')">Leave Current Squad</button>
                </div>
                <h6 class="mt-4 mb-3" style="font-family: 'Orbitron'; font-size: 13px; color: var(--accent-gold); font-weight: 900; text-transform: uppercase;">Squad Roster Network</h6>
                <div id="ui-team-list"></div>
            </div>
        </div>

    </div>

    <nav class="premium-nav">
        <button class="nav-link-btn active" id="nav-task" onclick="switchView('task')">Ledger</button>
        <button class="nav-link-btn" id="nav-arena" onclick="switchView('arena')">Arena</button>
        <button class="nav-link-btn" id="nav-ranks" onclick="switchView('ranks')">Ranks</button>
        <button class="nav-link-btn" id="nav-team" onclick="switchView('team')">Squad</button>
    </nav>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        tg.headerColor = "#050505";
        tg.backgroundColor = "#050505";

        const USER_ID = tg.initDataUnsafe?.user?.id || 987654321;
        const USER_NAME = tg.initDataUnsafe?.user?.first_name || "Anonymous Operative";
        
        let currentLbTab = "users";

        window.addEventListener('load', () => {
            setTimeout(() => {
                const splash = document.getElementById('splash-screen');
                splash.style.opacity = '0';
                setTimeout(() => {
                    splash.style.display = 'none';
                    document.getElementById('app-viewport').style.display = 'block';
                    refreshDashboard();
                }, 600);
            }, 3000);
        });

        function switchView(viewId) {
            document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-link-btn').forEach(n => n.classList.remove('active'));
            
            document.getElementById('view-' + viewId).classList.add('active');
            document.getElementById('nav-' + viewId).classList.add('active');

            if(viewId === 'task') refreshDashboard();
            if(viewId === 'ranks') loadLeaderboard();
            if(viewId === 'team') loadTeamInfo();
        }

        async function refreshDashboard() {
            try {
                const res = await fetch(`/api/user?id=${USER_ID}&name=${encodeURIComponent(USER_NAME)}`);
                const data = await res.json();
                
                document.getElementById('ui-username').innerText = USER_NAME;
                document.getElementById('ui-points').innerText = data.points.toFixed(2);
                document.getElementById('ui-wager').innerText = data.wager.toFixed(2);
                document.getElementById('ui-rank').innerText = "Rank #" + data.rank;
                
                let prog = Math.min((data.points / 500) * 100, 100);
                document.getElementById('ui-progress').style.width = prog + "%";

                document.getElementById('ui-history').innerHTML = data.history.map(h => `
                    <div class="history-card">
                        <span class="history-reason">${h.reason}</span>
                        <span style="color: ${h.pts >= 0 ? '#4ade80':'#f87171'}; font-weight: 900; font-family: 'Orbitron'; font-size: 13px;">
                            ${h.pts >= 0 ? '+':''}${h.pts.toFixed(2)}
                        </span>
                    </div>
                `).join('') || '<div class="text-center text-muted small py-4">No transactions authenticated in network.</div>';
            } catch (e) {
                console.error("Dashboard error:", e);
            }
        }

        async function handleArena(mode) {
            const log = document.getElementById('game-log');
            const stage = document.getElementById('game-stage');
            
            log.innerText = "Transmitting Execution Protocol...";
            stage.innerHTML = '<div class="spinner-border text-warning" style="width: 3rem; height: 3rem;" role="status"></div>';

            try {
                const res = await fetch('/api/play', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: USER_ID, game: mode})
                });
                const data = await res.json();

                setTimeout(() => {
                    if(data.res === 'ERR') {
                        alert(data.msg);
                        stage.innerHTML = '<div style="font-size: 65px;">⚠️</div>';
                        log.innerText = data.msg;
                    } else if(data.res === 'WIN') {
                        stage.innerHTML = '<div style="font-size: 65px;" class="animate__animated animate__bounceIn">💎</div>';
                        log.innerText = `VICTORY! ${data.val}`;
                        refreshDashboard();
                    } else {
                        stage.innerHTML = '<div style="font-size: 65px;" class="animate__animated animate__shakeX">💥</div>';
                        log.innerText = `DEFEAT! ${data.val}`;
                        refreshDashboard();
                    }
                }, 800);
            } catch(err) {
                log.innerText = "Network Sync Timeout";
                stage.innerHTML = '<div style="font-size: 65px;">❌</div>';
            }
        }

        function switchLeaderboardTab(tab) {
            currentLbTab = tab;
            document.getElementById('tab-users').classList.remove('active');
            document.getElementById('tab-teams').classList.remove('active');
            document.getElementById('tab-' + tab).classList.add('active');
            loadLeaderboard();
        }

        async function loadLeaderboard() {
            try {
                const res = await fetch(`/api/lb?type=${currentLbTab}`);
                const data = await res.json();
                
                if (currentLbTab === "users") {
                    document.getElementById('ui-leaderboard').innerHTML = data.map((u, i) => `
                        <div class="rank-row">
                            <span class="rank-num">#${i+1}</span>
                            <span class="rank-name">${u.name}</span>
                            <span class="rank-pts">${u.pts.toFixed(2)} LP</span>
                        </div>
                    `).join('');
                } else {
                    document.getElementById('ui-leaderboard').innerHTML = data.map((t, i) => `
                        <div class="rank-row">
                            <span class="rank-num">#${i+1}</span>
                            <span class="rank-name">${t.name}</span>
                            <span class="rank-pts">${t.cumulative_pts.toFixed(2)} SQ</span>
                        </div>
                    `).join('');
                }
            } catch (e) {
                document.getElementById('ui-leaderboard').innerHTML = '<div class="text-center text-danger small">Failed loading metrics</div>';
            }
        }

        async function loadTeamInfo() {
            try {
                const res = await fetch(`/api/team?id=${USER_ID}`);
                const data = await res.json();
                if(data.has) {
                    document.getElementById('team-setup-ui').style.display = 'none';
                    document.getElementById('team-active-ui').style.display = 'block';
                    document.getElementById('active-team-name').innerText = data.name;
                    document.getElementById('active-team-code').innerText = data.code;
                    document.getElementById('ui-team-list').innerHTML = data.m.map(m => `
                        <div class="rank-row">
                            <span style="color:#ffffff; font-weight:600;">${m.name}</span>
                            <span class="text-warning small font-monospace">${m.pts.toFixed(2)}</span>
                        </div>
                    `).join('');
                } else {
                    document.getElementById('team-setup-ui').style.display = 'block';
                    document.getElementById('team-active-ui').style.display = 'none';
                }
            } catch (e) {
                console.error("Team info screen loading issue");
            }
        }

        async function teamAction(act) {
            const name = document.getElementById('inp-tname').value;
            const code = document.getElementById('inp-tcode').value;
            
            if(act === 'create' && !name.trim()) { alert("Please provide a valid squad tag!"); return; }
            if(act === 'join' && !code.trim()) { alert("Please input authorization code!"); return; }

            try {
                const res = await fetch('/api/team_act', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: USER_ID, action: act, tname: name, tcode: code})
                });
                const data = await res.json();
                alert(data.msg);
                loadTeamInfo();
            } catch(e) {
                alert("Action verification timeout");
            }
        }
    </script>
</body>
</html>
"""

# ================= SERVER ROUTING AND BACKEND ENGINE =================

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
        
    if u.get('username') != name and name != 'Unknown':
        users_col.update_one({"user_id": uid}, {"$set": {"username": name}})
    
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
    
    if not u:
        return jsonify({"res": "ERR", "msg": "User Record System Missing"})
        
    if u.get('points', 0.0) < 1.0:
        return jsonify({"res": "ERR", "msg": "Insufficient Main Credits (Requires 1.00)"})
    
    # Strictly deduct 1 Wallet Point on every execution
    users_col.update_one({"user_id": uid}, {"$inc": {"points": -1.0}})
    
    win = random.random() < 0.38  # Balanced probabilistic matrix 
    if win:
        # Earn exactly +2.0 Wager Credits on Win
        users_col.update_one({"user_id": uid}, {"$inc": {"wager": 2.0}})
        history_col.insert_one({"user_id": uid, "reason": "Arena Match Won", "points": -1.0})
        history_col.insert_one({"user_id": uid, "reason": "Wager Reward Dropped", "points": 2.0}) # Logged logically
        return jsonify({"res": "WIN", "val": "+2.00 Wager Pool Added"})
    else:
        # Lose: Nothing else is added, 1 wallet point reduction stands
        history_col.insert_one({"user_id": uid, "reason": "Arena Combat Lost", "points": -1.0})
        return jsonify({"res": "LOSE", "val": "Burned 1.00 Main Point"})

@app.route('/api/lb')
def leaderboard():
    ltype = request.args.get('type', 'users')
    
    if ltype == 'users':
        data = users_col.find().sort("points", -1).limit(30)
        return jsonify([{"name": x['username'], "pts": x['points']} for x in data])
    else:
        # Dual tab group calculations across matching squad parameters
        pipelines = [
            {"$group": {"_id": "$team_code", "cumulative_pts": {"$sum": "$points"}}},
            {"$match": {"_id": {"$ne": None}}}
        ]
        aggregated = list(users_col.aggregate(pipelines))
        teams_list = []
        for item in aggregated:
            team_meta = teams_col.find_one({"code": item["_id"]})
            team_name = team_meta["name"] if team_meta else f"Squad Module ({item['_id']})"
            teams_list.append({"name": team_name, "cumulative_pts": item["cumulative_pts"]})
            
        teams_list.sort(key=lambda x: x["cumulative_pts"], reverse=True)
        return jsonify(teams_list[:20])

@app.route('/api/team')
def team_info():
    uid = int(request.args.get('id', 0))
    u = users_col.find_one({"user_id": uid})
    if not u or not u.get('team_code'):
        return jsonify({"has": False})
    
    t = teams_col.find_one({"code": u['team_code']})
    if not t:
        return jsonify({"has": False})
        
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
        return jsonify({"msg": f"Squad Active Designation: {code}"})
        
    elif act == 'join':
        exists = teams_col.find_one({"code": tcode.strip()})
        if exists:
            users_col.update_one({"user_id": uid}, {"$set": {"team_code": tcode.strip()}})
            return jsonify({"msg": f"Synchronized with squad {exists['name']}"})
        return jsonify({"msg": "Authorization Key Invalid!"})
        
    elif act == 'leave':
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": None}})
        return jsonify({"msg": "Severed current network squad bounds."})

# ================= ADVANCED TELEGRAM BOT CONSOLE MANAGEMENT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def start_handler(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Enter Monk Arena ⛩️", web_app=WebAppInfo(url=MINI_APP_URL))
    ]])
    await m.answer(
        f"<b>Welcome Operative {m.from_user.first_name}</b>\n\n"
        "The Premium Monk Ledger and Gaming Matrix Console is live. Manage your profile balances securely.",
        reply_markup=kb,
        parse_mode="HTML"
    )

# Advanced /add multi-line operational handler with conversion schema mechanics
@dp.message(Command("add"))
async def add_command_initiator(m: Message, state: FSMContext):
    # Standard security protocol placeholder check: modify if restricting to exact admin IDs
    await m.answer("<b>[SECURE ENTRY]</b>\nPlease input the transaction reason name to reflect inside the user logs:")
    await state.set_state(AdminAddStates.waiting_for_reason)

@dp.message(AdminAddStates.waiting_for_reason)
async def add_reason_catcher(m: Message, state: FSMContext):
    reason_text = m.text.strip()
    await state.update_data(reason=reason_text)
    
    await m.answer(
        "<b>[REASON RESOLVED]</b>\nNow send the User IDs and Amounts precisely matching this design profile:\n\n"
        "<code>id amount\nid amount</code>\n\n"
        "<i>Example:</i>\n<code>1234567 50\n9876543 25.5</code>",
        parse_mode="HTML"
    )
    await state.set_state(AdminAddStates.waiting_for_data)

@dp.message(AdminAddStates.waiting_for_data)
async def add_data_processor(m: Message, state: FSMContext):
    state_data = await state.get_data()
    log_reason = state_data.get('reason', 'System Refunding')
    
    lines = m.text.strip().split('\n')
    success_logs = []
    error_logs = []
    
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 2:
            error_logs.append(f"Format broken layer: '{line}'")
            continue
            
        try:
            target_uid = int(parts[0])
            add_amount = float(parts[1])
            
            user_record = users_col.find_one({"user_id": target_uid})
            if not user_record:
                error_logs.append(f"UID {target_uid}: User Node non-existent")
                continue
                
            current_wager = user_record.get('wager', 0.0)
            
            # Conversion mechanics logic:
            # 1 normal point added allows 2 wager points to become active real points!
            allowed_conversion_units = add_amount * 2.0
            actual_conversion_processed = min(current_wager, allowed_conversion_units)
            
            # Points modification calculation updates
            new_points_balance = user_record.get('points', 0.0) + add_amount + actual_conversion_processed
            new_wager_balance = current_wager - actual_conversion_processed
            
            users_col.update_one(
                {"user_id": target_uid},
                {"$set": {"points": new_points_balance, "wager": new_wager_balance}}
            )
            
            # Track changes inside logs database system seamlessly
            history_col.insert_one({
                "user_id": target_uid,
                "reason": log_reason,
                "points": add_amount
            })
            
            if actual_conversion_processed > 0:
                history_col.insert_one({
                    "user_id": target_uid,
                    "reason": "Wager Vault Liquidated",
                    "points": actual_conversion_processed
                })
                success_logs.append(f"✓ UID {target_uid}: added {add_amount}, converted {actual_conversion_processed} wager.")
            else:
                success_logs.append(f"✓ UID {target_uid}: added {add_amount} smoothly.")
                
        except ValueError:
            error_logs.append(f"Numeric validation failed line: '{line}'")
            
    # Compile execution statement response text
    report = "<b>Transaction Protocol Batch Processing Complete:</b>\n\n"
    if success_logs:
        report += "<b>Success Logs:</b>\n" + "\n".join(success_logs) + "\n\n"
    if error_logs:
        report += "<b>Error Logs:</b>\n" + "\n".join(error_logs)
        
    await m.answer(report, parse_mode="HTML")
    await state.clear()

async def start_services():
    # Execute Flask as non-blocking background daemon thread matrix
    threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0", 
            port=int(os.environ.get("PORT", 5000)), 
            debug=False, 
            use_reloader=False
        ), 
        daemon=True
    ).start()
    
    # Execute primary bot foreground event loops polling systems
    print("System Matrix Engines Online. Running Bot Polling...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        print("Engines Deactivated safely.")
