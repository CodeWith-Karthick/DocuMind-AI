# 📄 DocuMind AI – Intelligent Document Q&A System

**DocuMind AI** is a Flask-based web application that allows users to upload documents, store vector embeddings for context-aware search, and get accurate answers either from the uploaded content or via fallback to a powerful LLM (Groq's LLaMA 3).

---

## 🚀 Features

- 🔐 User registration, login, and password recovery via email
- 📤 Upload and process unstructured documents
- 🔍 Vector-based semantic search with **LangChain + Chroma**
- 🧠 Fallback to **Groq LLM (LLaMA 3)** when no relevant context is found
- 📚 Chunk viewer for uploaded documents
- 🗑️ Clear vector database
- ✉️ Email integration for password reset

---

## 📁 Directory Structure

DocuMind-AI/
│
├── app.py # Main Flask app
├── users.db # SQLite database
├── uploads/ # Uploaded files
├── doc_db/ # Chroma vector DB files
├── templates/ # HTML templates
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── secret.html
│ ├── reset_password.html
│ └── forget.html
└── static/ # Static assets like CSS, JS, etc.

markdown
Copy
Edit

---

## ⚙️ Tech Stack

- **Flask** – Web Framework
- **SQLite + SQLAlchemy** – Database
- **Flask-Login** – User Session Management
- **LangChain** – Embeddings & Document Chunks
- **Chroma** – Vector Store
- **HuggingFace Embeddings** – `all-MiniLM-L6-v2`
- **Groq LLM** – `llama3-8b-8192` model for fallback Q&A
- **SMTP (Gmail)** – For sending password recovery codes

---

## 🔑 Environment Variables

Create a `.env` file in the root directory and add:

GROQ_API_KEY=your_groq_api_key
Make sure python-dotenv is installed.

🔧 Installation & Run
1. Clone the Repo

git clone https://github.com/CodeWith-Karthick/DocuMind-AI.git
cd DocuMind-AI
2. Install Dependencies

pip install -r requirements.txt
If requirements.txt is missing, install manually:


pip install flask flask_sqlalchemy flask_login python-dotenv langchain langchain-community chromadb sentence-transformers unstructured requests
3. Run the App

python app.py
Visit http://localhost:5001

📬 Email Recovery Setup
Ensure you update the following in send_recovery_email():


from_email = "noreplyyourapp@gmail.com"
from_password = "your_app_password"  # App password, not Gmail login password
Enable 2-Step Verification in Gmail and generate an App Password to use here.

🧪 Example Flow
Register an account

Login

Upload a PDF or DOCX file

Ask a question related to the content

If no match is found, AI will suggest fallback to Groq

Optionally clear all chunks and upload another file

📄 Sample Query

POST /ask_llm
{
  "user_query": "What is a heart attack?"
}
If a match is found in vector DB, it is returned. Otherwise:


{
  "needs_permission": true,
  "message": "I couldn't find an answer in your document. Can I use AI to help?"
}
❗ Security Note
Your current Groq API key and Gmail credentials are hardcoded – move them to .env for security.

Rate-limit email requests in production to avoid abuse.

💡 Future Improvements
Add PDF parsing preview

Add file format validation

Improve UI with Tailwind or Bootstrap

Log user questions and AI responses

Use Redis or PostgreSQL for scalable DB

🧑‍💻 Author
Karthick G
🔗 GitHub

📜 License
This project is licensed under the MIT License.
