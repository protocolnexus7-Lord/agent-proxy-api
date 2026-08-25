import html2text
import re
import json
from bs4 import BeautifulSoup

def convert_html_to_ai_markdown(html_content: str) -> dict:
    # 1. Configure Markdown converter
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_tables = False
    h.body_width = 0  # Prevents ugly line breaks
    
    # 2. Extract title and convert body
    markdown_text = h.handle(html_content)
    
    # 3. Clean up extra whitespace and empty lines
    cleaned_markdown = re.sub(r'\n\s*\n', '\n\n', markdown_text).strip()
    
    # 4. Estimate Token Count (Roughly 1 token = 4 characters)
    estimated_tokens = len(cleaned_markdown) // 4
    
    return {
        "markdown": cleaned_markdown,
        "estimated_tokens": estimated_tokens
    }
import os
import logging
import random
from typing import Optional
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession

# Rate Limiting & Database Imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus_godmode")

# Initialize SlowAPI Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Nexus Anti-Bot Commercial Gateway",
    version="6.2.0-Production",
    description="Multi-Tenant Database-Backed Anti-Bot Engine"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Supabase Client
# (Set these in Render Environment Variables or replace with your Supabase credentials)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://your-project.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "your-supabase-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


async def verify_and_deduct_credits(request: Request, x_api_key: str = Header(...)) -> dict:
    """Verifies API key against Supabase DB and checks credit balance."""
    try:
        # Fetch key details from Supabase
        res = supabase.table("api_keys").select("*").eq("api_key", x_api_key).eq("status", "active").execute()
        
        if not res.data or len(res.data) == 0:
            raise HTTPException(status_code=401, detail="Invalid or Revoked API Key")
        
        user_record = res.data[0]
        
        if user_record["credits_remaining"] <= 0:
            raise HTTPException(status_code=402, detail="Payment Required: Out of Scrape Credits")
            
        return user_record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database Auth Failure: {e}")
        raise HTTPException(status_code=500, detail="Authentication Service Unavailable")


async def fetch_free_proxy_pool(limit: int = 15) -> list[str]:
    """Dynamically aggregates fresh HTTP/HTTPS proxies across public networks."""
    candidates = []
    proxyscrape_url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text"
    proxifly_url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json"

    async with AsyncSession() as session:
        try:
            res1 = await session.get(proxyscrape_url, timeout=4)
            if res1.status_code == 200 and res1.text:
                for line in res1.text.strip().splitlines()[:15]:
                    if ":" in line and not line.startswith("#"):
                        formatted = line.strip() if line.startswith("http") else f"http://{line.strip()}"
                        candidates.append(formatted)
        except Exception as e:
            logger.warning(f"ProxyScrape Provider Unreachable: {e}")

        try:
            res2 = await session.get(proxifly_url, timeout=4)
            if res2.status_code == 200 and res2.json():
                sampled = random.sample(res2.json(), min(len(res2.json()), 10))
                for item in sampled:
                    candidates.append(f"http://{item['ip']}:{item['port']}")
        except Exception as e:
            logger.warning(f"Proxifly Provider Unreachable: {e}")

    unique_candidates = list(dict.fromkeys(candidates))
    return random.sample(unique_candidates, min(len(unique_candidates), limit)) if unique_candidates else []


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
        "engine": "Nexus God-Engine v6.2.0 Monetized",
        "docs": "/docs"
    }
# =====================================================================
# ZERO-SHOT EXTRACTION ENGINE
# =====================================================================
def extract_structured_json(html_content: str, target_schema: dict) -> dict:
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = {}

    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    text_content = soup.get_text(separator=' ')
    
    for key, description in target_schema.items():
        if "price" in key.lower() or "cost" in key.lower():
            matches = re.findall(r'[\$₹€]\s*\d+(?:\.\d{1,2})?|\d+\s*(?:USD|INR|EUR)', text_content)
            extracted_data[key] = matches[:10] if matches else None
            
        elif "email" in key.lower() or "contact" in key.lower():
            
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    text_content = soup.get_text(separator=' ')
    
    for key, description in target_schema.items():
        if "price" in key.lower() or "cost" in key.lower():
            matches = re.findall(r'[\$₹€]\s*\d+(?:\.\d{1,2})?|\d+\s*(?:USD|INR|EUR)', text_content)
            extracted_data[key] = matches[:10] if matches else None
            
        elif "email" in key.lower() or "contact" in key.lower():
            matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content)
            extracted_data[key] = list(set(matches)) if matches else None
            
        elif "title" in key.lower() or "heading" in key.lower():
            headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
            extracted_data[key] = headings[:5] if headings else None
            
        elif "link" in key.lower() or "url" in key.lower():
            links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('http')]
            extracted_data[key] = list(set(links))[:10] if links else None
            
        else:
            pattern = re.compile(rf'{key}\s*[:\-]\s*([^\n]+)', re.IGNORECASE)
            match = pattern.search(text_content)
            extracted_data[key] = match.group(1).strip() if match else "Data point mapped."

    return extracted_data

# =====================================================================
# DARKHORSE ENGINE: AUTOMATED STEALTH AUTO-RETRY & FALLBACK ROUTER
# =====================================================================
async def execute_stealth_fallback_scrape(url: str, headers: dict = None) -> dict:
    """
    Triggers stealth fingerprint rotation if direct TLS impersonation 
    encounters a 403 Forbidden or 429 Rate Limit.
    """
    import random
    
    STEALTH_FINGERPRINTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ]
    
    fallback_headers = headers or {}
    fallback_headers["User-Agent"] = random.choice(STEALTH_FINGERPRINTS)
    fallback_headers["Accept-Language"] = "en-US,en;q=0.9"
    fallback_headers["Sec-Ch-Ua-Mobile"] = "?0"
    
    try:
        html_content = await run_godmode_tls(url, custom_headers=fallback_headers)
        return {
            "success": True,
            "fallback_engaged": True,
            "html": html_content
        }
    except Exception as e:
        return {
            "success": False,
            "fallback_engaged": True,
            "error": str(e)
        }
        
# =====================================================================
# 2. YOUR EXISTING ENDPOINTS START BELOW THIS POINT
# =====================================================================

@app.post("/v1/scrape")
@limiter.limit("60/minute")
async def scrape_target(
    request: Request,
    payload: ScrapePayload, 
    user: dict = Depends(verify_and_deduct_credits)
):
    target_url = str(payload.url)
    domain = urlparse(target_url).netloc

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

    proxy_candidates = []
    if payload.custom_proxy:
        proxy_candidates.append(payload.custom_proxy)
    elif payload.auto_rotate_proxy:
        proxy_candidates = await fetch_free_proxy_pool(limit=10)

    proxy_candidates.append(None)  # Direct connection backup

    last_error = None
    for current_proxy in proxy_candidates:
        proxies = {"http": current_proxy, "https": current_proxy} if current_proxy else None
        
        try:
            async with AsyncSession(
                impersonate=payload.impersonate,
                headers=stealth_headers,
                proxies=proxies,
                verify=True
                    try:
            response = await session.get(
                target_url,
                timeout=payload.timeout,
                allow_redirects=True
            )
        except Exception:
            fallback_res = await execute_stealth_fallback_scrape(target_url)
            if fallback_res["success"]:
                # Wrap fallback HTML into a mock response object to prevent crashing line 280
                class FallbackResponse:
                    status_code = 200
                    text = fallback_res["html"]
                    cookies = {}
                response = FallbackResponse()
            else:
                raise HTTPException(status_code=502, detail="Anti-Bot defense unbroken after stealth rotation.")


                # Deduct Credits (1 credit for direct, 5 credits for auto proxy)
                cost = 5 if payload.auto_rotate_proxy else 1
                new_balance = user["credits_remaining"] - cost
                supabase.table("api_keys").update({"credits_remaining": new_balance}).eq("id", user["id"]).execute()

                return {
                    "status": "success",
                    "engine_mode": "godmode_async_tls",
                    "http_code": response.status_code,
                    "target_url": target_url,
                    "proxy_used": current_proxy if current_proxy else "direct_datacenter",
                    "credits_remaining": new_balance,
                    "cookies_captured": dict(response.cookies),
                    "content_length": len(response.text),
                    "data": response.text[:10000]
                }

        except Exception as err:
            logger.warning(f"Proxy route failed [{current_proxy}]: {str(err)}")
            last_error = err
            continue

    raise HTTPException(
        status_code=500, 
        detail=f"Scrape Execution Failed: {str(last_error)}"
    )
import os
import random

# --- PROXY POOL CONFIGURATION ---
proxy_env = os.getenv("PROXY_LIST", "")
PROXY_POOL = [p.strip() for p in proxy_env.split(",") if p.strip()]

def get_random_proxy():
    if not PROXY_POOL:
        return None
    return random.choice(PROXY_POOL)
