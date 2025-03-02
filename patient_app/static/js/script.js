document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded!");

    // Handle password confirmation validation on registration page
    const passwordField = document.getElementById("password");
    const confirmPasswordField = document.getElementById("confirm_password");
    const passwordError = document.getElementById("password_error");

    if (passwordField && confirmPasswordField) {
        confirmPasswordField.addEventListener("input", validatePasswords);
    }

    // Multi-step Registration Form
    const nextButtons = document.querySelectorAll(".next-step");
    const prevButtons = document.querySelectorAll(".prev-step");
    const formSteps = document.querySelectorAll(".form-step");
    let currentStep = 0;

    function showStep(stepIndex) {
        formSteps.forEach((step, index) => {
            step.style.display = (index === stepIndex) ? "block" : "none";
        });
    }

    // Show the first step initially
    showStep(currentStep);

    nextButtons.forEach(button => {
        button.addEventListener("click", function () {
            if (validateCurrentStep()) {
                currentStep++;
                showStep(currentStep);
            }
        });
    });

    prevButtons.forEach(button => {
        button.addEventListener("click", function () {
            currentStep--;
            showStep(currentStep);
        });
    });

    // Password Validation
    function validatePasswords() {
        const password = passwordField.value;
        const confirmPassword = confirmPasswordField.value;

        if (password !== confirmPassword) {
            passwordError.style.display = "block";
        } else {
            passwordError.style.display = "none";
        }
    }

    // Validate the current step before moving to the next one
    function validateCurrentStep() {
        const inputs = formSteps[currentStep].querySelectorAll("input");
        let valid = true;

        inputs.forEach(input => {
            if (input.required && !input.value.trim()) {
                input.style.borderColor = "red";
                valid = false;
            } else {
                input.style.borderColor = "";
            }
        });

        return valid;
    }

    // Handle the medical condition dropdown to show "Other" condition input
    const medicalConditionSelect = document.getElementById("medical_condition");
    const otherConditionInput = document.getElementById("other_condition");

    if (medicalConditionSelect) {
        medicalConditionSelect.addEventListener("change", function () {
            if (this.value === "Other") {
                otherConditionInput.style.display = "block";
            } else {
                otherConditionInput.style.display = "none";
            }
        });
    }
});
