from pydantic import BaseModel

class MonitorCreate(BaseModel):
    id: str
    timeout: int
    alert_email: str