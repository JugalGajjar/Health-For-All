from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
import ollama

app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

USER_DATA_FILE = 'users.json'

# Replace <your_password> with your actual database password
uri = "mongodb+srv://kaustik:91NAtni1N5AMizF9@patientdetails.ldaao.mongodb.net/?retryWrites=true&w=majority&appName=PatientDetails"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)
    exit()  # Exit the script if connection fails

# Select the database and collection
db = client["patient"]  # Change as per your DB name
collection = db["Patient_User"]  # Collection for storing patient details

# Load user data
def load_users():
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If JSON is invalid, return an empty dictionary
            return {}
    return {}

# Save user data
def save_users(users):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Home route
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        users = load_users()
        if user_id in users and check_password_hash(users[user_id]['password'], password):
            session['user_id'] = user_id
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials, try again!')
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = generate_password_hash(request.form['password'])
        users = load_users()

        if user_id in users:
            return render_template('register.html', error='User ID already exists!')
        
        # Add user to the local JSON file
        users[user_id] = {'password': password, 'profile': {}}
        save_users(users)

        # Add user to MongoDB
        user_data = {
            'user_id': user_id,
            'password': password,
            'profile': {}
        }
        try:
            # Insert the user data into MongoDB
            collection.insert_one(user_data)
            print("Patient data inserted successfully to MongoDB!")
        except Exception as e:
            print("Data insertion to MongoDB failed:", e)

        session['user_id'] = user_id  # Store user session upon registration
        return redirect(url_for('registration'))  # Proceed to profile registration

    return render_template('register.html')

# Multi-step Registration
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        users = load_users()
        user_id = session['user_id']
        # Collect all profile data from the registration form
        users[user_id]['profile'] = request.form.to_dict()
        save_users(users)

        # Also update the profile in MongoDB
        try:
            collection.update_one(
                {'user_id': user_id},
                {'$set': {'profile': users[user_id]['profile']}}
            )
            print("Profile updated successfully in MongoDB!")
        except Exception as e:
            print("Profile update in MongoDB failed:", e)

        return redirect(url_for('dashboard'))

    return render_template('registration.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    users = load_users()
    user_id = session['user_id']
    profile = users.get(user_id, {}).get('profile', {})
    return render_template('dashboard.html', profile=profile)

# Medical Profile route
@app.route('/medical_profile')
def medical_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    users = load_users()
    user_id = session['user_id']
    profile = users.get(user_id, {}).get('profile', {})
    return render_template('medical_profile.html', profile=profile)

@app.route('/start_consultation', methods=['GET', 'POST'])
def start_consultation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        users = load_users()

        # Capture form data
        has_happened_before = request.form['has_happened_before']
        symptoms = request.form['symptoms']
        severity = request.form['severity']
        duration = request.form['duration']
        med = request.form['medication']

        # Create a consultation entry with a unique key using the date
        consultation_key = f'consultation_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
        consultation_data = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'has_happened_before': has_happened_before,
            'symptoms': symptoms,
            'severity': severity,
            'duration': duration,
            'current_medications': med
        }

        # Store consultation data locally
        if 'consultations' not in users[user_id]:
            users[user_id]['consultations'] = {}
        users[user_id]['consultations'][consultation_key] = consultation_data

        message = users[user_id]
        for key in message:
            if "beneficiary" in key:
                del message[key]
        del message["password"]
        message = "You are a medical assistant providing an initial diagnosis based on the patient's symptoms. Your response should be concise, accurate, and directly address the most likely causes of the symptoms. Avoid unnecessary explanations and focus on actionable insights. Following is the every detail you need to consider:\n" + \
            str(message) + \
            "\n" + \
            "**Task:**\n\1Summarize patient details.n2. List the **most likely causes** of these symptoms, ordered by probability.\n3. Provide **immediate recommendations** for the patient." + \
            "**Response Format:**1. **Patient Summary:**\n[Brief summary]\n" + \
            "2. **Most Likely Causes:**\n- Cause 1: [Brief explanation]\n- Cause 2: [Brief explanation]\n- Cause 3: [Brief explanation]\n" + \
            "3. **Immediate Recommendations:**\n- Recommendation 1: [Actionable step]\n- Recommendation 2: [Actionable step]\n- Recommendation 3: [Actionable step]"

        response = ollama.generate(model='deepseek-r1:1.5b', prompt=message)
        response = response['response'][response['response'].index("</think>")+9:]
        print(response)

        id_key = f'initial_diagnosis{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
        if 'initial_diagnosis' not in users[user_id]:
            users[user_id]['initial_diagnosis'] = {}
        users[user_id]['initial_diagnosis'][id_key] = response

        save_users(users)

        # Store consultation data in MongoDB
        try:
            collection.update_one(
                {'user_id': user_id},
                {'$set': {f'data.{consultation_key}': consultation_data}},
                upsert=True
            )
            print("Consultation data saved to MongoDB successfully!")
        except Exception as e:
            print("Failed to save consultation data to MongoDB:", e)

        return redirect(url_for('dashboard'))

    return render_template('start_consultation.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
