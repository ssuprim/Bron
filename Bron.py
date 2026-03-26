import streamlit as st
from openai import OpenAI
from deep_translator import GoogleTranslator
from elevenlabs.client import ElevenLabs
import tempfile

# ===================== CONFIG =====================
client = OpenAI(api_key="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")
eleven = ElevenLabs(api_key="sk_305bf9ef2c80188fdf366de16ba53adbc8a84fcfc91a5f0d")

# ===================== UI =====================
st.set_page_config(page_title="LeBron AI", layout="centered")
st.title("🏀 LeBron AI (Text Input Version)")

mode = st.selectbox("Language", ["English", "Nepali"])

# ===================== STATE =====================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===================== AI =====================
def get_response(user_input):
    system_prompt = """
    You are an AI that talks like LeBron James.

    - Calm, confident, mentor-like
    - Motivational but realistic
    - Keep responses short and natural
    - Uses phrases like:
      "At the end of the day..."
      "Stay locked in"
      "Control what you can control"
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
        voice_id="21m00Tcm4TlvDq8ikWAM"  # default LeBron-like voice
    )
    return audio

# ===================== USER INPUT =====================
st.subheader("Type your question for LeBron:")

user_input = st.text_input("Your question:")

if user_input:
    input_text = user_input
    if mode == "Nepali":
        input_text = to_english(user_input)

    # Get AI response
    response = get_response(input_text)

    if mode == "Nepali":
        response = to_nepali(response)

    st.write("🏀 AI:", response)

    # Generate voice
    audio_bytes = speak(response)
    st.audio(audio_bytes)
