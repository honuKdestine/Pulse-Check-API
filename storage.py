from __future__ import annotations

import asyncio
from typing import Any

# In-memory storage for this coding challenge.
monitors: dict[str, dict[str, Any]] = {}
monitor_tasks: dict[str, asyncio.Task] = {}
store_lock = asyncio.Lock()
