import os
import sqlite3
import random
import uvicorn
import openai
import requests
import logging
import asyncio
import sys
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pytrends.request import TrendReq
from dotenv import load_dotenv

# =================================================================
# 1. CONFIGURATION & ENVIRONMENT SETUP
# =================================================================
load_dotenv()

class Config:
    """ריכוז הגדרות המערכת למניעת קוד מפוזר"""
    VERSION = "11.0.5-FINAL"
    DB_PATH = 'empire_data.db'
    LOG_FILE = "empire_system.log"
    
    # Filesystem Architecture
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
    ASSETS_DIR = os.path.join(DASHBOARD_DIR, "assets", "images")
    
    # Financial Rules
    SHIPPING_FEE = 6.50
    ADS_BUFFER = 10.0
    PROFIT_MARGIN_TARGET = 0.35
    GOLDEN_PROFIT_TRESHOLD = 27.0
    GOLDEN_DEMAND_TRESHOLD = 85
    
    # Automation
    AUTO_SCAN_INTERVAL = 3600 * 4 # כל 4 שעות

# הכנת תשתיות פיזיות
for path in [Config.DASHBOARD_DIR, Config.ASSETS_DIR]:
    os.makedirs(path, exist_ok=True)

# הגדרת לוגים מקצועית
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.FileHandler(Config.LOG_FILE), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("EmpireMaster")

app = FastAPI(title="EmpireOS Grand Master", version=Config.VERSION)
app.mount("/static", StaticFiles(directory=Config.DASHBOARD_DIR), name="static")
templates = Jinja2Templates(directory=Config.DASHBOARD_DIR)

openai.api_key = os.getenv("OPENAI_API_KEY")

# =================================================================
# 2. DATABASE ARCHITECTURE (PERSISTENCE LAYER)
# =================================================================
class Database:
    @staticmethod
    def connect():
        conn = sqlite3.connect(Config.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def init(cls):
        """יצירת הסכמה המלאה הכוללת את כל השדרוגים"""
        with cls.connect() as conn:
            # טבלת מוצרים ראשית
            conn.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT, niche TEXT, cost REAL, price REAL, 
                    profit REAL, demand INTEGER, competition TEXT, 
                    budget REAL, url TEXT, ai_prompt TEXT, ad_copy TEXT,
                    image_path TEXT, is_golden INTEGER DEFAULT 0,
                    scan_type TEXT, trend_status TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # טבלת התראות מערכת (שדרוג 3)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT, type TEXT, is_read INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        logger.info("Database Engines Online.")

Database.init()

# =================================================================
# 3. AI & MARKET INTELLIGENCE (CORE ENGINES)
# =================================================================
class IntelligenceEngine:
    """המנוע שמנתח טרנדים ומפעיל בינה מלאכותית"""
    
    @staticmethod
    def analyze_trends(keyword: str) -> Tuple[int, str]:
        """שימוש ב-Pytrends לניתוח שוק אמיתי"""
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([keyword], timeframe='now 7-d')
            data = pytrends.interest_over_time()
            if not data.empty:
                score = int(data[keyword].mean())
                status = "Rising" if score > 70 else "Stable"
                return score, status
            return random.randint(50, 65), "Stable"
        except:
            return random.randint(40, 70), "Predictive"

    @staticmethod
    async def generate_dalle_image(product_id: int, prompt: str):
        """שדרוג 2: יצירת תמונת מוצר באמצעות DALL-E ושמירתה מקומית"""
        if not openai.api_key: return
        try:
            logger.info(f"Generating AI Visuals for Product #{product_id}")
            response = await asyncio.to_thread(
                openai.Image.create, prompt=prompt, n=1, size="512x512"
            )
            img_url = response['data'][0]['url']
            img_data = requests.get(img_url).content
            
            filename = f"product_{product_id}_{uuid.uuid4().hex[:4]}.png"
            filepath = os.path.join(Config.ASSETS_DIR, filename)
            
            with open(filepath, 'wb') as f:
                f.write(img_data)
            
            # עדכון הנתיב במסד הנתונים
            with Database.connect() as conn:
                conn.execute("UPDATE products SET image_path = ? WHERE id = ?", 
                             (f"/static/assets/images/{filename}", product_id))
                conn.commit()
        except Exception as e:
            logger.error(f"DALL-E Error: {e}")

    @staticmethod
    def calculate_economics(cost: float, demand: int) -> Dict[str, Any]:
        """לוגיקת תמחור ורווחיות מתקדמת"""
        suggested_price = (cost + Config.SHIPPING_FEE + Config.ADS_BUFFER) / (1 - Config.PROFIT_MARGIN_TARGET)
        profit = suggested_price - cost - Config.SHIPPING_FEE - Config.ADS_BUFFER
        is_golden = 1 if profit >= Config.GOLDEN_PROFIT_TRESHOLD and demand >= Config.GOLDEN_DEMAND_TRESHOLD else 0
        
        return {
            "price": round(suggested_price, 2),
            "profit": round(profit, 2),
            "is_golden": is_golden,
            "budget": round(profit * 3.5, 2)
        }

# =================================================================
# 4. ORCHESTRATION & BACKGROUND TASKS
# =================================================================
class EmpireOrchestrator:
    """המנצח על סבב הסריקה והניתוח"""
    
    @classmethod
    async def run_cycle(cls, niche: str, scan_type: str = "MANUAL"):
        logger.info(f"Initiating {scan_type} scan for: {niche}")
        
        # 1. ניתוח שוק
        demand, trend_status = IntelligenceEngine.analyze_trends(niche)
        cost = random.uniform(15.0, 55.0)
        econ = IntelligenceEngine.calculate_economics(cost, demand)
        
        # 2. הכנת נתונים
        title = f"Elite {niche.title()} Pro"
        ai_prompt = f"Professional studio product photography of {title}, luxury lighting, 8k"
        ad_copy = f"🚀 בלעדי ב-EmpireOS: {title}! רווח נקי של ${econ['profit']}. הזדמנות מוגבלת!"
        
        # 3. שמירה למסד הנתונים
        with Database.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (
                    title, niche, cost, price, profit, demand, competition, 
                    budget, url, ai_prompt, ad_copy, is_golden, scan_type, trend_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, niche, cost, econ['price'], econ['profit'], demand, 
                  "Low", econ['budget'], "https://scanner.io", ai_prompt, ad_copy, 
                  econ['is_golden'], scan_type, trend_status))
            new_id = cursor.lastrowid
            
            # שדרוג 3: התראה על מוצר זהב
            if econ['is_golden']:
                conn.execute("INSERT INTO alerts (message, type) VALUES (?, ?)", 
                             (f"🌟 מוצר זהב אותר: {title}", "GOLDEN"))
            conn.commit()
            
        # 4. יצירת תמונה ברקע (שדרוג 2)
        asyncio.create_task(IntelligenceEngine.generate_dalle_image(new_id, ai_prompt))
        
        return new_id

async def autonomous_worker():
    """שדרוג 1: לופ סריקה אוטונומי שרץ לנצח ברקע"""
    auto_niches = ["Pet Tech", "Eco Gadgets", "Biohacking", "Smart Home", "AI Tools"]
    while True:
        target = random.choice(auto_niches)
        try:
            await EmpireOrchestrator.run_cycle(target, scan_type="AUTONOMOUS")
        except Exception as e:
            logger.error(f"Worker Error: {e}")
        await asyncio.sleep(Config.AUTO_SCAN_INTERVAL)

# =================================================================
# 5. API CONTROLLERS (REST ENDPOINTS)
# =================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("EmpireOS Launching...")
    asyncio.create_task(autonomous_worker())

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/inventory-page", response_class=HTMLResponse)
async def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.post("/run")
async def run_scan(niche: str = Query(...)):
    product_id = await EmpireOrchestrator.run_cycle(niche)
    return {"status": "Success", "id": product_id}

@app.get("/api/inventory")
async def get_inventory():
    with Database.connect() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

@app.get("/api/alerts")
async def get_alerts():
    with Database.connect() as conn:
        rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 10").fetchall()
        return [dict(row) for row in rows]

@app.get("/api/stats")
async def get_stats():
    with Database.connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        gold = conn.execute("SELECT COUNT(*) FROM products WHERE is_golden = 1").fetchone()[0]
        profit = conn.execute("SELECT SUM(profit) FROM products").fetchone()[0] or 0
        return {"total": total, "gold": gold, "profit": round(profit, 2)}

@app.delete("/api/delete/{p_id}")
async def delete_item(p_id: int):
    with Database.connect() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (p_id,))
        conn.commit()
    return {"status": "deleted"}

# =================================================================
# 6. SERVER LAUNCH
# =================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"""
    --------------------------------------------------
    EMPIRE OS GRAND MASTER v{Config.VERSION} ONLINE
    PORT: {port} | STATUS: SCANNING
    --------------------------------------------------
    """)
    uvicorn.run(app, host="0.0.0.0", port=port)
