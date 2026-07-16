import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Viva Tip: DistilBART is a distilled (compressed) version of BART. 
# It's faster and requires less memory but maintains similar accuracy.
MODEL_ID = "sshleifer/distilbart-cnn-12-6"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

def get_pdf_summary(text, *args):
    if not HF_API_KEY:
        return "⚠️ Hugging Face API Key missing in .env!"

    if not text or len(text.strip()) < 10:
        return "⚠️ Summarize karne ke liye content bahut chhota hai. Kam se kam 2-3 lines bhejiye."

    # Headers ko ekdum saaf rakhte hain
    headers = {"Authorization": f"Bearer {HF_API_KEY.strip()}"}
    
    # Payload
    payload = {
        "inputs": text[:3000], 
        "parameters": {"max_length": 130, "min_length": 30, "do_sample": False}
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        # Terminal mein ye print hoga, check karna!
        print(f"DEBUG: URL -> {API_URL}")
        print(f"DEBUG: Status Code -> {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and "summary_text" in data[0]:
                return f"📌 **BART Summary:**\n\n{data[0]['summary_text']}"
            return "⚠️ Unexpected JSON format."

        elif response.status_code == 503:
            return "⚙️ Model Hugging Face par 'sleep' mode mein hai. 10-15 seconds mein jaag jayega, please retry!"
            
        elif response.status_code == 404:
            return "❌ Model Not Found (404). Shayad Hugging Face API mein koi issue hai. Retry karein."

        return f"❌ API Error {response.status_code}: {response.text[:100]}"

    except Exception as e:
        return f"❌ System Error: {str(e)}"