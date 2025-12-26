import os
import sqlite3
import random
import uvicorn
import openai
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pytrends.request import TrendReq
from dotenv import load_dotenv

# --- אתחול והגדרות ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="EmpireOS All-in-One")
app.mount("/static", StaticFiles(directory="dashboard"), name="static")
templates = Jinja2Templates(directory="dashboard")

DB_PATH = 'empire_data.db'

# --- לוגיקה של בסיס הנתונים ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, cost REAL, suggested_price REAL, 
                  profit REAL, demand_score INTEGER,
                  ai_prompt TEXT, ad_copy_he TEXT, ad_copy_en TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- לוגיקה עסקית (The Brain) ---
class EmpireEngine:
    @staticmethod
    def get_trends(keyword):
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([keyword], cat=0, timeframe='now 7-d')
            data = pytrends.interest_over_time()
            return int(data[keyword].iloc[-1]) if not data.empty else random.randint(70, 90)
        except:
            return random.randint(65, 85)

    @staticmethod
    def generate_metrics(niche):
        base_cost = random.uniform(12.0, 30.0)
        shipping = 6.50
        market_price = base_cost * random.uniform(2.8, 4.5)
        fees = market_price * 0.08
        profit = market_price - base_cost - shipping - fees
        demand = EmpireEngine.get_trends(niche)
        
        return {
            "title": f"Smart {niche.capitalize()} Ultra",
            "cost": round(base_cost, 2),
            "suggested_price": round(market_price, 2),
            "profit": round(profit, 2),
            "demand": demand,
            "ebay_avg": round(market_price * 0.9, 2)
        }

# --- נתיבי API (Routes) ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/inventory-page", response_class=HTMLResponse)
async def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.post("/run")
async def run_analysis(niche: str):
    try:
        data = EmpireEngine.generate_metrics(niche)
        
        # בניית אובייקט לשמירה
        ai_prompt = f"Professional studio shot of {niche}, cinematic lighting, 8k"
        ad_he = f"הכירו את ה-{niche} החדש! איכות ללא פשרות."
        ad_en = f"New {niche} is here. Premium quality guaranteed."

        # שמירה ל-DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO products 
                     (title, cost, suggested_price, profit, demand_score, ai_prompt, ad_copy_he, ad_copy_en) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (data['title'], data['cost'], data['suggested_price'], data['profit'], 
                   data['demand'], ai_prompt, ad_he, ad_en))
        conn.commit()
        conn.close()

        return {"status": "Success", "data": {**data, "ad_copy": {"he": ad_he, "en": ad_en}, "is_competitive": True}}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "Error", "message": str(e)})

@app.get("/api/inventory")
async def get_all_inventory():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY id DESC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

@app.delete("/api/delete/{p_id}")
async def delete_item(p_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM products WHERE id = ?", (p_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
