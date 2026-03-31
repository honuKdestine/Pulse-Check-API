from fastapi import FastAPI
from routes.monitors import router as monitor_router

app = FastAPI(
    title="Pulse Check API",
    description="Dead Man's Switch Monitoring Service",
    version="1.0.0",
)

app.include_router(monitor_router)


@app.get("/")
def root():
    return {"message": "Pulse Check API is running"}