import logging
import random
from typing import Optional
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from curl_cffi import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_stealth_v5")

app = FastAPI(
    title="Nexus Anti-Bot Enterprise Engine",
    version="5.0.0",
    description="Unbeatable Dual-Mode Auto-Retrying Anti-Bot API"
)

API_KEY_CREDENTIAL = "sk_live_nexus_2026"

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
    timeout: Optional[int] = 15

def get_dynamic_proxy():
    """Fetches a fresh public proxy list live if needed."""
    try:
        res = requests.get("https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json", timeout=5)
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

    # Intelligent Auto-Retry Engine Loop (Up to 3 attempts)
    max_retries = 3 if payload.auto_rotate_proxy else 1
    last_error = ""

    for attempt in range(max_retries):
        selected_proxy = None
        if payload.custom_proxy:
            selected_proxy = payload.custom_proxy
        elif payload.auto_rotate_proxy and attempt > 0:
            selected_proxy = get_dynamic_proxy()

        proxies = {"http": selected_proxy, "https": selected_proxy} if selected_proxy else None

        try:
            logger.info(f"Attempt {attempt+1}/{max_retries} -> Target: {domain} | Proxy: {selected_proxy}")
            
            response = requests.get(
                target_url,
                impersonate=payload.impersonate,
                headers=stealth_headers,
                proxies=proxies,
                timeout=payload.timeout,
                allow_redirects=True
            )

            # Return immediately on successful response
            if response.status_code in [200, 301, 302]:
                return {
                    "status": "success",
                    "engine_mode": "stealth_tls",
                    "http_code": response.status_code,
                    "target_url": target_url,
                    "attempts": attempt + 1,
                    "proxy_used": selected_proxy if selected_proxy else "direct_datacenter",
                    "content_length": len(response.text),
                    "data": response.text[:10000]
                }
            
            last_error = f"Target returned HTTP {response.status_code}"

        except Exception as err:
            last_error = str(err)
            logger.warning(f"Attempt {attempt+1} failed: {last_error}")

    raise HTTPException(status_code=500, detail=f"Unbeatable Engine Executions Failed. Last Error: {last_error}")
