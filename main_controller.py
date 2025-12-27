import os
import sqlite3
import random
import asyncio
import logging
import json
import statistics
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# =================================================================
# 1. CORE SYSTEM CONFIGURATION (הגדרות מערכת)
# =================================================================
class EmpireSettings:
    VERSION = "6.0.0-PREMIUM"
    DB_PATH = "empire_vault.db"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DASHBOARD_PATH = os.path.join(BASE_DIR, "dashboard")
    LOGS_PATH = os.path.join(BASE_DIR, "logs")
    
    # Financial Thresholds
    MIN_GOLDEN_PROFIT = 25.0
    MIN_GOLDEN_DEMAND = 85
    AD_CONVERSION_ESTIMATE = 0.025  # 2.5% Conversion rate for simulations
    AVG_CPC = 0.75  # Average Cost Per Click in USD

# יצירת תשתיות תיקיות
for path in [EmpireSettings.DASHBOARD_PATH, EmpireSettings.LOGS_PATH]:
    if not os.path.exists(path):
        os.makedirs(path)

# הגדרת לוגים מתקדמת
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(EmpireSettings.LOGS_PATH, "system_core.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("EmpireOS_Core")

app = FastAPI(
    title="EmpireOS - Autonomous Business Controller",
    description="The central brain for market scouting and asset management.",
    version=EmpireSettings.VERSION
)

# Mounting static files for GUI
app.mount("/dashboard", StaticFiles(directory=EmpireSettings.DASHBOARD_PATH), name="dashboard")

# =================================================================
# 2. DATABASE ARCHITECTURE (ניהול מסד הנתונים)
# =================================================================
class DatabaseManager:
    """מחלקה לניהול ישיר של שאילתות ומבנה הנתונים"""
    
    @staticmethod
    def connect():
        conn = sqlite3.connect(EmpireSettings.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def setup_tables(cls):
        conn = cls.connect()
        db = conn.cursor()
        
        # טבלת נכסים (Inventory)
        db.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
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
                is_golden INTEGER,
                ai_copy_he TEXT,
                ai_copy_en TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת ביצועים (Performance Tracking)
        db.execute('''
            CREATE TABLE IF NOT EXISTS performance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                action_type TEXT,
                result_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(asset_id) REFERENCES inventory(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database Schema deployed successfully.")

# אתחול ה-DB בזמן העלייה
DatabaseManager.setup_tables()

# =================================================================
# 3. DATA MODELS (מודלים להעברת נתונים)
# =================================================================
class AssetCreate(BaseModel):
    title: str = Field(..., min_length=2)
    niche: str = "General"
    cost: float = Field(..., gt=0)
    suggested_price: float = Field(..., gt=0)
    demand_score: int = Field(..., ge=0, le=100)
    competition: str = "Medium"
    url: Optional[str] = "N/A"

class SimulationRequest(BaseModel):
    asset_id: int
    ad_spend: float

# =================================================================
# 4. INTELLIGENCE ENGINE (מנוע הבינה העסקית)
# =================================================================
class EmpireIntelligence:
    """המנוע שמנתח נתונים ומקבל החלטות"""
    
    @staticmethod
    def evaluate_asset(profit: float, demand: int) -> bool:
        return profit >= EmpireSettings.MIN_GOLDEN_PROFIT and demand >= EmpireSettings.MIN_GOLDEN_DEMAND

    @staticmethod
    def generate_marketing_content(title: str, niche: str) -> Dict[str, str]:
        """מחולל תוכן שיווקי בסיסי - ניתן להרחיב עם API של OpenAI"""
        return {
            "he": f"הכירו את הטרנד החדש בנישת ה-{niche}: {title}! פתרון מושלם לרווחיות גבוהה.",
            "en": f"Check out the new {niche} trend: {title}! High demand and great ROI potential."
        }

    @staticmethod
    def run_market_simulation(asset_data: Dict) -> Dict:
        """סימולציית מכירות מבוססת הסתברות"""
        clicks = 1000 # Default test batch
        conv_rate = (asset_data['demand_score'] / 100) * EmpireSettings.AD_CONVERSION_ESTIMATE
        sales = round(clicks * conv_rate)
        total_profit = round(sales * asset_data['profit'], 2)
        
        return {
            "projected_sales": sales,
            "projected_profit": total_profit,
            "roi_percentage": round((total_profit / (clicks * EmpireSettings.AVG_CPC)) * 100, 2)
        }

# =================================================================
# 5. API CONTROLLERS (נתיבי שליטה)
# =================================================================

@app.get("/api/inventory", tags=["Assets"])
async def get_inventory(niche: Optional[str] = None):
    """שליפת כל הנכסים מהכספת עם אפשרות לסינון"""
    conn = DatabaseManager.connect()
    cursor = conn.cursor()
    
    if niche:
        cursor.execute("SELECT * FROM inventory WHERE niche = ? ORDER BY created_at DESC", (niche,))
    else:
        cursor.execute("SELECT * FROM inventory ORDER BY created_at DESC")
    
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data

@app.post("/api/assets/add", tags=["Assets"])
async def add_asset(asset: AssetCreate):
    """הוספת נכס חדש וביצוע ניתוח ראשוני"""
    profit = round(asset.suggested_price - asset.cost, 2)
    is_gold = 1 if EmpireIntelligence.evaluate_asset(profit, asset.demand_score) else 0
    marketing = EmpireIntelligence.generate_marketing_content(asset.title, asset.niche)
    
    try:
        conn = DatabaseManager.connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (
                title, niche, cost, suggested_price, profit, 
                demand_score, competition, url, is_golden, 
                ai_copy_he, ai_copy_en
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.title, asset.niche, asset.cost, asset.suggested_price, 
            profit, asset.demand_score, asset.competition, asset.url, 
            is_gold, marketing['he'], marketing['en']
        ))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"Asset #{new_id} ({asset.title}) registered. Golden: {bool(is_gold)}")
        return {"status": "success", "asset_id": new_id, "is_golden": bool(is_gold)}
    except Exception as e:
        logger.error(f"Failed to add asset: {e}")
        raise HTTPException(status_code=500, detail="Database insertion failed")

@app.get("/api/stats/global", tags=["Analytics"])
async def get_global_stats():
    """חישוב נתונים אגרגטיביים לכל האימפריה"""
    conn = DatabaseManager.connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total, SUM(profit) as potential FROM inventory")
    base_stats = dict(cursor.fetchone())
    
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE is_golden = 1")
    base_stats['golden_count'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT niche, COUNT(*) as count FROM inventory GROUP BY niche")
    base_stats['niche_distribution'] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return base_stats

@app.post("/api/scan/autonomous", tags=["Automation"])
async def trigger_scout(background_tasks: BackgroundTasks, niche: str = "Trending"):
    """הפעלת סורק אוטונומי שפועל ברקע"""
    
    async def scout_worker(target_niche: str):
        logger.info(f"Scout Worker started for niche: {target_niche}")
        await asyncio.sleep(5) # Simulate web scraping & AI processing
        
        # Logic to "find" a high-potential item
        mock_price = random.uniform(30, 150)
        mock_cost = mock_price * 0.4
        
        auto_asset = AssetCreate(
            title=f"AI-Detected {target_niche} Product",
            niche=target_niche,
            cost=round(mock_cost, 2),
            suggested_price=round(mock_price, 2),
            demand_score=random.randint(75, 98),
            competition="Low",
            url="https://aliexpress.com/scout_found_this"
        )
        await add_asset(auto_asset)
        logger.info(f"Autonomous scout found and saved new {target_niche} asset.")

    background_tasks.add_task(scout_worker, niche)
    return {"status": "Scout Deployed", "target": niche}

@app.delete("/api/assets/{asset_id}", tags=["Assets"])
async def delete_asset(asset_id: int):
    """מחיקת נכס וכל הלוגים הקשורים אליו"""
    conn = DatabaseManager.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (asset_id,))
    cursor.execute("DELETE FROM performance_logs WHERE asset_id = ?", (asset_id,))
    conn.commit()
    conn.close()
    return {"status": "Asset Purged"}

# =================================================================
# 6. PAGE ROUTING (ניתוב דפי ממשק)
# =================================================================

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(os.path.join(EmpireSettings.DASHBOARD_PATH, "index.html"))

@app.get("/inventory", include_in_schema=False)
async def inventory_page():
    return FileResponse(os.path.join(EmpireSettings.DASHBOARD_PATH, "inventory.html"))

@app.get("/health")
async def health_check():
    """בדיקת תקינות המערכת"""
    return {
        "status": "online",
        "version": EmpireSettings.VERSION,
        "database": "connected" if os.path.exists(EmpireSettings.DB_PATH) else "error",
        "timestamp": datetime.now().isoformat()
    }

# =================================================================
# 7. EXECUTION (הפעלת השרת)
# =================================================================
if __name__ == "__main__":
    # Banner
    print("="*60)
    print(f"EMPIRE OS - {EmpireSettings.VERSION}")
    print(f"STARTING CENTRAL CONTROLLER...")
    print(f"DASHBOARD: http://localhost:8000")
    print(f"API DOCS: http://localhost:8000/docs")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# EOF - End of Main Controller v6.0
