import os
from dotenv import load_dotenv

# טעינה מהקובץ המותאם לטלפון
load_dotenv("env.txt")

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SHOPIFY_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_URL = os.getenv("SHOPIFY_STORE_URL")

# חוקי המערכת (הלוגיקה המקורית שלך + שדרוגים)
TARGET_MARGIN = 0.3
SHIPPING_COST = 5.0
ADS_COST_ESTIMATE = 10.0
MIN_PROFIT_THRESHOLD = 15.0
PRICE_ALERT_THRESHOLD = 3.0
