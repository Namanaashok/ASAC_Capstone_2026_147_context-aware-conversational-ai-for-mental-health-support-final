import streamlit as st
import random
import datetime
from bot_engine import BotEngine
from sentiment_analyzer import SentimentAnalyzer
from tts_engine import TTSEngine
import streamlit.components.v1 as components

st.set_page_config(page_title="Aura - Mental Health Companion", page_icon="🌿", layout="centered")

CUSTOM_CSS = """
<style>
    /* Global App Background */
    .stApp {
        background-color: #F9FDF9;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #E8F5E9;
        border-right: 1px solid #C8E6C9;
    }
    section[data-testid="stSidebar"] * {
        color: #2E4C30 !important;
    }
    
    /* Text overrides to look softer than pure black */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #1A301B !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Style Chat Messages */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    /* Make assistant messages slightly greener */
    .stChatMessage[data-testid="chatAvatarIcon-assistant"] {
        background-color: #F1F8F1;
        border: 1px solid #C8E6C9;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 20px;
        border: none;
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #388E3C !important;
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
        transform: translateY(-2px);
    }
    
    /* Input Box */
    .stChatInputContainer {
        border-radius: 24px !important;
        border: 2px solid #A5D6A7 !important;
        background-color: #FFFFFF;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #E8F5E9;
        border-radius: 8px 8px 0 0;
        color: #2E4C30;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

AFFIRMATIONS = [
    "You are capable of amazing things.",
    "Every day is a fresh start.",
    "Your feelings are valid and important.",
    "You are stronger than you know.",
    "It's okay to take a break and rest.",
    "You are worthy of love and respect.",
    "Small steps are still progress.",
    "Be kind to yourself today.",
    "You are doing your best, and that is enough.",
    "There is light at the end of the tunnel."
]

# Initialize Session State
if "tts_engine" not in st.session_state:
    st.session_state.tts_engine = TTSEngine()

JOURNAL_PROMPTS = [
    "What is one small thing that brought you joy today?",
    "If you could speak to your younger self right now, what would you say?",
    "What is a heavy thought you've been carrying that you'd like to put down?",
    "Describe a place where you feel completely safe and at peace.",
    "What are three things you are grateful for in this exact moment?",
    "When was the last time you felt truly proud of yourself?",
    "What is something you need to forgive yourself for?"
]

# --- CSS for Breathing Animation ---
BREATHING_CSS = """
<style>
.breathing-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
    margin: 20px 0;
}
.circle {
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, #8bc34a 20%, #4caf50 80%);
    border-radius: 50%;
    animation: breathe 11s infinite ease-in-out;
    box-shadow: 0 0 40px rgba(76, 175, 80, 0.4);
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-family: sans-serif;
    font-size: 24px;
    font-weight: bold;
}
@keyframes breathe {
    0% { transform: scale(0.6); content: "Breathe In"; }
    36% { transform: scale(1.2); } /* 4s Inhale */
    100% { transform: scale(0.6); } /* 7s Exhale */
}
</style>
<div class="breathing-container">
    <div class="circle"></div>
</div>
"""

# Initialize Session State
if "bot_engine" not in st.session_state:
    st.session_state.bot_engine = BotEngine(model_name="phi3:latest") 
    
if "sentiment_analyzer" not in st.session_state:
    with st.spinner("Initializing Sentiment Analysis module..."):
        st.session_state.sentiment_analyzer = SentimentAnalyzer()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there. I'm Aura. I'm here to listen and support you in a safe, judgment-free space. How are you feeling today?"}
    ]

if "daily_affirmation" not in st.session_state:
    st.session_state.daily_affirmation = random.choice(AFFIRMATIONS)

if "mood_scores" not in st.session_state:
    st.session_state.mood_scores = []
    
if "let_go_key" not in st.session_state:
    st.session_state.let_go_key = 0

# UI Components
st.title("🌿 Aura")
st.markdown("Your local, context-aware mental health companion.")
st.markdown("---")

# Sidebar Components
with st.sidebar:
    st.header("✨ Daily Affirmation")
    st.info(f'"{st.session_state.daily_affirmation}"')
    
    st.markdown("---")
    
    st.header("📊 Session Mood")
    if st.session_state.mood_scores:
        avg_mood = sum(st.session_state.mood_scores) / len(st.session_state.mood_scores)
        if avg_mood > 0.15:
            mood_label = "Positive 😊"
            mood_delta = "Uplifting"
        elif avg_mood < -0.15:
            mood_label = "Challenging 🌧️"
            mood_delta = "Needs Support"
        else:
            mood_label = "Neutral 😐"
            mood_delta = "Balanced"
        st.metric(label="Overall Sentiment", value=mood_label, delta=mood_delta)
    else:
        st.write("Start chatting to track your mood.")
        
    st.markdown("---")
    
    st.header("⚙️ Settings")
    st.session_state.enable_voice = st.toggle("Enable Voice (TTS)", value=False, help="Aura will speak responses out loud.")
    
    selected_model = st.selectbox("Local LLM (via Ollama)", ["phi3:latest", "llama3:latest", "mistral:latest"])
    if st.button("Update Model"):
        st.session_state.bot_engine = BotEngine(model_name=selected_model)
        st.success(f"Model updated to {selected_model}")
        
    st.markdown("---")
    
    st.header("💾 Export Session")
    chat_export = "Aura Chat Session Log\n"
    chat_export += f"Date: {datetime.date.today()}\n"
    chat_export += "="*30 + "\n\n"
    
    for msg in st.session_state.messages:
        role_name = "Aura" if msg["role"] == "assistant" else "You"
        chat_export += f"[{role_name}]: {msg['content']}\n\n"
        
    st.download_button(
        label="Download Chat History",
        data=chat_export,
        file_name=f"aura_chat_log_{datetime.date.today()}.txt",
        mime="text/plain"
    )

# --- TABS LAYOUT ---
tab1, tab2, tab3 = st.tabs(["💬 Chat with Aura", "🌬️ Mindfulness Corner", "📥 The Letting Go Box"])

with tab1:
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Generate Journal Prompt", help="Get a unique question to reflect on.", use_container_width=True):
            prompt = random.choice(JOURNAL_PROMPTS)
            # Inject as assistant message to prompt the user
            st.session_state.messages.append({"role": "assistant", "content": f"**Reflective Prompt**: {prompt}"})
            st.rerun()
            
    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    if prompt := st.chat_input("Type your message here..."):
        # Track Mood score before updating UI
        score = st.session_state.sentiment_analyzer.analyze_score(prompt)
        st.session_state.mood_scores.append(score)
        
        # Add user message to state and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Process Response
        with st.chat_message("assistant"):
            # 1. Analyze Sentiment for context
            sentiment = st.session_state.sentiment_analyzer.analyze(prompt)
            
            # 2. Get Bot Response Stream
            response_stream = st.session_state.bot_engine.get_response_stream(prompt, sentiment)
            
            # Display the streamed response
            response = st.write_stream(response_stream)
            
            # Speak the response if TTS is enabled
            if st.session_state.get("enable_voice", False):
                st.session_state.tts_engine.speak(response)
                
        # Add assistant response to state
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

with tab2:
    st.header("Mindfulness Breathing Pacer")
    st.markdown("Take a moment to center yourself. Follow the expanding and contracting circle. **Breathe in** as it grows (4 seconds), and **breathe out** slowly as it shrinks (7 seconds).")
    
    components.html(BREATHING_CSS, height=350)
    
    st.info("Practicing this breathing technique can help calm your nervous system and reduce anxiety rapidly.")

with tab3:
    st.header("The Letting Go Box")
    st.markdown("Sometimes, we just need a place to dump our heavy thoughts, intrusive worries, or frustrations without anyone responding or judging. Type whatever is bothering you below.")
    st.markdown("**When you are ready, click 'Release'. Your words will be permanently deleted—they are not saved in the chat or on your device.**")
    
    # We use a changing key to force the text area to clear when the button is pressed
    worry_text = st.text_area("What is weighing heavily on your mind right now?", height=200, key=f"let_go_box_{st.session_state.let_go_key}")
    
    if st.button("🔥 Release and Let Go", type="primary", use_container_width=True):
        if worry_text.strip():
            st.balloons()
            st.success("You have let it go. Your thought has been released into the ether and permanently deleted.")
            # Increment key to clear the text area on rerun
            st.session_state.let_go_key += 1
            st.rerun()
        else:
            st.warning("Type something in the box first before releasing.")
