from fastapi import FastAPI
from app.api import novels

app = FastAPI(title="Novel Generator")
app.include_router(novels.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
