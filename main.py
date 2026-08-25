import logging
import random
from typing import Optional
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_godmode")

app = FastAPI(
    title="Nexus Anti-Bot Commercial Gateway",
    version="6.1.1",
    description="Enterprise Protocol-Accurate TLS/HTTP2 Scraping Engine with Resilient Proxy Fallback"
)

API_KEY_CREDENTIAL = "sk_live_nexus_2026"

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

async def fetch_free_proxy_pool(limit: int = 10) -> list[str]:
    """Fetches multiple candidate proxies from public lists."""
    cdn_url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json"
    candidates = []
    try:
        async with AsyncSession() as session:
            response = await session.get(cdn_url, timeout=5)
            if response.status_code == 200:
                proxies = response.json()
                if proxies and isinstance(proxies, list):
                    # Pick a sample of up to `limit` proxies to try
                    sampled = random.sample(proxies, min(len(proxies), limit))
                    for item in sampled:
                        candidates.append(f"http://{item['ip']}:{item['port']}")
    except Exception as err:
        logger.error(f"Free proxy list fetch error: {str(err)}")
    return candidates

class ScrapePayload(BaseModel):
    url: HttpUrl
    impersonate: Optional[str] = "chrome"
    auto_rotate_proxy: Optional[bool] = False
    custom_proxy: Optional[str] = None
    timeout: Optional[int] = 15

@app.get("/")
async def root():
    return {
        "status": "online",
        "engine": "Nexus God-Engine v6.1.1 Enterprise",
        "docs": "/docs"
    }

@app.post("/v1/scrape")
async def scrape_target(
    payload: ScrapePayload, 
    api_key: str = Depends(verify_api_key)
):
    target_url = str(payload.url)
    parsed_url = urlparse(target_url)
    domain = parsed_url.netloc

    stealth_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    # Determine Proxy Candidates
    proxy_candidates = []
    if payload.custom_proxy:
        proxy_candidates.append(payload.custom_proxy)
    elif payload.auto_rotate_proxy:
        proxy_candidates = await fetch_free_proxy_pool(limit=5)

    # Always add Direct Connection (None) as the final fallback to guarantee response success
    proxy_candidates.append(None)

    # Execution Loop with Failover Protection
    last_error = None
    for current_proxy in proxy_candidates:
        proxies = {"http": current_proxy, "https": current_proxy} if current_proxy else None
        
        try:
            logger.info(f"Attempting Scrape -> Target: {domain} | Proxy: {current_proxy if current_proxy else 'Direct'}")
            
            async with AsyncSession(
                impersonate=payload.impersonate,
                headers=stealth_headers,
                proxies=proxies,
                verify=True
            ) as session:
                response = await session.get(
                    target_url,
                    timeout=payload.timeout,
                    allow_redirects=True
                )

                # Successfully executed request
                return {
                    "status": "success",
                    "engine_mode": "godmode_async_tls",
                    "http_code": response.status_code,
                    "target_url": target_url,
                    "proxy_used": current_proxy if current_proxy else "direct_datacenter",
                    "cookies_captured": dict(response.cookies),
                    "content_length": len(response.text),
                    "data": response.text[:10000]
                }

        except Exception as err:
            logger.warning(f"Proxy attempt failed ({current_proxy}): {str(err)}. Retrying next...")
            last_error = err
            continue

    # If all attempts fail
    raise HTTPException(
        status_code=500, 
        detail=f"Scrape Execution Failed across all routes: {str(last_error)}"
    )
