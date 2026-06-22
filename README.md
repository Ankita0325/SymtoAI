# 🧠 SymtoAI  
### *Understand Risks. Take Action Early.*

SymtoAI is an AI-powered health screening and risk analysis system that helps users understand potential health issues by analyzing symptoms, family history, and conversational input. It acts as an early warning assistant that encourages timely medical consultation.

---

## 🔗 Repository
`github.com/your-username/symtoai`

---

## 📄 Project Overview

SymtoAI is a smart health assistant that uses AI-driven symptom analysis and risk prediction to provide personalized health insights.

It enables users to describe symptoms in natural language, tracks health progression, and integrates family medical history to improve risk accuracy.

---

## 🧩 Abstract

SymtoAI bridges the gap between self-reported symptoms and early medical awareness. Unlike static symptom checkers, it provides:

- Conversational symptom input  
- Intelligent symptom extraction  
- Dynamic follow-up questions  
- Family history-based risk scoring  
- AI-powered health insights using Groq API  

---

## ❗ Problem Statement

People often ignore early symptoms due to lack of awareness and poor guidance tools.

### Key Issues:
- Ignoring early warning signs  
- No personalization in symptom checkers  
- No family history integration  
- No symptom tracking  
- Static non-AI systems  

### Impact:
- Delayed diagnosis  
- Increased healthcare cost  
- Preventable complications  
- Unnecessary hospital visits  

---

## 💡 Proposed Solution

SymtoAI provides a conversational AI health assistant that:

- Understands natural language symptoms  
- Extracts medical signals  
- Asks dynamic follow-up questions  
- Uses family medical history  
- Generates real-time risk scores  
- Provides actionable recommendations  

---

## 🚀 Features

- 💬 AI Health Chatbot (Groq API)  
- 🧠 Symptom Extraction Engine  
- 📊 Risk Scoring Dashboard  
- 👨‍👩‍👧 Family History Tracking  
- 🔍 Dynamic Question System  
- 📈 Symptom Timeline  
- ⚠️ Risk Classification (Minimal → High)  
- 🧾 Personalized Recommendations  

---

## 🏗️ System Architecture

User → Chat Interface → Symptom Parser → AI Service → Risk Engine → Dashboard → Recommendations

---

## ⚙️ Tech Stack

Frontend:
- HTML5
- CSS3
- Tailwind CSS
- JavaScript
- Jinja2

Backend:
- Flask
- Python
- Groq API (LLM)
- dotenv

Data Storage:
- JSON Files (lightweight database)

---

## 📁 Project Structure
├── 📁 data
│   ├── ⚙️ conversations.json
│   ├── ⚙️ family_history.json
│   ├── ⚙️ patients.json
│   ├── ⚙️ reports.json
│   ├── ⚙️ symptoms.json
│   └── ⚙️ users.json
├── 📁 services
│   ├── 🐍 groq_service.py
│   ├── ⚙️ package-lock.json
│   ├── 🐍 question_generator.py
│   ├── 🐍 risk_engine.py
│   └── 🐍 symptom_parser.py
├── 📁 static
│   ├── 📁 css
│   │   └── 🎨 style.css
│   ├── 📁 image
│   │   └── 🖼️ logo.png
│   └── 📁 js
│       ├── 📄 chat.js
│       ├── 📄 dashboard.js
│       └── 📄 family.js
├── 📁 templates
│   ├── 🌐 chat.html
│   ├── 🌐 dashboard.html
│   ├── 🌐 family_history.html
│   ├── 🌐 index.html
│   ├── 🌐 login.html
│   ├── 🌐 report_view_detailed.html
│   ├── 🌐 reports.html
│   └── 🌐 signup.html
├── 📁 utils
│   └── 🐍 helpers.py
├── ⚙️ .gitattributes
├── ⚙️ .gitignore
├── 📝 README.md
├── 🐍 app.py
├── 📄 requirements.txt
└── 📄 runtime.txt


---

## 🧠 Core Modules

### 💬 Chat Module
- Natural symptom input  
- AI responses  
- Symptom extraction  
- Follow-up questions  

---

### 🧮 Risk Engine
- Score: 0–100  
- Levels:
  - 0–19 Minimal  
  - 20–39 Low  
  - 40–69 Moderate  
  - 70+ High  
- Personalized recommendations  

---

### 🔍 Symptom Parser
- Detects:
  - Fever  
  - Cough  
  - Headache  
  - Fatigue  
  - Chest pain  
  - Dizziness  

---

### ❓ Question Generator
- Dynamic follow-ups:
  - Fever → “How high is your temperature?”  
  - Cough → “Dry or productive?”  

---

### 👨‍👩‍👧 Family History Module
- Stores genetic conditions  
- Improves risk accuracy  
- Multi-member support  

---

### 🤖 AI Service (Groq API)
- Conversational health responses  
- Empathetic AI guidance  
- Safe recommendations  

---

## 🔄 System Workflow

User Input → Symptom Parser → AI Response → Follow-up Questions → Risk Engine → Dashboard → Recommendations

---

## 📊 Risk Levels

| Score | Level | Action |
|------|------|--------|
| 0–19 | Minimal | Monitor |
| 20–39 | Low | Observe |
| 40–69 | Moderate | Doctor Visit |
| 70+ | High | Immediate Care |

---

## 📈 Impact

### Users
- Early health risk detection  
- Better symptom awareness  
- Personalized guidance  

### Healthcare
- Reduces delayed diagnosis  
- Promotes preventive care  
- Reduces hospital burden  

---

## 💡 Innovation Highlights

- AI-based symptom understanding  
- Dynamic conversation flow  
- Family history integration  
- Real-time risk scoring  
- Healthcare-focused AI system  

---

## 🧠 Challenges Faced

- Converting free text into medical signals  
- Designing risk scoring logic  
- Handling ambiguous symptoms  
- Ensuring AI safety in healthcare  
- Balancing accuracy and simplicity  

---

## 📚 What I Learned

- Flask full-stack development  
- AI/LLM integration (Groq API)  
- NLP-based symptom extraction  
- System design for healthcare apps  
- JSON-based data modeling  

---

## 🏁 Conclusion

SymtoAI is an AI-powered health risk analysis system that enables early detection of health conditions through conversational AI and intelligent risk scoring.