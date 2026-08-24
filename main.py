from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from curl_cffi import requests
import logging

# Configure production logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus-engine")

app = FastAPI(
    title="Nexus Anti-Bot Scraper API",
    description="High-IQ Agentic Bypass Engine Powered by Stealth TLS Impersonation",
    version="1.0.0"
)

# Enable CORS so developers can call your API directly from frontends or AI frameworks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active API Key Database (Add customer keys here or connect to a database later)
VALID_API_KEYS = {
    "sk_live_nexus_2026": {"tier": "Pro", "status": "active"},
    "sk_test_demo_key": {"tier": "Free", "status": "active"}
}

# Request Body Schema
class ScrapeRequest(BaseModel):
    url: str
    impersonate: str = "chrome124"  # Default browser signature
    timeout: int = 15

@app.get("/")
def health_check():
    """Root endpoint for Render health checks and uptime monitoring."""
    return {
        "status": "online",
        "engine": "Nexus Stealth Proxy Core",
        "version": "1.0.0",
        "authorization": "Active"
    }

@app.post("/v1/scrape")
async def execute_bypass(
    payload: ScrapeRequest,
    x_api_key: str = Header(None, alias="x-api-key")
):
    """
    Main anti-bot extraction endpoint.
    Bypasses Cloudflare, DataDome, and TLS/JA3 fingerprint checks.
    """
    # 1. Authentication Layer
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or missing 'x-api-key' header."
        )

    key_info = VALID_API_KEYS[x_api_key]
    if key_info["status"] != "active":
        raise HTTPException(status_code=403, detail="API Key is suspended or inactive.")

    target_url = payload.url.strip()
    if not target_url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400, 
            detail="Invalid URL format. Must start with http:// or https://"
        )

    logger.info(f"Executing stealth request to target: {target_url}")

    # 2. Execution Layer (C-Level TLS Impersonation)
    try:
        response = requests.get(
            target_url,
            impersonate=payload.impersonate,
            timeout=payload.timeout,
            headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Upgrade-Insecure-Requests": "1"
            }
        )

        return {
            "status": "success",
            "http_code": response.status_code,
            "target_url": target_url,
            "content_length": len(response.text),
            "data": response.text
        }

    except requests.errors.RequestsError as req_err:
        logger.error(f"Target connection failed: {str(req_err)}")
        raise HTTPException(
            status_code=502, 
            detail=f"Target server connection error: {str(req_err)}"
        )
    except Exception as err:
        logger.error(f"Unexpected bypass failure: {str(err)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Engine Error: {str(err)}"
        )
