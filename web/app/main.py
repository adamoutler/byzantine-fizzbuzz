import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import config
from app.database.models import DocketLedger
from app.engine.observer_manager import ActiveObserverManager
from app.engine.scheduler import DocketScheduler
from app.engine.async_engine import AsyncByzantineConsensusEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("byzantine.main")

# State instances
ledger = DocketLedger(config.database_path)
observer_mgr = ActiveObserverManager()
scheduler = DocketScheduler(observer_mgr)
engine = AsyncByzantineConsensusEngine(ledger, observer_mgr)

class DocketSubmission(BaseModel):
    payload: str = Field(..., min_length=1, max_length=100)

async def background_adjudication_loop():
    """
    Main continuous loop for the Byzantine Courtroom.
    Conserves compute when 0 active observers are present.
    """
    logger.info("Starting Byzantine Courtroom background adjudication loop.")

    while True:
        try:
            # 1. Zero-Compute Standby Gate: Halt if no human is actively watching
            await observer_mgr.wait_for_active_observer()

            # 2. Parliamentary Recess & 1-Deep Queue Window
            logger.info(f"Court in recess for {config.recess_seconds} seconds.")
            for remaining in range(config.recess_seconds, 0, -1):
                # If all observers disconnect mid-recess, wait_for_active_observer will pause next round
                await observer_mgr.broadcast({
                    "event": "RECESS_TICK",
                    "seconds_remaining": remaining,
                    "queue_status": scheduler.get_status()
                })
                await asyncio.sleep(1.0)

            # Re-check active observer gate before launching full LLM deliberation
            await observer_mgr.wait_for_active_observer()

            # 3. Select next docket payload (Priority queue takes precedence over calendar)
            payload, source = await scheduler.select_next_payload()
            logger.info(f"Commencing adjudication for payload '{payload}' (Source: {source})")

            # 4. Execute 9-Phase Tribunal Deliberation (or Official Mistrial if inference quorum fails)
            transcript = await engine.adjudicate(payload, source, range_end=scheduler.range_end)
            if transcript.get("final_token") == "Mistrial":
                await scheduler.register_mistrial(payload, source)

        except asyncio.CancelledError:
            logger.info("Adjudication loop cancelled.")
            break
        except Exception as e:
            logger.exception(f"Unexpected error in adjudication loop: {e}")
            await asyncio.sleep(5.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist, purge legacy corrupted rows, and resume statutory calendar
    await ledger.initialize()
    deleted_legacy = await ledger.delete_mistrial_dockets()
    if deleted_legacy:
        logger.info(f"Purged {deleted_legacy} legacy corrupted docket rows on startup.")
    highest_cal, missing_seqs = await ledger.get_calendar_state(config.initial_range_start)
    scheduler.resume_from_calendar_seq(highest_cal, missing_seqs)
    adjudication_task = asyncio.create_task(background_adjudication_loop())
    yield
    # Shutdown
    adjudication_task.cancel()
    await engine.close()

app = FastAPI(title="Zero-Trust Byzantine FizzBuzz Live Courtroom", lifespan=lifespan)

# REST Endpoints
@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health():
    return {
        "status": "healthy",
        "active_observers": observer_mgr.active_count,
        "total_connections": observer_mgr.total_count,
        "range_start": scheduler.range_start,
        "range_end": scheduler.range_end,
        "min_allowed": config.min_allowed_docket,
        "max_allowed": config.max_allowed_docket,
    }

@app.get("/api/status")
async def get_status():
    return {
        "active_observers": observer_mgr.active_count,
        "total_connections": observer_mgr.total_count,
        "scheduler": scheduler.get_status()
    }

@app.get("/api/history")
async def get_history(limit: int = 50):
    return await ledger.get_recent_dockets(limit=limit)

@app.get("/api/archives")
async def get_archives(order: str = "desc"):
    dockets = await ledger.get_all_dockets(order=order)
    return {
        "total": len(dockets),
        "order": "asc" if order.lower() == "asc" else "desc",
        "dockets": dockets
    }

@app.get("/api/docket/{case_id}")
async def get_docket(case_id: str):
    docket = await ledger.get_docket_details(case_id)
    if not docket:
        raise HTTPException(status_code=404, detail="Docket not found")
    return docket

@app.post("/api/queue")
async def queue_docket(submission: DocketSubmission, request: Request):
    client_ip = request.client.host if request.client else "Remote"
    success, message, current_status = await scheduler.submit_to_queue(submission.payload, client_ip)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message, "status": current_status}

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    observer_mgr.register(ws)
    
    # Send initial state snapshot upon connecting
    history = await ledger.get_recent_dockets(limit=25)
    await ws.send_json({
        "event": "INITIAL_STATE",
        "active_observers": observer_mgr.active_count,
        "scheduler": scheduler.get_status(),
        "history": history
    })

    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")
            if msg_type == "VISIBILITY_HEARTBEAT":
                is_active = bool(data.get("active", True))
                observer_mgr.set_visibility(ws, is_active)
            elif msg_type == "HEARTBEAT":
                await ws.send_json({"event": "HEARTBEAT_ACK"})
    except WebSocketDisconnect:
        observer_mgr.unregister(ws)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        observer_mgr.unregister(ws)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return FileResponse("app/static/index.html", headers={"Cache-Control": "no-cache"})

@app.api_route("/manifest.json", methods=["GET", "HEAD"])
@app.api_route("/manifest.webmanifest", methods=["GET", "HEAD"])
async def pwa_manifest():
    return FileResponse("app/static/manifest.json", media_type="application/manifest+json")

@app.api_route("/sw.js", methods=["GET", "HEAD"])
async def service_worker():
    return FileResponse(
        "app/static/sw.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"}
    )

@app.api_route("/favicon.ico", methods=["GET", "HEAD"])
async def favicon_ico():
    return FileResponse("app/static/icons/favicon.ico", media_type="image/x-icon")

@app.api_route("/ads.txt", methods=["GET", "HEAD"])
async def ads_txt():
    # Google AdSense authorized sellers verification
    return JSONResponse(
        content=f"google.com, {config.adsense_pub_id}, DIRECT, f08c47fec0942fa0\n",
        media_type="text/plain"
    )
