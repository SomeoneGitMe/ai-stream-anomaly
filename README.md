📈 AI Streaming Anomaly Detector
A real-time full-stack dashboard that streams simulated financial market data via WebSockets. Instead of just displaying raw numbers, an integrated AI agent monitors the live data stream. If a sudden price spike (anomaly) is detected, the AI instantly generates a 1-sentence speculative market reason for the event and pushes it to the frontend alert feed.

🧠 How It Works
Data Stream: A FastAPI backend generates a simulated stock price every 2 seconds, with a 5% chance of triggering a massive price spike (anomaly).
WebSocket Bridge: The backend maintains a live WebSocket connection with the frontend, pushing price updates in real-time.
AI Anomaly Detection: When an anomaly occurs, the backend instantly calls the Groq LLM API, passing the price change data. The AI generates a realistic market hypothesis (e.g., "FDA approval rumors", "Viral CEO tweet").
Live UI: The frontend updates the price ticker green/red dynamically and flashes a red alert card with the AI's reasoning.

🛠 Tech Stack
Backend: Python, FastAPI, Uvicorn, Asyncio
AI/LLM: Groq (Llama-3.1-8b-instant) via the OpenAI Python SDK
Frontend: HTML, Tailwind CSS, Vanilla JS
Architecture: WebSockets, Real-Time Data Streaming, Event-Driven AI

🚀 Getting Started
1. Clone the repository
git clone https://github.com/SomeoneGitMe/ai-stream-anomaly.gitcd ai-stream-anomaly
2. Install dependencies
bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
3. Set up environment variables
Create a .env file in the root directory and add your Groq API key:

text

GROQ_API_KEY=your_groq_api_key_here
4. Run the server
bash

uvicorn app:app --reload
5. View the Dashboard
Navigate to http://127.0.0.1:8000 in your browser. Watch the price ticker update. Within 30-60 seconds, you will see a red anomaly alert flash on the screen with the AI's real-time analysis.