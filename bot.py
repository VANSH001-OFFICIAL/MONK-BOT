import asyncio
import os
import random
import string
import threading
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from flask import Flask, render_template_string, jsonify, request
from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from pymongo import MongoClient, DESCENDING, UpdateOne
from pymongo.errors import PyMongoError, DuplicateKeyError

# ==================== SYSTEM LOGGING INITIALIZATION ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("MonkTaskPremiumCore")

# ==================== ENVIRONMENT CONFIGURATION ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8445493171:AAFpi_rg_CSImfp0vjvtsxuxQ-k2Wsv3ds0")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://shaurya59rt_db_user:admin123@cluster0.sw408wn.mongodb.net/?appName=Cluster0")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://monk-bot-sh8z.onrender.com")

# Strict fallback verification for administrative boundaries
ADMIN_IDS: List[int] = [
    int(x) for x in os.environ.get("MONK_ADMIN_IDS", "123456789,987654321").split(",") if x.strip().isdigit()
]
# For testing local overrides if environment vars aren't present
if not ADMIN_IDS:
    ADMIN_IDS = [123456789] 

# ==================== INDUSTRIAL MONGODB DRIVER INSTANTIATION ====================
try:
    logger.info("Initializing high-availability MongoDB client pools...")
    client: MongoClient = MongoClient(
        MONGO_URI, 
        maxPoolSize=50, 
        minPoolSize=10, 
        serverSelectionTimeoutMS=5000,
        retryWrites=True
    )
    db = client['telegram_bot_db']
    
    # Core operational collections
    users_col = db['users']
    history_col = db['history']
    teams_col = db['teams']
    admin_logs_col = db['admin_audit_logs']

    # Performance indexing layers for sub-millisecond route resolution
    logger.info("Verifying cluster structural indexing optimization layers...")
    users_col.create_index([("user_id", 1)], unique=True)
    users_col.create_index([("points", -1)])
    users_col.create_index([("team_code", 1)])
    history_col.create_index([("user_id", 1), ("_id", -1)])
    teams_col.create_index([("code", 1)], unique=True)
    
    logger.info("Database cluster state synchronized successfully.")
except Exception as db_err:
    logger.critical(f"Fatal exception during MongoDB cluster configuration: {db_err}")
    raise db_err

# ==================== FLASK SERVER PRESET CONFIGURATION ====================
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET", "MonkSecretCoreEngine99X")

# ==================== EXTENDED PREMIUM MONK INTERFACE TEMPLATE ====================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Monk Task Premium Arena</title>
    
    <!-- External Structural Design Vectors -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Orbitron:wght@400;600;900&family=Inter:wght@300;400;600;800&display=swap');

        :root {
            --monk-gold-base: #ffd700;
            --monk-gold-deep: #b8860b;
            --monk-gold-glow: rgba(255, 215, 0, 0.35);
            --bg-ultra-dark: #050505;
            --bg-card-obsidian: rgba(18, 18, 18, 0.9);
            --bg-input-field: #0f0f0f;
            --border-gold-low: rgba(255, 215, 0, 0.12);
            --border-gold-mid: rgba(255, 215, 0, 0.25);
            --text-pure-white: #ffffff;
            --text-muted-gray: #9c9c9c;
            --text-emerald-win: #4ade80;
            --text-crimson-loss: #f87171;
            --transition-curve: cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Core Canvas Resets */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
            -webkit-user-select: none;
            user-select: none;
        }

        body {
            background-color: var(--bg-ultra-dark);
            color: var(--text-pure-white);
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            position: relative;
            height: 100vh;
            width: 100vw;
        }

        /* Animated Ambient Space Noise Canvas Background */
        body::before {
            content: '';
            position: absolute;
            width: 200%;
            height: 200%;
            top: -50%;
            left: -50%;
            background-image: 
                radial-gradient(circle at 30% 20%, rgba(255, 215, 0, 0.03) 0%, transparent 40%),
                radial-gradient(circle at 75% 70%, rgba(184, 134, 11, 0.04) 0%, transparent 45%);
            z-index: 0;
            pointer-events: none;
        }

        /* --- SPLASH SCREEN SYSTEM --- */
        #splash-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at center, #0d0d0d 0%, #020202 100%);
            z-index: 100000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            opacity: 1;
            transition: opacity 0.7s var(--transition-curve);
        }
        
        .monk-sigil-wrapper {
            position: relative;
            width: 140px;
            height: 140px;
            margin-bottom: 35px;
        }

        .monk-orbital-ring {
            position: absolute;
            width: 100%;
            height: 100%;
            border: 3px solid var(--monk-gold-base);
            border-radius: 50%;
            border-top-color: transparent;
            border-bottom-color: transparent;
            animation: ringSpin 1.8s cubic-bezier(0.5, 0.1, 0.5, 0.9) infinite;
            box-shadow: 0 0 15px var(--monk-gold-glow);
        }

        .monk-inner-sigil {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-family: 'Cinzel', serif;
            color: var(--monk-gold-base);
            font-size: 52px;
            font-weight: 800;
            text-shadow: 0 0 25px var(--monk-gold-base);
            animation: sigilPulse 2.2s ease-in-out infinite;
        }

        @keyframes ringSpin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes sigilPulse {
            0%, 100% { opacity: 0.9; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 0.4; transform: translate(-50%, -50%) scale(0.94); }
        }

        .splash-branding {
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 10px;
            color: var(--monk-gold-base);
            text-transform: uppercase;
            font-size: 16px;
            font-weight: 900;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
        }

        .splash-status-sub {
            margin-top: 20px;
            font-size: 11px;
            letter-spacing: 2px;
            color: var(--text-muted-gray);
            text-transform: uppercase;
            font-family: 'Orbitron', sans-serif;
        }

        /* --- STABLE VIEWPORT FRAMEWORK --- */
        #app-viewport {
            position: relative;
            z-index: 10;
            height: 100vh;
            width: 100vw;
            display: none;
            overflow: hidden;
        }

        .view-scroll-container {
            height: calc(100vh - 85px);
            overflow-y: auto;
            padding: 25px 20px 40px 20px;
            -webkit-overflow-scrolling: touch;
        }

        .view-section {
            display: none;
        }

        .view-section.active {
            display: block;
            animation: viewFadeIn 0.4s var(--transition-curve) forwards;
        }

        @keyframes viewFadeIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* --- PREMIUM MONK CORE UI RE-STYLES --- */
        .gold-card {
            background: var(--bg-card-obsidian);
            border: 1px solid var(--border-gold-low);
            border-radius: 20px;
            padding: 22px;
            margin-bottom: 22px;
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.75);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            transition: border 0.3s ease, box-shadow 0.3s ease;
        }

        .gold-card:hover {
            border-color: var(--border-gold-mid);
            box-shadow: 0 15px 45px rgba(255, 215, 0, 0.04);
        }

        .gold-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -150%;
            width: 150%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.06), transparent);
            transform: skewX(-25deg);
            transition: none;
        }

        .gold-card.animated-shimmer::before {
            animation: cardShine 6s infinite ease-in-out;
        }

        @keyframes cardShine {
            0% { left: -150%; }
            20%, 100% { left: 150%; }
        }

        .stat-header {
            font-family: 'Orbitron', sans-serif;
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted-gray);
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .stat-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 32px;
            font-weight: 900;
            color: var(--text-pure-white);
            letter-spacing: 1px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.5);
        }

        /* Custom Operational Progress Track */
        .monk-progress-container {
            margin-top: 15px;
            height: 6px;
            background: #161616;
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.02);
        }

        .monk-progress-bar {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, var(--monk-gold-deep) 0%, var(--monk-gold-base) 100%);
            border-radius: 4px;
            box-shadow: 0 0 12px var(--monk-gold-base);
            transition: width 0.8s cubic-bezier(0.4, 0, 0.1, 1);
        }

        /* --- COMPONENT STYLES --- */
        .btn-monk {
            background: linear-gradient(135deg, var(--monk-gold-base) 0%, #d4af37 50%, var(--monk-gold-deep) 100%);
            color: #000000;
            border: none;
            padding: 16px;
            border-radius: 14px;
            width: 100%;
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 13px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 14px;
            box-shadow: 0 5px 20px rgba(255, 215, 0, 0.2);
            transition: transform 0.15s ease, cubic-bezier(0, 0, 0, 1), box-shadow 0.2s ease;
            position: relative;
        }

        .btn-monk:active {
            transform: scale(0.96);
            box-shadow: 0 2px 8px rgba(255, 215, 0, 0.1);
        }

        .btn-monk-outline {
            background: transparent;
            border: 1px solid var(--monk-gold-base);
            color: var(--monk-gold-base);
            padding: 15px;
            border-radius: 14px;
            width: 100%;
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 14px;
            transition: background 0.3s, transform 0.15s;
        }

        .btn-monk-outline:active {
            transform: scale(0.96);
            background: rgba(255, 215, 0, 0.05);
        }

        /* Form Controls with High-Contrast System Safety */
        .form-control.monk-input {
            background-color: var(--bg-input-field) !important;
            border: 1px solid var(--border-gold-low) !important;
            color: var(--text-pure-white) !important;
            border-radius: 12px;
            padding: 14px 16px;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        .form-control.monk-input:focus {
            outline: none !important;
            border-color: var(--monk-gold-base) !important;
            box-shadow: 0 0 10px rgba(255, 215, 0, 0.15) !important;
        }

        .form-control.monk-input::placeholder {
            color: #4a4a4a;
        }

        /* --- ARENA DESIGN MATRIX --- */
        .arena-box {
            height: 220px;
            background: linear-gradient(180deg, rgba(20,20,20,0.4) 0%, rgba(5,5,5,0.8) 100%);
            border-radius: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin-bottom: 22px;
            border: 1px dashed var(--border-gold-mid);
            position: relative;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.9);
        }

        #stage-icon {
            font-size: 68px;
            filter: drop-shadow(0 0 15px rgba(255, 215, 0, 0.4));
            transition: transform 0.5s ease;
        }

        .arena-log-line {
            font-family: 'Orbitron', sans-serif;
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 2px;
            color: var(--text-muted-gray);
            text-transform: uppercase;
        }

        /* --- TRANSACTION LOGS & SQUAD DATA MATRIX --- */
        .log-row-item {
            background: rgba(10, 10, 10, 0.6);
            border-left: 3px solid var(--monk-gold-base);
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255,255,255,0.01);
            border-bottom: 1px solid rgba(0,0,0,0.3);
        }

        .log-row-reason {
            font-size: 13px;
            font-weight: 400;
            color: #e0e0e0;
        }

        .log-row-delta {
            font-family: 'Orbitron', sans-serif;
            font-size: 12px;
            font-weight: 900;
        }

        .rank-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            transition: background 0.2s;
        }

        .rank-row:hover {
            background: rgba(255,255,255,0.01);
        }

        .rank-number-tag {
            font-family: 'Orbitron', sans-serif;
            color: var(--monk-gold-base);
            font-weight: 900;
            width: 45px;
            font-size: 14px;
        }

        .rank-username {
            flex-grow: 1;
            font-weight: 600;
            font-size: 14px;
            color: #f0f0f0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            padding-right: 15px;
        }

        .rank-score {
            font-family: 'Orbitron', sans-serif;
            color: var(--monk-gold-base);
            font-weight: 900;
            font-size: 14px;
            text-shadow: 0 0 8px var(--monk-gold-glow);
        }

        /* --- PREMIUM PERSISTENT NAVIGATION --- */
        .premium-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: linear-gradient(360deg, #000000 70%, rgba(10,10,10,0.95) 100%);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border-top: 1px solid rgba(255, 215, 0, 0.18);
            display: flex;
            justify-content: space-around;
            padding: 10px 0 24px 0;
            z-index: 9999;
            box-shadow: 0 -10px 35px rgba(0,0,0,0.9);
        }

        .nav-link-item {
            text-align: center;
            color: #555555;
            text-decoration: none;
            font-size: 9px;
            font-weight: 900;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            transition: all 0.25s var(--transition-curve);
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .nav-link-item i {
            display: block;
            font-size: 21px;
            margin-bottom: 5px;
            transition: transform 0.25s var(--transition-curve);
        }

        .nav-link-item:hover {
            color: #999;
        }

        .nav-link-item.active {
            color: var(--monk-gold-base) !important;
            text-shadow: 0 0 12px var(--monk-gold-glow);
        }

        .nav-link-item.active i {
            transform: translateY(-2px);
            color: var(--monk-gold-base);
        }

        /* Structural Global Layout Header */
        .monk-header-sub {
            font-size: 11px;
            color: var(--monk-gold-base);
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-family: 'Orbitron', sans-serif;
        }

        .monk-header-title {
            font-family: 'Orbitron', sans-serif;
            font-weight: 900;
            font-size: 20px;
            color: var(--text-pure-white);
        }

        /* Custom Processing Spinner */
        .monk-spinner {
            width: 2.5rem;
            height: 2.5rem;
            border: 3px solid rgba(255, 215, 0, 0.1);
            border-radius: 50%;
            border-top-color: var(--monk-gold-base);
            animation: monkSpin 0.9s linear infinite;
        }

        @keyframes monkSpin {
            to { transform: rotate(360deg); }
        }

        /* Standard Scrollbar Redefinition */
        ::-webkit-scrollbar {
            width: 4px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-ultra-dark);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--monk-gold-deep);
            border-radius: 10px;
        }
    </style>
</head>
<body>

    <!-- SYSTEM LAYER: SPLASH CORE -->
    <div id="splash-screen">
        <div class="monk-sigil-wrapper">
            <div class="monk-orbital-ring"></div>
            <div class="monk-inner-sigil">M</div>
        </div>
        <div class="splash-branding">Monk Task</div>
        <div class="splash-status-sub">Synchronizing Secure Core...</div>
    </div>

    <!-- MAIN VIEWPORT CONTEXT -->
    <div id="app-viewport">
        <div class="view-scroll-container">
            
            <!-- SECTION 1: USER DASHBOARD -->
            <div id="view-task" class="view-section active">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <div class="monk-header-sub">Operative Network</div>
                        <h4 id="ui-username" class="monk-header-title">---</h4>
                    </div>
                    <div class="text-end">
                        <div id="ui-rank" style="background: rgba(255,215,0,0.07); padding: 6px 16px; border-radius: 20px; color: var(--monk-gold-base); font-size: 11px; font-weight: 900; border: 1px solid rgba(255,215,0,0.3); font-family: 'Orbitron';">Rank --</div>
                    </div>
                </div>

                <div class="gold-card animated-shimmer">
                    <div class="stat-header">Available Balance</div>
                    <div class="stat-value" id="ui-points">0.00</div>
                    <div class="monk-progress-container">
                        <div id="ui-progress" class="monk-progress-bar"></div>
                    </div>
                </div>

                <div class="row g-3 mb-4">
                    <div class="col-6">
                        <div class="gold-card m-0 py-3 text-center" style="padding: 15px !important;">
                            <div class="stat-header" style="font-size: 9px;">Total Wagered</div>
                            <div style="font-family: 'Orbitron'; font-weight: 900; font-size: 18px; color: var(--text-pure-white);" id="ui-wager">0.0</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="gold-card m-0 py-3 text-center" style="padding: 15px !important;">
                            <div class="stat-header" style="font-size: 9px;">Core Status</div>
                            <div style="font-family: 'Orbitron'; font-weight: 900; font-size: 18px; color: var(--text-emerald-win);">SECURE</div>
                        </div>
                    </div>
                </div>

                <h6 class="stat-header mb-3" style="color: var(--monk-gold-base);">Historical Ledger</h6>
                <div id="ui-history"></div>
            </div>

            <!-- SECTION 2: ARENA MODULE -->
            <div id="view-arena" class="view-section">
                <h4 class="text-center mb-4" style="font-family: 'Orbitron'; font-weight: 900; letter-spacing: 3px; color: var(--text-pure-white);">MONK ARENA</h4>
                
                <div class="gold-card text-center">
                    <div class="arena-box" id="game-stage">
                        <div id="stage-icon">☯️</div>
                    </div>
                    <div id="game-log" class="arena-log-line">Select Operational Protocol</div>
                </div>

                <button class="btn-monk" onclick="executeArenaGame('dice')"><i class="fa-solid relative-icon fa-dice me-2"></i> Roll Monk Dice</button>
                <button class="btn-monk" onclick="executeArenaGame('flip')"><i class="fa-solid relative-icon fa-coins me-2"></i> Flip Monk Coin</button>
                <button class="btn-monk-outline" onclick="executeArenaGame('spin')"><i class="fa-solid relative-icon fa-circle-notch me-2"></i> Spin Monk Wheel</button>
            </div>

            <!-- SECTION 3: GLOBAL LEADERBOARDS -->
            <div id="view-ranks" class="view-section">
                <h4 class="mb-4" style="font-family: 'Orbitron'; font-weight: 900; letter-spacing: 1px;">GLOBAL RADAR</h4>
                <div class="gold-card" style="padding: 10px 5px;">
                    <div id="ui-leaderboard"></div>
                </div>
            </div>

            <!-- SECTION 4: SQUAD SYSTEM -->
            <div id="view-team" class="view-section">
                <div id="team-setup-ui">
                    <h4 class="mb-4" style="font-family: 'Orbitron'; font-weight: 900; letter-spacing: 1px;">SQUAD INTERFACE</h4>
                    
                    <div class="gold-card">
                        <div class="stat-header" style="color: var(--monk-gold-base);">Initialize New Squad</div>
                        <p class="text-muted" style="font-size: 11px; margin-bottom: 15px;">Establish a secure tactical cell to coordinate metrics with other operatives.</p>
                        <input type="text" id="inp-tname" class="form-control monk-input mb-3" placeholder="Enter Squad Designation...">
                        <button class="btn-monk m-0" style="padding: 12px;" onclick="executeTeamAction('create')">Form Squad</button>
                    </div>
                    
                    <div class="gold-card">
                        <div class="stat-header" style="color: var(--text-pure-white);">Link Existing Squad</div>
                        <p class="text-muted" style="font-size: 11px; margin-bottom: 15px;">Input your encrypted validation token to append your local ledger.</p>
                        <input type="text" id="inp-tcode" class="form-control monk-input mb-3" placeholder="MONK-XXXXXX">
                        <button class="btn-monk-outline m-0" style="padding: 12px;" onclick="executeTeamAction('join')">Authenticate Token</button>
                    </div>
                </div>
                
                <div id="team-active-ui" style="display:none;">
                    <div class="gold-card text-center">
                        <div class="monk-header-sub">Active Squad Sector</div>
                        <h3 id="active-team-name" style="font-family: 'Orbitron'; color: var(--monk-gold-base); font-weight: 900; margin-top: 5px;">---</h3>
                        <code id="active-team-code" class="d-inline-block px-3 py-1 my-3" style="color: var(--text-muted-gray); background: rgba(0,0,0,0.4); border-radius: 6px; border: 1px solid rgba(255,255,255,0.03); letter-spacing: 1px;">---</code>
                        <button class="btn btn-outline-danger btn-sm w-100" style="border-radius: 10px; font-family: 'Orbitron'; font-weight: 600; font-size: 11px; letter-spacing: 1px; padding: 10px;" onclick="executeTeamAction('leave')">Decommission Active Connection</button>
                    </div>
                    <h6 class="stat-header mb-3" style="color: var(--monk-gold-base);">Squad Operatives Ledger</h6>
                    <div class="gold-card" style="padding: 10px 5px;">
                        <div id="ui-team-list"></div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- CORE FRAME PERSISTENT NAVIGATION -->
    <nav class="premium-nav">
        <div class="nav-link-item active" onclick="transitionActiveView('task', this)">
            <i class="fa-solid fa-gauge-high"></i>Task
        </div>
        <div class="nav-link-item" onclick="transitionActiveView('arena', this)">
            <i class="fa-solid fa-gavel"></i>Arena
        </div>
        <div class="nav-link-item" onclick="transitionActiveView('ranks', this)">
            <i class="fa-solid fa-trophy"></i>Ranks
        </div>
        <div class="nav-link-item" onclick="transitionActiveView('team', this)">
            <i class="fa-solid fa-users-viewfinder"></i>Team
        </div>
    </nav>

    <!-- SYSTEM LAYER: JAVASCRIPT APPLICATION CONTROL RUNTIME -->
    <script>
        const telegramEngine = window.Telegram.WebApp;
        telegramEngine.expand();
        telegramEngine.headerColor = "#050505";
        telegramEngine.backgroundColor = "#050505";

        // Global structural parameters mapped back safely to fallback domains
        const SECURE_USER_ID = telegramEngine.initDataUnsafe?.user?.id || 123456;
        const SECURE_USER_NAME = telegramEngine.initDataUnsafe?.user?.first_name || "Monk Operative";

        // Runtime initialization loop
        window.addEventListener('load', () => {
            setTimeout(() => {
                const splashDom = document.getElementById('splash-screen');
                splashDom.style.opacity = '0';
                setTimeout(() => {
                    splashDom.style.display = 'none';
                    document.getElementById('app-viewport').style.display = 'block';
                    syncDashboardMetrics();
                }, 700);
            }, 3000);
        });

        function transitionActiveView(targetSection, navigationElement) {
            document.querySelectorAll('.view-section').forEach(section => section.classList.remove('active'));
            document.querySelectorAll('.nav-link-item').forEach(nav => nav.classList.remove('active'));
            
            document.getElementById('view-' + targetSection).classList.add('active');
            navigationElement.classList.add('active');

            if(targetSection === 'task') syncDashboardMetrics();
            if(targetSection === 'ranks') fetchGlobalLeaderboard();
            if(targetSection === 'team') fetchSquadStructuralState();
        }

        async function syncDashboardMetrics() {
            try {
                const networkQueryUrl = `/api/user?id=${SECURE_USER_ID}&name=${encodeURIComponent(SECURE_USER_NAME)}`;
                const networkResponse = await fetch(networkQueryUrl);
                if (!networkResponse.ok) throw new Error("Operational network latency error");
                
                const responseDataset = await networkResponse.json();
                
                document.getElementById('ui-username').innerText = SECURE_USER_NAME;
                document.getElementById('ui-points').innerText = parseFloat(responseDataset.points).toFixed(2);
                document.getElementById('ui-wager').innerText = parseFloat(responseDataset.wager).toFixed(1);
                document.getElementById('ui-rank').innerText = "Rank #" + responseDataset.rank;
                
                let balanceRatio = Math.min((responseDataset.points / 150) * 100, 100);
                document.getElementById('ui-progress').style.width = balanceRatio + "%";

                const logHistoryContainer = document.getElementById('ui-history');
                if (responseDataset.history && responseDataset.history.length > 0) {
                    logHistoryContainer.innerHTML = responseDataset.history.map(item => {
                        const styleDelta = item.pts > 0 ? 'color: var(--text-emerald-win);' : 'color: var(--text-crimson-loss);';
                        const symbolPrefix = item.pts > 0 ? '+' : '';
                        return `
                            <div class="log-row-item">
                                <span class="log-row-reason">${escapeHtmlString(item.reason)}</span>
                                <span class="log-row-delta" style="${styleDelta}">${symbolPrefix}${parseFloat(item.pts).toFixed(1)}</span>
                            </div>
                        `;
                    }).join('');
                } else {
                    logHistoryContainer.innerHTML = '<div class="text-center text-muted small py-4">No records in ledger channel</div>';
                }
            } catch (err) {
                console.error("Dashboard engine failure:", err);
            }
        }

        async function executeArenaGame(selectedGameMode) {
            const logElement = document.getElementById('game-log');
            const stageElement = document.getElementById('game-stage');
            
            logElement.innerText = "Synchronizing Node Matrix...";
            logElement.style.color = "var(--text-muted-gray)";
            stageElement.innerHTML = '<div class="monk-spinner"></div>';

            try {
                const actionResponse = await fetch('/api/play', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: SECURE_USER_ID, game: selectedGameMode})
                });
                
                const finalDataset = await actionResponse.json();

                setTimeout(() => {
                    if(finalDataset.res === 'ERR') {
                        stageElement.innerHTML = '<div id="stage-icon">⚠️</div>';
                        logElement.innerText = finalDataset.msg;
                        logElement.style.color = "var(--text-crimson-loss)";
                    } else if (finalDataset.res === 'WIN') {
                        stageElement.innerHTML = '<div id="stage-icon">💎</div>';
                        logElement.innerText = `VICTORY: ${finalDataset.val}`;
                        logElement.style.color = "var(--text-emerald-win)";
                        syncDashboardMetrics();
                    } else {
                        stageElement.innerHTML = '<div id="stage-icon">💥</div>';
                        logElement.innerText = `DEFEAT: ${finalDataset.val}`;
                        logElement.style.color = "var(--text-crimson-loss)";
                        syncDashboardMetrics();
                    }
                }, 900);
            } catch (networkFatal) {
                stageElement.innerHTML = '<div id="stage-icon">❌</div>';
                logElement.innerText = "Transmission Termination Error";
            }
        }

        async function fetchGlobalLeaderboard() {
            const container = document.getElementById('ui-leaderboard');
            container.innerHTML = '<div class="text-center py-4"><div class="monk-spinner mx-auto"></div></div>';
            
            try {
                const lbResponse = await fetch('/api/lb?type=users');
                const lbDataset = await lbResponse.json();
                
                if(lbDataset.length === 0) {
                    container.innerHTML = '<div class="text-center text-muted small py-4">Leaderboard is clean</div>';
                    return;
                }

                container.innerHTML = lbDataset.map((userRow, loopIndex) => `
                    <div class="rank-row">
                        <span class="rank-number-tag">#${loopIndex + 1}</span>
                        <span class="rank-username">${escapeHtmlString(userRow.name)}</span>
                        <span class="rank-score">${parseFloat(userRow.pts).toFixed(1)}</span>
                    </div>
                `).join('');
            } catch (lbErr) {
                container.innerHTML = '<div class="text-center text-danger small py-4">Error loading data array</div>';
            }
        }

        async function fetchSquadStructuralState() {
            try {
                const squadResponse = await fetch(`/api/team?id=${SECURE_USER_ID}`);
                const squadDataset = await squadResponse.json();
                
                if(squadDataset.has) {
                    document.getElementById('team-setup-ui').style.display = 'none';
                    document.getElementById('team-active-ui').style.display = 'block';
                    document.getElementById('active-team-name').innerText = squadDataset.name;
                    document.getElementById('active-team-code').innerText = squadDataset.code;
                    
                    document.getElementById('ui-team-list').innerHTML = squadDataset.m.map(memberRow => `
                        <div class="rank-row">
                            <span class="rank-username" style="font-weight: normal;">${escapeHtmlString(memberRow.name)}</span>
                            <span class="rank-score" style="font-size:12px; color: var(--text-muted-gray);">${parseFloat(memberRow.pts).toFixed(1)}</span>
                        </div>
                    `).join('');
                } else {
                    document.getElementById('team-setup-ui').style.display = 'block';
                    document.getElementById('team-active-ui').style.display = 'none';
                }
            } catch (teamFatal) {
                console.error("Squad communication layer error:", teamFatal);
            }
        }

        async function executeTeamAction(intendedActionStr) {
            const teamNameInputVal = document.getElementById('inp-tname').value.trim();
            const teamTokenInputVal = document.getElementById('inp-tcode').value.trim();
            
            if(intendedActionStr === 'create' && !teamNameInputVal) {
                alert("Squad designation string required.");
                return;
            }
            if(intendedActionStr === 'join' && !teamTokenInputVal) {
                alert("Squad authentication secure token required.");
                return;
            }

            try {
                const actionResponse = await fetch('/api/team_act', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        id: SECURE_USER_ID, 
                        action: intendedActionStr, 
                        tname: teamNameInputVal, 
                        tcode: teamTokenInputVal
                    })
                });
                const actionResultDataset = await actionResponse.json();
                alert(actionResultDataset.msg);
                
                // Clear state inputs safely
                document.getElementById('inp-tname').value = '';
                document.getElementById('inp-tcode').value = '';
                
                fetchSquadStructuralState();
            } catch (err) {
                alert("Action execution channel failure.");
            }
        }

        function escapeHtmlString(rawStringValue) {
            return rawStringValue
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }
    </script>
</body>
</html>
"""

# ==================== REST FRAMEWORK ROUTE MAPPINGS ====================

@app.route('/')
def home_route():
    """Serves the central rich layout visual component shell."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/user', methods=['GET'])
def get_user_state_package():
    """
    Fetches or safely executes atomic upserts for requested user metrics profiles.
    Guarantees isolation level checks to clear potential structural thread race collisions.
    """
    try:
        uid_param = request.args.get('id', '0')
        if not uid_param.isdigit():
            return jsonify({"points": 0.0, "wager": 0.0, "rank": "--", "history": []}), 400
            
        uid = int(uid_param)
        username_str = request.args.get('name', 'Anonymous Operative').strip()
        username = username_str if username_str else 'Anonymous Operative'

        # Atomic structural read/write isolation step
        user_record = users_col.find_one({"user_id": uid})
        if not user_record:
            user_record = {
                "user_id": uid,
                "username": username,
                "points": 10.0,
                "wager": 0.0,
                "team_code": None,
                "created_at": datetime.utcnow()
            }
            try:
                users_col.insert_one(user_record)
            except DuplicateKeyError:
                # Concurrent request resolution fall-through safety
                user_record = users_col.find_one({"user_id": uid})

        # Dynamically evaluate exact rank metric using count aggregates
        higher_score_count = users_col.count_documents({"points": {"$gt": user_record.get('points', 10.0)}})
        calculated_rank = higher_score_count + 1

        # Fetch isolated execution transaction streams
        historical_cursor = history_col.find({"user_id": uid}).sort("_id", DESCENDING).limit(6)
        formatted_history_bundle = [
            {"reason": entry.get('reason', 'System Process'), "pts": entry.get('points', 0.0)} 
            for entry in historical_cursor
        ]

        return jsonify({
            "points": float(user_record.get('points', 0.0)),
            "wager": float(user_record.get('wager', 0.0)),
            "rank": calculated_rank,
            "history": formatted_history_bundle
        })
    except PyMongoError as db_ex:
        logger.error(f"Database transaction failure inside user api: {db_ex}")
        return jsonify({"res": "ERR", "msg": "Database tier disconnected."}), 500


@app.route('/api/play', methods=['POST'])
def process_arena_wager_turn():
    """
    Validates account financial locks, processes specific probability matrices,
    and updates balances atomically across the system.
    """
    try:
        incoming_payload = request.json or {}
        if 'id' not in incoming_payload or 'game' not in incoming_payload:
            return jsonify({"res": "ERR", "msg": "Malformed Data Context"}), 400
            
        uid = int(incoming_payload['id'])
        game_mode = str(incoming_payload['game']).strip()

        user_profile = users_col.find_one({"user_id": uid})
        if not user_profile:
            return jsonify({"res": "ERR", "msg": "Operative Security Profile Missing"}), 404

        current_balance = float(user_profile.get('points', 0.0))
        if current_balance < 1.0:
            return jsonify({"res": "ERR", "msg": "Insufficient Credits for Wager"}), 400

        # Operational probability gate evaluation (35% Win Odds)
        is_victory_turn = random.random() < 0.35
        
        if is_victory_turn:
            reward_increment = 2.0
            users_col.update_one(
                {"user_id": uid},
                {"$inc": {"wager": 2.0, "points": reward_increment}}
            )
            history_col.insert_one({
                "user_id": uid,
                "reason": f"Arena Victory ({game_mode.upper()})",
                "points": reward_increment,
                "timestamp": datetime.utcnow()
            })
            return jsonify({"res": "WIN", "val": "+2.0 Wager Credits Earned"})
        else:
            loss_deductions = -1.0
            users_col.update_one(
                {"user_id": uid},
                {"$inc": {"points": loss_deductions}}
            )
            history_col.insert_one({
                "user_id": uid,
                "reason": f"Arena Loss ({game_mode.upper()})",
                "points": loss_deductions,
                "timestamp": datetime.utcnow()
            })
            return jsonify({"res": "LOSE", "val": "-1.0 Wallet Credit Absorbed"})

    except (PyMongoError, ValueError, TypeError) as system_ex:
        logger.error(f"Critical execution error inside game module loop: {system_ex}")
        return jsonify({"res": "ERR", "msg": "Core Engine Execution Error"}), 500


@app.route('/api/lb', methods=['GET'])
def get_global_leaderboard_array():
    """Returns top 20 active players ordered by points."""
    try:
        leaderboard_cursor = users_col.find().sort("points", DESCENDING).limit(20)
        output_payload_list = [
            {"name": record.get('username', 'Unknown Operative'), "pts": float(record.get('points', 0.0))}
            for record in leaderboard_cursor
        ]
        return jsonify(output_payload_list)
    except PyMongoError as db_ex:
        logger.error(f"Leaderboard fetch database structural fault: {db_ex}")
        return jsonify([]), 500


@app.route('/api/team', methods=['GET'])
def get_squad_structural_package():
    """Fetches details of a user's active team/squad."""
    try:
        uid_param = request.args.get('id', '0')
        if not uid_param.isdigit():
            return jsonify({"has": False}), 400
            
        uid = int(uid_param)
        user_record = users_col.find_one({"user_id": uid})
        
        if not user_record or not user_record.get('team_code'):
            return jsonify({"has": False})

        assigned_team_code = user_record['team_code']
        team_profile = teams_col.find_one({"code": assigned_team_code})
        
        if not team_profile:
            # Clear invalid sync pointer reference gracefully
            users_col.update_one({"user_id": uid}, {"$set": {"team_code": None}})
            return jsonify({"has": False})

        synchronized_members_cursor = users_col.find({"team_code": assigned_team_code}).sort("points", DESCENDING)
        members_list_payload = [
            {"name": record.get('username', 'Unknown member'), "pts": float(record.get('points', 0.0))}
            for record in synchronized_members_cursor
        ]

        return jsonify({
            "has": True,
            "name": team_profile.get('name', 'Unnamed Tactical Core'),
            "code": assigned_team_code,
            "m": members_list_payload
        })
    except PyMongoError as db_err:
        logger.error(f"Squad management data validation failure: {db_err}")
        return jsonify({"has": False, "msg": "Database execution error."}), 500


@app.route('/api/team_act', methods=['POST'])
def execute_squad_mutation_action():
    """Handles creating, joining, and leaving squads."""
    try:
        payload = request.json or {}
        if 'id' not in payload or 'action' not in payload:
            return jsonify({"msg": "Validation constraints error"}), 400
            
        uid = int(payload['id'])
        action_directive = str(payload['action']).strip()
        
        user_record = users_col.find_one({"user_id": uid})
        if not user_record:
            return jsonify({"msg": "Profile authorization error"}), 404

        if action_directive == 'create':
            squad_name = str(payload.get('tname', '')).strip()
            if not squad_name or len(squad_name) < 2:
                return jsonify({"msg": "Invalid deployment signature name"}), 400
                
            generated_token = "MONK-" + ''.join(random.choices(string.string.ascii_uppercase + string.digits, k=6))
            
            teams_col.insert_one({
                "code": generated_token,
                "name": squad_name,
                "creator": uid,
                "created_at": datetime.utcnow()
            })
            users_col.update_one({"user_id": uid}, {"$set": {"team_code": generated_token}})
            return jsonify({"msg": f"Squad operational code locked: {generated_token}"})

        elif action_directive == 'join':
            target_token = str(payload.get('tcode', '')).strip().upper()
            matched_team = teams_col.find_one({"code": target_token})
            
            if matched_team:
                users_col.update_one({"user_id": uid}, {"$set": {"team_code": target_token}})
                return jsonify({"msg": "Authentication verified. Channel linked."})
            return jsonify({"msg": "Token verification failed. Action denied."})

        elif action_directive == 'leave':
            users_col.update_one({"user_id": uid}, {"$set": {"team_code": None}})
            return jsonify({"msg": "Squad links cleanly disconnected."})

        return jsonify({"msg": "Action syntax execution routing path error"}), 400
    except PyMongoError as execution_fault:
        logger.error(f"Squad action mutation layer failure: {execution_fault}")
        return jsonify({"msg": "Internal database communication fault."}), 500

# ==================== TELEGRAM BOT DISPATCH ENGINE ====================

bot = Bot(token=BOT_TOKEN)
storage_memory = MemoryStorage()
dp = Dispatcher(storage=storage_memory)

# State Machine Management Matrix for Admin Operations
class AdministrativeProtocolStates(StatesGroup):
    awaiting_target_user_id = State()
    awaiting_allocation_value = State()
    awaiting_audit_justification = State()


@dp.message(CommandStart())
async def command_start_dispatcher(message: Message):
    """Initializes the main menu and WebApp links."""
    try:
        user_first_name = message.from_user.first_name
        welcome_keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Enter Monk Arena ⛩️", web_app=WebAppInfo(url=MINI_APP_URL))
        ]])
        
        escaped_name = html.escape(user_first_name)
        response_text = (
            f"<b>Welcome Operative {escaped_name}</b>\n\n"
            f"The Monk Task Premium interface ecosystem is online.\n"
            f"Select the structural link vector below to enter the terminal."
        )
        await message.answer(response_text, reply_markup=welcome_keyboard, parse_mode="HTML")
    except Exception as telegram_err:
        logger.error(f"Error handling /start command stream: {telegram_err}")


# ==================== /ADD ADMIN TELEGRAM STATE ENGINE ====================

@dp.message(Command("add"))
async def start_admin_credit_allocation(message: Message, state: FSMContext):
    """
    Validates user administrative privileges and initiates credit allocation workflow.
    Syntax checked: /add [Target User ID] [Amount] [Reason]
    """
    operator_id = message.from_user.id
    if operator_id not in ADMIN_IDS:
        await message.answer("<b>ACCESS DENIED:</b> Operational privilege boundary mismatch.", parse_mode="HTML")
        return

    command_tokens = message.text.split(maxsplit=3)
    
    # Check if parameters were passed inline
    if len(command_tokens) >= 3:
        try:
            target_uid = int(command_tokens[1])
            allocation_amount = float(command_tokens[2])
            audit_reason = command_tokens[3] if len(command_tokens) == 4 else "Administrative Allocation Adjustments"
            
            await execute_database_credit_injection(message, target_uid, allocation_amount, audit_reason)
            return
        except ValueError:
            await message.answer("<b>SYNTAX REJECTED:</b> Parameters invalid. Usage: <code>/add [uid] [amount] [reason]</code>", parse_mode="HTML")
            return

    # Fall back to step-by-step state machine prompts if arguments are missing
    await message.answer("<b>ADMINISTRATIVE MODE INITIALIZED</b>\n\nInput targeted system User ID parameter string:", parse_mode="HTML")
    await state.set_state(AdministrativeProtocolStates.awaiting_target_user_id)


@dp.message(AdministrativeProtocolStates.awaiting_target_user_id)
async def process_admin_input_uid(message: Message, state: FSMContext):
    """Captures and validates the targeted user ID string."""
    input_text = message.text.strip()
    if not input_text.isdigit():
        await message.answer("Validation failure: User ID must contain integers only. Re-enter target context:")
        return
        
    await state.update_data(target_uid=int(input_text))
    await message.answer("Input numerical balance allocation delta increments (e.g. 25.50 or -10.00):")
    await state.set_state(AdministrativeProtocolStates.awaiting_allocation_value)


@dp.message(AdministrativeProtocolStates.awaiting_allocation_value)
async def process_admin_input_value(message: Message, state: FSMContext):
    """Captures and verifies the requested numerical adjustments value."""
    input_text = message.text.strip()
    try:
        allocation_value = float(input_text)
        await state.update_data(allocation_amount=allocation_value)
        await message.answer("Provide operational audit reason logging string:")
        await state.set_state(AdministrativeProtocolStates.awaiting_audit_justification)
    except ValueError:
        await message.answer("Validation failure: Value must be standard floating numerical decimal. Re-enter balance adjustments:")


@dp.message(AdministrativeProtocolStates.awaiting_audit_justification)
async def process_admin_input_justification_and_finalize(message: Message, state: FSMContext):
    """Extracts final parameter contexts and executes balance operations safely."""
    audit_reason_string = message.text.strip()
    session_data = await state.get_data()
    await state.clear()

    target_uid = session_data['target_uid']
    allocation_amount = session_data['allocation_amount']
    
    await execute_database_credit_injection(message, target_uid, allocation_amount, audit_reason_string)


async def execute_database_credit_injection(trigger_msg: Message, uid: int, amount: float, reason: str):
    """Helper method executing database operations and providing deployment telemetry."""
    try:
        # Check profile target constraint presence
        target_profile = users_col.find_one({"user_id": uid})
        if not target_profile:
            # Construct shell trace automatically if profile doesn't exist yet
            users_col.insert_one({
                "user_id": uid,
                "username": "Initialized via Sync Admin Channel",
                "points": 10.0,
                "wager": 0.0,
                "team_code": None,
                "created_at": datetime.utcnow()
            })
            target_profile = users_col.find_one({"user_id": uid})

        # Process transactional pipeline synchronization locks
        users_col.update_one(
            {"user_id": uid},
            {"$inc": {"points": amount}}
        )
        
        # Inject synchronized historical records block
        history_col.insert_one({
            "user_id": uid,
            "reason": f"System Allocation: {reason}",
            "points": amount,
            "timestamp": datetime.utcnow()
        })

        # Log action inside dedicated security audit indexes
        admin_logs_col.insert_one({
            "operator_id": trigger_msg.from_user.id,
            "target_user_id": uid,
            "allocated_delta": amount,
            "audit_context_reason": reason,
            "timestamp": datetime.utcnow()
        })

        refreshed_user = users_col.find_one({"user_id": uid})
        updated_balance = refreshed_user.get('points', 0.0)

        success_telemetry_message = (
            f"✨ <b>LEDGER TRANSACTION SYSTEM SYNCHRONIZED</b>\n\n"
            f"<b>Target User Target:</b> <code>{uid}</code>\n"
            f"<b>Adjustment Metrics Allocation:</b> <code>{amount:+.2f} Units</code>\n"
            f"<b>Audit Validation:</b> {html.escape(reason)}\n"
            f"<b>Refreshed Account Value Balance:</b> <code>{updated_balance:.2f} Units</code>"
        )
        await trigger_msg.answer(success_telemetry_message, parse_mode="HTML")

        # Attempt proactive alert tracking transmission directly to targeted user channel
        try:
            notification_alert = (
                f"🔔 <b>SECURE LOG INCOMING</b>\n\n"
                f"Your credit configuration was adjusted via administrative action.\n"
                f"<b>Allocation Delta:</b> <code>{amount:+.2f} Credits</code>\n"
                f"<b>Reason Trace:</b> {html.escape(reason)}\n"
                f"<b>Current Active Balance:</b> <code>{updated_balance:.2f}</code>"
            )
            await bot.send_message(chat_id=uid, text=notification_alert, parse_mode="HTML")
        except Exception:
            # Suppress failures if the remote chat space hasn't active initialized sequences yet
            pass

    except PyMongoError as transactional_fault:
        logger.error(f"Admin credit injection pipeline dropped database tier errors: {transactional_fault}")
        await trigger_msg.answer("❌ <b>TRANSACTION ABORTED:</b> Database connection pool execution error.")


# ==================== SYSTEM BOOTSTRAP CONTROL ENGINE ====================

def run_flask_networking_service():
    """Runs the web server framework inside a background thread worker."""
    target_port = int(os.environ.get("PORT", 5000))
    logger.info(f"Binding Flask HTTP engine listener to 0.0.0.0 Interface on Port {target_port}...")
    app.run(host="0.0.0.0", port=target_port, debug=False, use_reloader=False)


async def main_asynchronous_orchestration_loop():
    """
    Launches structural assets in parallel, 
    connecting the polling framework and background web server.
    """
    logger.info("Spawning secondary execution worker thread loops for Flask instance...")
    flask_worker_thread = threading.Thread(target=run_flask_networking_service, daemon=True)
    flask_worker_thread.start()

    logger.info("Purging orphaned updates stack and starting Telegram polling gateway...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main_asynchronous_orchestration_loop())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Termination signal caught. Closing connection pools safely...")
        client.close()
        logger.info("System instance context cleanly torn down.")
