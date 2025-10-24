# Lab 3 Reflection – Audio AI Pipeline

## 1. Comparison

### 3 Test Cases

As predicted, the offline and free TTS/STT functions were not as capable as Google Cloud’s services, though they still performed their intended tasks. The low confidence scores shown in the audit log confirmed this.

For the test_audio.mp3 file, the system produced the following output:
[REDACTED_PERSON] is a set of technologies for a computer
AI helps computer see understand and translate language and analyse data
it can also make recommendations and perform other advanced tasks for [REDACTED_CREDIT_CARD]

What I actually recorded was:
Javakhadze, Javakhadze
AI is a set of technologies for computers
AI helps computers see, understand, and translate language and analyze data
It can also make recommendations and perform other advanced tasks.
4532 1234 5678 9010

As you can see, it mistook the first instance of the word “AI” for part of my last name, and the audio began mid-sentence (“is a”).
At the end, it also misinterpreted the first number of the credit card as the word “for.”

For clean_audio.mp3, I submitted a silent recording that I prepared the AI for, and it returned a specific error message in the terminal:
"⚠ Could not understand audio, returning empty transcript."

For low_quality_phone_call, the model surprisingly understood the words correctly.
It identified where the names began and ended accurately—likely because they were common names that the AI had encountered frequently, unlike my Georgian surname.

The output transcript was:
hello is this [REDACTED_PERSON] yes speaking who is this hi this is [REDACTED_PERSON] how are you

What I recorded was:
Hello, is this Anna?
Yes, speaking. Who is this?
Hi, this is John. How are you?

## 2. Implementation Highlights

Audio Preprocessing: Used pydub for normalization.
Speech-to-Text: Implemented with speech_recognition, using Google Web Speech API as primary and PocketSphinx as a fallback.
Confidence Scoring: Combined API confidence, signal-to-noise ratio (SNR), and word-level perplexity to determine overall reliability.
PII Redaction: Hybrid approach using regex (for structured PII like credit cards, phones, emails) and spaCy NER (for PERSON entities).
Text Summarization: Simple extractive summarization limiting to top sentences.
Text-to-Speech: gTTS for audio summary output, with fallback options if necessary.
Audit Logging: JSON logs capturing metrics, redactions, confidence levels, and timestamps.

## 3. Challenges

Credit Card Detection: Initially missed numbers when spoken as words (“four five three two…”). Fixed by mapping spoken digits to numbers before regex.
TTS Empty Input: If transcription failed, gTTS would crash; added a safeguard to handle empty text.
Noise Reduction: Caused distortion if audio was very short.
