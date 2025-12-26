from fastapi import FastAPI
from main_controller import EmpireController
import uvicorn

app = FastAPI()
controller = EmpireController()

@app.post("/run")
async def start_process(niche: str):
    result = await controller.run_autonomous_cycle(niche)
    return {"message": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
