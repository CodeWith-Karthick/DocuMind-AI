import smtplib
from datetime import datetime, timedelta
import secrets
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import werkzeug
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, flash, get_flashed_messages
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import IntegrityError
from flask import flash, redirect, url_for, request, render_template
import re 
from flask import Flask, render_template, request
from flask import Flask, render_template, request
from flask import Flask, request, render_template, jsonify
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import requests


load_dotenv()


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SECRET_KEY'] = '3f8c2e7a9b4d12f7c6a8e9f1b2d3c4e5f6a7b8c9d0e1f2a3b4c5d6e7f8g9h0i1'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

CHROMA_DB_DIR = "doc_db"
os.makedirs(CHROMA_DB_DIR, exist_ok=True)

# Initialize embedding model
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectordb = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embedding)

# Groq API setup
GROQ_API_KEY = "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"  # Replace with your actual key
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(unique=False, nullable=False)


class RecoveryCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    expiry_time = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', back_populates='recovery_codes')


User.recovery_codes = db.relationship('RecoveryCode', back_populates='user', lazy=True)

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_username:
            flash("Username already exists. Please choose a different one.", "error")
            return render_template("register.html", username=username, email=email)

        if existing_email:
            flash("Email already exists. Please use a different email.", "error")
            return render_template("register.html", username=username, email=email)

        if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[A-Z]", password):
            flash("Password must be at least 8 characters long, contain one uppercase letter, and one number.", "error")
            return render_template("register.html", username=username, email=email)

        hash_password = generate_password_hash(password, method='pbkdf2:sha256:600000', salt_length=8)

        try:
            user = User(username=username, email=email, password=hash_password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful! You can now log in.", "success")
            return redirect(url_for("login"))

        except IntegrityError:
            db.session.rollback()
            flash("An error occurred. Please try again.", "error")
            return render_template("register.html", username=username, email=email)

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User.query.filter_by(username=email).first()

        if user:
            if werkzeug.security.check_password_hash(user.password, password):
                login_user(user)
                flash("Login successful!", "success")  # Store the success message
                return redirect(url_for("secretz"))  # Redirect to the next page
            else:
                flash("Password is incorrect!", "error")
        else:
            flash("Username or email is incorrect!", "error")

    return render_template("login.html")

def send_recovery_email(to_email, code):
    from_email = "noreplymedifetch@gmail.com"
    from_password = "alefcqkhfwehxktp"
    subject = 'Password Recovery Code-MediFetch'
    body = (f'Your recovery code is {code}.'
            f'It will expire in 15 minutes.'
            f'If Code expired kindly press resend code')

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, from_password)
            server.sendmail(from_email, to_email, msg.as_string())
            print(f"Recovery email sent successfully! to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")


@app.route('/forgetpassword', methods=['GET', 'POST'])
def forgetpassword():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a 4-byte hex recovery code
            code = secrets.token_hex(4)
            expiry_time = datetime.utcnow() + timedelta(minutes=15)

            # Store recovery code in the database
            recovery_code = RecoveryCode(user_id=user.id, code=code, expiry_time=expiry_time)
            db.session.add(recovery_code)
            db.session.commit()

            # Send recovery email
            send_recovery_email(user.email, code)

            flash(f"A recovery code has been sent to your email! {email}","success")
            return redirect(url_for('reset_password'))  # Redirect to reset password page

        else:
            flash("Invalid email. Please enter a registered email.", "error")

    return render_template("forget.html")
    

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get("email")
        code = request.form.get("code")
        new_password = request.form.get("password")

        print(email, code, new_password)

        # Check if the email exists
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Invalid email. Please enter a registered email.", "error")
            return redirect(url_for('reset_password'))

        # Check if recovery code exists and is still valid
        recovery_code = RecoveryCode.query.filter_by(user_id=user.id, code=code).first()
        if not recovery_code or recovery_code.expiry_time < datetime.utcnow():
            flash("Invalid or expired recovery code. Request a new one.", "error")
            return redirect(url_for('reset_password'))

        # Validate password strength
        if len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(char.isupper() for char in new_password):
            flash("Password must be at least 8 characters long, contain an uppercase letter and a number.", "error")
            return redirect(url_for('reset_password'))

        # Update user password
        hash_password = generate_password_hash(new_password, method='pbkdf2:sha256:600000', salt_length=8)
        user.password = hash_password
        db.session.delete(recovery_code)  # Delete used recovery code
        db.session.commit()

        flash("Your password has been updated successfully!", "success")
        return redirect(url_for('login'))

    return render_template("reset_password.html")


@app.route('/secretz', methods=['GET', 'POST'])
@login_required
def secretz():
    message = ""
    if request.method == "POST":
        if "document" in request.files:
            file = request.files["document"]
            if file and file.filename:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                try:
                    loader = UnstructuredFileLoader(filepath)
                    docs = loader.load()

                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    chunks = splitter.split_documents(docs)

                    vectordb.add_documents(chunks)
                    vectordb.persist()
                    message = f"✅ Stored {len(chunks)} chunks from '{file.filename}'"
                except Exception as e:
                    message = f"❌ Error processing file: {str(e)}"
                finally:
                    os.remove(filepath)

    return render_template("secret.html", message=message)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route('/download', methods=['GET'])
@login_required
def download():
    if request.method == "GET":
        return send_from_directory('static', 'Drug report.pdf')


@app.route("/home", methods=["GET", "POST"])
def home():
    reviews = []
    drug_name = ""

    if request.method == "POST":
        drug_name = request.form["drug_name"].strip()
        

    return render_template("screte.html", drug=drug_name, reviews=reviews)


@app.route('/secret', methods=['GET'])
def secret():
    """Display the input form"""
    return render_template('secret.html')


@app.route("/hello", methods=["GET", "POST"])
def hello():
    message = ""
    if request.method == "POST":
        if "document" in request.files:
            file = request.files["document"]
            if file and file.filename:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                try:
                    loader = UnstructuredFileLoader(filepath)
                    docs = loader.load()

                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    chunks = splitter.split_documents(docs)

                    vectordb.add_documents(chunks)
                    vectordb.persist()
                    message = f"✅ Stored {len(chunks)} chunks from '{file.filename}'"
                except Exception as e:
                    message = f"❌ Error processing file: {str(e)}"
                finally:
                    os.remove(filepath)

    return render_template("secret.html", message=message)


@app.route("/ask_llm", methods=["POST"])
def ask_llm():
    user_query = request.json.get("user_query")

    # Search in vector DB
    results = vectordb.similarity_search_with_score(user_query, k=5)
    relevant_context = "\n\n".join([doc.page_content for doc, score in results if score < 0.75])

    if relevant_context:
        return jsonify({
            "answer": relevant_context
        })
    else:
        return jsonify({
            "needs_permission": True,
            "message": "I couldn't find an answer in your document. Can I use AI to help?"
        })

@app.route("/ask_groq", methods=["POST"])
def ask_groq():
    user_query = request.json.get("user_query")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_query}
        ]
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return jsonify({"answer": data["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"error": f"❌ Failed to get answer from Groq: {str(e)}"}), 500

@app.route("/get_chunks", methods=["GET"])
def get_chunks():
    try:
        all_docs = vectordb.get()
        chunks = []

        for i, doc in enumerate(all_docs["documents"]):
            metadata = all_docs["metadatas"][i]
            chunks.append({
                "id": i,
                "content": doc,
                "metadata": metadata
            })

        return jsonify({"chunks": chunks})
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve chunks: {str(e)}"}), 500

@app.route("/clear_db", methods=["POST"])
def clear_db():
    try:
        vectordb._collection.delete(where={})  # Clear all entries
        return jsonify({"message": "✅ All data cleared. You can upload a new document."})
    except Exception as e:
        return jsonify({"error": f"❌ Failed to clear database: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
