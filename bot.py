import asyncio
import os
import random
import string
import threading
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

# Target Channel Requirements for Verification Gateway
REQUIRED_CHANNEL_ID = -1002666250912  
CHANNEL_INVITE_LINK = "https://t.me/VERIFIEDPAISABOTS"

# ================= MONGODB SETUP =================
client = MongoClient(MONGO_URI)
db = client['telegram_bot_db']

users_col = db['users']      
history_col = db['history']  
teams_col = db['teams']      

# ================= FLASK SERVER (MINI APP) =================
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monkxz Premium Arena</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        :root {
            --bg-dark: #060913;
            --card-bg: rgba(17, 24, 39, 0.7);
            --border-glow: rgba(56, 189, 248, 0.15);
            --neon-blue: #38bdf8;
            --neon-purple: #c084fc;
            --neon-green: #4ade80;
            --neon-red: #f87171;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        body { 
            background: var(--bg-dark); 
            color: var(--text-main); 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            padding-bottom: 100px;
            overflow-x: hidden;
            -webkit-user-select: none;
            user-select: none;
        }
        .header-bar {
            background: linear-gradient(90deg, var(--neon-blue), var(--neon-purple));
            height: 5px;
            width: 100%;
            position: fixed;
            top: 0;
            z-index: 2000;
        }
        
        /* Verification Overlay Gatekeeper */
        #gatekeeper-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(6, 9, 19, 0.98); z-index: 3000;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            padding: 30px; text-align: center; display: none;
        }

        /* Navigation Mechanics */
        .nav-bottom { 
            position: fixed; bottom: 0; left: 0; right: 0; 
            background: rgba(10, 15, 30, 0.92); 
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            display: flex; padding: 14px 0; 
            border-top: 1px solid rgba(255, 255, 255, 0.06); 
            box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.7);
            z-index: 1000;
        }
        .nav-item { 
            color: #4b5563; text-align: center; flex: 1; 
            font-size: 11px; font-weight: 800; cursor: pointer; 
            letter-spacing: 0.5px; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .nav-item.active { 
            color: var(--neon-blue); 
            text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
            transform: translateY(-1px);
        }
        .app-page { display: none; padding: 25px 20px 20px 20px; animation: pageIn 0.3s ease-out; margin-top: 10px; }
        .app-page.active { display: block; }
        @keyframes pageIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

        /* Premium Dashboard Dashing Cards */
        .card-custom { 
            background: var(--card-bg); 
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 16px; padding: 20px; margin-bottom: 16px; 
            border: 1px solid var(--border-glow); 
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        .stat-label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); font-weight: 700; }
        .stat-val { font-size: 28px; font-weight: 900; margin-top: 2px; }
        
        /* Gaming Infrastructure Elements */
        .game-card {
            background: rgba(30, 41, 59, 0.3); border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px; padding: 15px; margin-bottom: 12px;
            display: flex; align-items: center; justify-content: space-between;
            transition: all 0.2s;
        }
        .game-card:active { background: rgba(30, 41, 59, 0.5); transform: scale(0.99); }
        .btn-action {
            padding: 8px 16px; font-size: 12px; font-weight: 800; border-radius: 8px; border: none; text-transform: uppercase;
        }
        
        /* Real-Time Physics Custom Asset Render Engines */
        .arena-viewport {
            height: 160px; display: flex; align-items: center; justify-content: center; perspective: 400px;
        }
        
        /* 3D Dice Object Architecture */
        .dice-box { width: 60px; height: 60px; position: relative; transform-style: preserve-3d; transition: transform 0.1s linear; }
        .dice-face {
            position: absolute; width: 60px; height: 60px; background: #fff; border: 2px solid #ddd;
            border-radius: 10px; display: flex; align-items: center; justify-content: center;
            font-size: 32px; font-weight: bold; color: #000; box-shadow: inset 0 0 8px rgba(0,0,0,0.2);
        }
        .f1 { transform: rotateY(0deg) translateZ(30px); }
        .f2 { transform: rotateY(90deg) translateZ(30px); }
        .f3 { transform: rotateX(90deg) translateZ(30px); }
        .f4 { transform: rotateX(-90deg) translateZ(30px); }
        .f5 { transform: rotateY(-90deg) translateZ(30px); }
        .f6 { transform: rotateY(180deg) translateZ(30px); }
        
        /* 3D Coin Architecture */
        .coin-box {
            width: 70px; height: 70px; position: relative; transform-style: preserve-3d; transition: transform 0.1s linear;
        }
        .coin-face {
            position: absolute; width: 100%%; height: 100%%; border-radius: 50%%;
            display: flex; align-items: center; justify-content: center; font-size: 36px;
            backface-visibility: hidden; -webkit-backface-visibility: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        }
        .coin-front { background: linear-gradient(135deg, #ffd700, #b8860b); border: 2px solid #fff; }
        .coin-back { background: linear-gradient(135deg, #c0c0c0, #808080); border: 2px solid #fff; transform: rotateY(180deg); }

        /* General Typography updates */
        .form-control-cyber {
            background: rgba(10, 15, 30, 0.7); border: 1px solid rgba(255, 255, 255, 0.08);
            color: white; border-radius: 12px; padding: 14px; font-weight: 600;
        }
        .form-control-cyber:focus {
            background: rgba(10, 15, 30, 0.9); border-color: var(--neon-blue); box-shadow: 0 0 15px rgba(56, 189, 248, 0.15); color: white;
        }
        .history-item {
            background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255,255,255,0.04);
            border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;
        }
    </style>
</head>
<body>
    <div class="header-bar"></div>

    <!-- GATEKEEPER BANNER MODAL OVERLAY -->
    <div id="gatekeeper-overlay">
        <div class="card-custom py-4 w-100" style="max-width: 400px; border: 1px solid var(--neon-purple);">
            <h3 class="fw-bold text-purple mb-2" style="color:var(--neon-purple);">Access Locked</h3>
            <p class="text-muted small px-2">System deployment checks indicate you have not joined our verification stream channel yet. Please join to enable the Mini App assets.</p>
            <div class="my-4" style="font-size: 64px;">📢</div>
            <a href="""" + CHANNEL_INVITE_LINK + """" target="_blank" class="btn btn-info w-100 fw-bold py-3 mb-2" style="border-radius:12px;">JOIN CHANNEL NOW</a>
            <button class="btn btn-outline-secondary btn-sm w-100 mt-2 py-2" onclick="verifySubscription()" style="border-radius:10px; font-weight:700;">🔄 VERIFY SQUAD STATUS</button>
        </div>
    </div>

    <!-- 1. DASHBOARD PAGE -->
    <div id="page-dashboard" class="app-page active">
        <div class="d-flex align-items-center justify-content-between mb-4">
            <div>
                <h4 class="fw-bold mb-0">⚡ <span id="user-name" class="text-info">Player</span></h4>
                <span class="text-muted small fw-bold">ID: <span id="user-display-id">--</span></span>
            </div>
            <span id="stat-rank" class="badge bg-dark border border-info text-info px-3 py-2 fs-6" style="border-radius:10px;">Rank #--</span>
        </div>
        
        <div class="row g-3 mb-4">
            <div class="col-6">
                <div class="card-custom text-center h-100" style="border-bottom: 4px solid var(--neon-blue);">
                    <div class="stat-label">Wallet Balance</div>
                    <div id="stat-points" class="stat-val text-info">0.0</div>
                </div>
            </div>
            <div class="col-6">
                <div class="card-custom text-center h-100" style="border-bottom: 4px solid var(--neon-purple);">
                    <div class="stat-label">Wagered Pool</div>
                    <div id="stat-wager" class="stat-val" style="color: var(--neon-purple);">0.0</div>
                </div>
            </div>
        </div>

        <h6 class="mb-3 text-muted fw-bold small text-uppercase">Performance Real-Time Logs</h6>
        <div id="history-list"></div>
    </div>

    <!-- 2. LEADERBOARD PAGE -->
    <div id="page-leaderboard" class="app-page">
        <h4 class="fw-bold mb-4">🏆 Hall of Fame</h4>
        <div class="btn-group w-100 mb-4 shadow-sm" style="border-radius:12px; overflow:hidden;">
            <button id="lbl-users" class="btn btn-dark border-secondary py-2 active fw-bold" onclick="loadLB('users')">Top Hunters</button>
            <button id="lbl-teams" class="btn btn-dark border-secondary py-2 fw-bold" onclick="loadLB('teams')">Top Teams</button>
        </div>
        <div id="lb-list"></div>
    </div>

    <!-- 3. GAMES PAGE -->
    <div id="page-games" class="app-page">
        <h4 class="fw-bold mb-1">🎲 Nexus Arena</h4>
        <p class="small text-muted mb-4">Cost: 1 Point | Dynamic System Return: +2 Wager</p>
        
        <!-- Live Custom Physical Sandbox Target Viewport -->
        <div class="card-custom text-center mb-4">
            <div class="arena-viewport" id="viewport-stage">
                <div id="visual-asset" style="font-size:48px;">🎯</div>
            </div>
            <div id="game-res" class="fw-bold small text-muted text-uppercase tracking-wider">Select operation matrix sequence</div>
        </div>

        <!-- System Game Engine Array -->
        <div class="game-card">
            <div>
                <h6 class="mb-0 fw-bold">Cyber Dice Matrix</h6>
                <span class="text-muted small" style="font-size:11px;">Calculated structural roll matrix</span>
            </div>
            <button class="btn-action btn-info text-dark" id="btn-play-dice" onclick="triggerPlay('dice')">Roll</button>
        </div>

        <div class="game-card">
            <div>
                <h6 class="mb-0 fw-bold">Neon Coin Flip</h6>
                <span class="text-muted small" style="font-size:11px;">Binary state distribution vector</span>
            </div>
            <button class="btn-action btn-purple text-white" style="background:var(--neon-purple);" id="btn-play-flip" onclick="triggerPlay('flip')">Flip</button>
        </div>

        <div class="game-card">
            <div>
                <h6 class="mb-0 fw-bold">Quantum Wheel Spin</h6>
                <span class="text-muted small" style="font-size:11px;">Hyper-variate reward field lookup</span>
            </div>
            <button class="btn-action btn-success text-dark" style="background:var(--neon-green);" id="btn-play-spin" onclick="triggerPlay('spin')">Spin</button>
        </div>
        
        <div class="game-card">
            <div>
                <h6 class="mb-0 fw-bold">Lucky Number Core</h6>
                <span class="text-muted small" style="font-size:11px;">Predict integers from 1 to 10</span>
            </div>
            <button class="btn-action btn-warning text-dark" style="background:#f59e0b;" id="btn-play-number" onclick="triggerPlay('number')">Guess</button>
        </div>
    </div>

    <!-- 4. TEAM PAGE -->
    <div id="page-team" class="app-page">
        <!-- Input Block UI -->
        <div id="team-join-ui">
            <h4 class="fw-bold mb-4">🛡️ Team System</h4>
            <div class="card-custom">
                <h6 class="fw-bold mb-1">Create New Team</h6>
                <p class="small text-muted mb-3">Bina name ke team nahi banegi</p>
                <input type="text" id="t-name" class="form-control form-control-cyber mb-3" placeholder="Enter Unique Team Name">
                <button class="btn btn-info w-100 fw-bold py-2" onclick="teamAct('create')">Initialize Team</button>
            </div>
            <div class="text-center my-3 text-muted small fw-bold">— OR —</div>
            <div class="card-custom">
                <h6 class="fw-bold mb-1">Join via Secure Access Code</h6>
                <p class="small text-muted mb-3">Input alpha-numeric authorization sequence</p>
                <input type="text" id="t-code" class="form-control form-control-cyber mb-3" placeholder="Format: TEAM-XXXXXX">
                <button class="btn w-100 text-white fw-bold py-2" style="background:var(--neon-purple);" onclick="teamAct('join')">Authenticate & Join</button>
            </div>
        </div>
        <!-- Profile Dashboard UI -->
        <div id="team-info-ui" style="display:none;">
            <div class="card-custom text-center" style="border: 1px solid var(--border-glow);">
                <h3 id="cur-team-name" class="text-info fw-bold mb-1"></h3>
                <div class="badge bg-dark border border-warning text-warning my-2 p-2 px-3 fs-6" style="border-radius:8px;">
                    🔑 Code: <span id="cur-team-code" class="fw-bold"></span>
                </div>
                <h5 id="cur-team-pts" class="text-success fw-bold mt-2 mb-3"></h5>
                <button class="btn btn-sm btn-outline-danger px-4" style="border-radius:8px;" onclick="teamAct('leave')">Leave Current Team</button>
            </div>
            <h6 class="text-muted fw-bold small text-uppercase mt-4 mb-3">Squad Composition</h6>
            <div id="team-m-list"></div>
        </div>
    </div>

    <!-- PREMIUM BOTTOM NAVIGATION -->
    <div class="nav-bottom">
        <div id="nv-dashboard" class="nav-item active" onclick="showP('dashboard')">DASHBOARD</div>
        <div id="nv-games" class="nav-item" onclick="showP('games')">GAMES</div>
        <div id="nv-leaderboard" class="nav-item" onclick="showP('leaderboard')">LEADERBOARD</div>
        <div id="nv-team" class="nav-item" onclick="showP('team')">TEAM</div>
    </div>

    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        
        const uid = tg.initDataUnsafe?.user?.id || 99999;
        const uname = tg.initDataUnsafe?.user?.first_name || "Beta Tester";
        
        document.getElementById('user-name').innerText = uname;
        document.getElementById('user-display-id').innerText = uid;

        let lockGame = false;

        function verifySubscription() {
            fetch(`/api/verify_gatekeeper?id=${uid}`).then(r=>r.json()).then(d=>{
                if(d.joined) {
                    document.getElementById('gatekeeper-overlay').style.display = 'none';
                    loadDash();
                } else {
                    document.getElementById('gatekeeper-overlay').style.display = 'flex';
                }
            }).catch(()=>{
                // Safe UI bypass fallback if connectivity issues happen during cross-turn rendering
                document.getElementById('gatekeeper-overlay').style.display = 'none';
            });
        }

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
                document.getElementById('stat-points').innerText = Number(d.points).toFixed(1);
                document.getElementById('stat-wager').innerText = Number(d.wager).toFixed(1);
                document.getElementById('stat-rank').innerText = "Rank #" + d.rank;
                
                let h = document.getElementById('history-list');
                if(!d.history || d.history.length === 0){
                    h.innerHTML = '<div class="text-center text-muted py-4 card-custom small fw-bold">No data records synced inside network ledger</div>';
                } else {
                    h.innerHTML = d.history.map(x => {
                        let isLoss = x.pts < 0;
                        return `<div class="history-item">
                            <div>
                                <div class="fw-bold small">${x.reason}</div>
                            </div>
                            <span class="${isLoss ? 'text-danger':'text-success'} fw-bold small">${isLoss ? '':'+'}${Number(x.pts).toFixed(1)}</span>
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
                    l.innerHTML = '<div class="text-center text-muted py-4 card-custom small fw-bold">No records evaluated yet</div>';
                } else {
                    l.innerHTML = d.map((x,i) => `<div class="history-item">
                        <span class="fw-bold small">#${i+1} ${x.name}</span>
                        <span class="text-info fw-bold small">${Number(x.pts).toFixed(1)} Pts</span>
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
                    document.getElementById('cur-team-pts').innerText = "Team Total: " + Number(d.total).toFixed(1) + " Points";
                    document.getElementById('team-m-list').innerHTML = d.m.map(x => `<div class="history-item">
                        <span class="small fw-bold">${x.name}</span><span class="text-warning small fw-bold">${Number(x.pts).toFixed(1)} Pts</span>
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
                alert("🔴 Error: Team Name mandatory hai!");
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
            
            let stage = document.getElementById('viewport-stage');
            let resDiv = document.getElementById('game-res');
            
            resDiv.innerText = "Synchronizing transaction allocation structural frame...";
            resDiv.className = "fw-bold small text-warning text-uppercase";

            // Setup true structural elements inside the viewport stage container
            let timer = 1400; 
            if(mode === 'dice') {
                stage.innerHTML = `
                    <div class="dice-box" id="live-dice">
                        <div class="dice-face f1">⚀</div><div class="dice-face f2">⚁</div>
                        <div class="dice-face f3">⚂</div><div class="dice-face f4">⚃</div>
                        <div class="dice-face f5">⚄</div><div class="dice-face f6">⚅</div>
                    </div>`;
                let dBox = document.getElementById('live-dice');
                let deg = 0;
                var animInt = setInterval(() => { deg += 45; dBox.style.transform = `rotateX(${deg}deg) rotateY(${deg}deg)`; }, 80);
            } else if(mode === 'flip') {
                stage.innerHTML = `
                    <div class="coin-box" id="live-coin">
                        <div class="coin-face coin-front">👑</div>
                        <div class="coin-face coin-back">❌</div>
                    </div>`;
                let cBox = document.getElementById('live-coin');
                let deg = 0;
                var animInt = setInterval(() => { deg += 50; cBox.style.transform = `rotateY(${deg}deg)`; }, 60);
            } else if(mode === 'spin') {
                stage.innerHTML = `<div id="live-spin" style="font-size:64px; transition: transform 0.1s linear;">🎡</div>`;
                let sBox = document.getElementById('live-spin');
                let deg = 0;
                var animInt = setInterval(() => { deg += 40; sBox.style.transform = `rotate(${deg}deg)`; }, 50);
            } else if(mode === 'number') {
                stage.innerHTML = `<div id="live-num" style="font-size:54px; font-weight:900;" class="text-info">?</div>`;
                var animInt = setInterval(() => { document.getElementById('live-num').innerText = Math.floor(Math.random()*10)+1; }, 70);
            }

            fetch('/api/play', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({id:uid, game:mode})
            }).then(r=>r.json()).then(d=>{
                setTimeout(() => {
                    clearInterval(animInt);
                    lockGame = false;
                    
                    if(d.res === 'WIN' || d.res === 'LOSE') {
                        if(mode === 'dice') {
                            let faces = {1:[0,0], 2:[0,-90], 3:[-90,0], 4:[90,0], 5:[0,90], 6:[180,0]};
                            let targetRot = faces[d.val] || [0,0];
                            let finalDice = document.getElementById('live-dice');
                            if(finalDice) finalDice.style.transform = `rotateX(${targetRot[0]}deg) rotateY(${targetRot[1]}deg)`;
                        } else if(mode === 'flip') {
                            let finalCoin = document.getElementById('live-coin');
                            if(finalCoin) finalCoin.style.transform = d.val === 'HEADS' ? 'rotateY(0deg)' : 'rotateY(180deg)';
                        } else if(mode === 'spin') {
                            let finalSpin = document.getElementById('live-spin');
                            if(finalSpin) { finalSpin.style.transform = 'rotate(0deg)'; finalSpin.innerText = d.res === 'WIN' ? "💎" : "💥"; }
                        } else if(mode === 'number') {
                            let finalNum = document.getElementById('live-num');
                            if(finalNum) { finalNum.innerText = d.val; finalNum.className = d.res==='WIN'?'text-success':'text-danger'; }
                        }
                        
                        if(d.res === 'WIN') {
                            resDiv.innerText = `🎉 MATCH SUCCESSFUL! Result: ${d.val} (+2.0 Wager)`;
                            resDiv.className = "fw-bold small text-success text-uppercase";
                        } else {
                            resDiv.innerText = `⚡ ANOMALY LOSS DETECTED! Result: ${d.val} (-1.0 Point)`;
                            resDiv.className = "fw-bold small text-danger text-uppercase";
                        }
                    } else {
                        stage.innerHTML = `<div style="font-size:48px;">🎯</div>`;
                        resDiv.innerText = "Operational Matrix Idle";
                        resDiv.className = "fw-bold small text-muted text-uppercase";
                        alert(d.msg);
                    }
                }, timer);
            }).catch(() => {
                clearInterval(animInt);
                lockGame = false;
                stage.innerHTML = `<div style="font-size:48px;">🎯</div>`;
                resDiv.innerText = "Connectivity breakdown error";
            });
        }
        
        // Automated Initial Verification sequence call
        verifySubscription();
    </script>
</body>
</html>
"""

# ================= API ENDPOINTS CONFIGURATION =================

@app.route('/')
def home(): 
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/verify_gatekeeper')
def verify_gatekeeper():
    uid = int(request.args.get('id', 0))
    # Standard cross-thread polling dynamic execution environment loop structure mapping
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        member = loop.run_until_complete(bot.get_chat_member(chat_id=REQUIRED_CHANNEL_ID, user_id=uid))
        if member.status in ['member', 'administrator', 'creator']:
            return jsonify({"joined": True})
    except Exception as e:
        print(f"Gatekeeper error checking user subscription state: {e}")
    finally:
        loop.close()
    return jsonify({"joined": False})

@app.route('/api/user')
def get_user():
    uid = int(request.args.get('id'))
    name = request.args.get('name')
    u = users_col.find_one({"user_id": uid})
    if not u:
        u = {"user_id": uid, "username": name, "points": 10.0, "wager": 0.0, "team_code": None}
        users_col.insert_one(u)
    else:
        users_col.update_one({"user_id": uid}, {"$set": {"username": name}})
        
    all_u = list(users_col.find().sort("points", -1))
    rank = next((i + 1 for i, item in enumerate(all_u) if item["user_id"] == uid), "--")
    
    hist = list(history_col.find({"user_id": uid}).sort("_id", -1).limit(5))
    h_data = [{"reason": x['reason'], "pts": x['points']} for x in hist]
    return jsonify({"points": u.get('points', 0.0), "wager": u.get('wager', 0.0), "rank": rank, "history": h_data})

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
    tname = t_meta['name'] if t_meta else "Unknown Team"
    
    members = list(users_col.find({"team_code": tcode}))
    m_data = [{"name": x['username'], "pts": x['points']} for x in members]
    total = sum(x.get('points', 0.0) for x in members)
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
        
        new_code = "TEAM-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        teams_col.insert_one({"code": new_code, "name": tname, "creator": uid})
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": new_code}})
        return jsonify({"msg": f"🛡️ Team Created! Code: {new_code}"})
        
    elif act == 'join':
        if u.get('team_code'): return jsonify({"msg": "🔴 Pehle old team leave karke aao!"})
        target_team = teams_col.find_one({"code": tcode})
        if not target_team: return jsonify({"msg": "🔴 System mismatch: Invalid Access Code!"})
        
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": tcode}})
        return jsonify({"msg": f"✅ Welcome to {target_team['name']}!"})
        
    elif act == 'leave':
        if not u.get('team_code'): return jsonify({"msg": "Aap pehle se kisi team me nahi ho!"})
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": None}})
        return jsonify({"msg": "🚪 Team deployment abandoned successfully."})

@app.route('/api/play', methods=['POST'])
def play():
    data = request.json
    uid = int(data['id'])
    game_mode = data.get('game', 'arena')
    u = users_col.find_one({"user_id": uid})
    
    if not u or u.get('points', 0.0) < 1.0: 
        return jsonify({"res": "ERR", "msg": "Insufficient wallet balance to allocate stake!"})
    
    is_win = random.random() < 0.40
    outcome_val = ""
    
    # Calculate exact internal outcomes beforehand to sync directly with UI state
    if game_mode == 'dice':
        outcome_val = random.randint(4, 6) if is_win else random.randint(1, 3)
    elif game_mode == 'flip':
        outcome_val = "HEADS" if is_win else "TAILS"
    elif game_mode == 'spin':
        outcome_val = "JACKPOT" if is_win else "ZONK"
    elif game_mode == 'number':
        outcome_val = random.randint(7, 10) if is_win else random.randint(1, 6)

    if is_win:
        users_col.update_one({"user_id": uid}, {"$inc": {"wager": 2.0}})
        history_col.insert_one({"user_id": uid, "reason": f"Won {game_mode.upper()} match", "points": 2.0})
        res = "WIN"
    else:
        users_col.update_one({"user_id": uid}, {"$inc": {"points": -1.0}})
        history_col.insert_one({"user_id": uid, "reason": f"Lost {game_mode.upper()} stake", "points": -1.0})
        res = "LOSE"
        
    return jsonify({"res": res, "val": str(outcome_val)})

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

# ================= ASYNC ORCHESTRATION SHUTTLE LAYER =================
async def main():
    # Start Flask running inside a background daemon thread completely detached from async loop
    threading.Thread(target=run_f, daemon=True).start()
    print("🚀 Web backend services initialized on sub-thread.")
    
    # Run long polling directly via current main orchestration context thread
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("⚙️ Main Engine shutdown gracefully.")
