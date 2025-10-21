Lab 3: Speech Processing Scripts

This repository contains Python scripts demonstrating audio processing with Google Cloud Speech-to-Text and Text-to-Speech APIs.

Prerequisites

Clone the repository and navigate to it:

git clone <repo-url>
cd lab3


Set up a virtual environment and install dependencies:

python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows PowerShell
pip install -r requirements.txt


Google Cloud setup

Obtain a service account JSON key from your Google Cloud project.

Enable required APIs:

Cloud Speech-to-Text API

Cloud Text-to-Speech API

Set the environment variable for authentication:

$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"


Replace the path with your own JSON key.

Scripts Usage
1. Basic Speech-to-Text
python scripts\1_basic_stt.py audio_samples\test_audio.mp3


Transcribes the audio file.

Prints transcript, confidence, and word-level timings.

2. Confidence Scoring
python scripts\2_confidence_scoring.py audio_samples\test_audio.mp3


Computes detailed confidence scores for each word.

Helps analyze transcription reliability.

3. PII Redaction
python scripts\3_pii_redaction.py audio_samples\test_audio.mp3


Detects and redacts personally identifiable information (PII) from transcripts.

Useful for anonymizing sensitive data.

4. STT → Summarize → TTS Pipeline
python scripts\4_tts_summary.py audio_samples\test_audio.mp3


Transcribes the audio.

Summarizes the transcript (extractive summary).

Generates a spoken summary audio file (output_summary.mp3).

Notes

Ensure the audio file is in audio_samples/ or provide the full path.



Run the script with an audio file

python scripts\1_basic_stt.py audio_samples\test_audio.mp3
