from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from models import MonitorCreate, MonitorView
from storage import monitors, store_lock
from timers import expiry_iso, start_timer, stop_timer, utc_iso

router = APIRouter(prefix="", tags=["monitors"])


def _remaining_seconds(expires_at: str | None) -> int | None:
    # Convert expiry timestamp into a live countdown value for responses.
    if not expires_at:
        return None

    expires_dt = datetime.fromisoformat(expires_at)
    delta = expires_dt - datetime.now(timezone.utc)
    return max(0, int(delta.total_seconds()))


def _monitor_view(monitor_data: dict) -> MonitorView:
    # Build the API response model from internal monitor state.
    return MonitorView(
        id=monitor_data["id"],
        timeout=monitor_data["timeout"],
        alert_email=monitor_data["alert_email"],
        status=monitor_data["status"],
        created_at=monitor_data["created_at"],
        updated_at=monitor_data["updated_at"],
        last_heartbeat=monitor_data["last_heartbeat"],
        expires_at=monitor_data["expires_at"],
        remaining_seconds=_remaining_seconds(monitor_data["expires_at"]),
    )


@router.post("/monitors", status_code=201)
async def register_monitor(monitor: MonitorCreate):
    async with store_lock:
        # Prevent duplicate monitor IDs.
        if monitor.id in monitors:
            raise HTTPException(status_code=400, detail="Monitor already exists")

        now = utc_iso()
        monitor_state = {
            "id": monitor.id,
            "timeout": monitor.timeout,
            "alert_email": monitor.alert_email,
            "status": "alive",
            "created_at": now,
            "updated_at": now,
            "last_heartbeat": now,
            "expires_at": expiry_iso(monitor.timeout),
        }

        monitors[monitor.id] = monitor_state
        # Start countdown immediately after registration.
        start_timer(monitor.id, monitor.timeout)

        return {
            "message": f"Monitor {monitor.id} registered",
            "monitor": _monitor_view(monitor_state),
        }


@router.post("/monitors/{monitor_id}/heartbeat")
async def heartbeat(monitor_id: str):
    async with store_lock:
        # Heartbeat extends monitor lifetime and keeps it alive.
        monitor = monitors.get(monitor_id)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        if monitor["status"] == "down":
            raise HTTPException(
                status_code=409,
                detail="Monitor is down and cannot accept heartbeats",
            )

        was_paused = monitor["status"] == "paused"
        now = utc_iso()
        monitor["status"] = "alive"
        monitor["updated_at"] = now
        monitor["last_heartbeat"] = now
        monitor["expires_at"] = expiry_iso(monitor["timeout"])
        # Reset timer so timeout counts from this heartbeat.
        start_timer(monitor_id, monitor["timeout"])

        return {
            "message": (
                f"Monitor {monitor_id} resumed and heartbeat received"
                if was_paused
                else f"Heartbeat received for {monitor_id}"
            ),
            "monitor": _monitor_view(monitor),
        }


@router.post("/monitors/{monitor_id}/pause")
async def pause_monitor(monitor_id: str):
    async with store_lock:
        # Pausing suspends timeout tracking without deleting monitor data.
        monitor = monitors.get(monitor_id)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        if monitor["status"] == "down":
            raise HTTPException(status_code=409, detail="Down monitors cannot be paused")

        monitor["status"] = "paused"
        monitor["updated_at"] = utc_iso()
        monitor["expires_at"] = None
        # Pause means no active countdown task.
        stop_timer(monitor_id)

        return {
            "message": f"Monitor {monitor_id} paused",
            "monitor": _monitor_view(monitor),
        }


@router.get("/monitors/{monitor_id}", response_model=MonitorView)
async def get_monitor(monitor_id: str):
    async with store_lock:
        # Read-only endpoint to inspect current monitor status.
        monitor = monitors.get(monitor_id)
        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        return _monitor_view(monitor)
