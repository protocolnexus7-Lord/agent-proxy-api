import re
import json
import random
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import html2text
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession

app = FastAPI(title="Nexus v6.2 Backend")

# Dummy Supabase / Auth Check placeholder
def verify_api_key(x_api_key: str = Header(...)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

class ScrapePayload(BaseModel):
    url: HttpUrl
    timeout: int = 15
    auto_rotate_proxy: bool = False
    extract_markdown: bool = False
    schema: Optional[Dict[str, Any]] = None
    impersonate: str = "chrome110"

# =====================================================================
# STEALTH FALLBACK SCAVENGER
# =====================================================================

async def execute_stealth_fallback_scrape(url: str) -> dict:
    """
    Tier-2 Python Stealth Engine: Uses dynamic TLS fingerprint cycling 
    and Chrome/Safari impersonation layers without external OS dependencies.
    """
    profiles = ["chrome120", "chrome119", "safari15_5", "edge101"]
    
    for profile in profiles:
        try:
            async with AsyncSession(impersonate=profile) as session:
                res = await session.get(
                    url, 
                    timeout=25, 
                    allow_redirects=True,
                    headers={
                        "Accept-Language": "en-US,en;q=0.9",
                        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"Windows"',
                        "Upgrade-Insecure-Requests": "1"
                    }
                )
                if res.status_code < 400:
                    return {"success": True, "html": res.text, "status_code": res.status_code}
        except Exception:
            continue
            
    return {"success": False, "error": "Anti-Bot defense unbroken after multi-profile TLS rotation."}

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
    
