import os
import sqlite3
import random
import uvicorn
import openai
import requests
import logging
import asyncio
import json
import sys
import shutil
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Query, HTTPException, BackgroundTasks, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator
from pytrends.request import TrendReq
from dotenv import load_dotenv

# =================================================================
# 1. CORE SYSTEM CONFIGURATION & ENVIRONMENT
# =================================================================
load_dotenv()

class SystemConfig:
    """הגדרות ליבה של האימפריה - ריכוז כל הפרמטרים במקום אחד"""
    VERSION = "10.0.0-GRANDMASTER"
    DB_PATH = 'empire_vault_v10.db'
    LOG_FILE = "empire_master.log"
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
    IMAGES_DIR = os.path.join(DASHBOARD_DIR, "assets", "generated")
    
    # Business Logic Constants
    SHIPPING_COST = 6.25
    AD_TEST_MULTIPLIER = 3.5
    MIN_PROFIT_MARGIN = 0.32
    GOLDEN_PROFIT_LIMIT = 28.0
    GOLDEN_DEMAND_LIMIT = 82
    
    # Automation
    AUTO_SCAN_INTERVAL = 3600 * 4 # 4 Hours
    DEFAULT_NICHES = ["Cyber Security Tools", "Biohacking Gear", "Smart Home AI", "Eco-Transport"]

# אתחול לוגים ברמה גבוהה
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | [%(name)s] | %(message)s',
    handlers=[logging.FileHandler(SystemConfig.LOG_FILE), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("EmpireOS_GrandMaster")

# יצירת מבנה תיקיות פיזי
for path in [SystemConfig.DASHBOARD_DIR, SystemConfig.IMAGES_DIR]:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

app = FastAPI(title="EmpireOS Grand Master", version=SystemConfig.VERSION)
app.mount("/static", StaticFiles(directory=SystemConfig.DASHBOARD_DIR), name="static")
templates = Jinja2Templates(directory=SystemConfig.DASHBOARD_DIR)

openai.api_key = os.getenv("OPENAI_API_KEY")

# =================================================================
# 2. DATABASE ARCHITECTURE & ORM LIGHT
# =================================================================
class DatabaseManager:
    """ניהול כל האינטראקציה עם מסד הנתונים"""
    @staticmethod
    def get_connection():
        return sqlite3.connect(SystemConfig.DB_PATH)

    @classmethod
    def initialize(cls):
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        # טבלת מוצרים - המחסן המרכזי
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                niche TEXT,
                cost REAL,
                suggested_price REAL,
                profit REAL,
                demand_score INTEGER,
                competition TEXT,
                ad_budget REAL,
                url TEXT,
                ai_prompt TEXT,
                ad_copy_he TEXT,
                image_path TEXT,
                is_golden INTEGER DEFAULT 0,
                source_type TEXT,
                trend_rating TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת התראות (שדרוג 3)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                severity TEXT,
                message TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת היסטוריית סריקות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT,
                results_found INTEGER,
                status TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database Schema deployed successfully.")

DatabaseManager.initialize()

# =================================================================
# 3. ADVANCED BUSINESS INTELLIGENCE ENGINE
# =================================================================
class EmpireIntelligence:
    """המנוע שמקבל החלטות, מנתח טרנדים ומפעיל AI"""
    
    @staticmethod
    def get_google_trends(keyword: str) -> Dict[str, Any]:
        """ניתוח טרנדים אמיתי (שדרוג)"""
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([keyword], timeframe='now 7-d')
            interest = pytrends.interest_over_time()
            if not interest.empty:
                score = int(interest[keyword].mean())
                status = "EXPLOSIVE" if score > 80 else "GROWING" if score > 50 else "STABLE"
                return {"score": score, "status": status}
            return {"score": 50, "status": "STABLE"}
        except Exception as e:
            logger.warning(f"Trends API failure: {e}")
            return {"score": random.randint(45, 65), "status": "UNCERTAIN"}

    @classmethod
    async def generate_dalle_asset(cls, product_id: int, prompt: str):
        """שדרוג 2: יצירת תמונה מבוססת בינה מלאכותית"""
        if not openai.api_key:
            return None
        
        try:
            logger.info(f"Requesting DALL-E asset for Product ID: {product_id}")
            response = await asyncio.to_thread(
                openai.Image.create,
                prompt=prompt,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            
            # הורדת התמונה ושמירתה
            img_res = requests.get(image_url, stream=True)
            if img_res.status_code == 200:
                file_name = f"empire_prod_{product_id}.png"
                local_path = os.path.join(SystemConfig.IMAGES_DIR, file_name)
                with open(local_path, 'wb') as f:
                    shutil.copyfileobj(img_res.raw, f)
                
                # עדכון DB
                conn = DatabaseManager.get_connection()
                conn.execute("UPDATE products SET image_path = ? WHERE id = ?", 
                             (f"/static/assets/generated/{file_name}", product_id))
                conn.commit()
                conn.close()
                logger.info(f"Asset for #{product_id} saved to {local_path}")
        except Exception as e:
            logger.error(f"DALL-E Asset Error: {e}")

    @staticmethod
    def calculate_economics(cost: float, demand: int) -> Dict[str, Any]:
        """חישובים פיננסיים מתקדמים"""
        price = (cost + SystemConfig.SHIPPING_COST + 10) / (1 - SystemConfig.MIN_PROFIT_MARGIN)
        profit = price - cost - SystemConfig.SHIPPING_COST - 10
        is_golden = 1 if profit >= SystemConfig.GOLDEN_PROFIT_LIMIT and demand >= SystemConfig.GOLDEN_DEMAND_LIMIT else 0
        
        return {
            "suggested_price": round(price, 2),
            "profit": round(profit, 2),
            "ad_budget": round(profit * SystemConfig.AD_TEST_MULTIPLIER, 2),
            "is_golden": is_golden
        }

# =================================================================
# 4. BACKGROUND WORKERS (שדרוג 1: אוטונומיה מלאה)
# =================================================================
async def autonomous_scout_worker():
    """לופ סריקה אוטונומי - הלב הפועם של המערכת"""
    while True:
        try:
            niche = random.choice(SystemConfig.DEFAULT_NICHES)
            logger.info(f"AUTONOMOUS SCAN STARTING: Target Niche -> {niche}")
            
            # סימולציית סריקת שוק
            trends = EmpireIntelligence.get_google_trends(niche)
            cost = random.uniform(18.0, 60.0)
            econ = EmpireIntelligence.calculate_economics(cost, trends['score'])
            
            title = f"Industrial {niche} Solution v{random.randint(1,9)}"
            ad_copy = f"🚀 בלעדי: {title}! רווח נקי של ${econ['profit']}. המלאי אוזל!"
            prompt = f"Futuristic {niche} product, high-tech aesthetic, cinematic lighting, 8k"
            
            conn = DatabaseManager.get_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO products (title, niche, cost, suggested_price, profit, demand_score, 
                                    competition, ad_budget, ai_prompt, ad_copy_he, is_golden, 
                                    source_type, trend_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, niche, cost, econ['suggested_price'], econ['profit'], trends['score'],
                  "Low", econ['ad_budget'], prompt, ad_copy, econ['is_golden'], "AUTONOMOUS", trends['status']))
            
            new_id = c.lastrowid
            conn.commit()
            
            # יצירת התראה אם זה מוצר זהב (שדרוג 3)
            if econ['is_golden']:
                c.execute("INSERT INTO system_alerts (severity, message) VALUES (?, ?)",
                         ("GOLDEN", f"New Golden Opportunity Discovered: {title}"))
                conn.commit()
            
            conn.close()
            
            # הפעלת DALL-E (שדרוג 2)
            asyncio.create_task(EmpireIntelligence.generate_dalle_asset(new_id, prompt))
            
            logger.info(f"AUTONOMOUS SCAN COMPLETED: Product #{new_id} Secured.")
            
        except Exception as e:
            logger.error(f"Worker Error: {e}")
            
        await asyncio.sleep(SystemConfig.AUTO_SCAN_INTERVAL)

# =================================================================
# 5. API ROUTES & CONTROLLERS
# =================================================================

@app.on_event("startup")
async def on_startup():
    logger.info("EmpireOS starting up background services...")
    asyncio.create_task(autonomous_scout_worker())

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/inventory", response_class=HTMLResponse)
async def serve_inventory(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.post("/api/scan/manual")
async def manual_scan(niche: str = Query(...)):
    """סריקה ידנית יזומה מהממשק"""
    logger.info(f"Manual scan triggered for niche: {niche}")
    trends = EmpireIntelligence.get_google_trends(niche)
    cost = random.uniform(20, 50)
    econ = EmpireIntelligence.calculate_economics(cost, trends['score'])
    
    conn = DatabaseManager.get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO products (title, niche, cost, suggested_price, profit, demand_score, 
                            competition, ad_budget, ai_prompt, ad_copy_he, is_golden, 
                            source_type, trend_rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (f"Manual Discovery: {niche}", niche, cost, econ['suggested_price'], econ['profit'], 
          trends['score'], "Medium", econ['ad_budget'], "Product shot", "Ready to launch", 
          econ['is_golden'], "MANUAL", trends['status']))
    
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return {"status": "Success", "id": new_id, "is_golden": bool(econ['is_golden'])}

@app.get("/api/vault")
async def get_vault_data():
    """שליפת כל הנכסים מהכספת"""
    conn = DatabaseManager.get_connection()
    conn.row_factory = sqlite3.Row
    data = conn.execute("SELECT * FROM products ORDER BY is_golden DESC, created_at DESC").fetchall()
    conn.close()
    return [dict(row) for row in data]

@app.get("/api/alerts")
async def get_system_alerts():
    """שליפת התראות (שדרוג 3)"""
    conn = DatabaseManager.get_connection()
    conn.row_factory = sqlite3.Row
    data = conn.execute("SELECT * FROM system_alerts ORDER BY created_at DESC LIMIT 20").fetchall()
    conn.close()
    return [dict(row) for row in data]

@app.get("/api/stats/global")
async def get_global_stats():
    """חישוב נתונים מסכמים לאימפריה"""
    conn = DatabaseManager.get_connection()
    stats = {}
    stats['total_assets'] = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    stats['golden_wins'] = conn.execute("SELECT COUNT(*) FROM products WHERE is_golden = 1").fetchone()[0]
    stats['total_profit_potential'] = round(conn.execute("SELECT SUM(profit) FROM products").fetchone()[0] or 0, 2)
    
    # חלוקה לפי נישות
    conn.row_factory = sqlite3.Row
    stats['niche_analysis'] = [dict(r) for r in conn.execute("SELECT niche, COUNT(*) as count FROM products GROUP BY niche")]
    
    conn.close()
    return stats

@app.delete("/api/purge/{item_id}")
async def purge_item(item_id: int):
    conn = DatabaseManager.get_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"status": "Purged"}

@app.get("/system/health")
async def health():
    return {
        "status": "OPERATIONAL",
        "version": SystemConfig.VERSION,
        "database": os.path.exists(SystemConfig.DB_PATH),
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# =================================================================
# 6. ENGINE STARTUP
# =================================================================
if __name__ == "__main__":
    banner = f"""
    #######################################################
    #          EMPIRE OS - GRAND MASTER v{SystemConfig.VERSION}        #
    #    -----------------------------------------------  #
    #    [*] ASSETS: http://localhost:8000/inventory      #
    #    [*] MONITORING: ACTIVE                           #
    #    [*] AI WORKERS: DEPLOYED                         #
    #######################################################
    """
    print(banner)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
from fastapi.middleware.cors import CORSMiddleware

# אפשור לריאקט "לדבר" עם פייתון (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # בפיתוח מאפשרים הכל
    allow_methods=["*"],
    allow_headers=["*"],
)

# הגשת התמונות שה-AI מייצר בתיקייה static
app.mount("/images", StaticFiles(directory="backend/static"), name="images")
from fastapi.middleware.cors import CORSMiddleware

# הגדרת CORS - קריטי כדי שהדפדפן לא יחסום את החיבור
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # בייצור נגביל את זה לכתובת של ה-Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/inventory")
async def get_inventory():
    # כאן הקוד ששולף מה- empire_unified.db
    return inventory_items
