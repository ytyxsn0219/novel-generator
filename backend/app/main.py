from fastapi import FastAPI

app = FastAPI(title="Novel Generator")

@app.get("/health")
def health_check():
    return {"status": "ok"}
