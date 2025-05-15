# 🧠 EventAlly – Intelligent Event Assistant

EventBot is a smart AI-powered assistant designed to enhance workshop and event experiences. It offers real-time Q&A, session suggestions, similar participant matching, location guidance, and personalized networking, all powered by a vector search engine and LLMs.

---

## ✨ Features

- 🗓️ Agenda-aware query answering
- 👥 Participant similarity matching via resumes
- 📍 Location guidance (e.g., “Where is the lunch area?”)
- 🕒 Real-time time-to-session/lunch updates
- 💬 Conversational feedback collection
- 📚 Built with Gemini, Qdrant, Flask, and React

---

## 🏗️ Project Structure
```
eventbot/
├── backend/ # Flask API with & Qdrant
│ ├── geminiBot.py
| |── docker-compose.yml
│ └── utils/
├── frontend/ # React TypeScript UI
│ └── ...
├── qdrant/ # Qdrant Docker setup
│ 
└── README.md
```
---

## 🚀 Getting Started

### 🐳 Step 1: Run Qdrant Vector DB (Locally via Docker)

Make sure you have Docker installed. Then, run:

```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  qdrant/qdrant
📌 Qdrant will be available at: http://localhost:6333

🔍 Used for semantic vector search (e.g., similar resumes)
QDRANT_HOST=http://localhost:7000
```
🧠 Step 2: Backend Setup (Python + Flask)

```
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Create a .env file:

GEMINI_API_KEY=your-key
QDRANT_HOST=http://localhost:6333
QDRANT_COLLECTION=participants
Then run the server:

python app.py
```

💻 Step 3: Frontend Setup (React + TypeScript)
```
cd frontend
npm install
npm run dev
The app will run at http://localhost:3000
```

🧠 Tech Stack
Layer	Tech
Frontend	React, TypeScript, Tailwind, ShadCN
Backend	Flask, Python, Gemini
Vector DB	Qdrant (Docker)
Database	Qdrant collections as semantic store
Deployment	Docker, Vercel (frontend), Fly.io/Render (backend)


🛠️ TODO
 Add authentication (e.g., Clerk, Firebase)

 Resume PDF parser with embedding

 Admin dashboard for event organizers

 User analytics & feedback dashboard
