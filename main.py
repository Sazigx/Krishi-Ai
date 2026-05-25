import os
import io
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# 1. Setup API Client
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. DEFINE THE APP
app = FastAPI(title="Krishi AI Super App")

# ---------------------------------------------------------
# ULTIMATE ARCHITECTURE v2: Dynamic Weather, Market Categories & Advanced Search
# ---------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Krishi AI - Ultimate</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* CORE VARIABLES */
        :root {
            --primary: #059669; --primary-light: #10b981; --accent: #f59e0b; --danger: #ef4444; --success: #10b981;
            --bg-gradient: linear-gradient(135deg, #e0f2fe 0%, #dcfce7 100%);
            --app-bg: rgba(255, 255, 255, 0.65); --glass-bg: rgba(255, 255, 255, 0.85);
            --glass-border: rgba(255, 255, 255, 0.6); --text-main: #1e293b; --text-muted: #64748b;
            --shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
            --nav-bg: rgba(255, 255, 255, 0.95);
        }

        [data-theme="dark"] {
            --primary: #10b981; --primary-light: #34d399; --accent: #fbbf24;
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #064e3b 100%);
            --app-bg: rgba(15, 23, 42, 0.7); --glass-bg: rgba(30, 41, 59, 0.85);
            --glass-border: rgba(255, 255, 255, 0.1); --text-main: #f8fafc; --text-muted: #94a3b8;
            --shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            --nav-bg: rgba(15, 23, 42, 0.95);
        }

        /* GLOBAL STYLES */
        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg-gradient); margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; color: var(--text-main); transition: background 0.5s ease; }
        
        /* THE DEVICE */
        .app-container { width: 100%; max-width: 414px; height: 100vh; max-height: 896px; background: var(--app-bg); backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(25px); position: relative; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); border: 1px solid var(--glass-border); display: flex; flex-direction: column; }
        @media (min-width: 450px) { .app-container { height: 850px; border-radius: 40px; border: 8px solid #0f172a; margin: 20px; } }

        /* HEADER */
        .header-area { padding: 40px 20px 15px; flex-shrink: 0; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .user-profile { display: flex; align-items: center; gap: 12px; }
        .avatar { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--primary-light)); color: white; display: flex; justify-content: center; align-items: center; font-size: 20px; font-weight: 700; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.4); }
        .user-info h2 { margin: 0; font-size: 18px; font-weight: 800; letter-spacing: -0.5px; }
        .user-info p { margin: 0; font-size: 12px; color: var(--text-muted); font-weight: 600; display:flex; align-items:center; gap:4px;}
        
        .utility-btns { display: flex; gap: 8px; }
        .icon-btn { width: 38px; height: 38px; border-radius: 50%; border: 1px solid var(--glass-border); background: var(--glass-bg); color: var(--text-main); display: flex; justify-content: center; align-items: center; cursor: pointer; transition: 0.3s; font-weight: 700; font-size: 14px; }
        .icon-btn:hover { background: var(--primary); color: white; border-color: var(--primary); }

        /* CONTENT */
        .content { flex-grow: 1; overflow-y: auto; padding: 0 20px 95px; scroll-behavior: smooth; }
        .content::-webkit-scrollbar { display: none; }
        .tab-content { display: none; animation: slideUp 0.3s ease-out; height: 100%; flex-direction: column; }
        .tab-content.active { display: flex; }
        @keyframes slideUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

        /* CARDS */
        .glass-card { background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: 24px; padding: 20px; margin-bottom: 16px; box-shadow: var(--shadow); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .card-header h3 { margin: 0; font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; color: var(--text-main); }
        
        /* WEATHER */
        .weather-hero { display: flex; justify-content: space-between; align-items: center; padding-bottom: 15px; border-bottom: 1px solid var(--glass-border); margin-bottom: 15px; }
        .w-temp { font-size: 42px; font-weight: 800; line-height: 1; margin-bottom: 5px; color: var(--text-main); }
        .w-desc { font-size: 14px; color: var(--text-muted); font-weight: 600; }
        .w-icon { font-size: 48px; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1)); }
        .w-stats { display: flex; justify-content: space-between; text-align: center; }
        .w-stat-item { flex: 1; }
        .w-stat-val { font-size: 15px; font-weight: 700; color: var(--text-main); }
        .w-stat-lbl { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; font-weight: 600;}

        /* MARKET CATEGORIES */
        .category-tabs { display: flex; gap: 10px; margin-bottom: 15px; overflow-x: auto; padding-bottom: 5px; }
        .category-tabs::-webkit-scrollbar { display: none; }
        .cat-btn { padding: 8px 16px; border-radius: 20px; background: rgba(0,0,0,0.05); border: 1px solid transparent; color: var(--text-muted); font-weight: 600; font-size: 13px; cursor: pointer; white-space: nowrap; transition: 0.2s; }
        .cat-btn.active { background: var(--primary); color: white; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); }
        
        .market-list { display: none; }
        .market-list.active { display: block; animation: fadeIn 0.3s; }
        .market-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; background: rgba(128,128,128,0.05); border-radius: 12px; margin-bottom: 8px; border: 1px solid rgba(128,128,128,0.1); }
        .crop-name { font-weight: 700; font-size: 14px; display: flex; align-items: center; gap: 10px; }
        .crop-icon { width: 32px; height: 32px; background: var(--app-bg); border-radius: 8px; display: flex; justify-content: center; align-items: center; font-size: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
        .price-info { text-align: right; }
        .price { font-size: 15px; font-weight: 800; color: var(--text-main);}
        .trend { font-size: 12px; font-weight: 700; display:flex; align-items:center; justify-content:flex-end; gap:3px;}
        .trend.up { color: var(--success); }
        .trend.down { color: var(--danger); }

        /* SEARCH INPUT (LEARN TAB) */
        .search-box { position: relative; margin-bottom: 20px; }
        .search-box input { width: 100%; padding: 16px 20px 16px 45px; border: 1px solid var(--glass-border); border-radius: 16px; font-family: inherit; font-size: 15px; background: var(--glass-bg); color: var(--text-main); outline: none; box-shadow: inset 0 2px 5px rgba(0,0,0,0.02); transition: 0.3s; }
        .search-box input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2); }
        .search-box i { position: absolute; left: 16px; top: 50%; transform: translateY(-50%); color: var(--text-muted); font-size: 18px; }

        /* PREMIUM AI CHAT */
        .chat-container { flex-grow: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
        .chat-history { flex-grow: 1; overflow-y: auto; padding-bottom: 80px; display: flex; flex-direction: column; gap: 16px; }
        .chat-history::-webkit-scrollbar { display: none; }
        .message { max-width: 88%; padding: 15px 18px; border-radius: 22px; font-size: 14.5px; line-height: 1.5; position: relative; }
        .msg-user { background: linear-gradient(135deg, var(--primary), var(--primary-light)); color: white; align-self: flex-end; border-bottom-right-radius: 6px; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.25); }
        .msg-ai { background: var(--glass-bg); color: var(--text-main); border: 1px solid var(--glass-border); align-self: flex-start; border-bottom-left-radius: 6px; box-shadow: var(--shadow); }
        .msg-img { max-width: 100%; border-radius: 12px; margin-bottom: 8px; display: block; border: 2px solid rgba(255,255,255,0.2); }
        
        .input-dock { position: absolute; bottom: 0; left: 0; right: 0; background: var(--glass-bg); backdrop-filter: blur(25px); border: 1px solid var(--glass-border); border-radius: 24px; padding: 6px; display: flex; align-items: center; gap: 6px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); }
        .input-dock input[type="text"] { flex-grow: 1; background: transparent; border: none; color: var(--text-main); font-size: 15px; padding: 10px 12px; font-family: 'Plus Jakarta Sans'; outline: none; }
        .action-btn { width: 42px; height: 42px; border-radius: 50%; border: none; background: transparent; color: var(--text-muted); cursor: pointer; font-size: 18px; display: flex; justify-content: center; align-items: center; transition: 0.2s; }
        .action-btn:hover { background: rgba(0,0,0,0.05); color: var(--primary); }
        .action-btn.send { background: var(--primary); color: white; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.3); }
        .action-btn.recording { color: white; background: var(--danger); animation: pulse 1.5s infinite; }
        
        /* PREMIUM BOTTOM NAV */
        .bottom-nav { position: absolute; bottom: 0; left: 0; width: 100%; background: var(--nav-bg); backdrop-filter: blur(20px); border-top: 1px solid var(--glass-border); display: flex; justify-content: space-around; padding: 12px 10px 25px; z-index: 100; border-radius: 40px 40px 0 0; box-shadow: 0 -10px 30px rgba(0,0,0,0.05); }
        .nav-item { display: flex; flex-direction: column; align-items: center; gap: 4px; color: var(--text-muted); cursor: pointer; transition: 0.3s; width: 65px; position: relative; }
        .nav-item i { font-size: 20px; transition: 0.3s; z-index: 2; padding: 8px 16px; border-radius: 20px; }
        .nav-item span { font-size: 11px; font-weight: 700; z-index: 2; transition: 0.3s;}
        
        .nav-item.active { color: var(--primary); }
        .nav-item.active i { background: rgba(16, 185, 129, 0.15); transform: translateY(-2px); }
        
        /* Button */
        .btn-main { width: 100%; padding: 16px; background: var(--primary); color: white; border: none; border-radius: 16px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); display: flex; justify-content: center; align-items: center; gap: 8px; }
        .btn-main:hover { background: var(--primary-light); transform: translateY(-2px); box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4); }
    </style>
</head>
<body>
    <div class="app-container">
        
        <div class="header-area">
            <div class="top-bar">
                <div class="user-profile">
                    <div class="avatar"><i class="fas fa-leaf"></i></div>
                    <div class="user-info">
                        <h2 data-i18n="greeting">Hello, Farmer</h2>
                        <p><i class="fas fa-location-dot" style="color:var(--danger)"></i> <span id="locationText" data-i18n="loc_fetching">Locating...</span></p>
                    </div>
                </div>
                <div class="utility-btns">
                    <button class="icon-btn" onclick="toggleLang()" id="langBtn">ने</button>
                    <button class="icon-btn" onclick="toggleTheme()"><i class="fas fa-moon" id="themeIcon"></i></button>
                </div>
            </div>
        </div>

        <div class="content">
            
            <div id="tab-home" class="tab-content active">
                <div class="glass-card">
                    <div class="card-header">
                        <h3 style="color:var(--text-main)"><i class="fas fa-cloud-sun" style="color:var(--accent)"></i> <span data-i18n="weather_title">Live Environment</span></h3>
                    </div>
                    <div class="weather-hero">
                        <div>
                            <div class="w-temp" id="temp">--°</div>
                            <div class="w-desc" id="weatherDesc">...</div>
                        </div>
                        <i id="weatherIcon" class="fas fa-cloud w-icon" style="color:var(--text-muted)"></i>
                    </div>
                    <div class="w-stats">
                        <div class="w-stat-item">
                            <div class="w-stat-val" id="humidity">--%</div>
                            <div class="w-stat-lbl" data-i18n="humidity">Humidity</div>
                        </div>
                        <div class="w-stat-item">
                            <div class="w-stat-val" id="wind">--</div>
                            <div class="w-stat-lbl" data-i18n="wind">Wind</div>
                        </div>
                        <div class="w-stat-item">
                            <div class="w-stat-val" style="color:var(--success)">Good</div>
                            <div class="w-stat-lbl" data-i18n="soil">Soil</div>
                        </div>
                    </div>
                </div>

                <div class="glass-card" style="background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.05)); border:1px solid rgba(16,185,129,0.2);">
                    <h3 style="margin-top:0; color:var(--primary); font-size: 16px; display:flex; align-items:center; gap:8px;"><i class="fas fa-bell"></i> <span data-i18n="smart_alert">Smart Alert</span></h3>
                    <p style="font-size:14px; margin:0; line-height:1.5; color:var(--text-main);" data-i18n="alert_text">Optimal conditions for spraying fertilizers today. Wind speed is low.</p>
                </div>
            </div>

            <div id="tab-ai" class="tab-content">
                <div class="chat-container">
                    <div class="chat-history" id="chatBox">
                        <div class="message msg-ai">
                            <div style="font-weight: 800; margin-bottom: 6px; color: var(--primary); font-size:15px;"><i class="fas fa-sparkles"></i> Krishi AI</div>
                            <span data-i18n="ai_intro">I am your advanced farm assistant. Ask me anything, use your voice, or upload a photo of a crop for instant diagnosis.</span>
                        </div>
                    </div>
                    
                    <div class="input-dock">
                        <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageSelect()">
                        <button class="action-btn" onclick="document.getElementById('imageInput').click()">
                            <i class="fas fa-image" id="camIcon"></i>
                        </button>
                        <button class="action-btn" id="micBtn" onclick="toggleVoice()">
                            <i class="fas fa-microphone"></i>
                        </button>
                        <input type="text" id="chatInput" placeholder="Ask Krishi AI..." data-i18n-ph="chat_ph" onkeypress="handleEnter(event)">
                        <button class="action-btn send" onclick="sendMessage()">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>

            <div id="tab-market" class="tab-content">
                <div class="glass-card">
                    <h3 style="margin-top:0; color:var(--text-main); font-size: 18px;" data-i18n="market_title">Live Market Prices</h3>
                    <p style="font-size:12px; color:var(--text-muted); margin-bottom: 15px;" data-i18n="market_sub">Estimated rates in NPR (per kg/piece) for your region.</p>
                    
                    <div class="category-tabs">
                        <button class="cat-btn active" onclick="switchMarketCat('veg', this)" data-i18n="cat_veg">Vegetables</button>
                        <button class="cat-btn" onclick="switchMarketCat('fruit', this)" data-i18n="cat_fruit">Fruits</button>
                        <button class="cat-btn" onclick="switchMarketCat('crop', this)" data-i18n="cat_crop">Crops/Grains</button>
                    </div>

                    <div id="cat-veg" class="market-list active">
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🍅</div><span data-i18n="m_tomato">Tomato</span></div><div class="price-info"><div class="price">Rs. 65</div><div class="trend up"><i class="fas fa-arrow-up"></i> 4%</div></div></div>
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🥔</div><span data-i18n="m_potato">Potato</span></div><div class="price-info"><div class="price">Rs. 42</div><div class="trend down"><i class="fas fa-arrow-down"></i> 1%</div></div></div>
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🧅</div><span data-i18n="m_onion">Onion</span></div><div class="price-info"><div class="price">Rs. 85</div><div class="trend up"><i class="fas fa-arrow-up"></i> 8%</div></div></div>
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🥬</div><span data-i18n="m_cabbage">Cabbage</span></div><div class="price-info"><div class="price">Rs. 30</div><div class="trend up"><i class="fas fa-arrow-up"></i> 2%</div></div></div>
                    </div>

                    <div id="cat-fruit" class="market-list">
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🍎</div><span data-i18n="m_apple">Apple</span></div><div class="price-info"><div class="price">Rs. 250</div><div class="trend up"><i class="fas fa-arrow-up"></i> 5%</div></div></div>
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🍌</div><span data-i18n="m_banana">Banana (Doz)</span></div><div class="price-info"><div class="price">Rs. 120</div><div class="trend down"><i class="fas fa-arrow-down"></i> 2%</div></div></div>
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🥭</div><span data-i18n="m_mango">Mango</span></div><div class="price-info"><div class="price">Rs. 150</div><div class="trend up"><i class="fas fa-arrow-up"></i> 10%</div></div></div>
                    </div>

                    <div id="cat-crop" class="market-list">
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🌾</div><span data-i18n="m_rice">Rice (Paddy)</span></div><div class="price-info"><div class="price">Rs. 35</div><div class="trend up"><i class="fas fa-arrow-up"></i> 1%</div></div></div>
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🌽</div><span data-i18n="m_corn">Maize/Corn</span></div><div class="price-info"><div class="price">Rs. 40</div><div class="trend down"><i class="fas fa-arrow-down"></i> 3%</div></div></div>
                        <div class="market-item"><div class="crop-name"><div class="crop-icon">🌾</div><span data-i18n="m_wheat">Wheat</span></div><div class="price-info"><div class="price">Rs. 45</div><div class="trend up"><i class="fas fa-arrow-up"></i> 2%</div></div></div>
                    </div>
                </div>
            </div>

            <div id="tab-learn" class="tab-content">
                <div class="glass-card">
                    <div class="card-header">
                        <h3><i class="fas fa-book-open" style="color:var(--primary)"></i> <span data-i18n="learn_title">Knowledge Hub</span></h3>
                    </div>
                    <p style="font-size: 13px; color: var(--text-muted); margin-top:0;" data-i18n="learn_sub">Search any crop, fruit, or vegetable to generate a complete organic farming guide.</p>
                    
                    <div class="search-box">
                        <i class="fas fa-search"></i>
                        <input type="text" id="searchCrop" placeholder="e.g. Tomato, Apple, Wheat..." data-i18n-ph="search_ph">
                    </div>
                    
                    <button class="btn-main" onclick="getOrganicGuide()">
                        <i class="fas fa-magic"></i> <span data-i18n="btn_generate">Generate Guide</span>
                    </button>
                    
                    <div id="organicRes" style="display:none; margin-top: 20px; font-size: 14px; line-height: 1.6; background: rgba(0,0,0,0.02); padding: 15px; border-radius: 12px; border: 1px solid var(--glass-border);"></div>
                </div>
            </div>

        </div> <div class="bottom-nav">
            <div class="nav-item active" onclick="switchTab('home', this)">
                <i class="fas fa-house"></i><span data-i18n="nav_home">Home</span>
            </div>
            <div class="nav-item" onclick="switchTab('ai', this)">
                <i class="fas fa-sparkles"></i><span data-i18n="nav_ai">Krishi AI</span>
            </div>
            <div class="nav-item" onclick="switchTab('market', this)">
                <i class="fas fa-chart-simple"></i><span data-i18n="nav_market">Market</span>
            </div>
            <div class="nav-item" onclick="switchTab('learn', this)">
                <i class="fas fa-graduation-cap"></i><span data-i18n="nav_learn">Learn</span>
            </div>
        </div>

    </div>

    <script>
        // --- THEME ---
        let isDark = false;
        function toggleTheme() {
            isDark = !isDark;
            document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
            document.getElementById('themeIcon').className = isDark ? 'fas fa-sun' : 'fas fa-moon';
        }

        // --- I18N DICTIONARY ---
        const dict = {
            en: {
                greeting: "Hello, Farmer", loc_fetching: "Locating...",
                weather_title: "Live Environment", humidity: "Humidity", soil: "Soil", wind: "Wind",
                smart_alert: "Smart Alert", alert_text: "Optimal conditions for spraying fertilizers today. Wind speed is low.",
                ai_intro: "I am your advanced farm assistant. Ask me anything, use your voice, or upload a photo of a crop for instant diagnosis.", chat_ph: "Ask Krishi AI...",
                market_title: "Live Market Prices", market_sub: "Estimated rates in NPR (per kg/piece) for your region.",
                cat_veg: "Vegetables", cat_fruit: "Fruits", cat_crop: "Crops/Grains",
                m_tomato: "Tomato", m_potato: "Potato", m_onion: "Onion", m_cabbage: "Cabbage",
                m_apple: "Apple", m_banana: "Banana (Doz)", m_mango: "Mango",
                m_rice: "Rice (Paddy)", m_corn: "Maize/Corn", m_wheat: "Wheat",
                learn_title: "Knowledge Hub", learn_sub: "Search any crop, fruit, or vegetable to generate a complete organic farming guide.", search_ph: "e.g. Tomato, Apple, Wheat...", btn_generate: "Generate Guide",
                nav_home: "Home", nav_ai: "Krishi AI", nav_market: "Market", nav_learn: "Learn"
            },
            ne: {
                greeting: "नमस्ते, किसान", loc_fetching: "स्थान खोज्दै...",
                weather_title: "प्रत्यक्ष वातावरण", humidity: "आर्द्रता", soil: "माटो", wind: "हावा",
                smart_alert: "स्मार्ट अलर्ट", alert_text: "आज मल हाल्नको लागि उपयुक्त मौसम छ। हावाको गति कम छ।",
                ai_intro: "म तपाईंको उन्नत कृषि सहायक हुँ। मलाई केही सोध्नुहोस्, आवाज प्रयोग गर्नुहोस्, वा रोग पहिचान गर्न फोटो अपलोड गर्नुहोस्।", chat_ph: "Krishi AI लाई सोध्नुहोस्...",
                market_title: "प्रत्यक्ष बजार भाउ", market_sub: "तपाईंको क्षेत्रको लागि अनुमानित दर NPR (प्रति केजी/दर्जन)।",
                cat_veg: "तरकारी", cat_fruit: "फलफूल", cat_crop: "बाली/अन्न",
                m_tomato: "गोलभेँडा", m_potato: "आलु", m_onion: "प्याज", m_cabbage: "बन्दाकोबी",
                m_apple: "स्याउ", m_banana: "केरा (दर्जन)", m_mango: "आँप",
                m_rice: "धान", m_corn: "मकै", m_wheat: "गहुँ",
                learn_title: "ज्ञान केन्द्र", learn_sub: "कुनै पनि बाली, फलफूल वा तरकारीको जैविक खेती विधि जान्न खोज्नुहोस्।", search_ph: "जस्तै: गोलभेँडा, स्याउ, गहुँ...", btn_generate: "मार्गदर्शन तयार गर्नुहोस्",
                nav_home: "गृह", nav_ai: "कृषि एआई", nav_market: "बजार", nav_learn: "सिक्नुहोस्"
            }
        };

        let currentLang = 'en';
        function toggleLang() {
            currentLang = currentLang === 'en' ? 'ne' : 'en';
            document.getElementById('langBtn').innerText = currentLang === 'en' ? 'ने' : 'EN';
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if(dict[currentLang][key]) el.innerText = dict[currentLang][key];
            });
            document.querySelectorAll('[data-i18n-ph]').forEach(el => {
                const key = el.getAttribute('data-i18n-ph');
                if(dict[currentLang][key]) el.placeholder = dict[currentLang][key];
            });
            updateWeatherText();
        }

        // --- NAVIGATION ---
        function switchTab(tabId, element) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            element.classList.add('active');
            if(tabId === 'ai') {
                const cb = document.getElementById('chatBox');
                cb.scrollTop = cb.scrollHeight;
            }
        }

        function switchMarketCat(cat, element) {
            document.querySelectorAll('.market-list').forEach(list => list.classList.remove('active'));
            document.querySelectorAll('.cat-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('cat-' + cat).classList.add('active');
            element.classList.add('active');
        }

        // --- GEOLOCATION & WEATHER ---
        let isDayGlobal = true;
        
        async function getLocationAndWeather() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    async (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        // 1. Get City Name (Reverse Geocoding)
                        try {
                            const geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                            const geoData = await geoRes.json();
                            const city = geoData.address.city || geoData.address.town || geoData.address.village || geoData.address.county || "Nepal";
                            document.getElementById('locationText').innerText = city;
                        } catch(e) { document.getElementById('locationText').innerText = "Location Found"; }
                        
                        // 2. Get Weather for exactly that location
                        fetchWeatherData(lat, lon);
                    },
                    (error) => {
                        // Fallback to Damak if user denies location
                        document.getElementById('locationText').innerText = "Damak (Default)";
                        fetchWeatherData(26.66, 87.67);
                    }
                );
            } else {
                document.getElementById('locationText').innerText = "Damak (Default)";
                fetchWeatherData(26.66, 87.67);
            }
        }

        async function fetchWeatherData(lat, lon) {
            try {
                const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true&hourly=relativehumidity_2m`);
                const data = await res.json();
                document.getElementById('temp').innerText = Math.round(data.current_weather.temperature) + "°";
                document.getElementById('wind').innerText = data.current_weather.windspeed + " km/h";
                document.getElementById('humidity').innerText = data.hourly.relativehumidity_2m[0] + "%";
                isDayGlobal = data.current_weather.is_day;
                updateWeatherText();
            } catch (e) {
                console.log("Weather failed");
            }
        }

        function updateWeatherText() {
            const desc = document.getElementById('weatherDesc');
            const icon = document.getElementById('weatherIcon');
            if (isDayGlobal) {
                desc.innerText = currentLang === 'en' ? "Clear / Sunny" : "सफा / घमाइलो";
                icon.className = "fas fa-sun w-icon";
                icon.style.color = "var(--accent)";
            } else {
                desc.innerText = currentLang === 'en' ? "Clear Night" : "सफा रात";
                icon.className = "fas fa-moon w-icon";
                icon.style.color = "#94a3b8";
            }
        }

        // Initialize location on load
        getLocationAndWeather();


        // --- AI CHAT ENGINE ---
        let selectedFile = null;

        function handleImageSelect() {
            const file = document.getElementById('imageInput').files[0];
            if(file) {
                selectedFile = file;
                document.getElementById('camIcon').style.color = "var(--primary)";
            }
        }

        function appendMessage(htmlContent, isUser) {
            const chatBox = document.getElementById('chatBox');
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'msg-user' : 'msg-ai'}`;
            div.innerHTML = htmlContent;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function handleEnter(e) { if(e.key === 'Enter') sendMessage(); }

        async function sendMessage() {
            const inputEl = document.getElementById('chatInput');
            const text = inputEl.value.trim();
            if(!text && !selectedFile) return;

            let userHtml = "";
            if(selectedFile) userHtml += `<img src="${URL.createObjectURL(selectedFile)}" class="msg-img">`;
            if(text) userHtml += text;
            appendMessage(userHtml, true);

            inputEl.value = "";
            document.getElementById('camIcon').style.color = "";
            
            const typingId = "typing-" + Date.now();
            appendMessage(`<div id="${typingId}"><i class="fas fa-circle-notch fa-spin"></i></div>`, false);

            try {
                let responseText = "";
                if (selectedFile) {
                    const formData = new FormData();
                    formData.append("file", selectedFile);
                    formData.append("message", text || "Diagnose this.");
                    formData.append("lang", currentLang);
                    const r = await fetch('/analyze-crop', { method: 'POST', body: formData });
                    const d = await r.json();
                    responseText = d.analysis;
                    selectedFile = null; 
                    document.getElementById('imageInput').value = ""; 
                } else {
                    const r = await fetch('/ask', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question: text, lang: currentLang}) });
                    const d = await r.json();
                    responseText = d.answer;
                }
                document.getElementById(typingId).innerHTML = responseText.replace(/\\n/g, '<br>');
            } catch (e) {
                document.getElementById(typingId).innerHTML = "Connection Error.";
            }
        }

        // --- VOICE RECOGNITION ---
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.onresult = function(event) {
                document.getElementById('chatInput').value += event.results[0][0].transcript + " ";
                document.getElementById('micBtn').classList.remove('recording');
            };
            recognition.onerror = recognition.onend = function() {
                document.getElementById('micBtn').classList.remove('recording');
            };
        }

        function toggleVoice() {
            if (!recognition) return alert("Voice not supported in this browser.");
            recognition.lang = currentLang === 'en' ? 'en-US' : 'ne-NP';
            recognition.start();
            document.getElementById('micBtn').classList.add('recording');
        }

        // --- ADVANCED SEARCH (LEARN TAB) ---
        async function getOrganicGuide() {
            const crop = document.getElementById('searchCrop').value.trim();
            if(!crop) return alert(currentLang === 'en' ? "Please type a crop name first." : "कृपया पहिले बालीको नाम लेख्नुहोस्।");
            
            const resDiv = document.getElementById('organicRes');
            resDiv.style.display = "block";
            resDiv.innerHTML = "<div style='text-align:center;'><i class='fas fa-circle-notch fa-spin fa-2x' style='color:var(--primary); margin-bottom:10px;'></i><br>" + (currentLang === 'en' ? "Generating comprehensive guide..." : "विस्तृत मार्गदर्शन तयार गरिँदैछ...") + "</div>";
            
            const p = currentLang === 'en' 
                ? `Write a comprehensive organic farming guide for ${crop}. Include: 1. Soil preparation, 2. Planting, 3. Organic Fertilizers, 4. Pest Control.` 
                : `${crop} को लागि विस्तृत जैविक खेती मार्गदर्शन लेख्नुहोस्। जसमा समावेश होस्: १. माटो तयारी, २. रोप्ने तरिका, ३. जैविक मल, ४. रोग/कीरा नियन्त्रण।`;
                
            try {
                const r = await fetch('/ask', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question: p, lang: currentLang}) });
                const d = await r.json();
                resDiv.innerHTML = d.answer.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>');
            } catch(e) {
                resDiv.innerHTML = "Error generating plan.";
            }
        }
    </script>
</body>
</html>
"""

class UserMessage(BaseModel):
    question: str
    lang: str = "en"

@app.get("/")
async def read_index():
    headers = {"Cache-Control": "no-cache, no-store, must-revalidate"}
    return HTMLResponse(content=HTML_TEMPLATE, headers=headers)

@app.post("/ask")
def ask_ai(message: UserMessage):
    try:
        lang_prompt = "Respond in Nepali. Use simple terms." if message.lang == 'ne' else "Respond in English."
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"You are Krishi AI, a premium agricultural assistant in a smart app. {lang_prompt} Keep answers concise and structured. Use markdown bolding (**text**) for headings. Answer: {message.question}"
        )
        return {"answer": response.text}
    except Exception as e:
        return {"answer": "Krishi AI engine is currently resting (Quota Limit). Please try again tomorrow!"}

@app.post("/analyze-crop")
async def analyze_crop(file: UploadFile = File(...), message: str = Form(""), lang: str = Form("en")):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        lang_prompt = "Respond in Nepali." if lang == 'ne' else "Respond in English."
        prompt = f"User message: '{message}'. Diagnose this crop image. Give the disease name, cause, and a 2-step organic treatment. Use markdown bolding. {lang_prompt}"
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, image]
        )
        return {"analysis": response.text}
    except Exception as e:
        return {"analysis": "Krishi AI engine is currently resting (Quota Limit). Please try again tomorrow!"}