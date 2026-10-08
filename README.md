# TalentSkillMate AI

## AI-Powered Resume Screening & Candidate Matching System

TalentSkillMate AI is an AI-powered recruitment assistant designed to help HR professionals screen resumes, analyze candidate profiles, match candidates with job requirements, and generate recruiter-friendly insights.

The system uses AI, RAG, and structured candidate analysis to help recruiters make faster and more informed decisions. **TalentSkillMate AI provides recommendations and insights to recruiters; it does not make final hiring decisions.**

## 🚀 Features

- 📄 PDF and DOCX resume parsing
- 🤖 AI-powered resume analysis
- 🎯 Candidate-to-job matching
- 📊 Match score with matching insights
- 🔍 Hidden skill discovery
- 📝 Evidence-based candidate matching
- 🏆 Candidate ranking
- 💡 AI-generated interview questions
- 📑 Recruiter reports
- 🧠 RAG-based candidate knowledge retrieval
- 🔄 Duplicate resume detection and candidate profile updating
- 📥 Downloadable recruiter reports
- 🎨 Professional Streamlit recruitment dashboard
- 💬 AI recruiter assistant — SkyHigh
- 📈 Interactive charts and candidate analytics

## 🛠️ Technologies Used

- Python
- Streamlit
- Groq API
- OpenAI-compatible LLM API
- PyMuPDF
- python-docx
- ChromaDB
- RAG
- Plotly
- Pandas

## 🧠 AI & RAG Workflow

```text
Resume Upload
      ↓
PDF / DOCX Parsing
      ↓
Resume Text Extraction
      ↓
AI Resume Analysis
      ↓
Structured Candidate Profile
      ↓
Candidate Storage in ChromaDB
      ↓
RAG-Based Retrieval
      ↓
Job Description Matching
      ↓
Match Score & Evidence
      ↓
Candidate Ranking
      ↓
Recruiter Insights & Reports
```

## 🔄 Duplicate Resume Handling

TalentSkillMate AI is designed to maintain the latest candidate information in the RAG database.

- Same email + updated resume → latest resume replaces the previous profile
- Same email + same resume → profile is refreshed
- Same phone when email is unavailable → candidate profile is updated
- Same name + different email → treated as different candidates
- Same name + different resume content → treated as different candidates
- Exact duplicate resume content → detected using resume hashing

The system does not automatically reject a candidate based only on their name.

## 📊 Candidate Matching

Candidates are evaluated against the provided job description using factors such as:

- Required skills
- Relevant experience
- Educational qualifications
- Job-description relevance
- Evidence found in the resume
- Related or hidden skills

The system generates an overall match score along with supporting insights so recruiters can understand why a candidate received the score.

## 💡 Interview Studio

TalentSkillMate AI can generate interview questions based on:

- Candidate profile
- Resume skills
- Experience
- Job requirements
- Interview type

This helps recruiters prepare candidate-specific interview questions.

## 🧠 RAG Intelligence

The system uses **Retrieval-Augmented Generation (RAG)** with ChromaDB to store and retrieve candidate information.

RAG enables the recruiter assistant to retrieve relevant candidate information and provide contextual responses instead of relying only on the LLM's general knowledge.

## 🤖 SkyHigh AI Recruiter Assistant

**SkyHigh** is the AI recruiter assistant inside TalentSkillMate AI.

It can assist recruiters with:

- Candidate information retrieval
- Resume insights
- Candidate comparison
- Job matching
- Interview question generation
- Recruitment-related queries

## 📑 Recruiter Reports

TalentSkillMate AI generates recruiter-friendly reports containing information such as:

- Candidate details
- Skills
- Experience
- Education
- Match score
- Matching insights
- Candidate ranking
- Recruitment recommendations

Reports can be downloaded for further review.

## 🎨 Dashboard

The application provides a professional Streamlit dashboard for recruiters with dedicated sections for:

- Overview
- Resume Screening
- RAG Intelligence
- Ask SkyHigh
- Skill Discovery
- Candidate Matching
- Interview Studio
- Recruiter Reports
- Settings

## 📁 Project Structure

```text
talentskillmate-ai/
│
├── app.py
├── candidate_matcher.py
├── candidate_profile.json
├── llm_engine.py
├── rag_engine.py
├── resume_parser.py
├── report_generator.py
├── skyhigh_agent.py
├── requirements.txt
├── README.md
│
├── assets/
│
├── ui/
│   ├── components.py
│   ├── dashboard.py
│   └── styles.py
│
└── tests/
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/vinothinivino417-ui/talentskillmate-ai.git
cd talentskillmate-ai
```

### 2. Create a virtual environment

```bash
python -m venv venv313
```

### 3. Activate the virtual environment

Windows PowerShell:

```bash
.\venv313\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the API key

Create a `.env` file in the project root:

```env
LLM_PROVIDER=groq
LLM_API_KEY=YOUR_GROQ_API_KEY
LLM_MODEL=openai/gpt-oss-20b
LLM_BASE_URL=https://api.groq.com/openai/v1
```

**Never upload your `.env` file or API key to GitHub.**

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## 🔐 Security

API keys and other secrets should be stored in environment variables.

The `.env` file should be excluded from GitHub using `.gitignore`.

Example:

```text
.env
__pycache__/
*.pyc
venv/
venv313/
chroma_db/
```

## ⚠️ Disclaimer

TalentSkillMate AI is a recruitment decision-support system. Its scores, insights, rankings, and recommendations are intended to assist recruiters and should not be used as the sole basis for employment decisions.

## 👩‍💻 Project

**TalentSkillMate AI**  
AI-Powered Resume Screening & Candidate Matching System
