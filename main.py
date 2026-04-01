from fastapi import FastAPI
from routes.monitors import router as monitor_router

# Main FastAPI app configuration shown in Swagger/OpenAPI docs.
app = FastAPI(
    title="Pulse Check API",
    description="Dead Man's Switch Monitoring Service",
    version="1.0.0",
)

# Register monitor-related endpoints.
app.include_router(monitor_router)


@app.get("/")
def root():
    # Simple health check endpoint for quick uptime verification.
    return {"message": "Pulse Check API is running"}
