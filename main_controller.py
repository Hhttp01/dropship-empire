import os
import sqlite3
import random
import asyncio
import logging
import json
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, validator
import uvicorn

# =================================================================
# 1. GLOBAL SYSTEM CONFIGURATION & DIRECTORIES
# =================================================================
class EmpireCore:
    VERSION = "7.0.0-SUPREME"
    DB_NAME = "empire_vault.db"
    DASHBOARD_DIR = "dashboard"
    LOGS_DIR = "logs"
    
    # Thresholds for Golden Opportunities
    GOLDEN_PROFIT_LIMIT = 25.0
    GOLDEN_DEMAND_LIMIT = 85
    
    # Simulation Constants
    ESTIMATED_CONVERSION_RATE = 0.03 # 3%
    AVERAGE_CPC = 0.65 # USD

# Ensure system environment is ready
for folder in [EmpireCore.DASHBOARD_DIR, EmpireCore.LOGS_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Advanced Logging System
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(EmpireCore.LOGS_DIR, "empire_master.log")),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("EmpireOS_Master")

app = FastAPI(
    title="EmpireOS Master Controller",
    version=EmpireCore.VERSION,
    description="Full-scale autonomous business management engine."
)

# Mounting the Dashboard
if os.path.exists(EmpireCore.DASHBOARD_DIR):
    app.mount("/dashboard", StaticFiles(directory=EmpireCore.DASHBOARD_DIR), name="dashboard")
else:
    logger.error(f"Critical: {EmpireCore.DASHBOARD_DIR} directory missing!")

# =================================================================
# 2. DATABASE INFRASTRUCTURE (SQLite Controller)
# =================================================================
class DatabaseController:
    """Manages all persistent data storage and retrieval."""
    
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(EmpireCore.DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    @classmethod
    def initialize_vault(cls):
        """Initializes all necessary tables for the Empire."""
        conn = cls.get_db_connection()
        db = conn.cursor()
        
        # Table 1: Inventory Assets
        db.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                niche TEXT DEFAULT 'General',
                cost REAL NOT NULL,
                suggested_price REAL NOT NULL,
                profit REAL NOT NULL,
                demand_score INTEGER NOT NULL,
                competition TEXT CHECK(competition IN ('Low', 'Medium', 'High')),
                ad_budget REAL DEFAULT 15.0,
                url TEXT,
                is_golden INTEGER DEFAULT 0,
                ai_ads_he TEXT,
                ai_ads_en TEXT,
                tags TEXT,
                status TEXT DEFAULT 'Scanned',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 2: System Activity Logs
        db.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                description TEXT,
                severity TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table 3: Simulations History
        db.execute('''
            CREATE TABLE IF NOT EXISTS sim_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                projected_roi REAL,
                projected_sales INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database infrastructure verified and tables deployed.")

# Run database setup
DatabaseController.initialize_vault()

# =================================================================
# 3. SCHEMAS & DATA VALIDATION (Pydantic Models)
# =================================================================
class AssetModel(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    niche: Optional[str] = "General"
    cost: float = Field(..., gt=0)
    suggested_price: float = Field(..., gt=0)
    demand_score: int = Field(..., ge=0, le=100)
    competition: str = "Medium"
    url: Optional[str] = "N/A"
    ad_budget: Optional[float] = 15.0

    @validator('suggested_price')
    def price_must_be_greater_than_cost(cls, v, values):
        if 'cost' in values and v <= values['cost']:
            raise ValueError('Suggested price must be higher than production cost')
        return v

class SimConfig(BaseModel):
    asset_id: int
    test_budget: float = Field(..., gt=0)

# =================================================================
# 4. BUSINESS INTELLIGENCE & AI (The Brain)
# =================================================================
class EmpireIntelligence:
    """Engine for analyzing market data and generating content."""
    
    @staticmethod
    def calculate_golden_ratio(profit: float, demand: int) -> int:
        """Determines if a product is a high-priority asset."""
        if profit >= EmpireCore.GOLDEN_PROFIT_LIMIT and demand >= EmpireCore.GOLDEN_DEMAND_LIMIT:
            return 1
        return 0

    @staticmethod
    def generate_ad_copy(title: str, niche: str, profit: float) -> Dict[str, str]:
        """Procedural generation of marketing assets."""
        he_templates = [
            f"להרוויח {profit}$ על כל מכירה! המוצר שמשנה את נישת ה-{niche}: {title}.",
            f"הטרנד החדש של 2025 כבר כאן. {title} - ביקוש שיא!",
            f"דירוג ביקוש {random.randint(85,99)}%: {title} עכשיו במלאי מוגבל."
        ]
        en_templates = [
            f"High Profit Alert: ${profit} net/unit. Meet the new {title}.",
            f"The {niche} breakthrough you've been waiting for: {title}.",
            f"Skyrocket your ROI with {title}. Limited supply available."
        ]
        return {
            "he": random.choice(he_templates),
            "en": random.choice(en_templates)
        }

# =================================================================
# 5. API ROUTES (The Master Controllers)
# =================================================================

@app.get("/api/inventory", tags=["Vault"])
async def get_all_assets():
    """Retrieves the complete inventory list with advanced sorting."""
    try:
        conn = DatabaseController.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory ORDER BY is_golden DESC, timestamp DESC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Failed to fetch inventory: {e}")
        return JSONResponse(status_code=500, content={"message": "Internal Database Error"})

@app.post("/api/assets/add", tags=["Vault"])
async def secure_new_asset(asset: AssetModel):
    """Processes and secures a new asset into the vault."""
    profit = round(asset.suggested_price - asset.cost, 2)
    is_gold = EmpireIntelligence.calculate_golden_ratio(profit, asset.demand_score)
    ads = EmpireIntelligence.generate_ad_copy(asset.title, asset.niche, profit)
    
    try:
        conn = DatabaseController.get_db_connection()
        db = conn.cursor()
        db.execute('''
            INSERT INTO inventory (
                title, niche, cost, suggested_price, profit, 
                demand_score, competition, ad_budget, url, is_golden, 
                ai_ads_he, ai_ads_en, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.title, asset.niche, asset.cost, asset.suggested_price, 
            profit, asset.demand_score, asset.competition, asset.ad_budget, 
            asset.url, is_gold, ads['he'], ads['en'], 'Verified'
        ))
        conn.commit()
        asset_id = db.lastrowid
        conn.close()
        
        logger.info(f"Asset #{asset_id} Secured. Golden Opportunity: {bool(is_gold)}")
        return {"status": "Asset Secured", "id": asset_id, "is_golden": bool(is_gold)}
    except Exception as e:
        logger.error(f"Security Breach - Asset addition failed: {e}")
        raise HTTPException(status_code=500, detail="Vault storage failure")

@app.post("/api/scan/autonomous", tags=["Automation"])
async def launch_autonomous_scout(background_tasks: BackgroundTasks, niche: str = "Electronics"):
    """Deploys a background worker to find new products autonomously."""
    
    async def scout_process(target: str):
        logger.info(f"Background Scout deployed to: {target}")
        await asyncio.sleep(4) # Simulating heavy AI processing
        
        # Synthetic discovery logic
        price = round(random.uniform(40, 200), 2)
        mock_asset = AssetModel(
            title=f"Smart {target} Pro v{random.randint(10,99)}",
            niche=target,
            cost=round(price * 0.35, 2),
            suggested_price=price,
            demand_score=random.randint(65, 98),
            competition=random.choice(["Low", "Medium"]),
            url="https://aliexpress.com/scout_discovery"
        )
        await secure_new_asset(mock_asset)
        logger.info("Background Scout successfully reported a new discovery.")

    background_tasks.add_task(scout_process, niche)
    return {"status": "Scout Process Initiated", "niche": niche}

@app.post("/api/simulate", tags=["Analytics"])
async def run_market_simulation(config: SimConfig):
    """Runs a probability-based sales simulation for a specific asset."""
    conn = DatabaseController.get_db_connection()
    asset = conn.execute("SELECT * FROM inventory WHERE id = ?", (config.asset_id,)).fetchone()
    conn.close()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found in vault")
    
    asset_dict = dict(asset)
    clicks = config.test_budget / EmpireCore.AVERAGE_CPC
    conversion = (asset_dict['demand_score'] / 100) * EmpireCore.ESTIMATED_CONVERSION_RATE
    projected_sales = round(clicks * conversion)
    net_profit = round((projected_sales * asset_dict['profit']) - config.test_budget, 2)
    
    # Log simulation to history
    conn = DatabaseController.get_db_connection()
    conn.execute("INSERT INTO sim_history (asset_id, projected_roi, projected_sales) VALUES (?, ?, ?)",
                 (config.asset_id, net_profit, projected_sales))
    conn.commit()
    conn.close()
    
    return {
        "asset": asset_dict['title'],
        "projected_sales": projected_sales,
        "net_profit_potential": net_profit,
        "roi_status": "HIGH" if net_profit > config.test_budget else "STABLE"
    }

@app.get("/api/stats/summary", tags=["Analytics"])
async def get_empire_summary():
    """Generates high-level financial and operational statistics."""
    conn = DatabaseController.get_db_connection()
    db = conn.cursor()
    
    stats = {}
    stats['total_assets'] = db.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    stats['golden_opportunities'] = db.execute("SELECT COUNT(*) FROM inventory WHERE is_golden = 1").fetchone()[0]
    stats['total_potential_profit'] = db.execute("SELECT SUM(profit) FROM inventory").fetchone()[0] or 0
    
    # Niche analysis
    db.execute("SELECT niche, COUNT(*) as count FROM inventory GROUP BY niche")
    stats['niche_breakdown'] = [dict(row) for row in db.fetchall()]
    
    conn.close()
    return stats

@app.delete("/api/assets/{asset_id}", tags=["Vault"])
async def purge_asset(asset_id: int):
    """Permanently removes an asset from the vault."""
    conn = DatabaseController.get_db_connection()
    conn.execute("DELETE FROM inventory WHERE id = ?", (asset_id,))
    conn.execute("DELETE FROM sim_history WHERE asset_id = ?", (asset_id,))
    conn.commit()
    conn.close()
    logger.warning(f"Purged Asset #{asset_id} and all related records.")
    return {"status": "Asset Eliminated"}

# =================================================================
# 6. FRONTEND SERVING (UI Routes)
# =================================================================

@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(os.path.join(EmpireCore.DASHBOARD_DIR, "index.html"))

@app.get("/inventory", include_in_schema=False)
async def serve_inventory():
    return FileResponse(os.path.join(EmpireCore.DASHBOARD_DIR, "inventory.html"))

@app.get("/health")
async def system_health():
    """Returns the operational status of the Empire engine."""
    return {
        "engine_version": EmpireCore.VERSION,
        "db_status": "ONLINE",
        "uptime_reference": datetime.now().isoformat(),
        "vault_size": os.path.getsize(EmpireCore.DB_NAME) if os.path.exists(EmpireCore.DB_NAME) else 0
    }

# =================================================================
# 7. ENGINE LAUNCHER
# =================================================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print(f"  EMPIRE MASTER CONTROLLER - v{EmpireCore.VERSION}")
    print("="*50)
    print(f"  [*] STORAGE: {EmpireCore.DB_NAME}")
    print(f"  [*] INTERFACE: http://localhost:8000")
    print(f"  [*] DOCUMENTATION: http://localhost:8000/docs")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
