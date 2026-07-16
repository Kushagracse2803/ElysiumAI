import os
import google.generativeai as genai
from dotenv import  load_dotenv

dotenv_path=os.path.join(os.path.dirname(__file__),'.env')
load_dotenv(dotenv_path)
'''__file__: Kitaab (gen_text.py) khud se poochti hai, "Main kahan rakhi hoon?"

Jawaab milta hai: my-elysium-app ghar ke model kamre ke andar.
os.path.dirname(__file__): Phir kitaab poochti hai, "Mera kamra kaun sa hai?"

Jawaab milta hai: model kamra.
os.path.join(...): Aakhir mein kitaab kehti hai, "Theek hai, mere model kamre mein jo chaabi (.env) rakhi hai, uska poora address batao."'''
#   configuration of the gemini API
API_KEY=os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("Gemini_API_KEY not found. Please set in the .env file")
genai.configure(api_key=API_KEY)

#Intitialize the model
model =genai.GenerativeModel("gemini-1.5-flash")


def generate_text(user_prompt):
    try:
        response=model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response from Gemini: {e}")
        return "Sorry, I'm having trouble connecting to the AI service right now."


