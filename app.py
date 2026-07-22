import os
import asyncio
import random
import json
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI(title="AI Streaming Anomaly Detector")

def get_ai_analysis(price: float, change: float):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a high-frequency trading AI. A stock just spiked abnormally. In exactly ONE short sentence, speculate a realistic market reason for the spike (e.g., earnings, FDA approval, tweet). Do not use hashtags."},
                {"role": "user", "content": f"Stock price just moved {change}% to ${price}. Why?"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "AI analysis unavailable at the moment."

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

async def market_data_generator():
    base_price = 150.00
    tick_count = 0
    
    while True:
        tick_count += 1
        
        # Force an anomaly on tick 5 (5 seconds after a user connects) so they see it instantly
        if tick_count in [5, 6, 7]:
            is_anomaly = True
        else:
            # Otherwise, 15% chance of anomaly (keeps the feed active)
            is_anomaly = random.random() < 0.15
            
        if is_anomaly:
            change = random.uniform(3.0, 8.0) # 3% to 8% spike
            price = base_price * (1 + (change / 100))
            event_type = "ANOMALY DETECTED"
            reason = get_ai_analysis(price, change)
        else:
            # Normal small ticks every second
            change = random.uniform(-0.4, 0.4) 
            price = base_price * (1 + (change / 100))
            event_type = "NORMAL"
            reason = ""

        base_price = price

        data = {
            "price": round(price, 2),
            "change_percent": round(change, 2),
            "type": event_type,
            "reason": reason
        }

        for connection in manager.active_connections:
            await manager.send_personal_message(json.dumps(data), connection)
            
        # Tick every 1 second instead of 2 for a live feel
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(market_data_generator())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Anomaly Detector</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .flash-green { animation: flash-green 0.5s ease-out; }
            .flash-red { animation: flash-red 0.5s ease-out; }
            @keyframes flash-green { 0% { background-color: rgba(34, 197, 94, 0.3); } 100% { background-color: transparent; } }
            @keyframes flash-red { 0% { background-color: rgba(239, 68, 68, 0.3); } 100% { background-color: transparent; } }
        </style>
    </head>
    <body class="bg-gray-900 text-white flex items-center justify-center min-h-screen p-4">
        <div class="w-full max-w-3xl">
            <div class="bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-700">
                <div class="flex justify-between items-center mb-2">
                    <h1 class="text-3xl font-bold text-indigo-400">Live AI Market Monitor</h1>
                    <div id="status-badge" class="text-xs font-bold bg-red-900/50 text-red-400 px-3 py-1 rounded-full border border-red-800">🔴 Connecting...</div>
                </div>
                <p class="text-center text-gray-400 mb-8">Streaming simulated ticks. AI watches for anomalies.</p>
                
                <div id="price-card" class="bg-gray-900 p-6 rounded-xl mb-6 border border-gray-700 text-center transition-colors duration-300">
                    <p class="text-gray-500 text-sm uppercase tracking-wider mb-2">Current Price</p>
                    <h2 id="price" class="text-5xl font-mono font-bold text-green-400">$150.00</h2>
                    <p id="change" class="text-xl mt-2 text-gray-400">0.00%</p>
                </div>

                <div class="bg-gray-900 p-6 rounded-xl border border-gray-700">
                    <h3 class="text-xl font-bold mb-4 text-indigo-400">AI Alert Feed</h3>
                    <div id="alerts" class="space-y-3 max-h-60 overflow-y-auto">
                        <p class="text-gray-500">Waiting for market anomalies...</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const priceEl = document.getElementById('price');
            const changeEl = document.getElementById('change');
            const alertsEl = document.getElementById('alerts');
            const priceCard = document.getElementById('price-card');
            const statusBadge = document.getElementById('status-badge');

            // Dynamically determine WebSocket protocol (ws vs wss)
            const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
            const wsUrl = `${wsProtocol}${window.location.host}/ws`;
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                statusBadge.innerText = '🟢 Connected';
                statusBadge.className = 'text-xs font-bold bg-green-900/50 text-green-400 px-3 py-1 rounded-full border border-green-800';
            };

            ws.onclose = () => {
                statusBadge.innerText = '🔴 Disconnected';
                statusBadge.className = 'text-xs font-bold bg-red-900/50 text-red-400 px-3 py-1 rounded-full border border-red-800';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                const oldPrice = parseFloat(priceEl.innerText.replace('$', ''));
                const newPrice = data.price;
                
                priceEl.innerText = '$' + newPrice.toFixed(2);
                changeEl.innerText = (data.change_percent > 0 ? '+' : '') + data.change_percent.toFixed(2) + '%';
                
                // Flash effect
                priceCard.classList.remove('flash-green', 'flash-red');
                void priceCard.offsetWidth; // Trigger reflow to restart animation
                if (newPrice > oldPrice) {
                    priceEl.classList.remove('text-red-400');
                    priceEl.classList.add('text-green-400');
                    if (data.type !== 'ANOMALY DETECTED') priceCard.classList.add('flash-green');
                } else if (newPrice < oldPrice) {
                    priceEl.classList.remove('text-green-400');
                    priceEl.classList.add('text-red-400');
                    if (data.type !== 'ANOMALY DETECTED') priceCard.classList.add('flash-red');
                }

                if(data.type === 'ANOMALY DETECTED') {
                    const alertHtml = `
                        <div class="bg-red-900/50 border border-red-500 p-4 rounded-lg animate-pulse">
                            <p class="text-red-300 font-bold">⚠️ ANOMALY: ${data.change_percent.toFixed(2)}% Spike</p>
                            <p class="text-gray-300 text-sm mt-1">🤖 AI: ${data.reason}</p>
                        </div>
                    `;
                    alertsEl.innerHTML = alertHtml + alertsEl.innerHTML;
                }
            };
        </script>
    </body>
    </html>
    """