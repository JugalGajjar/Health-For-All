// Login Form
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `username=${username}&password=${password}`
        });

        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            alert('Invalid credentials');
        }
    });
}

// Register Form
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        // Check if passwords match
        if (document.getElementById('password').value !== document.getElementById('confirm_password').value) {
            alert('Passwords do not match');
            return;
        }

        // Create form data
        const formData = new FormData(document.getElementById('registerForm'));

        // Send form data to the server
        const response = await fetch('/register', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            window.location.href = '/';
        } else {
            alert('Registration failed');
        }
    });
}

// View Consultations
if (document.getElementById('consultationsList')) {
    async function fetchConsultations() {
        const response = await fetch('/view_consultations');
        const consultations = await response.json();
        const list = document.getElementById('consultationsList');

        consultations.forEach(consultation => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="/patient_consultation/${consultation.consultation_id}">
                    Consultation #${consultation.consultation_id} - ${consultation.status}
                </a>
            `;
            list.appendChild(li);
        });
    }

    fetchConsultations();
}

// Patient Consultation Form
if (document.getElementById('consultationForm')) {
    const consultationId = window.location.pathname.split('/').pop();

    document.getElementById('consultationForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const status = document.getElementById('status').value;
        const comments = document.getElementById('comments').value;

        const response = await fetch(`/patient_consultation/${consultationId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `status=${status}&comments=${comments}`
        });

        if (response.ok) {
            window.location.href = '/view_consultations';
        } else {
            alert('Failed to update consultation');
        }
    });
}

// Search Patient Profile Form
if (document.getElementById('searchForm')) {
    document.getElementById('searchForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        console.log(`Searching for username: ${username}`);  // Debug log

        const response = await fetch('/search_patient_profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `username=${encodeURIComponent(username)}`
        });

        if (response.ok) {
            const htmlContent = await response.text();
            document.getElementById('patientDetails').innerHTML = htmlContent;
        } else {
            alert('Failed to search for patient');
        }
    });
}

// Schedule Appointment Form
if (document.getElementById('appointmentForm')) {
    document.getElementById('appointmentForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const slots = [
            document.getElementById('slot1').value,
            document.getElementById('slot2').value,
            document.getElementById('slot3').value,
            document.getElementById('slot4').value,
            document.getElementById('slot5').value
        ];

        const response = await fetch('/schedule_appointment', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ slots })
        });

        if (response.ok) {
            alert('Appointment slots submitted successfully');
        } else {
            alert('Failed to submit slots');
        }
    });
}