from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import render_template_string, redirect, url_for, session
from twilio.rest import Client
import os
import re
import requests  # <-- Add this for Telegram API

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')  # Use a strong secret in production!
CORS(app)

# Configure Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

db = SQLAlchemy(app)

# Define the Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Simple admin user model (for demo)
class AdminUser(UserMixin):
    id = 1
    username = "admin"
    password = "Mongoue5050"  # Change this!

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@login_manager.user_loader
def load_user(user_id):
    if user_id == "1":
        return AdminUser()
    return None

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()

    if not name or not email or not message:
        return jsonify({'error': 'All fields are required.'}), 400
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email address.'}), 400
    if len(message) > 2000:
        return jsonify({'error': 'Message too long.'}), 400

    try:
        # Save to database
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()

        # Send Telegram message instead of email
        telegram_token = "7987408065:AAGTJUBrb9tkWFj7pTMae25iJVQOXPIOH_U"
        chat_id = "6026873134"  # Your Telegram user ID
        telegram_message = f"New Contact Form Submission:\nName: {name}\nEmail: {email}\nMessage:\n{message}"
        telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": telegram_message}
        telegram_response = requests.post(telegram_url, data=payload)
        if not telegram_response.ok:
            print('Telegram error:', telegram_response.text)
            return jsonify({'success': False, 'error': 'Failed to send Telegram message.'}), 500

        # Send WhatsApp message via Twilio (unchanged)
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_from = "whatsapp:+14155238886"  # Twilio Sandbox number
        whatsapp_to = "whatsapp:+237671290684"  # <-- Replace with your WhatsApp number

        client = Client(account_sid, auth_token)
        whatsapp_body = f"New Contact Form Submission:\nName: {name}\nEmail: {email}\nMessage:\n{message}"
        client.messages.create(
            body=whatsapp_body,
            from_=whatsapp_from,
            to=whatsapp_to
        )

        return jsonify({'success': True, 'message': 'Thank you for contacting us! We will respond soon.'}), 200
    except Exception as e:
        print('Error:', e)
        return jsonify({'success': False, 'error': 'Failed to send message. Please try again later.'}), 500

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Admin login page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == AdminUser.username and password == AdminUser.password:
            login_user(AdminUser())
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template_string("""
                <h2>Admin Login</h2>
                <form method="post">
                    <input name="username" placeholder="Username"><br>
                    <input name="password" type="password" placeholder="Password"><br>
                    <button type="submit">Login</button>
                </form>
                <p style="color:red;">Invalid credentials</p>
            """)
    return render_template_string("""
        <h2>Admin Login</h2>
        <form method="post">
            <input name="username" placeholder="Username"><br>
            <input name="password" type="password" placeholder="Password"><br>
            <button type="submit">Login</button>
        </form>
    """)

# Admin logout
@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

# Protect admin dashboard and messages
@app.route('/admin')
@login_required
def admin_dashboard():
    return send_from_directory('static/admin', 'index.html')

@app.route('/admin/messages')
@login_required
def view_messages():
    contacts = Contact.query.all()
    return jsonify([
        {'id': c.id, 'name': c.name, 'email': c.email, 'message': c.message}
        for c in contacts
    ])

@app.route('/admin/messages/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    contact = Contact.query.get_or_404(message_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'success': True})

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug_mode)
