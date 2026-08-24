import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from urllib.parse import urlparse
from curl_cffi import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stealth_engine")

app = FastAPI(
    title="Nexus Anti-Bot Stealth Engine",
    version="3.0.0",
    description="Ultra-grade anti-bot bypass scraping API"
)

API_KEY_CREDENTIAL = "sk_live_nexus_2026"

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

class ScrapePayload(BaseModel):
    url: HttpUrl
    impersonate: Optional[str] = "chrome124"
    timeout: Optional[int] = 30
    proxy: Optional[str] = None  # Format: http://user:pass@host:port

@app.post("/v1/scrape")
async def scrape_target(
    payload: ScrapePayload, 
    api_key: str = Depends(verify_api_key)
):
    target_url = str(payload.url)
    parsed_url = urlparse(target_url)
    domain = parsed_url.netloc

    # Dynamic target headers to match target domain authority
    stealth_headers = {
        "Host": domain,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

    proxies = {"http": payload.proxy, "https": payload.proxy} if payload.proxy else None

    logger.info(f"Stealth request initiated -> Target: {domain} | Impersonate: {payload.impersonate}")

    try:
        response = requests.get(
            target_url,
            impersonate=payload.impersonate,
            headers=stealth_headers,
            proxies=proxies,
            timeout=payload.timeout,
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
        logger.error(f"Engine failure: {str(err)}")
        raise HTTPException(status_code=500, detail=str(err))
        
