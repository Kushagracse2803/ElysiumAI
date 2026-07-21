import os
import importlib
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
import requests
import fitz  # PyMuPDF

# Professional modular import from the features directory
from features.quiz_generator import quiz_bot
from features.resume_analyzer import resume_expert
from features.summarizer import get_pdf_summary

# NOTE: adjust this import to match your actual filename — based on your
# VS Code screenshot it looked like "video_generator.py" inside features/.
try:
    from features.video_generator import video_engine
except ImportError:
    try:
        from features.text2video import video_engine
    except ImportError:
        print("⚠️ Warning: video_engine module not found — check the filename in features/.")
        video_engine = None

# ============================================================
# Load Environment Variables
# ============================================================
load_dotenv()

# Hamara local SLM engine import ho raha hai
try:
    from Ellysium_llm.elysium_inference import generate_response as elysium_slm
except ImportError:
    # Fallback agar folder/file mismatch ho
    print("⚠️ Warning: Elysium SLM module not found.")
    elysium_slm = lambda x: "[Error] Elysium engine not loaded."

# ============================================================
# Initialize Models
# ============================================================
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ============================================================
# Flask Setup
# ============================================================
app = Flask(__name__, static_folder="../react files/dist")
CORS(app)

messages = []

# NOTE: this is a process-wide dict, so it is shared across every user/tab.
# That's fine for a single-user local demo, but if you ever have more than
# one person hitting the backend at once, move this into a per-session
# store (e.g. keyed by a session_id the frontend sends, or flask.session).
session_mode = {"current": "chat"}  # "chat" | "summarize" | "resume" | "video" | "quiz"

# ============================================================
# Unified LLM dispatcher — every feature routes through this so the
# model dropdown (Groq / Gemini / ElysiumAI) is always respected.
# ============================================================

def generate_llm_response(prompt, model_choice):
    try:
        model_choice = (model_choice or "groq").lower()

        # --- ELYSIUM LOCAL SLM LOGIC ---
        if "elysium" in model_choice:
            return elysium_slm(prompt)

        # --- GEMINI ---
        elif "gemini" in model_choice:
            model = genai.GenerativeModel(GEMINI_MODEL)
            response = model.generate_content(prompt)
            return getattr(response, "text", str(response))

        # --- GROQ (default) ---
        elif "groq" in model_choice:
            resp = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=600,
            )
            return resp.choices[0].message.content.strip()

        else:
            return f"[Error] Unknown model: {model_choice}"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def run_summary(text, model_choice):
    """
    Summarization that respects the chosen model (Groq / Gemini / ElysiumAI)
    instead of being hardcoded to Groq.
    """
    model_choice = (model_choice or "groq").lower()

    # Keep using the existing Groq-tuned summarizer module when Groq is chosen,
    # since it already has its own clean-output post-processing.
    if "groq" in model_choice:
        return get_pdf_summary(text=text, groq_client=groq_client, model_name=GROQ_MODEL)

    # For Gemini / Elysium, reuse the same system instruction but route
    # through the unified dispatcher.
    system_instruction = (
        "You are a concise summarizer. Provide ONLY the summary in bullet points. "
        "Do not include any introductory phrases, metadata, or labels like 'Elysium Summary'. "
        "Use only plain text. No bold (**), no hashtags (#)."
    )
    prompt = f"{system_instruction}\n\nText to summarize:\n{text[:4000]}"
    raw_output = generate_llm_response(prompt, model_choice)
    clean_output = raw_output.replace("**", "").replace("#", "")
    return f"📌 Elysium Summary:\n\n{clean_output}"


def run_resume_analysis(text, model_choice):
    """
    Resume analysis that respects the chosen model (Groq / Gemini / ElysiumAI).
    Reuses resume_expert's carefully-built markdown prompt template, but
    executes it through the unified dispatcher so all three backends work.
    """
    model_choice = (model_choice or "groq").lower()
    prompt = resume_expert.generate_prompt(text)

    if "groq" in model_choice or "gemini" in model_choice:
        # resume_expert.analyze already supports both Groq and Gemini client
        # shapes natively, so let it handle those two directly.
        client = groq_client if "groq" in model_choice else genai.GenerativeModel(GEMINI_MODEL)
        model_name = GROQ_MODEL if "groq" in model_choice else GEMINI_MODEL
        return resume_expert.analyze(text, client, model_name)

    # ElysiumAI has no chat.completions / generate_content interface,
    # so route it through the plain-text dispatcher instead.
    return generate_llm_response(prompt, model_choice)


def generate_mcq_raw(topic, num_questions, model_choice):
    """
    Asks the chosen model (Groq / Gemini / ElysiumAI) for MCQs in the exact
    format quiz_bot.parse_questions() expects, then parses them.
    """
    prompt = f"""
You are an expert exam question setter.
Generate {num_questions} multiple-choice questions (MCQs) on the topic: "{topic}".

Format strictly like this for every question:
1. Question text
   a) Option 1
   b) Option 2
   c) Option 3
   d) Option 4
Answer: a
"""
    raw_output = generate_llm_response(prompt, model_choice)
    return quiz_bot.parse_questions(raw_output)


# ============================================================
# Main Route: Send Message
# ============================================================

@app.route("/send_message", methods=["POST"])
def send_message():
    global session_mode

    # 1. Capture user payload details
    user_text = request.form.get("text", "").strip()
    user_text_lower = user_text.lower()
    chosen_model = request.form.get("model", "groq")
    file = request.files.get("file")

    # ------------------------------------------------------------
    # Mode resolution, in priority order:
    #   1. Explicit frontend intent (feature buttons) — always wins.
    #   2. Feature keywords in THIS message — always override whatever
    #      mode we were previously stuck in. This is what fixes typing
    #      "analyze my resume" while a prior turn had locked us into
    #      summarize mode.
    #   3. Otherwise, keep the sticky mode (needed for follow-up turns
    #      like pasting a bare paragraph after selecting Summarize, or
    #      pasting a resume with no keywords in the accompanying text).
    # ------------------------------------------------------------
    frontend_intent = (request.form.get("intent", "") or "").lower()

    RESUME_KEYWORDS = ["resume", "cv"]
    SUMMARIZE_KEYWORDS = ["summarize", "summary", "shorten"]
    VIDEO_KEYWORDS = ["video", "generate a video", "make a video", "text to video", "text2video"]
    QUIZ_KEYWORDS = [
        "quiz", "mcq", "multiple choice", "multiple-choice",
        "generate question", "question generator", "practice questions"
    ]

    if frontend_intent in ("summarize", "summarization", "text_summarization"):
        session_mode["current"] = "summarize"
    elif frontend_intent in ("resume", "resume_analysis", "resume_analyzer", "cv"):
        session_mode["current"] = "resume"
    elif frontend_intent in ("video", "text_to_video", "text2video"):
        session_mode["current"] = "video"
    elif frontend_intent in ("quiz", "mcq", "mcq_generator", "quiz_generator"):
        session_mode["current"] = "quiz"
        quiz_bot.reset()
    elif frontend_intent in ("chat", "back"):
        session_mode["current"] = "chat"
    elif any(k in user_text_lower for k in RESUME_KEYWORDS):
        session_mode["current"] = "resume"
    elif any(k in user_text_lower for k in SUMMARIZE_KEYWORDS):
        session_mode["current"] = "summarize"
    elif any(k in user_text_lower for k in VIDEO_KEYWORDS):
        session_mode["current"] = "video"
    elif any(k in user_text_lower for k in QUIZ_KEYWORDS) and session_mode["current"] != "quiz":
        session_mode["current"] = "quiz"
        quiz_bot.reset()
    # else: no explicit signal in this message — keep whatever mode
    # session_mode["current"] already holds (sticky continuation).

    if not user_text and not file:
        return jsonify({"sender": "ai", "text": "⚠️ Please upload a file or type a message.", "model": "SYSTEM"}), 200

    # Universal exit command works from any locked mode
    if user_text_lower in ("back", "exit", "quit", "stop"):
        session_mode["current"] = "chat"
        return jsonify({
            "sender": "ai",
            "text": "🔄 Returning to general chat.",
            "model": "SYSTEM"
        }), 200

    # ============================================================
    # 📄 FILE HANDLER (PDF Logic) — mode-aware
    # ============================================================
    if file:
        try:
            pdf_stream = file.read()
            doc = fitz.open(stream=pdf_stream, filetype="pdf")
            extracted_text = "".join([page.get_text() for page in doc])

            if not extracted_text.strip():
                return jsonify({"sender": "ai", "text": "⚠️ System Error: Unable to extract text from the provided PDF.", "model": "ERROR"}), 200

            current_mode = session_mode["current"]

            if current_mode == "summarize":
                ai_text = run_summary(extracted_text, chosen_model)
                model_tag = f"SUMMARIZER ({chosen_model.upper()})"

            elif current_mode == "resume":
                ai_text = run_resume_analysis(extracted_text, chosen_model)
                model_tag = f"RESUME-EXPERT ({chosen_model.upper()})"
                # One-shot feature — return to chat so the next unrelated
                # message (possibly with a different model selected) isn't
                # mistaken for another resume upload.
                session_mode["current"] = "chat"

            else:
                # Not explicitly locked — fall back to keyword sniffing
                # on the accompanying text, then general doc-chat.
                query = user_text_lower
                if any(x in query for x in ["summarize", "summary", "shorten"]):
                    ai_text = run_summary(extracted_text, chosen_model)
                    model_tag = f"SUMMARIZER ({chosen_model.upper()})"
                elif any(x in query for x in ["resume", "analyze", "analyse", "cv"]):
                    ai_text = run_resume_analysis(extracted_text, chosen_model)
                    model_tag = f"RESUME-EXPERT ({chosen_model.upper()})"
                    session_mode["current"] = "chat"
                else:
                    prompt = f"Context: {extracted_text[:3000]}\n\nQuestion: {user_text}"
                    ai_text = generate_llm_response(prompt, chosen_model)
                    model_tag = f"DOC-CHAT ({chosen_model.upper()})"

            return jsonify({"sender": "ai", "text": ai_text, "model": model_tag}), 200
        except Exception as e:
            return jsonify({"sender": "ai", "text": f"❌ File processing error: {str(e)}", "model": "ERROR"}), 200

    # ============================================================
    # 📝 TEXT SUMMARIZATION MODE (no file attached)
    # ============================================================
    if session_mode["current"] == "summarize":
        keywords_to_check = ["summarize", "summarization", "text summarization", "summary", "shorten"]

        # Guard clause for confused/short/garbage prompts
        if user_text_lower in keywords_to_check or len(user_text.split()) < 4:
            return jsonify({
                "sender": "ai",
                "text": "❓ Please provide the paragraph or bulky text content you want me to summarize.",
                "model": "SUMMARIZER"
            }), 200

        # Strip prompt-noise wrapper words
        processing_text = user_text
        for word in keywords_to_check:
            if processing_text.lower().startswith(word):
                processing_text = processing_text[len(word):].strip()
            if processing_text.lower().endswith(word):
                processing_text = processing_text[:-len(word)].strip()

        ai_text = run_summary(processing_text, chosen_model)
        return jsonify({"sender": "ai", "text": ai_text, "model": f"SUMMARIZER ({chosen_model.upper()})"}), 200

    # ============================================================
    # 📎 RESUME ANALYSIS MODE (no file attached yet)
    # ============================================================
    if session_mode["current"] == "resume":
        return jsonify({
            "sender": "ai",
            "text": "📎 Please send your resume (PDF) so I can analyze it.",
            "model": "RESUME-EXPERT"
        }), 200

    # ============================================================
    # 🎬 TEXT → VIDEO MODE
    # ============================================================
    if session_mode["current"] == "video":
        if video_engine is None:
            return jsonify({
                "sender": "ai",
                "text": "❌ Video engine not loaded — check the import path in app.py against your features/ filename.",
                "model": "ERROR"
            }), 200

        # Strip the trigger word itself so a bare "video" doesn't get
        # passed straight into the generator as the prompt.
        prompt_text = user_text
        for word in VIDEO_KEYWORDS:
            if prompt_text.lower().strip() == word:
                prompt_text = ""
                break

        if not prompt_text.strip() or len(prompt_text.split()) < 3:
            return jsonify({
                "sender": "ai",
                "text": "🎬 What would you like the video to be about? Describe the scene or idea.",
                "model": "VIDEO-GENERATOR"
            }), 200

        try:
            ai_text = video_engine.generate(prompt_text)
        except Exception as e:
            ai_text = f"❌ Video generation error: {str(e)}"

        # One-shot feature — return to chat so the next unrelated message
        # (possibly with a different model selected) isn't mistaken for
        # another video prompt.
        session_mode["current"] = "chat"
        return jsonify({"sender": "ai", "text": ai_text, "model": "VIDEO-GENERATOR"}), 200

    # ============================================================
    # 🧩 MCQ / QUIZ GENERATOR MODE (multi-step, uses quiz_bot)
    # ============================================================
    if session_mode["current"] == "quiz":
        state = quiz_bot.state

        # Step 0: just entered quiz mode -> ask for topic
        if state["step"] == 0:
            state["step"] = 1
            return jsonify({
                "sender": "ai",
                "text": "🧩 What topic would you like the quiz on?",
                "model": "QUIZ-GENERATOR"
            }), 200

        # Step 1: user just gave the topic -> ask how many questions
        if state["step"] == 1:
            if not user_text:
                return jsonify({"sender": "ai", "text": "🧩 Please tell me a topic for the quiz.", "model": "QUIZ-GENERATOR"}), 200
            state["topic"] = user_text
            state["step"] = 2
            return jsonify({
                "sender": "ai",
                "text": f"🔢 How many questions would you like on \"{state['topic']}\"?",
                "model": "QUIZ-GENERATOR"
            }), 200

        # Step 2: user gives the number of questions -> generate the quiz
        if state["step"] == 2:
            digits = "".join(ch for ch in user_text if ch.isdigit())
            if not digits:
                return jsonify({
                    "sender": "ai",
                    "text": "🔢 Please reply with just a number, e.g. 5.",
                    "model": "QUIZ-GENERATOR"
                }), 200

            num_questions = max(1, min(int(digits), 15))  # sane bounds
            state["num"] = num_questions

            questions = generate_mcq_raw(state["topic"], num_questions, chosen_model)
            if not questions:
                quiz_bot.reset()
                session_mode["current"] = "chat"
                return jsonify({
                    "sender": "ai",
                    "text": "❌ Couldn't generate questions from the model's response. Please try again.",
                    "model": "QUIZ-GENERATOR"
                }), 200

            state["questions"] = questions
            state["current_index"] = 0
            state["score"] = 0
            state["step"] = 3

            q = questions[0]
            return jsonify({
                "sender": "ai",
                "text": f"Question 1/{len(questions)}:\n{q['question']}\n{q['options']}",
                "model": f"QUIZ-GENERATOR ({chosen_model.upper()})"
            }), 200

        # Step 3: user is answering questions one at a time
        if state["step"] == 3:
            answer = user_text_lower.strip().replace(")", "")
            idx = state["current_index"]
            questions = state["questions"]

            if idx >= len(questions):
                # Safety net — shouldn't normally happen
                quiz_bot.reset()
                session_mode["current"] = "chat"
                return jsonify({"sender": "ai", "text": "Quiz already finished.", "model": "QUIZ-GENERATOR"}), 200

            correct_answer = questions[idx]["answer"]
            is_correct = answer[:1] == correct_answer

            if is_correct:
                state["score"] += 1
                feedback = "✅ Correct!"
            else:
                feedback = f"❌ Wrong. The correct answer was {correct_answer})."

            state["current_index"] += 1

            if state["current_index"] < len(questions):
                next_q = questions[state["current_index"]]
                next_text = (
                    f"{feedback}\n\n"
                    f"Question {state['current_index'] + 1}/{len(questions)}:\n"
                    f"{next_q['question']}\n{next_q['options']}"
                )
                return jsonify({"sender": "ai", "text": next_text, "model": "QUIZ-GENERATOR"}), 200
            else:
                final_score = state["score"]
                total = len(questions)
                quiz_bot.reset()
                session_mode["current"] = "chat"
                return jsonify({
                    "sender": "ai",
                    "text": f"{feedback}\n\n🏁 Quiz complete! Your score: {final_score}/{total}",
                    "model": "QUIZ-GENERATOR"
                }), 200

    # ============================================================
    # ✍️ GENERAL CHAT LOGIC (Fallback)
    # ============================================================
    ai_text = generate_llm_response(user_text, chosen_model)
    return jsonify({"sender": "ai", "text": ai_text, "model": chosen_model.upper()}), 200


# ============================================================
# Dedicated PDF endpoint (kept, made model-aware too)
# ============================================================

@app.route("/process_pdf", methods=["POST"])
def process_pdf():
    """
    Dedicated endpoint for handling PDF-specific processing intents
    including professional resume analysis and document summarization.
    """
    if 'file' not in request.files:
        return jsonify({"text": "⚠️ No file detected in the request.", "model": "ERROR"}), 400

    file = request.files['file']
    intent = request.form.get("intent", "resume")
    chosen_model = request.form.get("model", "groq")

    try:
        pdf_stream = file.read()
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        extracted_text = "".join([page.get_text() for page in doc])

        if intent == "summary":
            ai_text = run_summary(extracted_text, chosen_model)
            model_tag = f"SUMMARIZER ({chosen_model.upper()})"
        else:
            ai_text = run_resume_analysis(extracted_text, chosen_model)
            model_tag = f"RESUME-EXPERT ({chosen_model.upper()})"

        session_mode["current"] = "chat"
        return jsonify({
            "sender": "ai",
            "text": ai_text,
            "model": model_tag
        }), 200

    except Exception as e:
        return jsonify({"text": f"❌ System Exception: {str(e)}", "model": "ERROR"}), 500


# ============================================================
# Serve Frontend
# ============================================================

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    full_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


# ============================================================
# Run App
# ============================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)