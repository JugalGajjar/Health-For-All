from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Load JSON data
def doctor_load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                data = []
                data = json.load(file)
                return data
        except json.JSONDecodeError:
            # If JSON is invalid, return an empty dictionary
            return []
    return []

def load_json(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If JSON is invalid, return an empty dictionary
            return {}
    return {}

def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    doctors = doctor_load_json('doctors.json')
    doctor = next((d for d in doctors if d['username'] == username), None)
    if doctor and check_password_hash(doctor['password'], password):
        session['doctor_username'] = username
        return redirect(url_for('dashboard'))
    return "Invalid credentials", 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        doctor_data = {
            "username": request.form['username'],
            "firstname": request.form['firstname'],
            "lastname": request.form['lastname'],
            "contact_number": request.form['contact_number'],
            "email": request.form['email'],
            "hospital_name": request.form['hospital_name'],
            "hospital_address": request.form['hospital_address'],
            "specialization": request.form['specialization'],
            "password": generate_password_hash(request.form['password'])  # Hash the password
        }
        doctors = doctor_load_json('doctors.json')
        doctors.append(doctor_data)
        save_json('doctors.json', doctors)
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'doctor_username' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

@app.route('/view_consultations')
def view_consultations():
    if 'doctor_username' not in session:
        return redirect(url_for('home'))

    consultations = load_json('consultations.json')
    doctor_username = session['doctor_username']

    # Fetch consultations for the logged-in doctor
    doctor_consultations = consultations.get(doctor_username, [])

    return render_template('view_consultations.html', consultations=doctor_consultations)

@app.route('/patient_consultation/<consultation_id>', methods=['GET', 'POST'])
def patient_consultation(consultation_id):
    if 'doctor_username' not in session:
        return redirect(url_for('home'))

    consultations = load_json('consultations.json')
    doctor_username = session['doctor_username']

    # Find the specific consultation
    consultation = None
    for consult in consultations.get(doctor_username, []):
        if consult['id'] == consultation_id:
            consultation = consult
            break

    if not consultation:
        return "Consultation not found", 404

    if request.method == 'POST':
        # Update the consultation status and comments
        consultation['status'] = request.form['status']
        consultation['comments'] = request.form.get('comments', '')

        # Save the updated consultations
        save_json('consultations.json', consultations)
        return redirect(url_for('view_consultations'))

    return render_template('patient_consultation.html', consultation=consultation)

@app.route('/search_patient_profile', methods=['GET', 'POST'])
def search_patient_profile():
    if 'doctor_username' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        print(f"Searching for username: {username}")  # Debug log

        users = load_json('/Users/jugalgajjar/Downloads/Experiments/Team-V5-George-Hacks/patient_app/users.json')

        patient = users.get(username)  # Get the user data by username
        if patient:
            print(f"Patient data found: {patient['profile']}")  # Debug log
            return jsonify(patient['profile'])  # Return JSON response
        else:
            return jsonify({})  # Return empty JSON if not found

    return render_template('search_patient_profile.html')

@app.route('/schedule_appointment')
def schedule_appointment():
    if 'doctor_username' not in session:
        return redirect(url_for('home'))
    return render_template('schedule_appointment.html')

@app.route('/logout')
def logout():
    session.pop('doctor_username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)