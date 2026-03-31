import asyncio
from storage import monitors


async def monitor_countdown(monitor_id: str, timeout: int):
    await asyncio.sleep(timeout)

    monitor = monitors.get(monitor_id)
    if not monitor:
        return

    if monitor["status"] == "alive":
        monitor["status"] == "down"
        print({"ALERT": f"Device {monitor_id} is down!"})


def start_timer(monitor_id: str, timeout: int):
    asyncio.create_task(monitor_countdown(monitor_id, timeout))
