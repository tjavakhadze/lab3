# Lab 3 – Audio AI Pipeline

**Course:** Building AI powered applications  
**Student:** Tinatin Javakhadze

---

## Overview

This project implements an end-to-end **Audio AI Pipeline** that processes speech recordings to generate redacted transcripts, audio summaries, and audit logs. The pipeline demonstrates practical applications of audio preprocessing, speech-to-text transcription, confidence scoring, named entity recognition, PII redaction, and text-to-speech synthesis.

The goal of this assignment was to design a modular, robust, and reproducible pipeline that could operate using free or offline resources while handling real-world challenges such as transcription error and sensitive information in audio recordings.

---

## Functional Requirements Addressed

1. **Input Handling:** Accepts audio files in multiple formats (MP3, WAV, AIFF).
2. **Preprocessing:** Prepares audio for processing.
3. **Speech-to-Text:** Uses Google Web Speech API with retry logic, with offline Sphinx as a fallback.
4. **Confidence Scoring:** Computes a **multi-factor confidence score** using API confidence, signal-to-noise ratio (SNR), and perplexity.
5. **PII Redaction:** Redacts sensitive information using **regex patterns** (emails, phone numbers, credit cards...) and **spaCy NER** (names).
6. **Summarization:** Extractive summarization produces a concise textual summary.
7. **Text-to-Speech:** Generates an audio summary via gTTS.
8. **Audit Logging:** Produces a structured JSON audit log containing metrics such as confidence, SNR, number of redactions, and summary length.
9. **Error Handling:** Includes input validation, retry logic, and clear messages for transcription failures or missing files.

---

## Project Structure

```text
lab3/
│
├─ audio_samples/
│   ├─ test_audio.mp3  # Example audio input
│   ├─ low_quality_phone_call.mp3
│   └─ clean_audio.mp3
│
├─ scripts/
│   ├─ 1_basic_stt.py
│   ├─ 2_confidence_scoring.py
│   ├─ 3_pii_redaction.py
│   ├─ 4_tss_summary.py
│
├─ tools/
│   └─ make_submission_zip.py
│
├─ venv/               # Python virtual environment
├─ audio_pipeline.py    # Main pipeline script
├─ requirements.txt
├─ .env.example
├─ .env
├─ LAB-3-HOMEWORK.md   # reflection
└─ README.md
```

## Setup Instructions

0. **It words with Python 3.12.3 and perhaps lower but not 3.13.
   And I'm using numpy version 1.26.4**

1. **Clone the repository:**

```bash
git clone [repo URL]
cd lab3
```

---

## Create and activate a virtual environment:

python -m venv venv

# Windows

venv\Scripts\Activate.ps1

# macOS/Linux

source venv/bin/activate

# Install requirements

pip install -r requirements.txt

## Copy .env.example to .env and modify:

INPUT_AUDIO=audio_samples/test_audio.mp3
VOICE_NAME=en-US-Neural2-A
SUMMARY_SENTENCES=2

### I have provided 3 test cases. When you run another one, just change the INPUT_AUDIO=audio_samples/test_audio.mp3 with INPUT_AUDIO=audio_samples/clean_audio.mp3 or INPUT_AUDIO=audio_samples/low_quality_phone_call.mp3

## Execution

Run the pipeline:

```bash
python audio_pipeline.py
```

---

## Outputs

### output_transcript.txt → Redacted transcript

### output_summary.mp3 → Audio summary

### audit.log → JSON audit log of processing metrics

---

## References

**pydub Documentation**

**SpeechRecognition Documentation**

**spaCy Documentation**

**gTTS Documentation**

---




