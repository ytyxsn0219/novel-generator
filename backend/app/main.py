from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import novels, chapters, jobs, feedback, config

app = FastAPI(title="Novel Generator")

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(novels.router)
app.include_router(chapters.router)
app.include_router(jobs.router)
app.include_router(feedback.router)
app.include_router(config.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
