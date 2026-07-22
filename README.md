📈 AI Streaming Anomaly Detector
A real-time full-stack dashboard that streams simulated financial market data via WebSockets. Instead of just displaying raw numbers, an integrated AI agent monitors the live data stream. If a sudden price spike (anomaly) is detected, the AI instantly generates a 1-sentence speculative market reason for the event and pushes it to the frontend alert feed.

🧠 How It Works
- Data Stream: A FastAPI backend generates a simulated stock price every 2 seconds, with a 5% chance of triggering a massive price spike (anomaly).
- WebSocket Bridge: The backend maintains a live WebSocket connection with the frontend, pushing price updates in real-time.
- AI Anomaly Detection: When an anomaly occurs, the backend instantly calls the Groq LLM API, passing the price change data. The AI generates a realistic market hypothesis (e.g., "FDA approval rumors", "Viral CEO tweet").
- Live UI: The frontend updates the price ticker green/red dynamically and flashes a red alert card with the AI's reasoning.

🛠 Tech Stack
- Backend: Python, FastAPI, Uvicorn, Asyncio
- AI/LLM: Groq (Llama-3.1-8b-instant) via the OpenAI Python SDK
- Frontend: HTML, Tailwind CSS, Vanilla JS
- Architecture: WebSockets, Real-Time Data Streaming, Event-Driven AI

💻 Engineering Highlights
- Real-Time WebSocket Streaming: Implemented a persistent WebSocket connection using asyncio to stream simulated market ticks to the frontend every second without requiring client-side polling.
- Event-Driven AI Hooks: The backend monitors a volatility threshold. When breached, it triggers an async hook to call the Groq LLM API, generating a speculative market hypothesis and pushing it to the frontend alert feed instantly.
- Frontend UI State Management: Managed complex DOM updates, including dynamic price flashing (green/red) based on tick direction, and auto-scrolling alert feeds for a Bloomberg-terminal-like user experience.
