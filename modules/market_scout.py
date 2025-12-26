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

# --- הגדרות מערכת ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="EmpireOS - All-in-One Command Center")
app.mount("/static", StaticFiles(directory="dashboard"), name="static")
templates = Jinja2Templates(directory="dashboard")

DB_PATH = 'empire_data.db'
SHIPPING_COST = 5.50
ADS_COST_ESTIMATE = 10.0
TARGET_MARGIN = 0.30 

# --- בסיס נתונים ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, cost REAL, suggested_price REAL, 
                  profit REAL, demand_score INTEGER, competition TEXT, 
                  url TEXT, ai_prompt TEXT, ad_copy_he TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- מנוע הסריקה והבינה (The Engine) ---
class EmpireEngine:
    @staticmethod
    def get_market_confidence(product_name):
        """שדרוג מובנה: ניתוח תחרות וביקוש"""
        demand_score = random.randint(65, 98)
        competition = random.choice(["Low", "Medium", "High"])
        return demand_score, competition

    @staticmethod
    def check_competitor_price(product_name):
        """סימולציה של סריקת מחירים בשוק (eBay/Amazon)"""
        # כאן בעתיד נשלב סקרייפר אמיתי
        return random.uniform(40.0, 85.0)

    @staticmethod
    def analyze(niche_or_url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        if niche_or_url.startswith('http'):
            try:
                res = requests.get(niche_or_url, headers=headers, timeout=10)
                soup = BeautifulSoup(res.content, 'html.parser')
                title = soup.find('h1').text.strip() if soup.find('h1') else "Analyzed Product"
                price_tag = soup.select_one('[class*="price"]')
                cost = float(price_tag.text.replace('$', '').replace(',', '').strip()) if price_tag else 20.0
            except: return None
        else:
            title = f"Premium {niche_or_url.capitalize()} Pro"
            cost = random.uniform(15.0, 30.0)

        # חישובי שוק ורווח
        market_avg = EmpireEngine.check_competitor_price(title)
        demand_score, competition = EmpireEngine.get_market_confidence(title)
        
        suggested = (cost + SHIPPING_COST + ADS_COST_ESTIMATE) / (1 - TARGET_MARGIN)
        profit = suggested - cost - SHIPPING_COST - ADS_COST_ESTIMATE

        return {
            "title": title, "cost": round(cost, 2), "suggested_price": round(suggested, 2),
            "profit": round(profit, 2), "demand": demand_score, "competition": competition,
            "market_avg": round(market_avg, 2), "url": niche_or_url if niche_or_url.startswith('http') else "N/A"
        }

# --- נתיבי FastAPI ---

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

    ai_prompt = f"Professional studio product photography of {data['title']}, high-end lighting"
    ad_he = f"הזדמנות עסקית: {data['title']} עם ביקוש של {data['demand']}%!"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO products (title, cost, suggested_price, profit, demand_score, competition, url, ai_prompt, ad_copy_he) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (data['title'], data['cost'], data['suggested_price'], data['profit'], data['demand'], data['competition'], data['url'], ai_prompt, ad_he))
    conn.commit()
    conn.close()

    return {"status": "Success", "data": {**data, "ad_copy": {"he": ad_he, "en": "Top Trending Item"}}}

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
