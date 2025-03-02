document.addEventListener("DOMContentLoaded", function () {
    console.log("Accessibility JavaScript Loaded!");

    let isTTSEnabled = false;
    let isSTTEnabled = false;
    let language = 'en-US'; // Default language (English)
    const languageSelect = document.getElementById('language-select');
    const userIdInput = document.getElementById('user-id');
    const passwordInput = document.getElementById('password');

    // Handle language selection change
    if (languageSelect) {
        languageSelect.addEventListener('change', function () {
            language = languageSelect.value;
            if (isTTSEnabled) {
                speakText('Language changed to ' + language, language); // Announce language change
            }
        });
    }

    // Function to toggle Text-to-Speech
    function toggleTextToSpeech() {
        isTTSEnabled = !isTTSEnabled;

        if (isTTSEnabled) {
            speakText('Text-to-speech enabled', language);
            // Add a listener for form focus or changes to input fields
            userIdInput.addEventListener('focus', function () {
                speakText('Please enter your user ID', language);
            });

            passwordInput.addEventListener('focus', function () {
                speakText('Please enter your password', language);
            });
        } else {
            speakText('Text-to-speech disabled', language);
        }
    }

    // Function to toggle Speech-to-Text
    function toggleSpeechToText() {
        isSTTEnabled = !isSTTEnabled;

        if (isSTTEnabled) {
            startSpeechToText();
        } else {
            stopSpeechToText();
        }
    }

    // Function to speak text (Text-to-Speech)
    function speakText(text, lang) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang; // Set the language based on user selection
        speechSynthesis.speak(utterance);
    }

    // Speech-to-Text Functionality (using Web Speech API)
    let recognition;

    function startSpeechToText() {
        if (!('SpeechRecognition' in window)) {
            alert("Speech Recognition is not supported in your browser.");
            return;
        }

        // Initialize SpeechRecognition
        recognition = new SpeechRecognition();
        recognition.lang = language; // Set the language of the recognition
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onstart = function () {
            speakText('Speech-to-text enabled. Please start speaking.', language);
        };

        recognition.onresult = function (event) {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }

            if (transcript) {
                console.log('Speech Input: ', transcript);
                if (isTTSEnabled) {
                    speakText('You said: ' + transcript, language); // Repeat back what was said
                }
            }
        };

        recognition.onerror = function (event) {
            speakText('Speech recognition error occurred. Please try again.', language);
        };

        recognition.onend = function () {
            if (isSTTEnabled) {
                startSpeechToText(); // Automatically restart recognition after ending
            }
        };

        recognition.start();
    }

    function stopSpeechToText() {
        if (recognition) {
            recognition.stop();
            speakText('Speech-to-text disabled.', language);
        }
    }

    // Example buttons to toggle TTS and STT
    document.getElementById("toggle-tts").addEventListener('click', toggleTextToSpeech);
    document.getElementById("toggle-stt").addEventListener('click', toggleSpeechToText);
});
