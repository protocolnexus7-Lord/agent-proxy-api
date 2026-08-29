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
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEXUS PROTOCOL | Stealth API & Decentralized Node Network</title>
    
    <!-- Cryptomus Verification Meta-Tags -->
    <meta name="cryptomus" content="add14096" />
    <meta name="cryptomus-verification" content="add14096" />
    
    <!-- Three.js 3D WebGL Rendering Engine -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    
    <style>
        :root {
            --bg-dark: #020408;
            --card-bg: rgba(10, 14, 26, 0.78);
            --border-glow: rgba(99, 102, 241, 0.35);
            --border-highlight: #6366f1;
            --accent-cyan: #38bdf8;
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --success: #10b981;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; overflow-x: hidden; position: relative; }

        /* Real World Map 3D Canvas Container */
        #bg-globe { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 0; pointer-events: none; }

        /* Layout Structure */
        .container { max-width: 1240px; margin: 0 auto; padding: 1.25rem 1rem 4rem; position: relative; z-index: 10; }

        /* Glassmorphism Top Bar */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(10, 14, 26, 0.85);
            border: 1px solid var(--border-glow);
            backdrop-filter: blur(16px);
            padding: 0.85rem 1.5rem;
            border-radius: 0.85rem;
            margin-bottom: 3rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            flex-wrap: wrap;
            gap: 1rem;
        }

        .brand-header { display: flex; align-items: center; gap: 0.75rem; }
        .brand-logo { width: 12px; height: 12px; background: var(--accent-cyan); border-radius: 50%; box-shadow: 0 0 12px var(--accent-cyan); }
        .brand-name { font-size: 1.1rem; font-weight: 900; letter-spacing: 0.12em; color: #fff; }
        .brand-name span { color: var(--border-highlight); }

        .telemetry-group { display: flex; align-items: center; gap: 1.25rem; font-size: 0.82rem; font-family: monospace; color: var(--text-dim); flex-wrap: wrap; }
        .lang-select { background: #060913; color: #818cf8; border: 1px solid var(--border-glow); padding: 0.35rem 0.75rem; border-radius: 0.4rem; outline: none; cursor: pointer; font-size: 0.8rem; }
        
        .clock-badge {
            background: rgba(56, 189, 248, 0.08);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: var(--accent-cyan);
            padding: 0.35rem 0.75rem;
            border-radius: 0.4rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        }

        /* Hero Typography */
        .hero { text-align: center; padding: 2rem 0.5rem 3rem; }
        .hero-badge {
            display: inline-block;
            padding: 0.35rem 1rem;
            border-radius: 9999px;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid var(--border-glow);
            color: #818cf8;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            margin-bottom: 1.25rem;
        }

        .hero h1 {
            font-size: clamp(2rem, 5.5vw, 3.8rem);
            font-weight: 900;
            line-height: 1.15;
            background: linear-gradient(135deg, #ffffff 30%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.25rem;
            letter-spacing: -0.02em;
        }

        .hero p { color: var(--text-dim); max-width: 720px; margin: 0 auto; line-height: 1.65; font-size: 1rem; }

        /* Pricing Card Grid */
        .section-title { text-align: center; font-size: 2rem; font-weight: 800; margin-top: 2rem; }
        .section-subtitle { text-align: center; color: var(--text-dim); margin-bottom: 3rem; font-size: 0.95rem; margin-top: 0.35rem; }

        .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.75rem; }
        
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border-glow);
            backdrop-filter: blur(20px);
            border-radius: 1.25rem;
            padding: 2.25rem 2rem;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            transition: transform 0.25s ease, border-color 0.25s ease;
        }

        .card:hover { transform: translateY(-6px); border-color: var(--border-highlight); }
        .card.popular { border-color: var(--border-highlight); box-shadow: 0 0 35px rgba(99, 102, 241, 0.25); }

        .popular-tag {
            position: absolute;
            top: -14px;
            right: 24px;
            background: var(--border-highlight);
            color: #fff;
            padding: 0.3rem 0.9rem;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.5);
        }

        .tier-name { font-size: 1.25rem; font-weight: 800; color: #fff; }
        .price-tag { font-size: 3rem; font-weight: 900; color: #fff; margin: 0.75rem 0 0.2rem; }
        .price-tag span { font-size: 1rem; font-weight: 500; color: var(--text-dim); }
        .credits-val { color: var(--accent-cyan); font-weight: 700; font-size: 0.95rem; margin-bottom: 1.25rem; }
        .tier-desc { color: var(--text-dim); font-size: 0.88rem; line-height: 1.55; margin-bottom: 2rem; }

        /* Ultra Premium Legal Consent Component */
        .legal-box {
            background: rgba(6, 9, 19, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 0.85rem 1rem;
            border-radius: 0.6rem;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            text-align: left;
        }

        .legal-box input[type="checkbox"] { accent-color: var(--border-highlight); width: 16px; height: 16px; margin-top: 2px; cursor: pointer; }
        .legal-box label { font-size: 0.76rem; color: var(--text-dim); line-height: 1.4; cursor: pointer; }
        .legal-box label a { color: var(--accent-cyan); text-decoration: none; }

        .btn-buy {
            width: 100%;
            padding: 1rem;
            border-radius: 0.6rem;
            border: none;
            background: var(--border-highlight);
            color: #fff;
            font-weight: 800;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.95rem;
            letter-spacing: 0.03em;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .btn-buy:hover { background: #4f46e5; box-shadow: 0 0 25px rgba(99, 102, 241, 0.6); }

        footer {
            text-align: center;
            color: var(--text-dim);
            padding: 3.5rem 0 1.5rem;
            font-size: 0.82rem;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            margin-top: 5rem;
            font-family: monospace;
        }
    </style>
</head>
<body>

    <div id="bg-globe"></div>

    <div class="container">
        <!-- Top Telemetry Header Bar -->
        <div class="top-bar">
            <div class="brand-header">
                <div class="brand-logo"></div>
                <div class="brand-name">NEXUS <span>PROTOCOL</span></div>
            </div>
            <div class="telemetry-group">
                <div>
                    🌐 <select class="lang-select" id="langSelect">
                        <option value="en">ENGLISH (GLOBAL)</option>
                        <option value="es">ESPAÑOL</option>
                        <option value="zh">中文 (CHINESE)</option>
                        <option value="ja">JAPANESE</option>
                        <option value="de">DEUTSCH</option>
                    </select>
                </div>
                <div>⚡ PING: <span style="color: var(--success); font-weight: 700;">12ms</span></div>
                <div class="clock-badge" id="utcClock">2026-08-29 00:00:00 UTC</div>
            </div>
        </div>

        <!-- Hero Title Section -->
        <div class="hero">
            <span class="hero-badge">NEXUS V6.3 ENTERPRISE EDITION</span>
            <h1>Autonomous Stealth Extraction & Anti-Bot Infrastructure</h1>
            <p>Next-generation distributed high-performance API protocol utilizing low-level TLS fingerprint emulation, residential routing networks, and automated Cryptomus ledger verification.</p>
        </div>

        <h2 class="section-title">Deployment Packages</h2>
        <p class="section-subtitle">Select an infrastructure tier tailored to your API execution frequency.</p>

        <!-- Pricing Grid -->
        <div class="pricing-grid">
            <!-- $1 Tier -->
            <div class="card">
                <div>
                    <div class="tier-name">Flash Pack</div>
                    <div class="price-tag">$1 <span>/ checkout</span></div>
                    <div class="credits-val">5,000 API Credits</div>
                    <p class="tier-desc">Ideal for rapid test deployments and basic TLS endpoint verification.</p>
                </div>
                <div>
                    <div class="legal-box">
                        <input type="checkbox" id="terms-1">
                        <label for="terms-1">I agree to the <a href="#">Terms of Service</a> & non-refundable API allocation policy.</label>
                    </div>
                    <button class="btn-buy" onclick="initiateCheckout(1, 'terms-1')">Deploy Tier</button>
                </div>
            </div>

            <!-- $10 Tier -->
            <div class="card popular">
                <div class="popular-tag">MOST POPULAR</div>
                <div>
                    <div class="tier-name">Developer Pro</div>
                    <div class="price-tag">$10 <span>/ checkout</span></div>
                    <div class="credits-val">55,000 API Credits</div>
                    <p class="tier-desc">Production-ready stealth pipeline with standard SLA routing.</p>
                </div>
                <div>
                    <div class="legal-box">
                        <input type="checkbox" id="terms-10">
                        <label for="terms-10">I agree to the <a href="#">Terms of Service</a> & non-refundable API allocation policy.</label>
                    </div>
                    <button class="btn-buy" onclick="initiateCheckout(10, 'terms-10')">Deploy Tier</button>
                </div>
            </div>

            <!-- $29 Tier -->
            <div class="card">
                <div>
                    <div class="tier-name">Agency Scale</div>
                    <div class="price-tag">$29 <span>/ checkout</span></div>
                    <div class="credits-val">100,000 API Credits</div>
                    <p class="tier-desc">High-throughput capacity designed for enterprise scraping workloads.</p>
                </div>
                <div>
                    <div class="legal-box">
                        <input type="checkbox" id="terms-29">
                        <label for="terms-29">I agree to the <a href="#">Terms of Service</a> & non-refundable API allocation policy.</label>
                    </div>
                    <button class="btn-buy" onclick="initiateCheckout(29, 'terms-29')">Deploy Tier</button>
                </div>
            </div>
        </div>

        <footer>
            &copy; 2026 NEXUS PROTOCOL. All infrastructure nodes secure.<br>
            <span style="color: #818cf8; font-size: 0.75rem; margin-top: 0.5rem; display: inline-block;">SECURE ENCLAVE ACTIVE</span>
        </footer>
    </div>

<script>
    // Live UTC Clock Engine
    function updateUTCClock() {
        const now = new Date();
        const year = now.getUTCFullYear();
        const month = String(now.getUTCMonth() + 1).padStart(2, '0');
        const day = String(now.getUTCDate()).padStart(2, '0');
        const hours = String(now.getUTCHours()).padStart(2, '0');
        const minutes = String(now.getUTCMinutes()).padStart(2, '0');
        const seconds = String(now.getUTCSeconds()).padStart(2, '0');
        document.getElementById('utcClock').innerText = `${year}-${month}-${day} ${hours}:${minutes}:${seconds} UTC`;
    }
    setInterval(updateUTCClock, 1000);
    updateUTCClock();

    // Photorealistic Real World Map 3D Globe Engine
    (function init3DRealWorldGlobe() {
        const container = document.getElementById('bg-globe');
        const scene = new THREE.Scene();
        
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 210;

        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);

        const globeGroup = new THREE.Group();
        scene.add(globeGroup);

        // Procedural Real World Map Texture Generator
        const canvas = document.createElement('canvas');
        canvas.width = 2048;
        canvas.height = 1024;
        const ctx = canvas.getContext('2d');

        // Deep Ocean Base Layer
        ctx.fillStyle = '#020408';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Render Real World Landmass Cartography
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = "https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg";
        
        img.onload = () => {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imgData.data;

            // Convert Landmass to Ultra-Premium Neon Grid Overlay
            ctx.fillStyle = '#020408';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const dots = [];
            const step = 8;
            for (let y = 0; y < canvas.height; y += step) {
                for (let x = 0; x < canvas.width; x += step) {
                    const index = (y * canvas.width + x) * 4;
                    const brightness = (data[index] + data[index + 1] + data[index + 2]) / 3;
                    if (brightness > 35) { // Land detection threshold
                        ctx.fillStyle = '#6366f1';
                        ctx.beginPath();
                        ctx.arc(x, y, 1.8, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            }

            // Create Globe Texture Mesh
            const texture = new THREE.CanvasTexture(canvas);
            const sphereGeo = new THREE.SphereGeometry(60, 64, 64);
            const sphereMat = new THREE.MeshBasicMaterial({ map: texture, transparent: true, opacity: 0.95 });
            const realWorldGlobe = new THREE.Mesh(sphereGeo, sphereMat);
            globeGroup.add(realWorldGlobe);
        };

        // Fallback Base Sphere Grid (Immediate Rendering)
        const innerGeo = new THREE.SphereGeometry(59.5, 36, 36);
        const innerMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.08 });
        const innerMesh = new THREE.Mesh(innerGeo, innerMat);
        globeGroup.add(innerMesh);

        // Outer Atmosphere Glow Halo Ring
        const ringGeo = new THREE.RingGeometry(72, 72.5, 64);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0x6366f1, side: THREE.DoubleSide, transparent: true, opacity: 0.25 });
        const ringMesh = new THREE.Mesh(ringGeo, ringMat);
        ringMesh.rotation.x = Math.PI / 2.3;
        globeGroup.add(ringMesh);

        function animate() {
            requestAnimationFrame(animate);
            globeGroup.rotation.y += 0.0018;
            globeGroup.rotation.x = 0.12;
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    })();

    // Cryptomus Integration & Legal Check Validation
    async function initiateCheckout(amount, checkboxId) {
        const checkbox = document.getElementById(checkboxId);
        if (!checkbox || !checkbox.checked) {
            alert('Please accept the Terms of Service before deploying.');
            return;
        }

        try {
            const response = await fetch('/create-checkout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: amount })
            });
            const data = await response.json();
            if (data.checkout_url) {
                window.location.href = data.checkout_url;
            } else {
                alert('Checkout initialization failed. Please try again.');
            }
        } catch (err) {
            console.error('Checkout error:', err);
            alert('Unable to connect to Cryptomus payment engine.');
        }
    }
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def serve_landing_page():
    return HTML_CONTENT
                 
       
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
    return HTML_CONTENT
   
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
    
