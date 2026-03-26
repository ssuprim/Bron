import streamlit as st
import openai
from deep_translator import GoogleTranslator
from elevenlabs.client import ElevenLabs
import tempfile

# ===================== CONFIG =====================
# Use Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
ELEVEN_API_KEY = st.secrets["ELEVEN_API_KEY"]
eleven = ElevenLabs(api_key=ELEVEN_API_KEY)

st.set_page_config(page_title="LeBron AI", layout="centered")
st.title("🏀 LeBron AI (Text + Audio)")

# ===================== STATE =====================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===================== UI OPTIONS =====================
mode = st.selectbox("Language", ["English", "Nepali"])
input_mode = st.radio("How do you want to ask LeBron?", ["Text", "Voice"])

# ===================== HELPER FUNCTIONS =====================
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

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # reliable for Streamlit Cloud
        messages=messages
    )

    reply = response.choices[0].message.content
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    return reply

def to_nepali(text):
    return GoogleTranslator(source='auto', target='ne').translate(text)

def to_english(text):
    return GoogleTranslator(source='auto', target='en').translate(text)

def speak(text):
    # Generate audio using ElevenLabs
    audio = eleven.text_to_speech.convert(
        text=text,
        voice_id="21m00Tcm4TlvDq8ikWAM"  # default LeBron-like voice
    )
    return audio

# ===================== USER INPUT =====================
user_input = ""

if input_mode == "Text":
    user_input = st.text_input("Type your question:")

elif input_mode == "Voice":
    audio_file = st.file_uploader("Upload a short audio clip (WAV/MP3):", type=["wav", "mp3"])
    if audio_file:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_file.read())
            tmp_path = tmp.name

        # Transcribe using OpenAI's audio transcription
        transcription = openai.Audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp_path, "rb")
        )
        user_input = transcription["text"]
        st.write("🗣️ You said:", user_input)

# ===================== PROCESS INPUT =====================
if user_input:
    input_text = user_input
    if mode == "Nepali":
        input_text = to_english(user_input)

    # Get AI response
    response = get_response(input_text)

    if mode == "Nepali":
        response = to_nepali(response)

    st.write("🏀 AI:", response)

    # Voice output
    audio_bytes = speak(response)
    st.audio(audio_bytes)

# ===================== CHAT HISTORY =====================
st.subheader("Chat History")
for msg in st.session_state.chat_history:
    role = "You" if msg["role"] == "user" else "LeBron"
    st.write(f"**{role}:** {msg['content']}")
