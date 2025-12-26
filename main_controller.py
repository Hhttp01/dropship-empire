import os
import sqlite3
import random
import asyncio
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# --- קונפיגורציה ומבנה נתונים ---
class EmpireConfig:
    DB_NAME = "empire_vault.db"
    DASHBOARD_DIR = "dashboard"
    GOLDEN_PROFIT_THRESHOLD = 25.0
    GOLDEN_DEMAND_THRESHOLD = 85

app = FastAPI(title="EmpireOS - Main Controller v4.0")

# וודא שתיקיית הממשק קיימת
if not os.path.exists(EmpireConfig.DASHBOARD_DIR):
    os.makedirs(EmpireConfig.DASHBOARD_DIR)

app.mount("/dashboard", StaticFiles(directory=EmpireConfig.DASHBOARD_DIR), name="dashboard")

# --- מודלים של Pydantic ל-API ---
class ProductSchema(BaseModel):
    title: str
    cost: float
    suggested_price: float
    profit: float
    demand_score: int
    competition: str
    ad_budget: Optional[float] = 10.0
    url: Optional[str] = "N/A"

# --- מנוע מסד הנתונים (Database Controller) ---
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
                is_golden INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

DatabaseController.initialize()

# --- לוגיקה עסקית (Business Logic Controller) ---
class MarketIntelligence:
    @staticmethod
    def analyze_golden_opportunity(profit: float, demand: int) -> int:
        if profit >= EmpireConfig.GOLDEN_PROFIT_THRESHOLD and demand >= EmpireConfig.GOLDEN_DEMAND_THRESHOLD:
            return 1
        return 0

    @staticmethod
    def generate_mock_scan(niche: str):
        """סימולטור סריקה ליצירת נתונים ראשוניים"""
        titles = [f"Premium {niche} Kit", f"Autonomous {niche} Tool", f"Digital {niche} Asset"]
        title = random.choice(titles)
        cost = round(random.uniform(5.0, 50.0), 2)
        price = round(cost + random.uniform(20.0, 100.0), 2)
        profit = round(price - cost, 2)
        demand = random.randint(60, 98)
        comp = random.choice(["Low", "Medium", "High"])
        return {
            "title": title, "cost": cost, "suggested_price": price,
            "profit": profit, "demand_score": demand, "competition": comp,
            "ad_budget": 15.0, "url": "https://example.com/source"
        }

# --- נתיבי API (The Main Controllers) ---

@app.get("/api/inventory", response_class=JSONResponse)
async def fetch_all_assets():
    """שליפת כל הנכסים מהכספת"""
    try:
        conn = DatabaseController.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY id DESC")
        assets = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan")
async def register_new_asset(product: ProductSchema):
    """רישום נכס חדש שנמצא בסריקה"""
    is_gold = MarketIntelligence.analyze_golden_opportunity(product.profit, product.demand_score)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = DatabaseController.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inventory (title, cost, suggested_price, profit, demand_score, competition, ad_budget, url, timestamp, is_golden)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (product.title, product.cost, product.suggested_price, product.profit, 
          product.demand_score, product.competition, product.ad_budget, product.url, timestamp, is_gold))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"status": "Asset Secured", "id": new_id, "golden": bool(is_gold)}

@app.get("/api/seed")
async def seed_data():
    """פקודה להזרקת נתוני ניסוי למערכת"""
    mock_data = MarketIntelligence.generate_mock_scan("AI Tech")
    p = ProductSchema(**mock_data)
    await register_new_asset(p)
    return {"message": "Mock data injected successfully"}

@app.delete("/api/delete/{asset_id}")
async def remove_asset(asset_id: int):
    """מחיקת נכס מהמערכת"""
    conn = DatabaseController.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()
    return {"status": "Asset Purged"}

# --- נתיבי הגשת הממשק (View Controllers) ---

@app.get("/")
async def serve_dashboard():
    return FileResponse(os.path.join(EmpireConfig.DASHBOARD_DIR, "index.html"))

@app.get("/inventory")
async def serve_inventory():
    return FileResponse(os.path.join(EmpireConfig.DASHBOARD_DIR, "inventory.html"))

# --- הפעלה ---
if __name__ == "__main__":
    print("""
    #################################################
    #             EMPIRE OS v4.0 RUNNING            #
    #        ----------------------------------     #
    #        GUI: http://localhost:8000             #
    #        VAULT: http://localhost:8000/inventory #
    #################################################
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
