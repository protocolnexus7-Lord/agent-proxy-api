import logging
import random
from typing import Optional
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession

# Initialize System Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_godmode")

app = FastAPI(
    title="Nexus Anti-Bot Commercial Gateway",
    version="6.1.1-Enterprise",
    description="Protocol-Accurate TLS/HTTP2 Scraping Gateway with Automatic Proxy Failover"
)

# API Authentication Credential
API_KEY_CREDENTIAL = "sk_live_nexus_2026"

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

async def fetch_free_proxy_pool(limit: int = 15) -> list[str]:
    """Dynamically aggregates fresh HTTP/HTTPS proxies across multiple public networks."""
    candidates = []
    
    # Provider 1: ProxyScrape API Endpoint
    proxyscrape_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"
    
    # Provider 2: Proxifly Public Feed
    proxifly_url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json"

    async with AsyncSession() as session:
        # Fetch Source 1 (ProxyScrape)
        try:
            res1 = await session.get(proxyscrape_url, timeout=4)
            if res1.status_code == 200 and res1.text:
                lines = res1.text.strip().splitlines()
                for line in lines[:15]:
                    if ":" in line and not line.startswith("#"):
                        # Normalize format
                        formatted = line.strip() if line.startswith("http") else f"http://{line.strip()}"
                        candidates.append(formatted)
        except Exception as e:
            logger.warning(f"ProxyScrape Provider Unreachable: {e}")

        # Fetch Source 2 (Proxifly)
        try:
            res2 = await session.get(proxifly_url, timeout=4)
            if res2.status_code == 200:
                proxies = res2.json()
                if proxies and isinstance(proxies, list):
                    sampled = random.sample(proxies, min(len(proxies), 10))
                    for item in sampled:
                        candidates.append(f"http://{item['ip']}:{item['port']}")
        except Exception as e:
            logger.warning(f"Proxifly Provider Unreachable: {e}")

    # Remove duplicates while maintaining order
    unique_candidates = list(dict.fromkeys(candidates))
    if not unique_candidates:
        return []
    
    return random.sample(unique_candidates, min(len(unique_candidates), limit))

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

    # Dynamic Stealther Headers (Chrome 120+ Parity)
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

    # Build Candidate Proxy Switchboard
    proxy_candidates = []
    if payload.custom_proxy:
        proxy_candidates.append(payload.custom_proxy)
    elif payload.auto_rotate_proxy:
        proxy_candidates = await fetch_free_proxy_pool(limit=10)

    # Always inject direct datacenter connection as ultimate fallback route
    proxy_candidates.append(None)

    # Execution Engine Loop with Failover Guarantee
    last_error = None
    for current_proxy in proxy_candidates:
        proxies = {"http": current_proxy, "https": current_proxy} if current_proxy else None
        
        try:
            logger.info(f"Triggering Socket -> Target: {domain} | Proxy: {current_proxy if current_proxy else 'Direct Datacenter'}")
            
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

                # Execution Success Response Payload
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
            logger.warning(f"Proxy route failed [{current_proxy}]: {str(err)}. Failing over...")
            last_error = err
            continue

    # Absolute Failure Handler (Triggers only if all proxies AND direct fallback fail)
    raise HTTPException(
        status_code=500, 
        detail=f"Scrape Execution Failed across all fallback routes: {str(last_error)}"
    )
