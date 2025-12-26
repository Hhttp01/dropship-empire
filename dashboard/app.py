import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from main_controller import EmpireController
import uvicorn

app = FastAPI()
controller = EmpireController()

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    base_path = os.path.dirname(__file__)
    with open(os.path.join(base_path, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/run")
async def run_logic(niche: str):
    result = await controller.run_autonomous_cycle(niche)
    return {"message": result}

if __name__ == "__main__":
    # Render מעביר לנו את הפורט במשתנה סביבה
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
# רשימה גלובלית זמנית לשמירת מוצרים (במקום בסיס נתונים כרגע)
products_db = []

@app.post("/run")
async def run_logic(niche: str):
    result_data = await controller.run_autonomous_cycle(niche)
    # שמירת המוצר ברשימה אם הוא רווחי
    if "Success" in result_data:
        products_db.append(result_data['product_info']) 
    return {"message": result_data}

@app.get("/inventory")
async def get_inventory():
    return products_db
@app.get("/inventory-page", response_class=HTMLResponse)
async def get_inventory_page():
    base_path = os.path.dirname(__file__)
    with open(os.path.join(base_path, "inventory.html"), "r", encoding="utf-8") as f:
        return f.read()
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from main_controller import EmpireController
import uvicorn

app = FastAPI()
controller = EmpireController()

# זיכרון זמני למוצרים (עד שנוסיף בסיס נתונים)
products_inventory = []

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    base_path = os.path.dirname(__file__)
    with open(os.path.join(base_path, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/inventory-page", response_class=HTMLResponse)
async def get_inventory_ui():
    base_path = os.path.dirname(__file__)
    with open(os.path.join(base_path, "inventory.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/run")
async def run_logic(niche: str):
    # הפעלת הסבב האוטונומי
    result = await controller.run_autonomous_cycle(niche)
    
    # אם הסבב הצליח, נוסיף את המוצר למלאי
    if "Success" in result:
        # כאן אנחנו שולפים את נתוני המוצר האחרון שסרקנו מה-engine
        product_info = controller.engine.last_scanned # נצטרך להוסיף את זה ב-engine
        products_inventory.append(product_info)
        
    return {"message": result}

@app.get("/api/inventory")
async def get_inventory_data():
    return products_inventory

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
import sqlite3
# ... (שאר הקוד הקיים)

@app.get("/api/inventory")
async def get_inventory_data():
    conn = sqlite3.connect('empire_data.db')
    conn.row_factory = sqlite3.Row # מאפשר לשלוף נתונים כמילון
    c = conn.cursor()
    c.execute("SELECT * FROM products ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    # המרה לפורמט JSON שהדפדפן מבין
    return [dict(row) for row in rows]
