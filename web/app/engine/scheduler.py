import asyncio
import logging
import re
from typing import Optional, Dict, Any, Tuple
from app.config import config
from app.engine.observer_manager import ActiveObserverManager

logger = logging.getLogger("byzantine.scheduler")

class DocketScheduler:
    """
    Manages statutory docket progression, dynamic range expansion,
    and the 1-deep user petition queue.
    """
    def __init__(self, observer_manager: ActiveObserverManager):
        self.observer_mgr = observer_manager
        
        # Sequential progression & dynamic expansion
        self.range_start = config.initial_range_start
        self.range_end = config.initial_range_end
        self.expansion_step = config.range_expansion_step
        self.current_seq = self.range_start
        
        # 1-Deep Priority Queue
        self.queued_docket: Optional[Dict[str, Any]] = None
        self.lock = asyncio.Lock()

    def resume_from_calendar_seq(self, highest_completed_seq: int) -> None:
        """Resumes the sequential statutory calendar after the highest completed calendar payload."""
        if highest_completed_seq <= 0:
            return
        self.current_seq = highest_completed_seq + 1
        while self.range_end < self.current_seq:
            self.range_end += self.expansion_step
        logger.info(
            f"Resumed statutory calendar from database: next_seq={self.current_seq}, range={self.range_start}..{self.range_end}"
        )

    def get_status(self) -> Dict[str, Any]:
        return {
            "range_start": self.range_start,
            "range_end": self.range_end,
            "current_seq": self.current_seq,
            "min_allowed": config.min_allowed_docket,
            "max_allowed": config.max_allowed_docket,
            "queued_docket": self.queued_docket,
            "is_queue_full": self.queued_docket is not None,
        }

    def sanitize_input(self, raw_input: str) -> Tuple[bool, str, str]:
        """
        Dual-layer sanitization:
        Enforces strict numeric format and container min/max bounds.
        Returns (is_valid, sanitized_payload, error_message).
        """
        cleaned = raw_input.strip()
        if not cleaned:
            return False, "", "Payload cannot be empty."

        # Reject any non-digit character (no letters, signs, binary, hex, decimals, commas)
        if not re.fullmatch(r"^[0-9]+$", cleaned):
            return False, "", "Invalid input: strictly decimal digits [0-9] are permitted."

        if len(cleaned) > 100:
            return False, "", "Payload exceeds 100-digit statutory cap (DoS prevention)."

        # Normalize leading zeros while preserving "0"
        normalized = cleaned.lstrip("0") or "0"

        # Check container min/max parameter bounds
        try:
            val = int(normalized)
            if val < config.min_allowed_docket:
                return False, "", f"Payload must be at least {config.min_allowed_docket}."
            if val > config.max_allowed_docket:
                return False, "", f"Payload cannot exceed {config.max_allowed_docket}."
        except ValueError:
            return False, "", "Invalid integer value."

        return True, normalized, ""

    async def submit_to_queue(self, raw_input: str, client_ip: str = "Anonymous") -> Tuple[bool, str, Dict[str, Any]]:
        """
        Attempts to submit a number to the 1-deep priority queue.
        """
        async with self.lock:
            if self.queued_docket is not None:
                return False, "Queue is currently full. Exactly one docket may be queued at a time.", self.get_status()

            is_valid, sanitized, err = self.sanitize_input(raw_input)
            if not is_valid:
                return False, err, self.get_status()

            self.queued_docket = {
                "payload": sanitized,
                "submitter": client_ip,
                "submitted_at": asyncio.get_event_loop().time()
            }
            logger.info(f"Docket {sanitized} queued by {client_ip}.")

        await self.observer_mgr.broadcast({
            "event": "QUEUE_UPDATED",
            "queue_status": self.get_status()
        })
        return True, f"Payload '{sanitized}' successfully queued for the upcoming docket.", self.get_status()

    async def select_next_payload(self) -> Tuple[str, str]:
        """
        Selects the next payload to adjudicate.
        If a user queued a docket, it is chosen and the queue is cleared.
        Otherwise, selects from the statutory calendar and expands when completed.
        Returns (payload_string, source_description).
        """
        async with self.lock:
            if self.queued_docket is not None:
                payload = self.queued_docket["payload"]
                source = f"Public Petition ({self.queued_docket['submitter']})"
                self.queued_docket = None
                
                await self.observer_mgr.broadcast({
                    "event": "QUEUE_UPDATED",
                    "queue_status": self.get_status()
                })
                return payload, source

            # Sequential calendar selection
            payload = str(self.current_seq)
            source = f"Statutory Calendar (#{self.current_seq} of {self.range_end})"
            self.current_seq += 1

            # Check if current range is exhausted
            if self.current_seq > self.range_end:
                old_end = self.range_end
                self.range_end += self.expansion_step
                logger.info(f"Docket calendar exhausted ({old_end}). Expanded statutory range to {self.range_start}..{self.range_end}")
                await self.observer_mgr.broadcast({
                    "event": "RANGE_EXPANDED",
                    "old_end": old_end,
                    "new_end": self.range_end,
                    "expansion_step": self.expansion_step
                })

            return payload, source
