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
