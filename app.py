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

# --- AI Anomaly Analyzer ---
def get_ai_analysis(price: float, change: float):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a high-frequency trading AI. A stock just spiked abnormally. In exactly ONE short sentence, speculate a realistic market reason for the spike (e.g., earnings, FDA approval, tweet). Do not use hashtags."},
                {"role": "user", "content": f"Stock price just moved {change}% to ${price}. Why?"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "AI analysis unavailable at the moment."

# --- WebSocket Manager ---
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

# --- Simulated Data Stream & Anomaly Detection ---
async def market_data_generator():
    base_price = 150.00
    while True:
        # 95% chance of normal movement, 5% chance of anomaly
        is_anomaly = random.random() < 0.05
        
        if is_anomaly:
            change = random.uniform(3.0, 8.0) # 3% to 8% spike
            price = base_price * (1 + (change / 100))
            event_type = "ANOMALY DETECTED"
            # Call AI for explanation
            reason = get_ai_analysis(price, change)
        else:
            change = random.uniform(-0.5, 0.5) # normal noise
            price = base_price * (1 + (change / 100))
            event_type = "NORMAL"
            reason = ""

        base_price = price # update price for next tick

        data = {
            "price": round(price, 2),
            "change_percent": round(change, 2),
            "type": event_type,
            "reason": reason
        }

        # Broadcast to all connected websockets
        for connection in manager.active_connections:
            await manager.send_personal_message(json.dumps(data), connection)
            
        await asyncio.sleep(2) # New tick every 2 seconds

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(market_data_generator())

# --- WebSocket Endpoint ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open, we are pushing data to client
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Modern Frontend Dashboard ---
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
    </head>
    <body class="bg-gray-900 text-white flex items-center justify-center min-h-screen p-4">
        <div class="w-full max-w-3xl">
            <div class="bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-700">
                <h1 class="text-3xl font-bold text-center mb-2 text-indigo-400">Live AI Market Monitor</h1>
                <p class="text-center text-gray-400 mb-8">Streaming simulated ticks. AI watches for anomalies.</p>
                
                <div class="bg-gray-900 p-6 rounded-xl mb-6 border border-gray-700 text-center">
                    <p class="text-gray-500 text-sm uppercase tracking-wider mb-2">Current Price</p>
                    <h2 id="price" class="text-5xl font-mono font-bold text-green-400">$0.00</h2>
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
            const ws = new WebSocket("ws://127.0.0.1:8000/ws");
            const priceEl = document.getElementById('price');
            const changeEl = document.getElementById('change');
            const alertsEl = document.getElementById('alerts');

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                priceEl.innerText = '$' + data.price.toFixed(2);
                changeEl.innerText = (data.change_percent > 0 ? '+' : '') + data.change_percent.toFixed(2) + '%';
                
                if(data.change_percent > 0) {
                    priceEl.classList.remove('text-red-400');
                    priceEl.classList.add('text-green-400');
                } else {
                    priceEl.classList.remove('text-green-400');
                    priceEl.classList.add('text-red-400');
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