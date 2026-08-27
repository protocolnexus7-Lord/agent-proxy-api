import re
import json
import random
import asyncio
import os
import hashlib
import base64
import httpx
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from readability import Document
import html2text
from fastapi import FastAPI, HTTPException, Header, Depends, Request, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession

app = FastAPI(title="Nexus v6.3 Backend")

@app.get("/add14096.html", response_class=PlainTextResponse)
@app.get("/cryptomus_add14096.html", response_class=PlainTextResponse)
def cryptomus_verification():
    return "Cryptomus=add14096"
    
# --- ROOT HEALTH CHECK ---
@app.get("/", response_class=HTMLResponse)
def health_check():
    return '''
    <!DOCTYPE html>
    <html>
      <head>
        <meta name="cryptomus" content="add14096-ff52-49d1-b188-a538aa30dd74" />
        <meta name="cryptomus" content="add14096" />
        <title>Nexus Protocol API</title>
      </head>
      <body>
        <h1>Nexus Protocol API Online</h1>
      </body>
    </html>
    '''

# --- CRYPTOMUS CONFIG & HELPERS ---
CRYPTOMUS_MERCHANT_ID = "YOUR_CRYPTOMUS_MERCHANT_ID"
CRYPTOMUS_API_KEY = "YOUR_CRYPTOMUS_PAYMENT_API_KEY"
BASE_URL = "https://nexus-protocol-api.onrender.com"

def generate_cryptomus_signature(payload_dict: dict, api_key: str) -> str:
    json_data = json.dumps(payload_dict, separators=(',', ':'))
    encoded_json = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    return hashlib.md5((encoded_json + api_key).encode('utf-8')).hexdigest()

def verify_webhook_signature(payload_dict: dict, sign_header: str, api_key: str) -> bool:
    data_to_hash = {k: v for k, v in payload_dict.items() if k != 'sign'}
    json_data = json.dumps(data_to_hash, ensure_ascii=False, separators=(',', ':'))
    encoded_json = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    calculated_sign = hashlib.md5((encoded_json + api_key).encode('utf-8')).hexdigest()
    return calculated_sign.lower() == sign_header.lower()

class CheckoutRequest(BaseModel):
    user_email: str

@app.post("/create-checkout")
async def create_checkout(request_data: CheckoutRequest):
    order_id = f"nexus_{hashlib.sha256(request_data.user_email.encode()).hexdigest()[:10]}"
    payload = {
        "amount": "29.00",
        "currency": "USD",
        "order_id": order_id,
        "url_callback": f"{BASE_URL}/webhooks/cryptomus",
        "url_success": f"{BASE_URL}/docs",
        "is_payment_multiple": False,
        "lifetime": 3600
    }
    signature = generate_cryptomus_signature(payload, CRYPTOMUS_API_KEY)
    headers = {
        "merchant": CRYPTOMUS_MERCHANT_ID,
        "sign": signature,
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("https://api.cryptomus.com/v1/payment", json=payload, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to create payment session")
    res_data = response.json()
    return {"status": "success", "order_id": order_id, "checkout_url": res_data["result"]["url"]}

@app.post("/webhooks/cryptomus")
async def cryptomus_webhook(request: Request):
    payload = await request.json()
    received_sign = payload.get("sign")
    if not received_sign or not verify_webhook_signature(payload, received_sign, CRYPTOMUS_API_KEY):
        raise HTTPException(status_code=401, detail="Invalid signature")
    if payload.get("status") in ["paid", "paid_over"]:
        # Logic to provision key in your DB
        pass
    return {"status": "received"}
    
# PRODUCTION SECURITY BOUNCER
async def verify_api_key(x_api_key: str = Header(None)):
    # 1. Reject missing or bad keys immediately
    if not x_api_key or not x_api_key.startswith("sk_live_"):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid API Key format."
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
    
