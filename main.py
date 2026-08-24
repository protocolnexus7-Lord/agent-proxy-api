from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from curl_cffi import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus-engine")

app = FastAPI(title="Nexus Anti-Bot Scraper API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_API_KEYS = {
    "sk_live_nexus_2026": {"tier": "Pro", "status": "active"},
    "sk_test_demo_key": {"tier": "Free", "status": "active"}
}

class ScrapeRequest(BaseModel):
    url: str
    impersonate: str = "chrome124"
    timeout: int = 15

# Real Chrome Browser Headers to trick Cloudflare WAF
ADVANCED_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

@app.get("/")
def health_check():
    return {"status": "online", "engine": "Nexus Stealth Proxy Core v2.0"}

@app.post("/v1/scrape")
async def execute_bypass(
    payload: ScrapeRequest,
    x_api_key: str = Header(None, alias="x-api-key")
):
    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    target_url = payload.url.strip()
    if not target_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    logger.info(f"Stealth request to: {target_url}")

    try:
        response = requests.get(
            target_url,
            impersonate=payload.impersonate,
            timeout=payload.timeout,
            headers=ADVANCED_HEADERS,
            allow_redirects=True
        )

        return {
            "status": "success",
            "http_code": response.status_code,
            "target_url": target_url,
            "content_length": len(response.text),
            "data": response.text[:10000]
        }

    except Exception as err:
        logger.error(f"Bypass error: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))
