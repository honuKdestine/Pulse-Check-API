from fastapi import APIRouter, HTTPException
from models import MonitorCreate
from storage import monitors

router = APIRouter()

@router.post("/monitors", status_code=201)
def register_monitor(monitor: MonitorCreate):
    if monitor.id in monitors:
        raise HTTPException(status_code=400, detail="Monitor already exists")

    monitors[monitor.id] = {
        "timeout": monitor.timeout,
        "status": "alive",
    }

    return {"message": f"Monitor {monitor.id} registered"}