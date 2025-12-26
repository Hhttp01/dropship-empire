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
