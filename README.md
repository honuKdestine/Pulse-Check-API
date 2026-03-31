# Pulse Check API

A Dead Man’s Switch backend service that monitors remote devices by tracking periodic heartbeat signals.  
If a device stops sending heartbeats within a configured timeout window, the system automatically triggers an alert, allowing operations teams to respond immediately to potential outages or failures.

---

## Architecture Overview

The system is designed as a **state-driven monitoring service** where each device monitor transitions between states based on heartbeat activity and timer expiration.

### Monitor State Flow

```mermaid
stateDiagram-v2
    [*] --> Registered

    Registered --> Alive : Monitor Created
    Alive --> Alive : Heartbeat Received\n(Timer Reset)

    Alive --> Down : Timeout Expired\n(No Heartbeat)
    Down --> [*] : Alert Fired

    Alive --> Paused : Pause Requested
    Paused --> Alive : Heartbeat Received\n(Resume Monitoring)


