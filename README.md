# 🛡️ User Authentication System - MediFetch (Front-End Only)

This is a **Flask-based front-end application** for user authentication, password recovery via email, and secure login/logout flows.

---

## 🚀 Features

- ✅ User Registration with validation
- ✅ Secure Login with Flask-Login
- ✅ Password recovery via email (recovery code with expiry)
- ✅ Password reset with validation (uppercase + number + min length)
- ✅ Logged-in protected route
- ✅ Logout functionality
- ✅ Download option (example: drug report PDF)

---

## 🛠️ Tech Stack

- **Backend Framework**: Flask (Python)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Authentication**: Flask-Login
- **Email Service**: Gmail SMTP
- **Templating**: Jinja2 (via HTML templates)
- **Password Security**: PBKDF2 Hashing
- **Environment Variables**: Python Dotenv

---

## 📁 Project Structure

User_Auth_Flask/
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── forget.html
│   ├── reset_password.html
│   ├── secret.html
├── static/
│   └── Drug report.pdf
├── app.py
├── .env
├── requirements.txt
├── README.md
🧪 Setup Instructions
🔹 1. Clone the Repository

Copy
Edit
git clone https:https://github.com/CodeWith-Karthick/cts-front-end.git
cd User_Auth_Flask
🔹 2. Set Up a Virtual Environment

Copy
Edit
python -m venv env
source env/bin/activate   # on macOS/Linux
env\Scripts\activate      # on Windows
🔹 3. Install Dependencies

Copy
Edit
pip install -r requirements.txt
Don’t forget to create a .env file and include Gmail credentials for password recovery.

🔹 4. Run the App

Copy
Edit
python app.py
Access the app at: http://localhost:5001

🔐 Sample .env File
ini
Copy
Edit
EMAIL_USER=your_email
EMAIL_PASS=your_app_password_here
❗ Note
This is only the front-end component. Backend data analysis, user insights, or dashboards are assumed to be part of a separate module.

📬 License
This project is part of the MediFetch ecosystem. Feel free to contribute or fork for educational purposes.

yaml
Copy
Edit

---

## Screenshots
![Screenshot (1712)](https://github.com/user-attachments/assets/f557468c-9b37-4d8f-9cc8-de402c64fd1f)
![Screenshot (1713)](https://github.com/user-attachments/assets/5751d24f-18b1-4d09-8f55-4cfd73d1cc86)
![Screenshot (1714)](https://github.com/user-attachments/assets/5d5666ee-1bef-4b7e-bb44-e132c8a023dc)
![Screenshot (1715)](https://github.com/user-attachments/assets/e18e7879-0008-4d45-9aa0-3ac8391e754a)
![Screenshot (1716)](https://github.com/user-attachments/assets/6b5ced52-3e51-404c-a0c0-b32b79b025a9)



