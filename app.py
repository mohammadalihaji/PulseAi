import os
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import sys

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

Sections:

**🚫 Things to Avoid**
- Each bullet with a short explanation.

**✅ Recovery Actions**
- Each bullet with a short explanation.

**📅 Daily Life Advice**
- Each bullet with a short explanation.

**🍽️ Sample 1-Day Diet Plan for Recovery**
- **Breakfast:** ...
- **Lunch:** ...
- **Snacks:** ...
- **Dinner:** ...

Disease/Condition: {disease}
"""
    try:
        response = MODEL.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini API Call Failed: {e}"

# ------------------ API Route ------------------
@app.route('/api/generate', methods=['POST'])
def generate_recommendation():
    data = request.get_json()
    if not data or 'disease' not in data:
        return jsonify({'error': 'No disease provided'}), 400

    disease = data['disease']
    recommendation_text = pulse_ai_response(disease)
    return jsonify({'recommendation': recommendation_text})

# ------------------ Serve Frontend Route ------------------
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# ------------------ Main ------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
