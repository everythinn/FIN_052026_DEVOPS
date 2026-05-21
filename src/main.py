from fastapi import FastAPI
from src.routers import groups, users, environments

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/version")
def version():
    return {"version": "1.0.0"}

app.include_router(users.router)
app.include_router(environments.router)
app.include_router(groups.router)
