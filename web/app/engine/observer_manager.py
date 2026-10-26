import asyncio
import json
import logging
from typing import Dict, Any
from starlette.websockets import WebSocket, WebSocketState

logger = logging.getLogger("byzantine.observers")

class ActiveObserverManager:
    """
    Zero-Compute Standby & Active Observer Coordinator.
    Tracks active viewers via WebSocket connection and Page Visibility API.
    When active viewers reach 0, the adjudication loop halts until awakened.
    """
    def __init__(self):
        # Maps WebSocket connection to its tab visibility status (True if visible, False if hidden)
        self.observers: Dict[WebSocket, bool] = {}
        self.wake_event = asyncio.Event()

    def register(self, ws: WebSocket):
        self.observers[ws] = True
        logger.info(f"Observer connected. Total sockets: {len(self.observers)}, active: {self.active_count}")
        self.wake_event.set()

    def set_visibility(self, ws: WebSocket, is_visible: bool):
        if ws in self.observers:
            self.observers[ws] = is_visible
            logger.info(f"Observer visibility changed: visible={is_visible}. Active count: {self.active_count}")
            if self.active_count > 0:
                self.wake_event.set()

    def unregister(self, ws: WebSocket):
        self.observers.pop(ws, None)
        logger.info(f"Observer disconnected. Total sockets: {len(self.observers)}, active: {self.active_count}")

    @property
    def total_count(self) -> int:
        return len(self.observers)

    @property
    def active_count(self) -> int:
        return sum(1 for is_visible in self.observers.values() if is_visible)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a JSON event to all connected observer sockets."""
        if not self.observers:
            return

        payload = json.dumps(message)
        dead_sockets = []

        for ws in list(self.observers.keys()):
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_text(payload)
                else:
                    dead_sockets.append(ws)
            except Exception as e:
                logger.warning(f"Error sending to websocket: {e}")
                dead_sockets.append(ws)

        for dead in dead_sockets:
            self.unregister(dead)

    async def wait_for_active_observer(self) -> bool:
        """
        If active_count is 0, awaits wake_event indefinitely.
        Returns True once an active observer is confirmed.
        """
        if self.active_count > 0:
            return True

        logger.info("Entering zero-compute standby mode: 0 active observers.")
        await self.broadcast({
            "event": "STANDBY_CHANGE",
            "is_standby": True,
            "message": "Court adjourned into standby: 0 active observers. Sleeping to conserve compute."
        })

        self.wake_event.clear()
        while self.active_count == 0:
            await self.wake_event.wait()
            self.wake_event.clear()

        logger.info(f"Waking from standby: {self.active_count} active observer(s) detected.")
        await self.broadcast({
            "event": "STANDBY_CHANGE",
            "is_standby": False,
            "message": "Observer detected. Court reconvened."
        })
        return True
