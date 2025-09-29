import gradio as gr
import google.generativeai as genai

# ------------------ Gemini API Key ------------------
API_KEY = 'AIzaSyCTWfbbc1Lrzvd2QsPl3fTkXyzsMQS7KXc'

# ------------------ Initialization ------------------
MODEL_NAME = "gemini-2.5-flash"
MODEL = None

try:
    genai.configure(api_key=API_KEY)
    MODEL = genai.GenerativeModel(model_name=MODEL_NAME)
except Exception as e:
    print(f"Error configuring or initializing GenerativeModel: {e}")

# ------------------ PulseAI Function ------------------
def pulse_ai_response(disease):
    if MODEL is None:
        return "Error: Gemini API initialization failed. Please check your API key and console for details."

    prompt = f"""
You are a helpful AI health assistant named PulseAI.
A user will tell you their disease or health condition.

Provide a **plain text**, **easy-to-read output** with **line breaks**.
Do not return JSON, proto objects, or Markdown formatting.
Use bullet points, but **after each bullet, add a short explanation** in simple words.
Make it like a friendly Word-style outline, not a table or numbered blocks.

Structure:

🚫 Things to Avoid
- Bullet points with a short explanation after each item.

✅ Recovery Actions
- Bullet points with a short explanation after each item.

📅 Daily Life Advice
- Bullet points with a short explanation after each item.

🍽️ Sample 1-Day Diet Plan for Recovery
- Breakfast, Lunch, Snacks, Dinner each as bullet points with short explanation.

Disease/Condition: {disease}
"""


    try:
        response = MODEL.generate_content(prompt)
        # Convert to plain text
        output_text = str(response.candidates[0].content)
        # Replace unnecessary symbols or extra formatting if any
        output_text = output_text.replace("* ", "").replace("-", "")
        return output_text.strip()

    except Exception as e:
        return f"Gemini API Call Failed: {e}"

# ------------------ Gradio UI ------------------
with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align:center; color:#00a99d;'>PulseAI</h1>")
    gr.Markdown("<p style='text-align:center; color:gray;'>AI-Powered Health & Diet Recommendations</p>")

    with gr.Row():
        disease_input = gr.Textbox(
            placeholder="Enter your disease or ailment (e.g., 'Cold', 'Flu', 'Diabetes')",
            label="", 
            elem_id="disease_input",
            lines=1
        )
        submit_button = gr.Button("Get Plan", elem_id="get_plan_btn")

    recommendation_output = gr.Textbox(
        label="Your Recommendation:",
        placeholder="PulseAI will provide your health and diet advice here...",
        lines=25
    )

    submit_button.click(pulse_ai_response, inputs=disease_input, outputs=recommendation_output)

# ------------------ Launch App ------------------
demo.launch()