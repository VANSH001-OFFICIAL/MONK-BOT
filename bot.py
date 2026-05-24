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

# ================= FLASK SERVER WITH ADVANCED GAME ANIMATIONS =================
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Monk Premium Interactive Arena</title>
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
            --text-main: #ffffff;
        }

        * { 
            box-sizing: border-box; 
            -webkit-tap-highlight-color: transparent; 
            user-select: none;
        }
        
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

        #app-viewport {
            height: 100vh; overflow-y: auto; padding: 25px 20px 130px 20px;
            display: none;
        }
        .view-section { display: none; }
        .view-section.active { display: block; animation: fadeInUp 0.4s ease-out; }

        .gold-card {
            background: var(--bg-card); 
            border: 1.5px solid rgba(255, 215, 0, 0.25);
            border-radius: 20px; padding: 22px; margin-bottom: 20px;
            box-shadow: 0 12px 35px rgba(0,0,0,0.7);
            position: relative; overflow: hidden;
        }
        .stat-header { font-family: 'Orbitron', sans-serif; font-size: 12px; color: var(--accent-gold); margin-bottom: 6px; font-weight: 900; }
        .stat-value { font-family: 'Orbitron', sans-serif; font-size: 32px; font-weight: 900; color: #ffffff; }

        .btn-monk {
            background: linear-gradient(135deg, #FFD700 0%, #b8860b 100%);
            color: #000000; border: none; padding: 15px; border-radius: 14px;
            width: 100%; font-family: 'Orbitron', sans-serif; font-weight: 900;
            text-transform: uppercase; margin-bottom: 14px;
            box-shadow: 0 5px 20px rgba(255,215,0,0.35);
        }

        .monk-input {
            background-color: #151515 !important;
            border: 2px solid rgba(255, 215, 0, 0.4) !important;
            color: #ffffff !important;
            border-radius: 10px; padding: 12px; font-size: 15px; width: 100%; margin-bottom: 15px;
        }

        .tab-btn-group { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn {
            flex: 1; padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255, 215, 0, 0.2); color: #aaaaaa; font-family: 'Orbitron'; font-weight: 900;
        }
        .tab-btn.active { background: var(--monk-gold); color: #000000; }

        .rank-row {
            display: flex; align-items: center; justify-content: space-between;
            padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.08); background: rgba(255,255,255,0.01);
        }
        .history-card {
            background: rgba(30, 30, 30, 0.85); border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px; padding: 12px 18px; margin-bottom: 10px; display: flex; justify-content: space-between;
        }

        /* ================= GAME ANIMATIONS ENGINE VISUAL LAYOUTS ================= */
        .arena-container {
            display: flex; flex-direction: column; gap: 25px; margin-bottom: 30px;
        }
        .game-wrapper {
            background: rgba(15, 15, 15, 0.95); border: 2px dashed rgba(255, 215, 0, 0.3);
            border-radius: 16px; padding: 20px; text-align: center; position: relative;
        }
        .game-title {
            font-family: 'Orbitron'; font-weight: 900; color: var(--monk-gold); font-size: 14px;
            text-transform: uppercase; margin-bottom: 15px; letter-spacing: 1px;
        }

        /* Module 1: Scratch Card Layout */
        .scratch-box {
            position: relative; width: 220px; height: 130px; margin: 0 auto;
            border-radius: 12px; overflow: hidden; background: #111;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
        }
        .scratch-underlying-result {
            position: absolute; top:0; left:0; width:100%; height:100%;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            font-family: 'Orbitron'; font-weight: 900; font-size: 20px; z-index: 1;
        }
        .scratch-canvas {
            position: absolute; top:0; left:0; width:100%; height:100%; z-index: 2; cursor: crosshair;
        }

        /* Module 2: 3D Dice Layout */
        .scene-dice {
            width: 80px; height: 80px; margin: 20px auto; perspective: 400px;
        }
        .dice-cube {
            width: 100%; height: 100%; position: relative; transform-style: preserve-3d;
            transform: translateZ(-40px); transition: transform 1.5s cubic-bezier(0.2, 0.8, 0.3, 1);
        }
        .dice-face {
            position: absolute; width: 80px; height: 80px; background: #ffffff;
            border: 3px solid var(--monk-gold); border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 36px; font-weight: 900; color: #000000; box-shadow: inset 0 0 15px rgba(0,0,0,0.2);
        }
        .face-1 { transform: rotateY(0deg) translateZ(40px); }
        .face-2 { transform: rotateY(90deg) translateZ(40px); }
        .face-3 { transform: rotateX(90deg) translateZ(40px); }
        .face-4 { transform: rotateX(-90deg) translateZ(40px); }
        .face-5 { transform: rotateY(-90deg) translateZ(40px); }
        .face-6 { transform: rotateY(180deg) translateZ(40px); }

        /* Module 3: 3D Coin Layout */
        .coin-box {
            width: 85px; height: 85px; margin: 15px auto; perspective: 600px;
        }
        .coin-circle {
            width: 100%; height: 100%; position: relative; transform-style: preserve-3d;
            transition: transform 1.2s cubic-bezier(0.25, 1, 0.5, 1);
        }
        .coin-side {
            position: absolute; width: 100%; height: 100%; border-radius: 50%;
            backface-visibility: hidden; display: flex; align-items: center; justify-content: center;
            font-family: 'Orbitron'; font-weight: 900; font-size: 13px; border: 4px solid var(--monk-gold);
            box-shadow: 0 0 15px rgba(255,215,0,0.3);
        }
        .side-front { background: radial-gradient(circle, #ffd700, #b8860b); color: #000000; }
        .side-back { background: #222222; color: var(--monk-gold); transform: rotateY(180deg); }

        /* Module 4: Canvas Spin Wheel Layout */
        .wheel-container-box {
            position: relative; width: 210px; height: 210px; margin: 0 auto;
        }
        .wheel-canvas {
            width: 100%; height: 100%; border-radius: 50%;
            border: 5px solid var(--monk-gold); box-shadow: 0 0 20px rgba(0,0,0,0.6);
            transition: transform 2.5s cubic-bezier(0.1, 0.8, 0.1, 1);
        }
        .wheel-pin {
            position: absolute; top: -10px; left: 50%; transform: translateX(-50%);
            width: 0; height: 0; border-left: 12px solid transparent; border-right: 12px solid transparent;
            border-top: 22px solid #ff0055; z-index: 10;
        }
    </style>
</head>
<body>

    <div id="splash-screen">
        <div class="monk-logo-container">
            <div class="monk-ring"></div>
            <div class="monk-center">M</div>
        </div>
        <div class="splash-text">Monk Task</div>
        <div style="margin-top: 15px; font-size: 11px; color: #666; font-family: 'Orbitron';">Interactive Canvas Core Active...</div>
    </div>

    <div id="app-viewport">
        
        <!-- VIEW: DASHBOARD -->
        <div id="view-task" class="view-section active">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <div style="font-size: 11px; color: var(--accent-gold); font-weight: 900; text-transform: uppercase;">Operative Profile</div>
                    <h4 id="ui-username" style="font-family: 'Orbitron'; font-weight: 900;">---</h4>
                </div>
                <div class="text-end">
                    <div id="ui-rank" style="background: rgba(255,215,0,0.1); padding: 6px 16px; border-radius: 20px; color: var(--monk-gold); font-size: 12px; font-weight: 900; border: 1.5px solid var(--monk-gold);">Rank --</div>
                </div>
            </div>

            <div class="gold-card">
                <div class="stat-header">Available Main Credits</div>
                <div class="stat-value" id="ui-points">0.00</div>
                <div style="margin-top: 12px; height: 6px; background: #222; border-radius: 3px;">
                    <div id="ui-progress" style="width: 0%; height: 100%; background: var(--monk-gold); border-radius: 3px;"></div>
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
                        <div class="stat-header">System Matrix</div>
                        <div style="font-family: 'Orbitron'; font-weight: 900; font-size: 20px; color: #4ade80;">Active</div>
                    </div>
                </div>
            </div>

            <h6 style="font-family: 'Orbitron'; font-size: 13px; color: var(--accent-gold); margin-bottom: 15px; font-weight: 900;">SYSTEM TRANSACTION LOGS</h6>
            <div id="ui-history"></div>
        </div>

        <!-- VIEW: FULLY ANIMATED ARENA -->
        <div id="view-arena" class="view-section">
            <h4 class="text-center mb-4" style="font-family: 'Orbitron'; font-weight: 900; letter-spacing: 2px;">MONK ANIMATION ARENA</h4>
            <p class="text-center text-muted small" style="margin-bottom: 25px;">Each attempt costs 1 Wallet Credit. 40% Win Strategy active across all parameters.</p>
            
            <div class="arena-container">
                
                <!-- GAME 1: SCRATCH CARD -->
                <div class="game-wrapper">
                    <div class="game-title">✨ Scratch Card Module</div>
                    <div class="scratch-box" id="scratchCardBox">
                        <div class="scratch-underlying-result" id="scratchResultContainer">
                            <span id="scratchStatusText" style="color: #fff;">PROCESSING...</span>
                            <small id="scratchWinnings" style="color: var(--monk-gold); font-size:12px;"></small>
                        </div>
                        <canvas class="scratch-canvas" id="scratchCanvas" width="220" height="130"></canvas>
                    </div>
                    <button class="btn-monk btn-sm mt-3" style="padding:8px; font-size:11px;" onclick="resetAndActivateScratch()">Initialize New Scratch</button>
                </div>

                <!-- GAME 2: 3D DICE ROLLER -->
                <div class="game-wrapper">
                    <div class="game-title">🎲 3D Dynamic Dice</div>
                    <div class="scene-dice">
                        <div class="dice-cube" id="visualDiceCube">
                            <div class="dice-face face-1">1</div>
                            <div class="dice-face face-2">2</div>
                            <div class="dice-face face-3">3</div>
                            <div class="dice-face face-4">4</div>
                            <div class="dice-face face-5">5</div>
                            <div class="dice-face face-6">6</div>
                        </div>
                    </div>
                    <div id="dice-log" class="small text-uppercase text-muted mb-2 font-monospace">Awaiting Roll Trigger</div>
                    <button class="btn-monk m-0" onclick="triggerDiceRoll()">Roll Cube</button>
                </div>

                <!-- GAME 3: PHOENIX COIN FLIP -->
                <div class="game-wrapper">
                    <div class="game-title">🪙 3D Core Coin Flip</div>
                    <div class="coin-box">
                        <div class="coin-circle" id="visualCoinCircle">
                            <div class="coin-side side-front">MONK</div>
                            <div class="coin-side side-back">VAULT</div>
                        </div>
                    </div>
                    <div id="coin-log" class="small text-uppercase text-muted mb-2 font-monospace">Awaiting Flip Protocol</div>
                    <button class="btn-monk m-0" onclick="triggerCoinFlip()">Flip Coin</button>
                </div>

                <!-- GAME 4: SPIN ORACLE WHEEL -->
                <div class="game-wrapper">
                    <div class="game-title">🎡 4-Slice Oracle Wheel</div>
                    <div class="wheel-container-box">
                        <div class="wheel-pin"></div>
                        <canvas class="wheel-canvas" id="wheelCanvas" width="210" height="210"></canvas>
                    </div>
                    <div id="wheel-log" class="small text-uppercase text-muted mt-3 mb-2 font-monospace">Awaiting Spin Vector</div>
                    <button class="btn-monk m-0" onclick="triggerWheelSpin()">Spin Vector</button>
                </div>

            </div>
        </div>

        <!-- VIEW: LEADERBOARD -->
        <div id="view-ranks" class="view-section">
            <h4 class="mb-4" style="font-family: 'Orbitron'; font-weight: 900;">GLOBAL DASHBOARD</h4>
            <div class="tab-btn-group">
                <button id="tab-users" class="tab-btn active" onclick="switchLeaderboardTab('users')">Top Users</button>
                <button id="tab-teams" class="tab-btn" onclick="switchLeaderboardTab('teams')">Top Squads</button>
            </div>
            <div id="ui-leaderboard"></div>
        </div>

        <!-- VIEW: SQUAD -->
        <div id="view-team" class="view-section">
            <div id="team-setup-ui">
                <h4 class="mb-4" style="font-family: 'Orbitron'; font-weight: 900;">SQUAD NETWORK</h4>
                <div class="gold-card">
                    <div class="stat-header">Form Squad Unit</div>
                    <input type="text" id="inp-tname" class="monk-input" placeholder="Squad Designation Name">
                    <button class="btn-monk" style="padding: 10px; margin: 0;" onclick="teamAction('create')">Initialize Unit</button>
                </div>
                <div class="gold-card">
                    <div class="stat-header">Authenticate Squad Entry</div>
                    <input type="text" id="inp-tcode" class="monk-input" placeholder="MONK-XXXXXX">
                    <button class="btn-monk" style="padding: 10px; margin: 0; background: #333;" onclick="teamAction('join')">Verify Code</button>
                </div>
            </div>
            
            <div id="team-active-ui" style="display:none;">
                <div class="gold-card text-center">
                    <h3 id="active-team-name" style="font-family: 'Orbitron'; color: var(--monk-gold);">---</h3>
                    <code id="active-team-code" class="d-block mb-3" style="color: #fff; background: #222; padding: 8px; border-radius: 6px;">---</code>
                    <button class="btn btn-outline-danger btn-sm w-100" onclick="teamAction('leave')">Decommission Position</button>
                </div>
                <h6 class="mt-4 mb-3" style="font-family: 'Orbitron'; font-size: 12px; color: var(--accent-gold);">Squad Operatives Connection</h6>
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

        const USER_ID = tg.initDataUnsafe?.user?.id || 987654321;
        const USER_NAME = tg.initDataUnsafe?.user?.first_name || "Monk Operative";
        
        let currentLbTab = "users";
        let scratchInitialized = false;
        let isScratchingLocked = false;

        window.addEventListener('load', () => {
            initWheelGraphics();
            setTimeout(() => {
                const splash = document.getElementById('splash-screen');
                splash.style.opacity = '0';
                setTimeout(() => {
                    splash.style.display = 'none';
                    document.getElementById('app-viewport').style.display = 'block';
                    refreshDashboard();
                    resetAndActivateScratch();
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
                document.getElementById('ui-progress').style.width = Math.min((data.points / 500) * 100, 100) + "%";

                document.getElementById('ui-history').innerHTML = data.history.map(h => `
                    <div class="history-card">
                        <span style="color:#ffffff; font-size:13px; font-weight:600;">${h.reason}</span>
                        <span style="color: ${h.pts >= 0 ? '#4ade80':'#f87171'}; font-weight:900; font-family:'Orbitron';">
                            ${h.pts >= 0 ? '+':''}${h.pts.toFixed(2)}
                        </span>
                    </div>
                `).join('') || '<div class="text-center text-muted small py-3">No logs in system node</div>';
            } catch (e) { console.error(e); }
        }

        // ================= SCRATCH CARD CANVAS IMPLEMENTATION =================
        function resetAndActivateScratch() {
            const canvas = document.getElementById('scratchCanvas');
            const ctx = canvas.getContext('2d');
            isScratchingLocked = false;
            
            document.getElementById('scratchStatusText').innerText = "Scratch Mask Area";
            document.getElementById('scratchWinnings').innerText = "";
            
            // Draw Gold Surface Layer
            ctx.fillStyle = '#b8860b';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Overlay Text Mask "MONK"
            ctx.font = '900 28px Orbitron';
            ctx.fillStyle = '#FFD700';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('MONK', canvas.width/2, canvas.height/2);
            
            // Add technical noise mapping overlay
            ctx.fillStyle = 'rgba(255,255,255,0.08)';
            for(let i=0; i<400; i++) {
                ctx.fillRect(Math.random()*canvas.width, Math.random()*canvas.height, 2, 2);
            }

            let isDrawing = false;
            
            function scratchExecution(e) {
                if(isScratchingLocked) return;
                const rect = canvas.getBoundingClientRect();
                const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
                const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
                
                ctx.globalCompositeOperation = 'destination-out';
                ctx.beginPath();
                ctx.arc(x, y, 16, 0, Math.PI * 2);
                ctx.fill();
                
                checkScratchPercentage();
            }

            canvas.onmousedown = () => { isDrawing = true; evalScratchCost(); };
            canvas.onmousemove = (e) => { if(isDrawing) scratchExecution(e); };
            canvas.onmouseup = () => { isDrawing = false; };
            
            canvas.ontouchstart = () => { isDrawing = true; evalScratchCost(); };
            canvas.ontouchmove = (e) => { if(isDrawing) scratchExecution(e); };
            canvas.ontouchend = () => { isDrawing = false; };
        }

        async function evalScratchCost() {
            if(isScratchingLocked) return;
            isScratchingLocked = true; // Temporary lock to prevent multiple balance deductions
            
            const res = await fetch('/api/play', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: USER_ID, game: 'scratch'})
            });
            const data = await res.json();
            
            if(data.res === 'ERR') {
                alert(data.msg);
                resetAndActivateScratch();
            } else {
                canvasDataResult = data;
                document.getElementById('scratchStatusText').innerText = data.res === 'WIN' ? '💎 WINNER' : '💥 LOSE';
                document.getElementById('scratchWinnings').innerText = data.val;
                refreshDashboard();
            }
        }

        function checkScratchPercentage() {
            const canvas = document.getElementById('scratchCanvas');
            const ctx = canvas.getContext('2d');
            const imgData = ctx.getImageData(0,0,canvas.width,canvas.height);
            let cleared = 0;
            for(let i=0; i<imgData.data.length; i+=4) {
                if(imgData.data[i+3] === 0) cleared++;
            }
            if(cleared / (canvas.width * canvas.height) > 0.45) {
                ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear entire mask once matched threshold
            }
        }

        // ================= 3D DICE ENGINE CORE ANIMATIONS =================
        async function triggerDiceRoll() {
            const cube = document.getElementById('visualDiceCube');
            const log = document.getElementById('dice-log');
            
            log.innerText = "Transmitting rolling protocols...";
            
            const res = await fetch('/api/play', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: USER_ID, game: 'dice'})
            });
            const data = await res.json();
            
            if(data.res === 'ERR') { alert(data.msg); log.innerText = data.msg; return; }

            // Generates completely random value 1-6 for target layout matching matrix mechanics
            const targetFace = Math.floor(Math.random() * 6) + 1;
            
            // Complex multi-axis rotational matrix application to ensure visible movement mechanics
            const extraRotX = 720 + (Math.random() * 360);
            const extraRotY = 720 + (Math.random() * 360);
            
            cube.style.transform = `rotateX(${extraRotX}deg) rotateY(${extraRotY}deg)`;
            
            setTimeout(() => {
                // Exact alignment facing matrix settings mapping
                let finalTransform = "";
                switch(targetFace) {
                    case 1: finalTransform = "rotateY(0deg) translateZ(40px)"; break;
                    case 2: finalTransform = "rotateY(-90deg) translateZ(40px)"; break;
                    case 3: finalTransform = "rotateX(-90deg) translateZ(40px)"; break;
                    case 4: finalTransform = "rotateX(90deg) translateZ(40px)"; break;
                    case 5: finalTransform = "rotateY(90deg) translateZ(40px)"; break;
                    case 6: finalTransform = "rotateY(180deg) translateZ(40px)"; break;
                }
                cube.style.transform = finalTransform;
                log.innerText = `${data.res}: LANDED ON FACE [${targetFace}] -> ${data.val}`;
                refreshDashboard();
            }, 1500);
        }

        // ================= 3D COIN MECHANICS CORE ANIMATIONS =================
        async function triggerCoinFlip() {
            const coin = document.getElementById('visualCoinCircle');
            const log = document.getElementById('coin-log');
            log.innerText = "Flipping system vectors...";

            const res = await fetch('/api/play', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: USER_ID, game: 'flip'})
            });
            const data = await res.json();
            if(data.res === 'ERR') { alert(data.msg); log.innerText = data.msg; return; }

            const randomSpins = 1080 + (data.res === 'WIN' ? 0 : 180); 
            coin.style.transform = `rotateY(${randomSpins}deg)`;

            setTimeout(() => {
                log.innerText = `${data.res}: CELL SINK -> ${data.val}`;
                refreshDashboard();
            }, 1200);
        }

        // ================= VECTOR WHEEL MATRIX ANIMATIONS =================
        function initWheelGraphics() {
            const canvas = document.getElementById('wheelCanvas');
            const ctx = canvas.getContext('2d');
            const colors = ['#222222', '#ffd700', '#111111', '#c5a059'];
            const labels = ['LOSE', 'WIN', 'LOSE', 'WIN'];
            
            let angle = 0;
            for(let i=0; i<4; i++) {
                ctx.fillStyle = colors[i];
                ctx.beginPath();
                ctx.moveTo(105, 105);
                ctx.arc(105, 105, 105, angle, angle + Math.PI/2);
                ctx.lineTo(105, 105);
                ctx.fill();
                
                // Add labels dynamically directly into geometry layout vector paths
                ctx.save();
                ctx.translate(105, 105);
                ctx.rotate(angle + Math.PI/4);
                ctx.fillStyle = (i % 2 === 1) ? '#000000' : '#ffffff';
                ctx.font = '900 12px Orbitron';
                ctx.fillText(labels[i], 45, 5);
                ctx.restore();
                
                angle += Math.PI/2;
            }
        }

        async function triggerWheelSpin() {
            const wheel = document.getElementById('wheelCanvas');
            const log = document.getElementById('wheel-log');
            log.innerText = "Accelerating rotation matrix...";

            const res = await fetch('/api/play', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: USER_ID, game: 'spin'})
            });
            const data = await res.json();
            if(data.res === 'ERR') { alert(data.msg); log.innerText = data.msg; return; }

            // Target calculations matching visual indicators precisely
            let targetDegree = data.res === 'WIN' ? 90 : 0; 
            let fullSpins = 1440 + targetDegree;
            wheel.style.transform = `rotate(${fullSpins}deg)`;

            setTimeout(() => {
                log.innerText = `${data.res} RESULT VECTOR: ${data.val}`;
                // Return structure matrix back gracefully
                wheel.style.transition = 'none';
                wheel.style.transform = `rotate(${targetDegree}deg)`;
                setTimeout(() => { wheel.style.transition = 'transform 2.5s cubic-bezier(0.1, 0.8, 0.1, 1)'; }, 50);
                refreshDashboard();
            }, 2500);
        }

        // ================= TAB MANAGEMENT AND EXTRA LOGIC =================
        function switchLeaderboardTab(tab) {
            currentLbTab = tab;
            document.getElementById('tab-users').classList.remove('active');
            document.getElementById('tab-teams').classList.remove('active');
            document.getElementById('tab-' + tab).classList.add('active');
            loadLeaderboard();
        }

        async function loadLeaderboard() {
            const res = await fetch(`/api/lb?type=${currentLbTab}`);
            const data = await res.json();
            if(currentLbTab === 'users') {
                document.getElementById('ui-leaderboard').innerHTML = data.map((u, i) => `
                    <div class="rank-row">
                        <span style="font-family:'Orbitron'; color:var(--monk-gold); font-weight:900;">#${i+1}</span>
                        <span style="color:#fff; font-weight:600; flex-grow:1; margin-left:15px;">${u.name}</span>
                        <span style="font-family:'Orbitron'; color:var(--monk-gold);">${u.pts.toFixed(2)} LP</span>
                    </div>
                `).join('');
            } else {
                document.getElementById('ui-leaderboard').innerHTML = data.map((t, i) => `
                    <div class="rank-row">
                        <span style="font-family:'Orbitron'; color:var(--monk-gold); font-weight:900;">#${i+1}</span>
                        <span style="color:#fff; font-weight:600; flex-grow:1; margin-left:15px;">${t.name}</span>
                        <span style="font-family:'Orbitron'; color:var(--monk-gold);">${t.cumulative_pts.toFixed(2)} SQ</span>
                    </div>
                `).join('');
            }
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
                    <div class="rank-row"><span>${m.name}</span><span class="text-warning">${m.pts.toFixed(2)}</span></div>
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

# ================= SERVER BACKEND CORE PROCESSING LOGIC =================

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
    
    if not u:
        return jsonify({"res": "ERR", "msg": "User account interface disconnected."})
    if u.get('points', 0.0) < 1.0:
        return jsonify({"res": "ERR", "msg": "Insufficient Main Credits (1.00 needed)"})
        
    # Strictly consume 1 point on every execution across all systems
    users_col.update_one({"user_id": uid}, {"$inc": {"points": -1.0}})
    
    # Precise 40% Win Strategy Matrix Core Rule Update
    win = random.random() < 0.40
    if win:
        users_col.update_one({"user_id": uid}, {"$inc": {"wager": 2.0}})
        history_col.insert_one({"user_id": uid, "reason": f"Game match won", "points": -1.0})
        return jsonify({"res": "WIN", "val": "+2.00 Wager Tokens"})
    else:
        history_col.insert_one({"user_id": uid, "reason": f"Game match lost", "points": -1.0})
        return jsonify({"res": "LOSE", "val": "No Rewards Dispatched"})

@app.route('/api/lb')
def leaderboard():
    ltype = request.args.get('type', 'users')
    if ltype == 'users':
        data = users_col.find().sort("points", -1).limit(25)
        return jsonify([{"name": x['username'], "pts": x['points']} for x in data])
    else:
        pipelines = [
            {"$group": {"_id": "$team_code", "cumulative_pts": {"$sum": "$points"}}},
            {"$match": {"_id": {"$ne": None}}}
        ]
        aggregated = list(users_col.aggregate(pipelines))
        teams_list = []
        for item in aggregated:
            team_meta = teams_col.find_one({"code": item["_id"]})
            if team_meta:
                teams_list.append({"name": team_meta["name"], "cumulative_pts": item["cumulative_pts"]})
        teams_list.sort(key=lambda x: x["cumulative_pts"], reverse=True)
        return jsonify(teams_list[:20])

@app.route('/api/team')
def team_info():
    uid = int(request.args.get('id', 0))
    u = users_col.find_one({"user_id": uid})
    if not u or not u.get('team_code'): return jsonify({"has": False})
    t = teams_col.find_one({"code": u['team_code']})
    members = list(users_col.find({"team_code": u['team_code']}))
    return jsonify({
        "has": True, "name": t['name'], "code": t['code'],
        "m": [{"name": x['username'], "pts": x['points']} for x in members]
    })

@app.route('/api/team_act', methods=['POST'])
def team_action():
    d = request.json
    uid, act, tname, tcode = d['id'], d['action'], d.get('tname'), d.get('tcode')
    if act == 'create':
        code = "MONK-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        teams_col.insert_one({"code": code, "name": tname})
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": code}})
        return jsonify({"msg": f"Squad Active: {code}"})
    elif act == 'join':
        exists = teams_col.find_one({"code": tcode.strip()})
        if exists:
            users_col.update_one({"user_id": uid}, {"$set": {"team_code": tcode.strip()}})
            return jsonify({"msg": "Successfully logged inside squad grid."})
        return jsonify({"msg": "Squad code validation failed."})
    elif act == 'leave':
        users_col.update_one({"user_id": uid}, {"$set": {"team_code": None}})
        return jsonify({"msg": "Squad linkages disconnected."})

# ================= TELEGRAM TELEMETRY CONTROL PANEL BOT =================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(CommandStart())
async def start_handler(m: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Enter Monk Arena ⛩️", web_app=WebAppInfo(url=MINI_APP_URL))
    ]])
    await m.answer(
        f"<b>Welcome Operative {m.from_user.first_name}</b>\n\n"
        "All fully animated canvas interactive arenas are deployment locked and functional. Launch console directly below.",
        reply_markup=kb, parse_mode="HTML"
    )

@dp.message(Command("add"))
async def add_command_initiator(m: Message, state: FSMContext):
    await m.answer("<b>[ADMIN PROTOCOL]</b>\nPlease post the standard label string reference for transaction history logs tracking:")
    await state.set_state(AdminAddStates.waiting_for_reason)

@dp.message(AdminAddStates.waiting_for_reason)
async def add_reason_catcher(m: Message, state: FSMContext):
    await state.update_data(reason=m.text.strip())
    await m.answer(
        "<b>[LABEL RESOLVED]</b>\nProvide block matrix mapping details cleanly formatted via multi-lines:\n\n"
        "<code>id amount\nid amount</code>", parse_mode="HTML"
    )
    await state.set_state(AdminAddStates.waiting_for_data)

@dp.message(AdminAddStates.waiting_for_data)
async def add_data_processor(m: Message, state: FSMContext):
    state_data = await state.get_data()
    log_reason = state_data.get('reason', 'Refund Processing')
    lines = m.text.strip().split('\n')
    s_logs, e_logs = [], []
    
    for line in lines:
        if not line.strip(): continue
        parts = line.split()
        if len(parts) != 2:
            e_logs.append(f"Broken schema format: '{line}'")
            continue
        try:
            target_uid = int(parts[0])
            add_amount = float(parts[1])
            user_record = users_col.find_one({"user_id": target_uid})
            if not user_record:
                e_logs.append(f"UID {target_uid}: Missing node entry profile.")
                continue
                
            current_wager = user_record.get('wager', 0.0)
            allowed_conversion_units = add_amount * 2.0
            actual_conversion_processed = min(current_wager, allowed_conversion_units)
            
            new_points_balance = user_record.get('points', 0.0) + add_amount + actual_conversion_processed
            new_wager_balance = current_wager - actual_conversion_processed
            
            users_col.update_one(
                {"user_id": target_uid},
                {"$set": {"points": new_points_balance, "wager": new_wager_balance}}
            )
            
            history_col.insert_one({"user_id": target_uid, "reason": log_reason, "points": add_amount})
            if actual_conversion_processed > 0:
                history_col.insert_one({"user_id": target_uid, "reason": "Vault Liquidated Match", "points": actual_conversion_processed})
                s_logs.append(f"✓ UID {target_uid}: added {add_amount}, converted {actual_conversion_processed} wager.")
            else:
                s_logs.append(f"✓ UID {target_uid}: added {add_amount} cleanly.")
        except ValueError:
            e_logs.append(f"Value parse compilation failure: '{line}'")
            
    report = "<b>Transaction Protocol Summary Deployment Result:</b>\n\n"
    if s_logs: report += "<b>Success Profiles:</b>\n" + "\n".join(s_logs) + "\n\n"
    if e_logs: report += "<b>Error Profiles:</b>\n" + "\n".join(e_logs)
    await m.answer(report, parse_mode="HTML")
    await state.clear()

async def start_services():
    threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False, use_reloader=False),
        daemon=True
    ).start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(start_services())
    except KeyboardInterrupt:
        pass
