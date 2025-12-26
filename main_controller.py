import os
import sqlite3
import random
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# --- הגדרות מערכת מתקדמות ---
class EmpireConfig:
    DB_NAME = "empire_vault.db"
    DASHBOARD_DIR = "dashboard"
    LOG_FILE = "empire_activity.log"
    # חוקי "זהב"
    GOLDEN_PROFIT_THRESHOLD = 25.0
    GOLDEN_DEMAND_THRESHOLD = 85
    # תקציבי מודעות ברירת מחדל
    DEFAULT_AD_BUDGET = 15.0

# הגדרת לוגים של המערכת
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(EmpireConfig.LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("EmpireOS")

app = FastAPI(title="EmpireOS - Ultimate Main Controller v5.0")

# וודא סביבת עבודה תקינה
for folder in [EmpireConfig.DASHBOARD_DIR, "logs"]:
    if not os.path.exists(folder): os.makedirs(folder)

app.mount("/dashboard", StaticFiles(directory=EmpireConfig.DASHBOARD_DIR), name="dashboard")

# --- מודלים מורחבים ---
class ProductSchema(BaseModel):
    title: str
    cost: float
    suggested_price: float
    profit: float
    demand_score: int
    competition: str
    ad_budget: Optional[float] = EmpireConfig.DEFAULT_AD_BUDGET
    url: Optional[str] = "N/A"
    niche: Optional[str] = "General"

class AdCampaign(BaseModel):
    product_id: int
    headline: str
    target_audience: str
    daily_budget: float

# --- בקר מסד הנתונים (Database Controller) ---
class DatabaseController:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(EmpireConfig.DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def initialize(cls):
        conn = cls.get_connection()
        cursor = conn.cursor()
        # טבלת מוצרים
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                cost REAL,
                suggested_price REAL,
                profit REAL,
                demand_score INTEGER,
                competition TEXT,
                ad_budget REAL,
                url TEXT,
                timestamp TEXT,
                is_golden INTEGER DEFAULT 0,
                niche TEXT
            )
        ''')
        # טבלת קמפיינים (שדרוג)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                headline TEXT,
                audience TEXT,
                budget REAL,
                status TEXT DEFAULT 'Pending'
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Database Engines Initialized.")

DatabaseController.initialize()

# --- בינה עסקית וסריקה (Market Scout Engine) ---
class MarketScout:
    @staticmethod
    async def simulate_ai_analysis(niche: str):
        """מדמה תהליך סריקה עמוק של AI בתוך ה-Backend"""
        await asyncio.sleep(2) # דימוי זמן עיבוד
        logger.info(f"AI Scout scanning niche: {niche}")
        
        # לוגיקה ליצירת נתונים
        cost = round(random.uniform(10, 60), 2)
        profit = round(random.uniform(15, 45), 2)
        demand = random.randint(50, 99)
        
        return {
            "title": f"The Ultimate {niche} Solution",
            "cost": cost,
            "suggested_price": cost + profit,
            "profit": profit,
            "demand_score": demand,
            "competition": random.choice(["Low", "Medium"]),
            "url": f"https://market.com/search?q={niche}",
            "niche": niche
        }

# --- נתיבי API (The Controllers) ---

@app.get("/api/inventory")
async def fetch_assets(min_profit: float = 0):
    """שליפת מוצרים עם פילטר רווח אופציונלי"""
    conn = DatabaseController.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory WHERE profit >= ? ORDER BY id DESC", (min_profit,))
    assets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return assets

@app.post("/api/scan/auto")
async def autonomous_scan(background_tasks: BackgroundTasks, niche: str = "Tech"):
    """הפעלת סורק אוטונומי ברקע"""
    async def run_process():
        data = await MarketScout.simulate_ai_analysis(niche)
        is_gold = 1 if data['profit'] > EmpireConfig.GOLDEN_PROFIT_THRESHOLD and data['demand_score'] > EmpireConfig.GOLDEN_DEMAND_THRESHOLD else 0
        
        conn = DatabaseController.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (title, cost, suggested_price, profit, demand_score, competition, ad_budget, url, timestamp, is_golden, niche)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['title'], data['cost'], data['suggested_price'], data['profit'], 
              data['demand_score'], data['competition'], 15.0, data['url'], 
              datetime.now().strftime("%Y-%m-%d %H:%M"), is_gold, data['niche']))
        conn.commit()
        conn.close()
        logger.info(f"New asset secured via Auto-Scout: {data['title']}")

    background_tasks.add_task(run_process)
    return {"status": "Processing", "message": f"Scout deployed to {niche} niche."}

@app.post("/api/ads/launch")
async def launch_campaign(campaign: AdCampaign):
    """בקר השקת קמפיינים"""
    conn = DatabaseController.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO campaigns (product_id, headline, audience, budget)
        VALUES (?, ?, ?, ?)
    ''', (campaign.product_id, campaign.headline, campaign.target_audience, campaign.daily_budget))
    conn.commit()
    conn.close()
    logger.info(f"Ad Campaign launched for product #{campaign.product_id}")
    return {"status": "Success", "ads_active": True}

@app.get("/api/stats/summary")
async def get_empire_stats():
    """בקר נתונים מסכם עבור ה-Dashboard"""
    conn = DatabaseController.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total, SUM(profit) as potential_profit FROM inventory")
    stats = dict(cursor.fetchone())
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE is_golden = 1")
    stats['golden_count'] = cursor.fetchone()[0]
    conn.close()
    return stats

@app.delete("/api/delete/{asset_id}")
async def delete_asset(asset_id: int):
    conn = DatabaseController.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()
    logger.warning(f"Asset #{asset_id} removed from vault.")
    return {"status": "Purged"}

# --- ניתוב דפים (UI Controllers) ---

@app.get("/")
async def index():
    return FileResponse(os.path.join(EmpireConfig.DASHBOARD_DIR, "index.html"))

@app.get("/inventory")
async def inventory_page():
    return FileResponse(os.path.join(EmpireConfig.DASHBOARD_DIR, "inventory.html"))

if __name__ == "__main__":
    logger.info("EmpireOS Main Controller v5.0 is igniting...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
