import logging
import random
from typing import Optional
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_stealth_v6")

app = FastAPI(
    title="Nexus Anti-Bot Enterprise God-Engine",
    version="6.0.0",
    description="Protocol-Accurate TLS/HTTP2 Session Impersonation API"
)

API_KEY_CREDENTIAL = "sk_live_nexus_2026"

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

class ScrapePayload(BaseModel):
    url: HttpUrl
    impersonate: Optional[str] = "chrome124"
    http_version: Optional[str] = "h2"  # Accepts: 'h2', 'http11', or 'h3'
    auto_rotate_proxy: Optional[bool] = False
    custom_proxy: Optional[str] = None
    timeout: Optional[int] = 20

async def fetch_dynamic_proxy():
    try:
        async with AsyncSession() as session:
            res = await session.get("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json", timeout=5)
            if res.status_code == 200:
                proxies = res.json()
                if proxies:
                    chosen = random.choice(proxies)
                    return f"http://{chosen['ip']}:{chosen['port']}"
    except Exception:
        pass
    return None

@app.post("/v1/scrape")
async def scrape_target(
    payload: ScrapePayload, 
    api_key: str = Depends(verify_api_key)
):
    target_url = str(payload.url)
    parsed_url = urlparse(target_url)
    domain = parsed_url.netloc

    # Pure Browser Header Engine (Letting curl_cffi order pseudo-headers natively)
    stealth_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    selected_proxy = payload.custom_proxy
    if not selected_proxy and payload.auto_rotate_proxy:
        selected_proxy = await fetch_dynamic_proxy()

    proxies = {"http": selected_proxy, "https": selected_proxy} if selected_proxy else None

    # Persistent Async Engine Session matching Chrome Native Networking
    async with AsyncSession(
        impersonate=payload.impersonate,
        headers=stealth_headers,
        proxies=proxies,
        verify=True
    ) as session:
        try:
            logger.info(f"Engine v6 Execution -> Domain: {domain} | Proxy: {selected_proxy}")
            
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
            logger.error(f"Engine v6 Failure: {str(err)}")
            raise HTTPException(status_code=500, detail=f"GodEngine Execution Error: {str(err)}")
