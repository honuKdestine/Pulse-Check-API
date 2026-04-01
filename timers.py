from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone

from storage import monitor_tasks, monitors, store_lock


def utc_now() -> datetime:
    # Centralized UTC timestamp helper to keep time handling consistent.
    return datetime.now(timezone.utc)


def utc_iso(dt: datetime | None = None) -> str:
    # Return ISO-8601 string for API responses and internal state.
    return (dt or utc_now()).isoformat()


def expiry_iso(timeout_seconds: int, from_dt: datetime | None = None) -> str:
    # Compute when a monitor should expire if no heartbeat is received.
    base = from_dt or utc_now()
    return utc_iso(base + timedelta(seconds=timeout_seconds))


async def _monitor_countdown(monitor_id: str, timeout_seconds: int) -> None:
    alert_payload: dict[str, str] | None = None

    try:
        # Wait for the monitor timeout window.
        await asyncio.sleep(timeout_seconds)

        async with store_lock:
            monitor = monitors.get(monitor_id)
            if not monitor:
                return

            # Ignore stale tasks that were replaced by a newer timer.
            if monitor_tasks.get(monitor_id) is not asyncio.current_task():
                return

            if monitor["status"] != "alive":
                return

            # Mark monitor as down once timeout expires.
            now = utc_iso()
            monitor["status"] = "down"
            monitor["updated_at"] = now
            monitor["expires_at"] = None
            alert_payload = {
                "ALERT": f"Device {monitor_id} is down!",
                "time": now,
            }
    finally:
        async with store_lock:
            # Remove this task from the registry when it finishes.
            if monitor_tasks.get(monitor_id) is asyncio.current_task():
                monitor_tasks.pop(monitor_id, None)

    if alert_payload:
        # Stub alert output (replace with email/webhook integration later).
        print(json.dumps(alert_payload), flush=True)


def start_timer(monitor_id: str, timeout_seconds: int) -> None:
    # Always cancel the previous timer before starting a new one.
    existing_task = monitor_tasks.get(monitor_id)
    if existing_task and not existing_task.done():
        existing_task.cancel()

    monitor_tasks[monitor_id] = asyncio.create_task(
        _monitor_countdown(monitor_id, timeout_seconds)
    )


def stop_timer(monitor_id: str) -> None:
    # Stop and discard the active timer when monitor is paused/removed.
    existing_task = monitor_tasks.pop(monitor_id, None)
    if existing_task and not existing_task.done():
        existing_task.cancel()
