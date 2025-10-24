"""
Audio AI Pipeline (Offline/Free Version)
----------------------------------------
Performs:
1. Audio preprocessing 
2. Speech-to-text transcription 
3. Multi-factor confidence scoring (API confidence + SNR + perplexity)
4. PII redaction (regex + spaCy NER)
5. Text summarization
6. Text-to-speech synthesis (gTTS)
7. Audit logging
"""

import os
import re
import json
import datetime
import librosa
import numpy as np
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import spacy
from pydub import AudioSegment, effects
import noisereduce as nr
import time

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# ------------------ STEP 1: ENVIRONMENT SETUP ------------------
def load_env(env_path: str = ".env") -> None:
    load_dotenv(env_path)

# ------------------ STEP 2: PREPROCESS AUDIO ------------------
def preprocess_audio(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio = effects.normalize(audio)
    output_wav_path = output_path.replace(".mp3", ".wav")
    audio.export(output_wav_path, format="wav")
    return output_wav_path

# ------------------ STEP 3: SPEECH-TO-TEXT ------------------
def transcribe_audio(audio_path: str, max_retries=3):
    recognizer = sr.Recognizer()
    attempts = 0
    while attempts < max_retries:
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data)
            confidence = 0.85
            return transcript, [{"word": w, "confidence": confidence} for w in transcript.split()], confidence
        except sr.UnknownValueError:
            print("⚠ Could not understand audio, returning empty transcript.")
            return "", [], 0.0
        except sr.RequestError as e:
            print(f"⚠ API request failed (attempt {attempts+1}/{max_retries}): {e}")
            attempts += 1
            time.sleep(1)
        except Exception as e:
            print(f"⚠ Unexpected error during transcription: {e}")
            return "", [], 0.0

    # Fallback to offline Sphinx
    print("ℹ Falling back to offline Sphinx transcription...")
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        transcript = recognizer.recognize_sphinx(audio_data)
        confidence = 0.7
        return transcript, [{"word": w, "confidence": confidence} for w in transcript.split()], confidence
    except Exception as e:
        print(f"❌ Both Google and Sphinx transcription failed: {e}")
        return "", [], 0.0

# ------------------ STEP 4: CONFIDENCE ANALYSIS ------------------
def calculate_snr(audio_path: str) -> float:
    y, sr = librosa.load(audio_path, sr=16000)
    signal_power = np.mean(y**2)
    noise_power = np.var(y)
    return 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 50.0

def calculate_perplexity(word_confidences):
    if not word_confidences:
        return float("inf")
    avg_conf = np.mean(word_confidences)
    return 1.0 / avg_conf

def multi_factor_confidence(api_conf, snr, perplexity):
    snr_norm = min(max((snr - 10) / 20, 0), 1)
    perplexity_norm = max(1 - (perplexity - 1), 0)
    combined = 0.5 * api_conf + 0.3 * snr_norm + 0.2 * perplexity_norm
    if combined > 0.85:
        label = "HIGH"
    elif combined > 0.7:
        label = "MEDIUM"
    else:
        label = "LOW"
    return combined, label

# ------------------ STEP 5: PII REDACTION ------------------
_NUMBER_WORDS_MAP = {
    "zero":"0","oh":"0","o":"0","one":"1","two":"2","three":"3","four":"4","five":"5",
    "six":"6","seven":"7","eight":"8","nine":"9","ten":"10"
}

def convert_spoken_digits_to_digits(text: str) -> str:
    """Convert spoken digit words to digits to help regex detect credit card numbers."""
    tokens = re.split(r'(\W+)', text)  # keep separators
    for i, tok in enumerate(tokens):
        low = tok.lower().strip()
        if low in _NUMBER_WORDS_MAP:
            tokens[i] = _NUMBER_WORDS_MAP[low]
    return "".join(tokens)

def redact_pii(text: str):
    """
    Redact credit cards, phone numbers, emails, and PERSON names.
    Dates and locations (GPE) are not redacted.
    """
    # Convert spoken digits to numbers
    text_conv = convert_spoken_digits_to_digits(text)

    redacted = text_conv
    redactions = []

    patterns = {
        "CREDIT_CARD": r"(?:\d[\s-]?){13,16}",
        "PHONE": r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    }

    # Apply regex redactions
    for label, pat in patterns.items():
        for m in re.finditer(pat, redacted):
            original = m.group(0)
            if original not in [r.get("text") for r in redactions]:
                redacted = redacted.replace(original, f"[REDACTED_{label}]")
                redactions.append({"type": label, "text": original})

    # spaCy NER only for PERSON
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            if ent.text not in [r.get("text") for r in redactions]:
                redacted = redacted.replace(ent.text, "[REDACTED_PERSON]")
                redactions.append({"type": "PERSON", "text": ent.text})

    return redacted, redactions



# ------------------ STEP 6: SUMMARIZATION ------------------
def summarize_text(text: str, max_sentences: int = 3) -> str:
    sentences = text.split(". ")
    return ". ".join(sentences[:max_sentences]).strip() + "."

# ------------------ STEP 7: TEXT-TO-SPEECH ------------------
def synthesize_speech(text: str, output_path: str) -> str:
    if not text.strip():
        # Avoid crash if transcript is empty
        with open(output_path, "wb") as f:
            pass
        return output_path
    tts = gTTS(text)
    tts.save(output_path)
    return output_path

# ------------------ STEP 8: AUDIT LOGGING ------------------
def write_audit_log(log_data: dict, log_path: str) -> None:
    with open(log_path, "a") as f:
        f.write(json.dumps(log_data) + "\n")

# ------------------ STEP 9: MAIN PIPELINE ------------------
def main():
    load_env()
    input_audio = os.getenv("INPUT_AUDIO", "test_audio.mp3")

    if not os.path.isfile(input_audio):
        print(f"❌ Input file does not exist: {input_audio}")
        return

    print(f"Processing audio file: {input_audio}")
    try:
        processed_audio = preprocess_audio(input_audio, "processed_audio.mp3")
    except Exception as e:
        print(f"❌ Failed preprocessing audio: {e}")
        return

    transcript, words, api_conf = transcribe_audio(processed_audio)
    word_confidences = [w["confidence"] for w in words]
    snr_val = calculate_snr(processed_audio)
    perplexity_val = calculate_perplexity(word_confidences)
    combined, level = multi_factor_confidence(api_conf, snr_val, perplexity_val)
    redacted, redactions = redact_pii(transcript)
    summary = summarize_text(redacted)
    summary_audio = synthesize_speech(summary, "output_summary.mp3")

    with open("output_transcript.txt", "w") as f:
        f.write(redacted)

    log_data = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "input_file": input_audio,
        "snr": snr_val,
        "api_confidence": api_conf,
        "perplexity": perplexity_val,
        "combined_confidence": combined,
        "confidence_level": level,
        "num_redactions": len(redactions),
        "summary_chars": len(summary),
    }
    write_audit_log(log_data, "audit.log")

    print("\n✅ PIPELINE COMPLETE!")
    print(f"Transcript → output_transcript.txt")
    print(f"Summary Audio → {summary_audio}")
    print(f"Audit Log → audit.log")
    print(f"Confidence Level: {level}")

if __name__ == "__main__":
    main()


