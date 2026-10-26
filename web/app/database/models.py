import aiosqlite
import json
import time
from typing import Dict, List, Optional, Any

CREATE_DOCKETS_TABLE = """
CREATE TABLE IF NOT EXISTS dockets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT UNIQUE NOT NULL,
    payload TEXT NOT NULL,
    digital_root TEXT NOT NULL,
    terminal_glyph TEXT NOT NULL,
    fizz_valid INTEGER NOT NULL,
    buzz_valid INTEGER NOT NULL,
    verdict TEXT NOT NULL,
    emitted_token TEXT NOT NULL,
    adjudicated_at REAL NOT NULL,
    transcript_json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dockets_payload ON dockets(payload);
CREATE INDEX IF NOT EXISTS idx_dockets_adjudicated ON dockets(adjudicated_at DESC);
"""

class DocketLedger:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(CREATE_DOCKETS_TABLE)
            await db.commit()

    async def record_docket(
        self,
        case_id: str,
        payload: str,
        digital_root: str,
        terminal_glyph: str,
        fizz_valid: bool,
        buzz_valid: bool,
        verdict: str,
        emitted_token: str,
        transcript: Dict[str, Any]
    ) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO dockets (
                    case_id, payload, digital_root, terminal_glyph,
                    fizz_valid, buzz_valid, verdict, emitted_token,
                    adjudicated_at, transcript_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    case_id,
                    payload,
                    digital_root,
                    terminal_glyph,
                    1 if fizz_valid else 0,
                    1 if buzz_valid else 0,
                    verdict,
                    emitted_token,
                    time.time(),
                    json.dumps(transcript)
                )
            )
            await db.commit()

    async def get_prior_rulings(self, payload: str) -> List[Dict[str, Any]]:
        """Retrieves past rulings on this specific payload for the Court Historian."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT case_id, payload, digital_root, terminal_glyph,
                       fizz_valid, buzz_valid, verdict, emitted_token,
                       adjudicated_at
                FROM dockets
                WHERE payload = ?
                ORDER BY adjudicated_at DESC
                """,
                (payload,)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_total_cases(self) -> int:
        """Returns the total number of adjudicated dockets in tribunal history."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM dockets")
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def get_highest_calendar_seq(self) -> int:
        """Returns the highest sequential integer adjudicated under the Statutory Calendar."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT payload, transcript_json FROM dockets"
            )
            rows = await cursor.fetchall()
            max_cal = 0
            for payload_str, t_json in rows:
                if t_json and "Statutory Calendar" in t_json:
                    try:
                        val = int(payload_str)
                        if val > max_cal:
                            max_cal = val
                    except ValueError:
                        pass
            return max_cal

    async def get_last_ruling(self) -> Optional[Dict[str, Any]]:
        """Returns the immediately preceding ruling of the court."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT case_id, payload, digital_root, terminal_glyph,
                       fizz_valid, buzz_valid, verdict, emitted_token,
                       adjudicated_at
                FROM dockets
                ORDER BY id DESC
                LIMIT 1
                """
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_recent_dockets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent dockets for the UI sidebar in order of inquisition."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, case_id, payload, digital_root, terminal_glyph,
                       fizz_valid, buzz_valid, verdict, emitted_token,
                       adjudicated_at
                FROM dockets
                ORDER BY id DESC, adjudicated_at DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_all_dockets(self, order: str = "desc") -> List[Dict[str, Any]]:
        """Retrieves all adjudicated dockets in order of inquisition for The Archives."""
        sort_clause = "id ASC, adjudicated_at ASC" if order.lower() == "asc" else "id DESC, adjudicated_at DESC"
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                f"""
                SELECT id, case_id, payload, digital_root, terminal_glyph,
                       fizz_valid, buzz_valid, verdict, emitted_token,
                       adjudicated_at
                FROM dockets
                ORDER BY {sort_clause}
                """
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_docket_details(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves full transcript and details for a specific historical case."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT case_id, payload, digital_root, terminal_glyph,
                       fizz_valid, buzz_valid, verdict, emitted_token,
                       adjudicated_at, transcript_json
                FROM dockets
                WHERE case_id = ?
                """,
                (case_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            res["transcript"] = json.loads(res["transcript_json"]) if res.get("transcript_json") else {}
            return res
