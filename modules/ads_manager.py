import os
import sqlite3
import random
import uvicorn
import openai
import requests
import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Query, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from pytrends.request import TrendReq
from dotenv import load_dotenv

# =================================================================
# 1. INITIALIZATION & CORE SETTINGS
# =================================================================
load_dotenv()

# הגדרת לוגים מקצועית למעקב אחרי סריקות
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[logging.FileHandler("empire_system.log"), logging.StreamHandler()]
)
logger = logging.getLogger("EmpireOS")

app = FastAPI(title="EmpireOS - Global Command Center v8.0")

# הגדרות נתיבים
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")

if not os.path.exists(DASHBOARD_DIR):
    os.makedirs(DASHBOARD_DIR)

app.mount("/static", StaticFiles(directory=DASHBOARD_DIR), name="static")
templates = Jinja2Templates(directory=DASHBOARD_DIR)

# קבועים עסקיים
DB_PATH = 'empire_data.db'
SHIPPING_COST = 5.50
ADS_COST_ESTIMATE = 10.0
TARGET_MARGIN = 0.30 
GOLDEN_THRESHOLD_PROFIT = 25.0
GOLDEN_THRESHOLD_DEMAND = 85

# הגדרת API Keys
openai.api_key = os.getenv("OPENAI_API_KEY")

# =================================================================
# 2. DATABASE ARCHITECTURE
# =================================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # טבלת מוצרים מורחבת
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, 
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
                  is_golden INTEGER DEFAULT 0,
                  trend_status TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # טבלת לוגים של המערכת
    c.execute('''CREATE TABLE IF NOT EXISTS system_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  event TEXT,
                  level TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
    logger.info("Database Engines Synchronized.")

init_db()

# =================================================================
# 3. ADVANCED INTELLIGENCE ENGINES
# =================================================================
class EmpireEngine:
    @staticmethod
    def get_market_trends(keyword: str):
        """שימוש ב-pytrends לניתוח מגבשות אמיתי"""
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([keyword], cat=0, timeframe='now 7-d')
            data = pytrends.interest_over_time()
            if not data.empty:
                trend_score = int(data[keyword].mean())
                return "Rising" if trend_score > 50 else "Stable"
            return "Unknown"
        except Exception as e:
            logger.error(f"Pytrends Error: {e}")
            return "Stable"

    @staticmethod
    def generate_ai_assets(title: str, profit: float):
        """יצירת תוכן שיווקי באמצעות OpenAI"""
        if not openai.api_key:
            return f"מבצע מטורף על {title}! רווח ליחידה: ${profit}", "Realistic product photo"
        
        try:
            # כאן ניתן להפעיל קריאת API אמיתית. כרגע כשלד כדי לא לבזבז טוקנים בטעות.
            ad_copy = f"🚀 בלעדי ב-EmpireOS: {title}! פוטנציאל רווח של ${profit}. מלאי מוגבל."
            image_prompt = f"Professional studio lighting for {title}, 8k resolution, minimalist background."
            return ad_copy, image_prompt
        except Exception as e:
            return f"Error generating AI content: {e}", "Default Prompt"

    @staticmethod
    def ads_manager_launch(title, profit, demand):
        """אופטימיזציה של תקציב פרסום"""
        base_budget = profit * 2.5
        if demand > 90:
            base_budget *= 1.5 # הגדלת תקציב למוצרים ויראליים
        return round(base_budget, 2)

    @staticmethod
    def scrape_and_analyze(niche_or_url):
        """מנוע סריקה משולב עם BeautifulSoup"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        if niche_or_url.startswith('http'):
            try:
                logger.info(f"Scraping URL: {niche_or_url}")
                res = requests.get(niche_or_url, headers=headers, timeout=15)
                res.raise_for_status()
                soup = BeautifulSoup(res.content, 'html.parser')
                
                title = soup.find('h1').text.strip() if soup.find('h1') else "Scraped Product"
                # ניסיון חילוץ מחיר פרימיטיבי
                price_text = soup.select_one('[class*="price"], [id*="price"]')
                cost = float(''.join(filter(str.isdigit, price_text.text))) / 100 if price_text else random.uniform(20, 50)
            except Exception as e:
                logger.error(f"Scrape Failed: {e}")
                return None
        else:
            title = f"Premium {niche_or_url.title()} Asset"
            cost = random.uniform(10.0, 45.0)

        # חישובים פיננסיים
        demand_score = random.randint(60, 99)
        competition = random.choice(["Low", "Medium", "High"])
        trend = EmpireEngine.get_market_trends(niche_or_url if not niche_or_url.startswith('http') else title)
        
        suggested = (cost + SHIPPING_COST + ADS_COST_ESTIMATE) / (1 - TARGET_MARGIN)
        profit = suggested - cost - SHIPPING_COST - ADS_COST_ESTIMATE
        
        is_golden = 1 if profit >= GOLDEN_THRESHOLD_PROFIT and demand_score >= GOLDEN_THRESHOLD_DEMAND else 0
        budget = EmpireEngine.ads_manager_launch(title, profit, demand_score)
        ad_copy, ai_prompt = EmpireEngine.generate_ai_assets(title, round(profit, 2))

        return {
            "title": title, "niche": niche_or_url[:20], "cost": round(cost, 2), 
            "suggested_price": round(suggested, 2), "profit": round(profit, 2), 
            "demand": demand_score, "competition": competition, "budget": budget, 
            "url": niche_or_url, "is_golden": is_golden, "trend": trend,
            "ad_copy": ad_copy, "ai_prompt": ai_prompt
        }

# =================================================================
# 4. API CONTROLLERS
# =================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard_main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/inventory", response_class=HTMLResponse)
async def inventory_view(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.post("/run")
async def process_market_request(background_tasks: BackgroundTasks, niche: str = Query(...)):
    """ביצוע ניתוח שוק ושמירה לכספת"""
    logger.info(f"Analysis started for: {niche}")
    
    data = EmpireEngine.scrape_and_analyze(niche)
    if not data:
        raise HTTPException(status_code=400, detail="Failed to analyze niche/URL")

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO products 
                     (title, niche, cost, suggested_price, profit, demand_score, 
                      competition, ad_budget, url, ai_prompt, ad_copy_he, is_golden, trend_status) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (data['title'], data['niche'], data['cost'], data['suggested_price'], 
                   data['profit'], data['demand'], data['competition'], data['budget'], 
                   data['url'], data['ai_prompt'], data['ad_copy'], data['is_golden'], data['trend']))
        conn.commit()
        conn.close()
        
        return {"status": "Asset Secured", "data": data}
    except Exception as e:
        logger.error(f"DB Error: {e}")
        return JSONResponse(status_code=500, content={"status": "Database Error"})

@app.get("/api/inventory")
async def fetch_vault_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY is_golden DESC, id DESC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

@app.get("/api/stats")
async def get_empire_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(profit), AVG(demand_score) FROM products")
    count, total_profit, avg_demand = c.fetchone()
    c.execute("SELECT COUNT(*) FROM products WHERE is_golden = 1")
    gold_count = c.fetchone()[0]
    conn.close()
    return {
        "total_items": count or 0,
        "total_profit": round(total_profit or 0, 2),
        "avg_demand": round(avg_demand or 0, 1),
        "gold_count": gold_count
    }

@app.delete("/api/delete/{p_id}")
async def delete_asset(p_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM products WHERE id = ?", (p_id,))
    conn.commit()
    conn.close()
    return {"status": "Success", "message": f"Asset {p_id} removed."}

@app.get("/health")
async def health_check():
    return {"status": "Operational", "timestamp": datetime.now().isoformat()}

# =================================================================
# 5. EXECUTION
# =================================================================
if __name__ == "__main__":
    print("""
    ==================================================
    EMPIRE OS v8.0 - CENTRAL COMMAND INITIALIZED
    --------------------------------------------------
    [*] SERVER: http://localhost:8000
    [*] VAULT: http://localhost:8000/inventory
    [*] STATUS: MONITORING MARKET TRENDS
    ==================================================
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
