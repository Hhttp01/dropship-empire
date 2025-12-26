def check_competitor_price(self, product_name):
    # סימולציה של סריקת eBay/Amazon
    # במציאות נשתמש ב-Requests כדי למשוך מחירים
    market_avg = 45.0
    return market_avgclass MarketScout:
    def find_hot_product(self, niche):
        # כאן תבוא לוגיקת Pytrends - כרגע מחזיר דאמי לניסיון
        return {"url": "https://example.com/item", "name": niche}
import random

class MarketScout:
    def find_hot_product(self, niche):
        # סימולציה של מציאת טרנד
        return {"url": "https://example.com/product", "name": niche}

    def get_market_confidence(self, product_name):
        """שדרוג 1: בדיקת רמת תחרות וביקוש"""
        demand_score = random.randint(60, 95) # ציון ביקוש
        competition_level = random.choice(["Low", "Medium", "High"])
        
        return {
            "score": demand_score,
            "competition": competition_level,
            "recommendation": "🚀 High Potential" if demand_score > 80 else "⚖️ Risky"
        }
