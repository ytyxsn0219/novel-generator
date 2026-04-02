from fastapi import FastAPI
from app.api import novels, chapters, jobs, feedback

app = FastAPI(title="Novel Generator")
app.include_router(novels.router)
app.include_router(chapters.router)
app.include_router(jobs.router)
app.include_router(feedback.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
