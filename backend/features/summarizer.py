import os

def get_pdf_summary(text, groq_client, model_name, *args, **kwargs):
    """
    Modular Text Summarizer feature module utilizing high-performance Groq API.
    Designed for clean, attractive plain-text output without markdown symbols.
    """
    try:
        clean_text = text.strip()
        if not clean_text:
            return "⚠️ Please provide some content text to summarize."

        if len(clean_text) < 10:
            return "⚠️ Text is too small to summarize effectively. Please provide more content."

        # Sharp corporate prompt structure with explicit constraints to avoid markdown
        system_instruction = (
    "You are a concise summarizer. Provide ONLY the summary in bullet points. "
    "Do not include any introductory phrases, metadata, or labels like 'Elysium Summary'. "
    "Use only plain text. No bold (**), no hashtags (#)."
)

        # Groq Pipeline Execution
        response = groq_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": clean_text[:4000]}
            ],
            temperature=0.3, 
            max_tokens=800
        )
        
        # Raw response cleaning
        raw_output = response.choices[0].message.content.strip()
        
        # Double safety layer to remove any accidental markdown symbols
        clean_output = raw_output.replace("**", "").replace("#", "")
        
        return f"📌 Elysium Groq Summary:\n\n{clean_output}"

    except Exception as e:
        return f"❌ Modular Summarizer Exception Error: {str(e)}"