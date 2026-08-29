import re
import json
import random
import asyncio
import os
import hmac
import hashlib
import base64
import logging
import httpx
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from readability import Document
import html2text
from fastapi import FastAPI, HTTPException, Header, Depends, Request, Security, status
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from curl_cffi.requests import AsyncSession
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# --- DYNAMIC CONFIGURATION & SECURITY SETUP ---
API_KEY_NAME = "x-api-key"
MASTER_API_KEY = os.getenv("MASTER_API_KEY", "sk_live_nexus_2026")
CRYPTOMUS_PAYMENT_KEY = os.getenv("CRYPTOMUS_PAYMENT_KEY", "your_cryptomus_payment_key")
CRYPTOMUS_MERCHANT_ID = os.getenv("CRYPTOMUS_MERCHANT_ID", "your_merchant_id")

app = FastAPI(
    title="Nexus v6.3 Backend",
    description="Enterprise Stealth Web Extraction & Anti-Bot Infrastructure",
    version="6.3.0",
    docs_url=None,
    redoc_url=None
)

app = FastAPI(title="Nexus Protocol")

@app.get("/", response_class=HTMLResponse)
async def serve_landing_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEXUS PROTOCOL — Autonomous Stealth Extraction Engine</title>
        <!-- Cryptomus Verification Meta-Tags -->
        <meta name="cryptomus" content="add14096-ff52-49d1-b188-a538aa30dd74" />
        <meta name="cryptomus-verification" content="add14096" />
        <style>
            :root {
                --bg: #02040a;
                --card-bg: rgba(11, 15, 25, 0.75);
                --accent: #6366f1;
                --accent-glow: rgba(99, 102, 241, 0.4);
                --text-main: #f9fafb;
                --text-muted: #9ca3af;
                --border: rgba(31, 41, 55, 0.9);
                --success: #10b981;
            }
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                background-color: var(--bg); 
                color: var(--text-main); 
                min-height: 100vh; 
                display: flex; 
                flex-direction: column; 
                align-items: center; 
                justify-content: flex-start; 
                overflow-x: hidden; 
                position: relative; 
                padding: 1.5rem 1rem;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
            
            /* Cyber Grid Background Effect */
            .grid-bg { position: fixed; width: 100vw; height: 100vh; background-image: linear-gradient(to right, rgba(99, 102, 241, 0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(99, 102, 241, 0.04) 1px, transparent 1px); background-size: 32px 32px; z-index: 0; pointer-events: none; }
            .glow-orb { position: absolute; width: 600px; height: 600px; background: radial-gradient(circle, var(--accent-glow) 0%, rgba(0,0,0,0) 70%); top: -150px; z-index: 0; pointer-events: none; filter: blur(60px); }

            /* Top Telemetry & Language Bar */
            .top-telemetry { position: relative; z-index: 2; width: 100%; max-width: 950px; display: flex; justify-content: space-between; align-items: center; background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem 1.2rem; margin-bottom: 2rem; backdrop-filter: blur(12px); font-size: 0.8rem; flex-wrap: wrap; gap: 0.8rem; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
            .telemetry-item { display: flex; align-items: center; gap: 0.5rem; color: var(--text-muted); }
            .telemetry-item span { color: var(--text-main); font-weight: bold; }
            .lang-select { background: #030712; color: #818cf8; border: 1px solid var(--accent); padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; outline: none; font-weight: bold; }

            .container { position: relative; z-index: 1; max-width: 950px; width: 100%; text-align: center; }
            .badge { display: inline-block; background: rgba(99, 102, 241, 0.15); border: 1px solid var(--accent); color: #818cf8; padding: 0.4rem 1.2rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1.5rem; box-shadow: 0 0 15px rgba(99, 102, 241, 0.2); }
            
            h1 { font-size: clamp(2.2rem, 4.5vw, 3.5rem); font-weight: 800; line-height: 1.15; margin-bottom: 1.2rem; background: linear-gradient(135deg, #ffffff 30%, #93c5fd 70%, #6366f1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.02em; }
            p.subtitle { font-size: 1.05rem; color: var(--text-muted); max-width: 720px; margin: 0 auto 2rem; line-height: 1.6; }

            .status-box { background: rgba(0, 0, 0, 0.7); border: 1px solid var(--border); border-radius: 10px; padding: 0.8rem 1.5rem; display: inline-flex; align-items: center; gap: 2rem; margin-bottom: 2rem; font-size: 0.85rem; box-shadow: inset 0 0 15px rgba(0,0,0,0.9); flex-wrap: wrap; justify-content: center; }
            .status-item { display: flex; align-items: center; gap: 0.6rem; }
            .dot { width: 9px; height: 9px; background-color: var(--success); border-radius: 50%; box-shadow: 0 0 10px var(--success); animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

            /* Terms Compliance Box */
            .compliance-box { background: rgba(11, 15, 25, 0.5); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1.25rem; margin: 0 auto 2.5rem; max-width: 750px; display: flex; align-items: flex-start; gap: 0.75rem; text-align: left; backdrop-filter: blur(8px); }
            .compliance-box input[type="checkbox"] { accent-color: var(--accent); margin-top: 0.2rem; cursor: pointer; }
            .compliance-box label { font-size: 0.75rem; color: var(--text-muted); line-height: 1.4; cursor: pointer; }

            /* Feature Grid */
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; text-align: left; margin-bottom: 3.5rem; }
            .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 1.8rem; backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; }
            .card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, var(--accent), transparent); opacity: 0; transition: opacity 0.3s; }
            .card:hover { transform: translateY(-5px); border-color: var(--accent); box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.3); }
            .card:hover::before { opacity: 1; }
            .card h3 { font-size: 1.1rem; color: #fff; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; font-weight: 700; }
            .card p { font-size: 0.88rem; color: var(--text-muted); line-height: 1.6; }

            /* Pricing Packages Section */
            .section-title { font-size: 1.8rem; font-weight: 800; margin-bottom: 0.5rem; color: #fff; letter-spacing: -0.01em; }
            .section-subtitle { font-size: 0.95rem; color: var(--text-muted); margin-bottom: 2rem; }
            .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem; text-align: left; margin-bottom: 4rem; }
            .pricing-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; padding: 2rem 1.5rem; display: flex; flex-direction: column; justify-content: space-between; backdrop-filter: blur(12px); position: relative; transition: all 0.3s ease; }
            .pricing-card.featured { border-color: var(--accent); box-shadow: 0 0 25px rgba(99, 102, 241, 0.25); background: rgba(15, 23, 42, 0.85); }
            .pricing-card.featured::after { content: 'MOST POPULAR'; position: absolute; top: -12px; right: 20px; background: var(--accent); color: #fff; font-size: 0.65rem; font-weight: 800; padding: 0.2rem 0.6rem; border-radius: 9999px; letter-spacing: 0.1em; }
            .pricing-card h4 { font-size: 1.2rem; color: #fff; margin-bottom: 0.5rem; }
            .pricing-card .price { font-size: 2.2rem; font-weight: 800; color: #fff; margin-bottom: 1rem; }
            .pricing-card .price span { font-size: 0.9rem; color: var(--text-muted); font-weight: 400; }
            .pricing-features { list-style: none; margin-bottom: 1.8rem; font-size: 0.85rem; color: var(--text-muted); }
            .pricing-features li { margin-bottom: 0.6rem; display: flex; align-items: center; gap: 0.5rem; }
            .pricing-features li::before { content: '✓'; color: var(--success); font-weight: bold; }
            
            .btn { display: inline-block; width: 100%; text-align: center; background: rgba(99, 102, 241, 0.1); border: 1px solid var(--accent); color: #fff; padding: 0.75rem 1rem; border-radius: 8px; font-weight: 700; font-size: 0.85rem; text-decoration: none; cursor: pointer; transition: all 0.2s ease; }
            .btn:hover { background: var(--accent); box-shadow: 0 0 15px rgba(99, 102, 241, 0.5); transform: translateY(-2px); }
            .btn-primary { background: var(--accent); box-shadow: 0 0 15px rgba(99, 102, 241, 0.3); }

            .footer { margin-top: 2rem; font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 2rem; display: flex; justify-content: space-between; align-items: center; width: 100%; flex-wrap: wrap; gap: 1rem; }
        </style>
    </head>
    <body>
        <div class="grid-bg"></div>
        <div class="glow-orb"></div>

        <!-- Top Telemetry Bar -->
        <div class="top-telemetry mono">
            <div class="telemetry-item">🌐 
                <select class="lang-select" id="langSelect">
                    <option value="en">ENGLISH (GLOBAL)</option>
                    <option value="es">ESPAÑOL</option>
                    <option value="zh">中文 (CHINESE)</option>
                    <option value="ja">日本語 (JAPANESE)</option>
                    <option value="de">DEUTSCH</option>
                    <option value="fr">FRANÇAIS</option>
                </select>
            </div>
            <div class="telemetry-item">⚡ PING: <span style="color: var(--success);">12ms</span></div>
            <div class="telemetry-item">🕒 UTC TIME: <span id="utcClock" style="color: #818cf8;">00:00:00 UTC</span></div>
        </div>

        <div class="container">
            <div class="badge mono">Nexus v6.3 Enterprise Edition</div>
            <h1>Autonomous Stealth Extraction & Anti-Bot Infrastructure</h1>
            <p class="subtitle">Next-generation distributed high-performance API protocol utilizing low-level TLS fingerprint emulation, residential routing networks, and automated Cryptomus ledger verification.</p>
            
            <div class="status-box mono">
                <div class="status-item"><span class="dot"></span> <strong>CORE ENGINE:</strong> <span style="color: var(--success);">ONLINE</span></div>
                <div class="status-item" style="color: var(--text-muted);">PROTOCOL: <span style="color: #fff;">TLS_ASYNC_v6.3</span></div>
                <div class="status-item" style="color: var(--text-muted);">ENCRYPTION: <span style="color: #fff;">HMAC-SHA256</span></div>
            </div>

            <!-- Compliance Box -->
            <div class="compliance-box mono">
                <input type="checkbox" id="termsAck" checked disabled />
                <label for="termsAck">
                    <strong>Operational Compliance Notice:</strong> Nexus Protocol provides a lawful, high-performance software infrastructure framework. Utilization of this software, routing pipelines, and data acquisition tools remains strictly at the sole discretion and legal responsibility of the end user, who assumes total liability for adherence to applicable jurisdictional regulations.
                </label>
            </div>

            <!-- Core Features -->
            <div class="grid">
                <div class="card">
                    <h3>🛡️ Stealth Pipeline</h3>
                    <p>Proprietary TLS fingerprint randomization delivering zero-friction data delivery across all edge targets.</p>
                </div>
                <div class="card">
                    <h3>⚡ High-Velocity Engine</h3>
                    <p>Ultra-low latency extraction architecture optimized for sub-second global response times.</p>
                </div>
                <div class="card">
                    <h3>💳 Automated Ledger</h3>
                    <p>Instant cryptographic settlement layer with secure, automated verification.</p>
                </div>
            </div>

            <!-- Packages / Pricing Section -->
            <h2 class="section-title">Deployment Packages</h2>
            <p class="section-subtitle">Select an infrastructure tier tailored to your API execution frequency.</p>
            
            <div class="pricing-grid">
                <!-- Standard Tier -->
                <div class="pricing-card">
                    <div>
                        <h4>Developer Tier</h4>
                        <div class="price mono">$299 <span>/mo</span></div>
                        <ul class="pricing-features mono">
                            <li>100,000 API Calls / month</li>
                            <li>Standard TLS Randomization</li>
                            <li>99.5% Uptime SLA</li>
                            <li>Community Discord Support</li>
                        </ul>
                    </div>
                    <a href="#checkout" class="btn mono">Deploy Tier</a>
                </div>

                <!-- Featured Tier -->
                <div class="pricing-card featured">
                    <div>
                        <h4>Professional Tier</h4>
                        <div class="price mono">$999 <span>/mo</span></div>
                        <ul class="pricing-features mono">
                            <li>1,000,000 API Calls / month</li>
                            <li>Advanced Stealth Routing</li>
                            <li>99.9% Uptime SLA</li>
                            <li>Sub-50ms Global Latency</li>
                            <li>Priority Telegram Support</li>
                        </ul>
                    </div>
                    <a href="#checkout" class="btn btn-primary mono">Deploy Tier</a>
                </div>

                <!-- Enterprise Tier -->
                <div class="pricing-card">
                    <div>
                        <h4>Enterprise Enclave</h4>
                        <div class="price mono">Custom</div>
                        <ul class="pricing-features mono">
                            <li>Unlimited Execution Nodes</li>
                            <li>Dedicated IP Infrastructure</li>
                            <li>Custom TLS Fingerprints</li>
                            <li>24/7 Dedicated Ops Support</li>
                            <li>Instant Crypto Settlement</li>
                        </ul>
                    </div>
                    <a href="#checkout" class="btn mono">Contact Ops</a>
                </div>
            </div>

            <div class="footer mono">
                <div>&copy; 2026 Nexus Protocol. All infrastructure nodes secure.</div>
                <div style="color: #818cf8; font-weight: bold;">SECURE ENCLAVE ACTIVE</div>
            </div>
        </div>

        <script>
            function updateClock() {
                const now = new Date();
                const utcString = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
                const clockEl = document.getElementById('utcClock');
                if (clockEl.innerText !== utcString) {
                    clockEl.innerText = utcString;
                }
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>
    </body>
    </html>
    """

async def serve_landing_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NEXUS PROTOCOL — Autonomous Stealth Extraction Engine</title>
        <meta name="cryptomus" content="add14096-ff52-49d1-b188-a538aa30dd74" />
        <meta name="cryptomus-verification" content="add14096" />
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            :root {
                --bg: #02040a;
                --card-bg: rgba(11, 15, 25, 0.75);
                --accent: #6366f1;
                --accent-glow: rgba(99, 102, 241, 0.4);
                --text-main: #f9fafb;
                --text-muted: #9ca3af;
                --border: rgba(31, 41, 55, 0.9);
                --success: #10b981;
            }
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }
            body { background-color: var(--bg); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; overflow-x: hidden; position: relative; padding: 1.5rem 1rem; }
            
            /* Cyber Grid Background Effect */
            .grid-bg { position: fixed; width: 100vw; height: 100vh; background-image: linear-gradient(to right, rgba(99, 102, 241, 0.04) 1px, transparent 1px), linear-gradient(to bottom, rgba(99, 102, 241, 0.04) 1px, transparent 1px); background-size: 32px 32px; z-index: 0; pointer-events: none; }
            .glow-orb { position: absolute; width: 500px; height: 500px; background: radial-gradient(circle, var(--accent-glow) 0%, rgba(0,0,0,0) 70%); top: -100px; z-index: 0; pointer-events: none; filter: blur(50px); }

            /* Top Telemetry & Language Bar */
            .top-telemetry { position: relative; z-index: 2; width: 100%; max-width: 950px; display: flex; justify-content: space-between; align-items: center; background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem 1.2rem; margin-bottom: 2rem; backdrop-filter: blur(12px); font-size: 0.8rem; flex-wrap: wrap; gap: 0.8rem; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
            .telemetry-item { display: flex; align-items: center; gap: 0.5rem; color: var(--text-muted); }
            .telemetry-item span { color: var(--text-main); font-weight: bold; }
            .lang-select { background: #030712; color: #818cf8; border: 1px solid var(--accent); padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; outline: none; font-weight: bold; }

            .container { position: relative; z-index: 1; max-width: 950px; width: 100%; text-align: center; }
            .badge { display: inline-block; background: rgba(99, 102, 241, 0.15); border: 1px solid var(--accent); color: #818cf8; padding: 0.4rem 1.2rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 1.5rem; box-shadow: 0 0 15px rgba(99, 102, 241, 0.2); }
            
            h1 { font-size: clamp(2.2rem, 4.5vw, 3.5rem); font-weight: 800; line-height: 1.15; margin-bottom: 1.2rem; background: linear-gradient(135deg, #ffffff 30%, #93c5fd 70%, #6366f1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            p.subtitle { font-size: 1.1rem; color: var(--text-muted); max-width: 700px; margin: 0 auto 2rem; line-height: 1.6; }

            .status-box { background: rgba(0, 0, 0, 0.7); border: 1px solid var(--border); border-radius: 10px; padding: 1rem 1.5rem; display: inline-flex; align-items: center; gap: 2rem; margin-bottom: 2rem; font-size: 0.85rem; box-shadow: inset 0 0 15px rgba(0,0,0,0.9); flex-wrap: wrap; justify-content: center; }
            .status-item { display: flex; align-items: center; gap: 0.6rem; }
            .dot { width: 9px; height: 9px; background-color: var(--success); border-radius: 50%; box-shadow: 0 0 10px var(--success); animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

            /* Terms Compliance Box */
            .compliance-box { background: rgba(11, 15, 25, 0.5); border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1.25rem; margin: 0 auto 2.5rem; max-width: 700px; display: flex; align-items: flex-start; gap: 0.75rem; text-align: left; backdrop-filter: blur(8px); }
            .compliance-box input[type="checkbox"] { accent-color: var(--accent); margin-top: 0.2rem; cursor: pointer; }
            .compliance-box label { font-size: 0.75rem; color: var(--text-muted); line-height: 1.4; cursor: pointer; }
            .compliance-box label span { color: #818cf8; font-weight: bold; }

            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; text-align: left; }
            .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 1.8rem; backdrop-filter: blur(10px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); position: relative; overflow: hidden; }
            .card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, var(--accent), transparent); opacity: 0; transition: opacity 0.3s; }
            .card:hover { transform: translateY(-5px); border-color: var(--accent); box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.3); }
            .card:hover::before { opacity: 1; }
            .card h3 { font-size: 1.1rem; color: #fff; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }
            .card p { font-size: 0.88rem; color: var(--text-muted); line-height: 1.6; }

            .footer { margin-top: 4rem; font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 2rem; display: flex; justify-content: space-between; align-items: center; width: 100%; flex-wrap: wrap; gap: 1rem; }
        #bg-globe {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: -1;
    pointer-events: none;
    opacity: 0.35;
}
        </style>
    </head>
    <body>
<canvas id="bg-globe"></canvas>
    
    
# --- SECURITY HEADERS & CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.middleware("http")
async def inject_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# --- GLOBAL UNHANDLED EXCEPTION ISOLATOR ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Internal Security Intercept: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An internal execution exception occurred. Request isolated safely."}
    )

# --- AUTHENTICATION & Cryptomus HMAC VERIFICATION ---
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(header_key: str = Security(api_key_header)):
    if not header_key or not hmac.compare_digest(header_key, MASTER_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API authorization token."
        )
    return header_key

def verify_webhook_signature(payload: dict, received_sign: str) -> bool:
    try:
        data = {k: v for k, v in payload.items() if k != "sign"}
        sorted_data = dict(sorted(data.items()))
        serialized = str(sorted_data).encode('utf-8')
        expected_sign = hmac.new(
            CRYPTOMUS_PAYMENT_KEY.encode('utf-8'),
            serialized,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sign, received_sign)
    except Exception:
        return False

# --- DEDICATED CRYPTOMUS FILE VERIFICATION ROUTES ---
@app.get("/add14096.html", response_class=PlainTextResponse)
@app.get("/cryptomus_add14096.html", response_class=PlainTextResponse)
def cryptomus_verification():
    return "Cryptomus=add14096"

    
# --- ROOT HEALTH CHECK ---
# --- ADVANCED IN-CODE GRAPHICAL SAAS LANDING PAGE & MODERATION ROUTE ---
@app.get("/", response_class=HTMLResponse)
def health_check():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Cryptomus Verification Meta-Tags -->
    <meta name="cryptomus" content="add14096-ff52-49d1-b188-a538aa30dd74" />
    <meta name="cryptomus" content="add14096" />
    <title>Nexus Protocol | Enterprise Stealth & Web Extraction Infrastructure</title>
    
    <style>
        :root {
            --bg-dark: #090d16;
            --panel-bg: rgba(30, 41, 59, 0.7);
            --border-color: #334155;
            --accent-blue: #38bdf8;
            --accent-glow: #0284c7;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        
        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            overflow-x: hidden;
            position: relative;
            min-height: 100vh;
        }

        /* Pure CSS Dynamic Canvas Backdrop */
        #bg-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
            opacity: 0.25;
            background: radial-gradient(circle at 50% 50%, rgba(2, 132, 199, 0.15), transparent 60%);
        }

        .content-layer {
            position: relative;
            z-index: 10;
            max-width: 1100px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* Graphical Glassmorphism Navigation Bar */
        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 18px 30px;
            background: var(--panel-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        .logo-text {
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--accent-blue);
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(16, 185, 129, 0.1);
            color: #10b981;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .dot { width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Hero Graphic Header */
        .hero {
            text-align: center;
            margin: 60px 0 40px 0;
        }

        .hero h1 {
            font-size: 3.2rem;
            font-weight: 900;
            line-height: 1.15;
            background: linear-gradient(135deg, #ffffff 0%, var(--accent-blue) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
        }

        .hero p {
            font-size: 1.15rem;
            color: var(--text-muted);
            max-width: 700px;
            margin: 0 auto 30px auto;
        }

        /* Grid Cards for Micro-Token Plans */
        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        .card {
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 35px 25px;
            text-align: center;
            position: relative;
            transition: all 0.3s ease;
            backdrop-filter: blur(8px);
        }

        .card:hover {
            transform: translateY(-5px);
            border-color: var(--accent-blue);
            box-shadow: 0 12px 30px rgba(2, 132, 199, 0.2);
        }

        .card.popular {
            border: 2px solid var(--accent-blue);
            background: rgba(30, 41, 59, 0.85);
        }

        .badge-popular {
            position: absolute;
            top: -12px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--accent-glow);
            color: #fff;
            padding: 4px 14px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .price-tag {
            font-size: 2.8rem;
            font-weight: 800;
            color: var(--text-main);
            margin: 15px 0 5px 0;
        }

        .credits-val {
            font-size: 1.1rem;
            color: var(--accent-blue);
            font-weight: 700;
            margin-bottom: 20px;
        }

        .btn-buy {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 10px;
            background: var(--accent-glow);
            color: #fff;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .btn-buy:hover { background: #0369a1; }

        /* API Console Simulation Area */
        .console-area {
            background: #020617;
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 25px;
            margin-top: 50px;
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.8);
        }

        .console-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
        }

        .circle { width: 12px; height: 12px; border-radius: 50%; }
        .red { background: #ef4444; }
        .yellow { background: #f59e0b; }
        .green { background: #10b981; }

        pre {
            color: #38bdf8;
            font-family: "Courier New", Courier, monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            white-space: pre-wrap;
        }

        footer {
            text-align: center;
            margin-top: 60px;
            color: var(--text-muted);
            font-size: 0.85rem;
            border-top: 1px solid var(--border-color);
            padding-top: 20px;
        }
    </style>
</head>
<body>
    <div id="bg-canvas"></div>

    <div class="content-layer">
        <nav>
            <div class="logo-text">⚡ NEXUS PROTOCOL</div>
            <div class="status-badge"><span class="dot"></span> Engine Online v6.3</div>
        </nav>

        <section class="hero">
            <h1>Autonomous Anti-Bot & Stealth Infrastructure</h1>
            <p>Zero-maintenance API proxy layer for AI agents, web extraction pipelines, and automated zero-shot structured JSON parsers.</p>
        </section>

        <div class="pricing-grid">
    <!-- $1 Tier -->
    <div class="card">
        <h3>Flash Pack</h3>
        <div class="price-tag">$1</div>
        <div class="credits-val">5,000 Credits</div>
        <p style="color: var(--text-dim);">Ideal for testing & micro-tasks</p>
        <button class="btn-buy" onclick="initiateCheckout(1.00)">Get 5,000 Credits</button>
    </div>

    <!-- $10 Tier -->
    <div class="card popular">
        <div class="badge-popular">MOST POPULAR</div>
        <h3>Developer Pro</h3>
        <div class="price-tag">$10</div>
        <div class="credits-val">55,000 Credits</div>
        <p style="color: var(--text-dim);">Best balance for scaling apps</p>
        <button class="btn-buy" onclick="initiateCheckout(10.00)">Get 55,000 Credits</button>
    </div>

    <!-- $29 Tier -->
    <div class="card">
        <h3>Agency Scale</h3>
        <div class="price-tag">$29</div>
        <div class="credits-val">100,000 Credits</div>
        <p style="color: var(--text-dim);">Maximum volume & performance</p>
        <button class="btn-buy" onclick="initiateCheckout(29.00)">Get 1 Lakh Credits</button>
    </div>
</div>

        <div class="console-area">
            <div class="console-header">
                <span class="circle red"></span>
                <span class="circle yellow"></span>
                <span class="circle green"></span>
                <span style="color: var(--text-muted); font-size: 0.8rem; margin-left: 10px;">SDK Endpoint Quickstart</span>
            </div>
            <pre><code>curl -X POST "https://nexus-protocol-api.onrender.com/api/v1/scrape" \
  -H "x-api-key: sk_live_nexus_2026" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://target-website.com/data"}'</code></pre>
        </div>

        <footer>
            &copy; 2026 Nexus Protocol Inc. All rights reserved. | Cryptomus Merchant Verification Node Active
        </footer>
    </div>

    <script>
       (function initFuturisticGlobe() {
    const canvas = document.getElementById('bg-globe');
    if (!canvas) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 220;

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const particleCount = 2800;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const radius = 95;

    for (let i = 0; i < particleCount; i++) {
        const phi = Math.acos(-1 + (2 * i) / particleCount);
        const theta = Math.sqrt(particleCount * Math.PI) * phi;

        positions[i * 3] = radius * Math.cos(theta) * Math.sin(phi);
        positions[i * 3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
        positions[i * 3 + 2] = radius * Math.cos(phi);
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
        color: 0x6366f1,
        size: 1.25,
        transparent: true,
        opacity: 0.85
    });

    const globeParticles = new THREE.Points(geometry, material);
    scene.add(globeParticles);

    const wireframeGeo = new THREE.IcosahedronGeometry(94, 3);
    const wireframeMat = new THREE.MeshBasicMaterial({
        color: 0x4f46e5,
        wireframe: true,
        transparent: true,
        opacity: 0.15
    });
    const wireframeMesh = new THREE.Mesh(wireframeGeo, wireframeMat);
    scene.add(wireframeMesh);

    const ringGeo = new THREE.RingGeometry(115, 116, 64);
    const ringMat = new THREE.MeshBasicMaterial({
        color: 0x818cf8,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.3
    });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 3;
    scene.add(ringMesh);

    let mouseX = 0, mouseY = 0;
    window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX - window.innerWidth / 2) * 0.0003;
        mouseY = (e.clientY - window.innerHeight / 2) * 0.0003;
    });

    function animate() {
        requestAnimationFrame(animate);

        globeParticles.rotation.y += 0.0015;
        wireframeMesh.rotation.y += 0.0015;
        ringMesh.rotation.z -= 0.0005;

        globeParticles.rotation.x += (mouseY - globeParticles.rotation.x) * 0.05;
        globeParticles.rotation.y += (mouseX - globeParticles.rotation.y) * 0.05;

        renderer.render(scene, camera);
    }

    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
})();

        async function initiateCheckout(amountVal, planId) {
            alert('Initializing Cryptomus payment node for $' + amountVal + ' USD...');
            try {
                const response = await fetch('/create-checkout', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_email: 'user_123@nexus.io', amount: amountVal, plan_id: planId })
                });
                const data = await response.json();
                if (data.checkout_url) {
                    window.location.href = data.checkout_url;
                }
            } catch (err) {
                console.log('Checkout initialisation mode standard redirect.');
            }
        }
    </script>
</body>
</html>
"""

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

PROCESSED_ORDERS = set()

@app.post("/webhooks/cryptomus")
async def cryptomus_webhook(request: Request):
    payload = await request.json()
    received_sign = payload.get("sign")
    
    if not received_sign or not verify_webhook_signature(payload, received_sign):
        raise HTTPException(status_code=401, detail="Invalid signature")
        
    order_id = payload.get("order_id", "")
    payment_status = payload.get("status", "")
    amount = float(payload.get("amount", 0))

    if order_id in PROCESSED_ORDERS:
        return {"status": "ignored", "reason": "already_processed"}

    if payment_status in ["paid", "paid_over"]:
        # Calculate dynamic credit allocation based on dollar amount
        credits_to_add = 0
        if amount >= 29.00:
            credits_to_add = 100000
        elif amount >= 10.00:
            credits_to_add = 55000
        elif amount >= 1.00:
            credits_to_add = 5000

        # Provision credits in Supabase or local state
        PROCESSED_ORDERS.add(order_id)
        return {"status": "success", "credited": credits_to_add, "order_id": order_id}

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
        "html": response.text[:1000] if not payload.extract_markdown else None,
    }

    if payload.schema and response.text:
        result["extracted_data"] = extract_structured_json(response.text, payload.schema)

    return result
    
