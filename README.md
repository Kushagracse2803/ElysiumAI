<div align="center">

# ✨ Elysium AI

**A Scalable Multi-Model Orchestration Gateway**
*One unified, fast and privacy-first Generative AI workspace.*

[![GitHub Repo](https://img.shields.io/badge/GitHub-ElysiumAI-181717?logo=github)](https://github.com/Kushagracse2803/ElysiumAI)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://lnkd.in/p/d4f-T3X9)


![Elysium AI Screenshot](docs/screenshot.png)

</div>

---

## 📖 About

**Elysium AI** is a final-year B.Tech project (CSE – Artificial Intelligence) built at **Pranveer Singh Institute of Technology (PSIT), Kanpur**, affiliated to Dr. A.P.J. Abdul Kalam Technical University, Lucknow.

Today's AI ecosystem is fragmented: users juggle several platforms for summarizing, quizzes, resumes and more, and cloud-only models are slow under load and send private data off-device. Elysium AI solves this with a **single gateway that routes every request to the best model**, combining cloud LLMs (Google Gemini, Groq) with local inference (Ollama and our own **Elysium SLM** built from scratch in PyTorch).

> ⚠️ AI may display inaccurate info, so always double-check its responses.

## 🚀 Features

- **💬 Multi-Model Chat**: Switch between models (e.g., Gemini, Groq) from the selector in the top-right corner.
- **🧠 Smart Router**: Detects the intent of each prompt and picks the best engine for speed, reasoning depth, or privacy.
- **📝 Text Summarizer**: Turn long documents into crisp summaries in seconds.
- **❓ MCQ / Quiz Generator**: Generate multiple-choice questions from any study material.
- **📄 Resume Analyzer**: Get scoring, gaps, and ATS-style feedback.
- **🖼️ Text → Image** and **🎬 Text → Video** *(experimental)*: Create visuals or video ideas from natural-language prompts.
- **🔒 Privacy-First Local Path**: Sensitive tasks can run on-device with the Elysium SLM or Ollama.
- **⚡ Real-Time Streaming**: Responses stream token by token (Server-Sent Events).
- **📎 File Attachments**, **🕘 Chat History**, and **🔐 JWT-based login/logout**.

## 🏗️ Architecture

Elysium AI uses a decoupled **three-tier architecture**:

| Tier | Role | Tech |
|------|------|------|
| **Presentation** | Prompt UI, real-time streaming | React.js, Tailwind CSS, Vite, Axios |
| **Logic (Gateway)** | Intent detection, smart routing, fallback, telemetry | Flask, LangChain, MongoDB |
| **Model** | Hybrid intelligence | Gemini, Groq (cloud) · Ollama, Elysium SLM (local) |

**Request flow:** user prompt → sanitization → smart router → best model (cloud or local) → response wrapper → streamed to UI → metrics logged.

## 🧬 The Elysium SLM

A custom **decoder-only Transformer** (Small Language Model) built from scratch with PyTorch: multi-head self-attention, causal masking, GELU, pre-LayerNorm, a custom BPE tokenizer, and **INT8 quantization** so it runs on standard laptops (~250 MB footprint). It was trained on the TinyStories dataset and instruction-tuned for local summarization and drafting.

## 📊 Results (from the project report)

| Metric | Result |
|--------|--------|
| Latency reduction vs. standard cloud path | **28.8%** (target: 25%) |
| Groq-path throughput | **820+ tokens/sec** |
| Concurrent users tested | **300+** at 99.8% success rate |
| Quiz JSON formatting accuracy | **97.2%** |
| Smart-router precision | **96.3%** |

> The local SLM showed signs of overfitting in training (see Chapter 5 of the report), so complex reasoning is still routed to cloud models.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React.js, Tailwind CSS, Vite, Axios |
| Backend | Python, Flask, REST APIs, JWT Auth |
| Database | MongoDB |
| AI / ML | PyTorch, LangChain, Hugging Face |
| Models | Google Gemini API, Groq API, Ollama (local) |

## ⚙️ Getting Started

### Prerequisites

- Python 3.10+ and Node.js 18+
- MongoDB (local or Atlas)
- API keys for Gemini and Groq
- *(Optional)* [Ollama](https://ollama.com) for local models

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Kushagracse2803/ElysiumAI.git
cd ElysiumAI

# 2. Backend setup
cd backend
pip install -r requirements.txt

# 3. Frontend setup
cd ../frontend
npm install
```

### Environment Variables

Create a `.env` file inside `backend/` (never commit it):

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret
```

> Adjust the variable names to match the ones used in your code.

### Run the App

```bash
# Terminal 1 – backend
cd backend
python app.py

# Terminal 2 – frontend
cd frontend
npm run dev
```

Then open the URL shown by Vite (usually **http://localhost:5173**).

## 💡 Usage

1. **Log in** to your account.
2. **Pick a model** from the dropdown in the top-right corner.
3. Type a prompt or attach a file, then hit **SEND**.
4. Try prompts like:
   - `Summarize the following text: ...`
   - `Please analyze my resume ...`
   - `Generate multiple-choice questions on ...`
   - `Create a short video script about ...`

## 🗂️ Project Structure

```
ElysiumAI/
├── backend/                          # Flask gateway: smart router, model integrations, API
│   └── app.py                        # Intent detection, routing and request handling
├── frontend/                         # React + Vite + Tailwind user interface
├── docs/
│   └── screenshot.png                # README screenshot
├── EllysiumAI_report.pdf             # Full B.Tech project report
├── ElysiumAI_Final_Year_Project.pptx # Project presentation slides
├── .gitignore
└── README.md
```

> `backend/` and `frontend/` contain more files than shown here. Expand them with your real file tree if you want a deeper view.

## 🗺️ Roadmap

- [ ] Larger, instruction-tuned SLM (e.g., Phi-3.5-mini via QLoRA)
- [ ] Multimodal support (vision, audio, video understanding)
- [ ] Mobile app (Android / iOS) with on-device AI
- [ ] Real video generation from text
- [ ] Enterprise tier: team workspaces, SSO, on-prem deployment


## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m "Add amazing feature"`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📬 Contact

**Kushagra Tiwari**

- GitHub: [@Kushagracse2803](https://github.com/Kushagracse2803)
- LinkedIn: [Connect with me](https://lnkd.in/p/d4f-T3X9)

---

<div align="center">

⭐ If you like this project, give it a star on [GitHub](https://github.com/Kushagracse2803/ElysiumAI)!

</div>
