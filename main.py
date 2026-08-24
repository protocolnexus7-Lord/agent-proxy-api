import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from urllib.parse import urlparse
from curl_cffi import requests
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_stealth_v4")

app = FastAPI(
    title="Nexus Anti-Bot Enterprise Engine",
    version="4.0.0",
    description="Dual-Mode Proxy Pool & Stealth Impersonation API"
)

# Core API Security Credential
API_KEY_CREDENTIAL = "sk_live_nexus_2026"

# Outbound proxy pool backup array
BACKUP_PROXY_POOL = [
    # Format: "http://username:password@ip:port" or "http://ip:port"
    "http://161.35.90.93:1082",
    "http://185.199.229.156:7492",
    "http://51.159.65.67:8888"
]

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

class ScrapePayload(BaseModel):
    url: HttpUrl
    impersonate: Optional[str] = "chrome"
    render_js: Optional[bool] = False
    auto_rotate_proxy: Optional[bool] = True
    custom_proxy: Optional[str] = None
    timeout: Optional[int] = 30

@app.post("/v1/scrape")
async def scrape_target(
    payload: ScrapePayload, 
    api_key: str = Depends(verify_api_key)
):
    target_url = str(payload.url)
    parsed_url = urlparse(target_url)
    domain = parsed_url.netloc

    # Dynamic target spoofing headers
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

    # Proxy selection routing logic
    selected_proxy = None
    if payload.custom_proxy:
        selected_proxy = payload.custom_proxy
    elif payload.auto_rotate_proxy and BACKUP_PROXY_POOL:
        selected_proxy = random.choice(BACKUP_PROXY_POOL)

    proxies = {"http": selected_proxy, "https": selected_proxy} if selected_proxy else None

    logger.info(f"Engine v4 Request -> Target: {domain} | Proxy Active: {bool(selected_proxy)}")

    try:
        # High-Speed TLS Impersonation Request
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
            "engine_mode": "stealth_tls",
            "http_code": response.status_code,
            "target_url": target_url,
            "proxy_used": selected_proxy if selected_proxy else "direct_datacenter",
            "content_length": len(response.text),
            "data": response.text[:10000]
        }

    except Exception as err:
        logger.error(f"Engine v4 Failure: {str(err)}")
        raise HTTPException(status_code=500, detail=f"Scrape Execution Error: {str(err)}")
