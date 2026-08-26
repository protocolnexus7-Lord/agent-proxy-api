import re
import json
import random
import asyncio
import os
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from readability import Document
import html2text
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession

app = FastAPI(title="Nexus v6.2 Backend")

# PRODUCTION SECURITY BOUNCER
async def verify_api_key(x_api_key: str = Header(...)):
    # 1. Reject missing or bad keys immediately
    if not x_api_key or not x_api_key.startswith("sk_live_"):
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Invalid or missing API key format."
        )
    
    # 2. Hardcoded master key check (for QA testing)
    if x_api_key == "sk_live_nexus_2026":
        return x_api_key

    # 3. Supabase Database Quota Check
    try:
        user = supabase.table("users").select("*").eq("api_key", x_api_key).execute()
        if not user.data:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid API key.")
        
        user_data = user.data[0]
        if user_data.get("usage_count", 0) >= user_data.get("limit", 50000):
            raise HTTPException(status_code=429, detail="Payment required: Monthly API limit exceeded.")
        
        # Increment usage counter
        supabase.table("users").update({"usage_count": user_data["usage_count"] + 1}).eq("api_key", x_api_key).execute()
    except Exception:
        # If Supabase is unconfigured, reject unknown keys safely
        if x_api_key != "sk_live_nexus_2026":
            raise HTTPException(status_code=401, detail="Unauthorized API key access.")

    return x_api_key
    
class ScrapePayload(BaseModel):
    url: HttpUrl
    timeout: int = 15
    auto_rotate_proxy: bool = False
    extract_markdown: bool = False
    schema: Optional[Dict[str, Any]] = None
    impersonate: str = "chrome110"

# ==============================================================================
# STEALTH FALLBACK SCAVENGER (ENTERPRISE $1M EDITION)
# ==============================================================================

STEALTH_PROFILES = [
    ("chrome120", "Windows", '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'),
    ("safari15_5", "macOS", '"Not_A Brand";v="99", "Safari";v="15"'),
    ("edge101", "Windows", '"Not_A Brand";v="99", "Microsoft Edge";v="101"')
]

ROTATING_PROXY = os.getenv("RESIDENTIAL_PROXY_URL", None)

async def execute_stealth_fallback_scrape(url: str, max_retries: int = 3) -> dict:
    """
    Enterprise Stealth Engine: Features dynamic TLS rotation, full Client-Hint 
    header spoofing, residential proxy fallback support, and exponential backoff.
    """
    for attempt in range(max_retries):
        impersonate_profile, os_name, sec_ua = STEALTH_PROFILES[attempt % len(STEALTH_PROFILES)]
        
        headers = {
            "User-Agent": f"Mozilla/5.0 ({os_name}; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-Ch-Ua": sec_ua,
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": f'"{os_name}"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        }
        
        proxies = {"http": ROTATING_PROXY, "https": ROTATING_PROXY} if (ROTATING_PROXY and attempt > 0) else None

        try:
            async with AsyncSession(impersonate=impersonate_profile, proxies=proxies) as session:
                res = await session.get(url, timeout=20, allow_redirects=True, headers=headers)
                
                if res.status_code == 200 and len(res.text) > 200 and "just a moment..." not in res.text.lower():
                    return {"success": True, "html": res.text, "status_code": res.status_code}
        except Exception:
            pass
            
        await asyncio.sleep(1.5 ** attempt)
            
    return {"success": False, "error": "Anti-bot defenses unbroken after multi-tier proxy & TLS rotation."}

# =====================================================================
# ZERO-SHOT EXTRACTION ENGINE
# =====================================================================
def extract_structured_json(html_content: str, target_schema: dict) -> dict:
    cleaned_html = Document(html_content).summary()
    soup = BeautifulSoup(cleaned_html, 'html.parser')
    extracted_data = {}
    
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    text_content = soup.get_text(separator=' ')
    
    for key, description in target_schema.items():
        if "price" in key.lower() or "cost" in key.lower():
            matches = re.findall(r'[\$₹€]\s*\d+(?:\.\d{1,2})?|\d+\s*(?:USD|INR|EUR)', text_content)
            extracted_data[key] = matches[:10] if matches else None
        elif "email" in key.lower() or "contact" in key.lower():
            matches = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text_content)
            extracted_data[key] = matches[:10] if matches else None
        else:
            extracted_data[key] = text_content[:200]

    return extracted_data

# =====================================================================
# SCRAPE ENDPOINT
# =====================================================================
@app.post("/v1/scrape")
async def scrape_target(payload: ScrapePayload, api_key: str = Depends(verify_api_key)):
    target_url = str(payload.url)
    stealth_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    proxy_candidates = [None]
    response = None
    last_error = None

    for current_proxy in proxy_candidates:
        proxies = {"http": current_proxy, "https": current_proxy} if current_proxy else None
        try:
            async with AsyncSession(
                impersonate=payload.impersonate,
                headers=stealth_headers,
                proxies=proxies,
                verify=True
            ) as session:
                try:
                    response = await session.get(
                        target_url,
                        timeout=payload.timeout,
                        allow_redirects=True
                    )
                except Exception:
                    fallback_res = await execute_stealth_fallback_scrape(target_url)
                    if fallback_res["success"]:
                        class FallbackResponse:
                            status_code = 200
                            text = fallback_res["html"]
                            cookies = {}
                        response = FallbackResponse()
                    else:
                        raise HTTPException(status_code=502, detail="Anti-Bot defense unbroken after stealth rotation.")
            break
        except Exception as e:
            last_error = str(e)

    if not response:
        raise HTTPException(status_code=500, detail=f"Scrape failed: {last_error}")

    result = {
        "status": "success",
        "engine_mode": "godmode_async_tls",
        "status_code": response.status_code,
        "html": response.text[:1000] if not payload.extract_markdown else None
    }

    if payload.schema and response.text:
        result["extracted_data"] = extract_structured_json(response.text, payload.schema)

    return result
    
