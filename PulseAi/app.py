import os
from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from dotenv import load_dotenv
import google.generativeai as genai
import sys

# Load environment variables from .env file
load_dotenv()

# ------------------ Flask App ------------------
app = Flask(__name__, static_folder='.', static_url_path='')

# ------------------ Gemini API Key ------------------
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    print("🚨 API_KEY is not set!")
    sys.exit(1)  # <-- Replace with your actual key

if not API_KEY or API_KEY == 'YOUR_GEMINI_API_KEY':
    print("="*80)
    print("🚨 FATAL ERROR: GOOGLE_API_KEY is not set in app.py!")
    print("🚨 Replace 'YOUR_GEMINI_API_KEY' with your actual key.")
    print("="*80)
    sys.exit(1)

# ------------------ Initialize Gemini API ------------------
genai.configure(api_key=API_KEY)

# ------------------ Choose a working model ------------------
# Fallback to a known supported model
MODEL_NAME = "gemini-2.5-flash"

try:
    MODEL = genai.GenerativeModel(model_name=MODEL_NAME)
    print(f"✅ GenerativeModel '{MODEL_NAME}' initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing model '{MODEL_NAME}': {e}")
    sys.exit(1)

# ------------------ PulseAI Response Function ------------------
def pulse_ai_response(disease):
    if MODEL is None:
        return "❌ Error: Gemini API initialization failed."

    prompt = f"""
You are a helpful AI health assistant named PulseAI.

Format the response in clean **Markdown** with bold section titles.
All diet suggestions must be based on **Indian cuisine and Indian food items** only.

Sections:

### 🚫 Things to Avoid
- Each bullet with a short explanation.

### ✅ Recovery Actions
- Each bullet with a short explanation.

### 📅 Daily Life Advice
- Each bullet with a short explanation.

### 🍽️ Sample 1-Day Indian Diet Plan for Recovery
Present this as a **Markdown table** with columns: Meal, Food Items, Notes.
Include rows for: Early Morning, Breakfast, Mid-Morning Snack, Lunch, Evening Snack, Dinner, Before Bed.
All items must be Indian foods (e.g. dal, roti, khichdi, upma, poha, idli, dosa, sabzi, raita, curd, buttermilk, etc.)

Disease/Condition: {disease}
"""
    try:
        response = MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini API Call Failed: {e}"

# ------------------ API Route (non-streaming) ------------------
@app.route('/api/generate', methods=['POST'])
def generate_recommendation():
    data = request.get_json()
    if not data or 'disease' not in data:
        return jsonify({'error': 'No disease provided'}), 400

    disease = data['disease']
    recommendation_text = pulse_ai_response(disease)
    return jsonify({'recommendation': recommendation_text})

# ------------------ Streaming API Route ------------------
@app.route('/api/stream', methods=['POST'])
def stream_recommendation():
    data = request.get_json()
    if not data or 'disease' not in data:
        return jsonify({'error': 'No disease provided'}), 400

    disease = data['disease']
    language = data.get('language', 'English')

    prompt = f"""
You are a helpful AI health assistant named PulseAI.

**IMPORTANT: Respond entirely in {language}.**

Format the response in clean **Markdown** with bold section titles.
All diet suggestions must be based on **Indian cuisine and Indian food items** only.

Sections:

### 🚫 Things to Avoid
- Each bullet with a short explanation.

### ✅ Recovery Actions
- Each bullet with a short explanation.

### 📅 Daily Life Advice
- Each bullet with a short explanation.

### 🍽️ Sample 1-Day Indian Diet Plan for Recovery
Present this as a **Markdown table** with columns: Meal, Food Items, Notes.
Include rows for: Early Morning, Breakfast, Mid-Morning Snack, Lunch, Evening Snack, Dinner, Before Bed.
All items must be Indian foods (e.g. dal, roti, khichdi, upma, poha, idli, dosa, sabzi, raita, curd, buttermilk, etc.)

Disease/Condition: {disease}
"""

    def generate():
        import json
        try:
            response = MODEL.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    # Send each chunk as a Server-Sent Event
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"
            # Signal end of stream
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )

# ------------------ Follow-up Chat Streaming Route ------------------
SYSTEM_INSTRUCTION = """You are PulseAI, a helpful AI health assistant.
You provide health and diet advice based on Indian cuisine.
Format responses in clean Markdown. Use ### for section headers.
When giving diet plans, use Markdown tables with columns: Meal, Food Items, Notes.
All food items must be Indian foods.
Keep follow-up answers concise and relevant to the ongoing conversation."""

@app.route('/api/chat', methods=['POST'])
def chat_stream():
    import json
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({'error': 'No messages provided'}), 400

    messages = data['messages']  # [{role: 'user'/'model', text: '...'}]
    language = data.get('language', 'English')

    # Build Gemini chat history
    history = []
    for msg in messages[:-1]:  # all except the last (which is current user message)
        history.append({
            'role': msg['role'],
            'parts': [{'text': msg['text']}]
        })

    current_message = f"[Respond in {language}] " + messages[-1]['text']

    def generate():
        try:
            chat = MODEL.start_chat(history=history)
            response = chat.send_message(current_message, stream=True)
            for chunk in response:
                if chunk.text:
                    yield f"data: {json.dumps({'text': chunk.text})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )

# ------------------ Serve Frontend Routes ------------------
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index3.html')

@app.route('/old')
def serve_old():
    return send_from_directory('.', 'index.html')

# ------------------ Main ------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
