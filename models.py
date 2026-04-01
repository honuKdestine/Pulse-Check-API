from pydantic import BaseModel, ConfigDict, Field, field_validator


class MonitorCreate(BaseModel):
    # Payload used when a client registers a new monitor.
    id: str = Field(min_length=1, max_length=120)
    timeout: int = Field(gt=0, le=86_400)
    alert_email: str = Field(min_length=3, max_length=254)

    @field_validator("id")
    @classmethod
    def normalize_id(cls, value: str) -> str:
        # Trim spaces so IDs like " device-1 " are stored consistently.
        normalized = value.strip()
        if not normalized:
            raise ValueError("id cannot be empty")
        return normalized

    @field_validator("alert_email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        # Normalize email for stable comparisons and storage.
        normalized = value.strip().lower()
        if "@" not in normalized:
            raise ValueError("alert_email must contain '@'")
        return normalized


class MonitorView(BaseModel):
    # Response shape returned by monitor endpoints.
    model_config = ConfigDict(extra="forbid")

    id: str
    timeout: int
    alert_email: str
    status: str
    created_at: str
    updated_at: str
    last_heartbeat: str | None = None
    expires_at: str | None = None
    remaining_seconds: int | None = None
