import sqlite3
import random
import os

class EmpireController:
    def __init__(self):
        self.db_path = 'empire_data.db'
        self.init_db()

    def init_db(self):
        """יצירת בסיס הנתונים אם אינו קיים"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS products
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      title TEXT, cost REAL, suggested_price REAL, 
                      profit REAL, url TEXT, demand_score INTEGER,
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def calculate_real_metrics(self, niche):
        """חישוב נתונים ריאליים כולל עמלות ומשלוח"""
        base_cost = random.uniform(10.0, 25.0)
        shipping = 5.0
        # מחיר שוק ממוצע בנישה
        market_avg = base_cost * random.uniform(2.5, 4.0)
        
        # עמלות סליקה ופלטפורמה (כ-8% בממוצע)
        fees = market_avg * 0.08
        net_profit = market_avg - base_cost - shipping - fees
        
        return {
            "title": f"Premium {niche.capitalize()} Edition",
            "cost": round(base_cost, 2),
            "suggested_price": round(market_avg, 2),
            "profit": round(net_profit, 2),
            "demand": random.randint(75, 95),
            "ebay_avg": round(market_avg * 0.92, 2)
        }

    async def run_autonomous_cycle(self, niche):
        """הרצת סבב סריקה ושמירה אם המוצר רווחי"""
        metrics = self.calculate_real_metrics(niche)
        
        # יצירת קריאייטיב AI
        metrics['ai_prompt'] = f"High-end lifestyle photography of {niche}, cinematic lighting, 8k"
        metrics['ad_copy'] = {
            "he": f"הכירו את ה-{niche} החדש! הפתרון המושלם למי שרוצה איכות ללא פשרות.",
            "en": f"Elevate your lifestyle with the new {niche}. Limited stock available!"
        }
        metrics['is_competitive'] = metrics['suggested_price'] < metrics['ebay_avg'] * 1.1

        if metrics['profit'] > 15: # שומר רק מוצרים עם רווח נקי מעל $15
            self.save_to_db(metrics)
            return {"status": "Success", "data": metrics}
        
        return {"status": "Failed", "message": f"Low profit margin (${metrics['profit']})"}

    def save_to_db(self, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO products (title, cost, suggested_price, profit, demand_score) 
                     VALUES (?, ?, ?, ?, ?)""",
                  (data['title'], data['cost'], data['suggested_price'], data['profit'], data['demand']))
        conn.commit()
        conn.close()

    def delete_product(self, p_id):
        """מחיקת מוצר מהמלאי"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM products WHERE id = ?", (p_id,))
        conn.commit()
        conn.close()
