# PulseAI 🩺

**PulseAI** is an AI-powered health assistant chatbot built with Flask and Google Gemini API. It provides personalized health and diet recommendations based on Indian cuisine.

## Features
- 🤖 AI health recommendations for any disease/condition
- 🍛 Indian diet plan in table format (dal, roti, khichdi, etc.)
- ⚡ Real-time streaming responses with typewriter effect
- 💬 Follow-up conversations — chatbot remembers previous messages
- 📱 Responsive, clean UI

## Tech Stack
- **Backend:** Python, Flask, Google Gemini API
- **Frontend:** HTML, CSS, Tailwind CSS, JavaScript
- **Streaming:** Server-Sent Events (SSE)

## Setup

1. Clone the repo:
```bash
git clone https://github.com/mohammadalihaji/PulseAi.git
cd PulseAi/PulseAi
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```
API_KEY=your_gemini_api_key_here
```

4. Run the app:
```bash
python app.py
```

5. Open `http://localhost:5000` in your browser.

## Deployment
This app is deployed on [Render](https://render.com). Set the `API_KEY` environment variable in Render's dashboard.

## License
MIT
