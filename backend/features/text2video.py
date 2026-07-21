import os
from dotenv import load_dotenv
import google.generativeai as genai


# --------------------------
# Load & Configure API Key
# --------------------------
def run(prompt_text: str):
    """
    Uses Gemini 2.5 Flash to generate a cinematic script idea.
    Later you can replace with Veo when public.
    """
    print(f"[🎬 ELYSIUM] Prompt received: {prompt_text}")

    load_dotenv()
    api_key = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "⚠️ Gemini API key is not configured. Add GEMINI_KEY or GEMINI_API_KEY to your environment to enable video generation."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            f"Create a cinematic short film concept or video script for this idea: {prompt_text}"
        )

        if hasattr(response, "text") and response.text.strip():
            return f"🎬 (Cinematic Preview)\n{response.text}"
        else:
            return "⚠️ No response text received from Gemini 2.5 model."

    except Exception as e:
        print(f"❌ Error in text2video: {e}")
        return f"❌ Failed to generate video (Gemini 2.0 API error): {e}"
