from fastapi import FastAPI

app = FastAPI(
    title="Pulse Check API",
    description="Dead Man's Switch Monitoring Service",
    version="1.0.0",
    
)


@app.get("/")
def root():
    return {"message": "Pulse Check API is running"}
