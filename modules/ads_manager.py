import os
import sqlite3
import random
import uvicorn
import openai
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pytrends.request import TrendReq
from dotenv import load_dotenv

# --- אתחול והגדרות ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="EmpireOS - Global Command Center")
app.mount("/static", StaticFiles(directory="dashboard"), name="static")
templates = Jinja2Templates(directory="dashboard")

DB_PATH = 'empire_data.db'
SHIPPING_COST = 5.50
ADS_COST_ESTIMATE = 10.0
TARGET_MARGIN = 0.30 

# --- יצירת בסיס הנתונים ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, cost REAL, suggested_price REAL, 
                  profit REAL, demand_score INTEGER, competition TEXT, 
                  ad_budget REAL, url TEXT, ai_prompt TEXT, ad_copy_he TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- מנוע ה-AI והמודעות (The Engine) ---
class EmpireEngine:
    @staticmethod
    def ads_manager_launch(title, profit):
        """שדרוג: חישוב תקציב מודעות אופטימלי לפי רווחיות"""
        # הקצאת תקציב טסט ראשוני: פי 3 מהרווח הצפוי ליחידה
        test_budget = round(profit * 3, 2)
        print(f"💰 Budget allocated for {title}: ${test_budget}")
        return test_budget

    @staticmethod
    def analyze(niche_or_url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        if niche_or_url.startswith('http'):
            try:
                res = requests.get(niche_or_url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.content, 'html.parser')
                title = soup.find('h1').text.strip() if soup.find('h1') else "Product Analysis"
                price_tag = soup.select_one('[class*="price"]')
                cost = float(price_tag.text.replace('$', '').replace(',', '').strip()) if price_tag else 25.0
            except: return None
        else:
            title = f"Elite {niche_or_url.capitalize()} Edition"
            cost = random.uniform(15.0, 40.0)

        # לוגיקת שוק
        demand_score = random.randint(70, 99)
        competition = random.choice(["Low", "Medium", "High"])
        
        suggested = (cost + SHIPPING_COST + ADS_COST_ESTIMATE) / (1 - TARGET_MARGIN)
        profit = suggested - cost - SHIPPING_COST - ADS_COST_ESTIMATE
        
        # הפעלת ה-Ads Manager
        budget = EmpireEngine.ads_manager_launch(title, profit)

        return {
            "title": title, "cost": round(cost, 2), "suggested_price": round(suggested, 2),
            "profit": round(profit, 2), "demand": demand_score, "competition": competition,
            "budget": budget, "url": niche_or_url if niche_or_url.startswith('http') else "N/A"
        }

# --- נתיבי API ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/inventory-page", response_class=HTMLResponse)
async def inventory_page(request: Request):
    return templates.TemplateResponse("inventory.html", {"request": request})

@app.post("/run")
async def run_analysis(niche: str = Query(...)):
    data = EmpireEngine.analyze(niche)
    if not data: return JSONResponse(status_code=400, content={"status": "Error"})

    ai_prompt = f"Hyper-realistic product shot of {data['title']}, white background, 8k"
    ad_he = f"🚀 מודעה מוכנה: {data['title']}! תקציב טסט: ${data['budget']}"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO products 
                 (title, cost, suggested_price, profit, demand_score, competition, ad_budget, url, ai_prompt, ad_copy_he) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (data['title'], data['cost'], data['suggested_price'], data['profit'], 
               data['demand'], data['competition'], data['budget'], data['url'], ai_prompt, ad_he))
    conn.commit()
    conn.close()

    return {"status": "Success", "data": {**data, "ad_copy": {"he": ad_he, "en": "Ready for Launch"}}}

@app.get("/api/inventory")
async def get_all():
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
