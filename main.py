import logging
import random
from typing import Optional
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_godmode")

app = FastAPI(
    title="Nexus Anti-Bot Commercial Gateway",
    version="6.1.0",
    description="Enterprise Protocol-Accurate TLS/HTTP2 Scraping Engine with Free Dynamic Proxy Support"
)

# API Security Key
API_KEY_CREDENTIAL = "sk_live_nexus_2026"

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

async def fetch_free_proxifly_proxy() -> str | None:
    """Fetches a dynamic live proxy from Proxifly's public feed (Zero API Key required)."""
    cdn_url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json"
    try:
        async with AsyncSession() as session:
            response = await session.get(cdn_url, timeout=5)
            if response.status_code == 200:
                proxies = response.json()
                if proxies and isinstance(proxies, list):
                    chosen = random.choice(proxies)
                    return f"http://{chosen['ip']}:{chosen['port']}"
    except Exception as err:
        logger.error(f"Free proxy fetch error: {str(err)}")
    return None

class ScrapePayload(BaseModel):
    url: HttpUrl
    impersonate: Optional[str] = "chrome"
    auto_rotate_proxy: Optional[bool] = False
    custom_proxy: Optional[str] = None
    timeout: Optional[int] = 20

@app.get("/")
async def root():
    return {
        "status": "online",
        "engine": "Nexus God-Engine v6.1 Enterprise",
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

    # Dynamic Stealth Header Engine
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

    # Proxy Selection Switchboard
    selected_proxy = None
    if payload.custom_proxy:
        # Priority 1: User passed their own proxy
        selected_proxy = payload.custom_proxy
    elif payload.auto_rotate_proxy:
        # Priority 2: Fetch a free dynamic proxy automatically
        selected_proxy = await fetch_free_proxifly_proxy()

    proxies = {"http": selected_proxy, "https": selected_proxy} if selected_proxy else None

    # Asynchronous Engine Socket Execution
    async with AsyncSession(
        impersonate=payload.impersonate,
        headers=stealth_headers,
        proxies=proxies,
        verify=True
    ) as session:
        try:
            logger.info(f"Scrape Triggered -> Domain: {domain} | Proxy: {selected_proxy}")
            
            response = await session.get(
                target_url,
                timeout=payload.timeout,
                allow_redirects=True
            )

            return {
                "status": "success",
                "engine_mode": "godmode_async_tls",
                "http_code": response.status_code,
                "target_url": target_url,
                "proxy_used": selected_proxy if selected_proxy else "direct_datacenter",
                "cookies_captured": dict(response.cookies),
                "content_length": len(response.text),
                "data": response.text[:10000]
            }

        except Exception as err:
            logger.error(f"Execution Exception: {str(err)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Scrape Execution Error: {str(err)}"
            )
