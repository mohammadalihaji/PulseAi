import gradio as gr
import google.generativeai as genai

# ------------------ Gemini API Key ------------------
API_KEY = 'your_api_key'
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
        return "❌ Error: Gemini API initialization failed. Please check your API key and console for details."

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

# ------------------ Status Helpers ------------------
def show_status(_):
    return "⚡ Generating your personalized health plan... please wait!"

def done_status(_):
    return "✅ Done!"

# ------------------ Gradio UI ------------------
with gr.Blocks(css="""
    body {background-color: #f4f7f9; font-family: 'Segoe UI', sans-serif;}
    #header {font-size: 2.2em; font-weight: 700; color: #00a99d; margin-bottom: 0;}
    #subheader {font-size: 1em; color: gray; margin-top: 0; margin-bottom: 20px;}
    #disease_input {border-radius: 12px; border: 1px solid #ddd; padding: 10px;}
    #get_plan_btn {background-color: #00a99d; color: white; font-weight: bold; border-radius: 12px;}
    #status_msg {font-style: italic; color: #555; margin-top: 10px; margin-bottom: 10px;}
    .gr-markdown {background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.05);}
""") as demo:

    gr.Markdown("<h1 id='header'>PulseAI</h1>")
    gr.Markdown("<p id='subheader'>AI-Powered Health & Diet Recommendations</p>")

    with gr.Row():
        disease_input = gr.Textbox(
            placeholder="Enter your disease or ailment (e.g., 'Cold', 'Flu', 'Diabetes')",
            label="", 
            elem_id="disease_input",
            lines=1
        )
        submit_button = gr.Button("Get Plan", elem_id="get_plan_btn")

    status_msg = gr.Markdown("⏳ Waiting for input...", elem_id="status_msg")

    recommendation_output = gr.Markdown()

    # Chain actions
    submit_button.click(
        show_status,
        inputs=disease_input,
        outputs=status_msg
    ).then(
        pulse_ai_response,
        inputs=disease_input,
        outputs=recommendation_output
    ).then(
        done_status,
        inputs=disease_input,
        outputs=status_msg
    )

# ------------------ Launch The Application ------------------
demo.launch()
