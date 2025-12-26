import asyncio
from modules.market_scout import MarketScout
from modules.product_engine import ProductEngine
from modules.ads_manager import AdsManager
from ai.content_gen import AIContentGenerator

class EmpireController:
    def __init__(self):
        self.scout = MarketScout()
        self.engine = ProductEngine()
        self.ads = AdsManager()
        self.ai = AIContentGenerator()

    async def run_autonomous_cycle(self, niche):
        # 1. חיזוי טרנדים (שדרוג 1)
        trend = self.scout.find_hot_product(niche)
        
        # 2. סריקה וניתוח (הקוד המקורי שלך)
        data = self.engine.analyze_url(trend['url'])
        
        # 3. בדיקת רווחיות
        if data['profit'] < 15.0:
            return f"Skipped: {data['title']} (Profit: ${data['profit']})"

        # 4. יצירת תוכן AI
        ai_assets = self.ai.generate_assets(data)
        
        # 5. השקת מודעות (שדרוג 2)
        self.ads.launch_test(data)
        
        return f"Success: {data['title']} is Live!"
class EmpireController:
    # ... (בתוך ה-run_autonomous_cycle) ...
    
    async def check_and_notify(self, data):
        """שדרוג 3: התראה על הזדמנות זהב"""
        if data['profit'] > 25:
            msg = f"🌟 GOLDEN OPPORTUNITY: {data['title']} has ${data['profit']} profit!"
            print(f"TELEGRAM NOTIFICATION: {msg}") # כאן יבוא החיבור לבוט בהמשך
import sqlite3
import asyncio
# ... (שאר ה-imports שלך)

class EmpireController:
    def __init__(self):
        # ... (הגדרות קיימות)
        self.init_db()

    def init_db(self):
        """יוצר את בסיס הנתונים אם הוא לא קיים"""
        conn = sqlite3.connect('empire_data.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS products
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      title TEXT, cost REAL, suggested_price REAL, 
                      profit REAL, url TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def save_to_db(self, data):
        """שומר מוצר חדש בבסיס הנתונים"""
        conn = sqlite3.connect('empire_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO products (title, cost, suggested_price, profit, url) VALUES (?, ?, ?, ?, ?)",
                  (data['title'], data['cost'], data['suggested_price'], data['profit'], data['url']))
        conn.commit()
        conn.close()

    async def run_autonomous_cycle(self, niche):
        # ... (הלוגיקה הקיימת שלך)
        if data['profit'] >= 15:
            self.save_to_db(data) # שמירה אוטומטית של מוצר רווחי
            await self.check_and_notify(data)
            return f"Success: {data['title']} is Live!"
        return "Profit too low."
async def run_autonomous_cycle(self, niche):
    # כאן נכניס את הסריקה האמיתית (למשל דרך SerpApi או סקרייפר)
    # לצורך הדוגמה, נדמה חישוב ROI אמיתי
    cost = 15.0  # מחיר ספק ממוצע שמצאנו
    suggested_price = 39.9
    profit = suggested_price - cost
    
    data = {
        "title": f"Premium {niche} Gadget",
        "cost": cost,
        "suggested_price": suggested_price,
        "profit": profit,
        "url": "https://aliexpress.com/item/123",
        "demand": 87 if "tech" in niche.lower() else 65 # לוגיקה בסיסית
    }
    
    if profit > 20:
        self.save_to_db(data)
        return {"status": "Success", "data": data}
    return {"status": "Failed", "message": "Low profit margin"}
