import os
from pydantic import BaseModel

class AppConfig(BaseModel):
    # Ollama LLM Inference Configuration (Fully customizable)
    ollama_server: str = os.getenv("OLLAMA_SERVER", "http://192.168.1.101:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gemma4:e2b")
    ollama_timeout: float = float(os.getenv("OLLAMA_TIMEOUT", "45.0"))

    # Pacing and Readable Presentation Controls
    phase_delay_seconds: float = float(os.getenv("PHASE_DELAY_SECONDS", os.getenv("STAGE_DELAY_SECONDS", "5.0")))
    stage_delay_seconds: float = float(os.getenv("PHASE_DELAY_SECONDS", os.getenv("STAGE_DELAY_SECONDS", "5.0")))
    token_stream_delay: float = float(os.getenv("TOKEN_STREAM_DELAY", "0.01"))
    recess_seconds: int = int(os.getenv("RECESS_SECONDS", "30"))
    max_caucus_rounds: int = int(os.getenv("MAX_CAUCUS_ROUNDS", "10"))
    heartbeat_interval_seconds: float = float(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "5.0"))

    # Docket Range and Expansion Parameters
    initial_range_start: int = int(os.getenv("INITIAL_RANGE_START", "1"))
    initial_range_end: int = int(os.getenv("INITIAL_RANGE_END", "10"))
    range_expansion_step: int = int(os.getenv("RANGE_EXPANSION_STEP", "10"))
    
    # Sanitization bounds: min and max selectable via container parameters
    min_allowed_docket: int = int(os.getenv("MIN_ALLOWED_DOCKET", "1"))
    max_allowed_docket: int = int(os.getenv("MAX_ALLOWED_DOCKET", "10000"))

    # Storage and Networking
    database_path: str = os.getenv("DATABASE_PATH", "data/dockets.db")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Monetization (Amazon Associates)
    amazon_associate_tag: str = os.getenv("AMAZON_ASSOCIATE_TAG", "adamoutler-20")
    adsense_pub_id: str = os.getenv("ADSENSE_PUB_ID", "ca-pub-6398207513410830")

config = AppConfig()
