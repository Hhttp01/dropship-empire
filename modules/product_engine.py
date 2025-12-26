import requests
from bs4 import BeautifulSoup
import config

class ProductEngine:
    def analyze_url(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            title = soup.find('h1').text.strip() if soup.find('h1') else "New Product"
            price_tag = soup.select_one('[class*="price"]')
            price = float(price_tag.text.replace('$', '').strip()) if price_tag else 10.0
            
            # חישוב ROI מקורי
            suggested = (price + config.SHIPPING_COST + config.ADS_COST_ESTIMATE) / (1 - config.TARGET_MARGIN)
            profit = suggested - price - config.SHIPPING_COST - config.ADS_COST_ESTIMATE
            
            return {"title": title, "cost": price, "suggested_price": round(suggested, 2), "profit": round(profit, 2), "url": url}
        except:
            return {"title": "Error", "profit": 0}
