import streamlit as st
from openai import OpenAI
from deep_translator import GoogleTranslator
from elevenlabs.client import ElevenLabs
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import numpy as np
import time

# ===================== CONFIG =====================
OPENAI_API_KEY = "PASTE_YOUR_KEY_HERE"
ELEVEN_API_KEY = "PASTE_YOUR_KEY_HERE"

OPENAI_API_KEY = "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"
ELEVEN_API_KEY = "sk_305bf9ef2c80188fdf366de16ba53adbc8a84fcfc91a5f0d"

# ===================== UI =====================
st.set_page_config(page_title="LeBron AI", layout="centered")
st.title("🏀 LeBron AI (Test Mode - No Wake Word)")

mode = st.selectbox("Language", ["English", "Nepali"])

# ===================== STATE =====================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "buffer" not in st.session_state:
    st.session_state.buffer = b""

if "last_audio_time" not in st.session_state:
    st.session_state.last_audio_time = time.time()

# ===================== AI =====================
def get_response(user_input):
    system_prompt = """
    You are an AI that talks like LeBron James.

    - Calm, confident, mentor-like
    - Motivational but realistic
    - Keep responses short and natural
    """

    messages = [{"role": "system", "content": system_prompt}]
    messages += st.session_state.chat_history
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-5",
        messages=messages
    )

    reply = response.choices[0].message.content

    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    return reply

# ===================== TRANSLATION =====================
def to_nepali(text):
    return GoogleTranslator(source='auto', target='ne').translate(text)

def to_english(text):
    return GoogleTranslator(source='auto', target='en').translate(text)

# ===================== VOICE =====================
def speak(text):
    audio = eleven.text_to_speech.convert(
        text=text,
        voice_id="21m00Tcm4TlvDq8ikWAM"
    )
    return audio

# ===================== AUDIO PROCESSOR =====================
class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten()

        volume = np.linalg.norm(audio) / len(audio)

        # VERY sensitive
        if volume > 0.003:
            st.session_state.last_audio_time = time.time()
            st.session_state.buffer += audio.tobytes()

        return frame

# ===================== STREAM =====================
st.subheader("🎤 Speak normally (no wake word)")

ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
)

# ===================== PROCESS =====================
SILENCE_DURATION = 2

if ctx.audio_processor:
    if len(st.session_state.buffer) > 0:
        silence_time = time.time() - st.session_state.last_audio_time

        if silence_time > SILENCE_DURATION:
            # Save audio
            with open("input.wav", "wb") as f:
                f.write(st.session_state.buffer)

            st.session_state.buffer = b""

            # Transcribe
            with open("input.wav", "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=f
                )

            text = transcript.text.strip()
            st.write("🧾 You said:", text)

            if mode == "Nepali":
                text = to_english(text)

            response = get_response(text)

            if mode == "Nepali":
                response = to_nepali(response)

            st.write("🏀 AI:", response)

            # Speak
            audio = speak(response)

            with open("output.mp3", "wb") as f:
                f.write(audio)

            st.audio("output.mp3")

            time.sleep(0.5)
            st.rerun()