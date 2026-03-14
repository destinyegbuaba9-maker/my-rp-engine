import streamlit as st
import tempfile
from pathlib import Path
import json
import time
import random

# Page config - makes it look good on mobile
st.set_page_config(
    page_title="Visual RP Engine",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile-friendly display
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a2e;
    }
    h1, h2, h3 {
        color: #e94560 !important;
    }
    .stButton button {
        background-color: #e94560;
        color: white;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'books_processed' not in st.session_state:
    st.session_state.books_processed = []
if 'current_character' not in st.session_state:
    st.session_state.current_character = None

# Sidebar navigation
st.sidebar.title("🎭 Visual RP")
page = st.sidebar.radio("Go to", ["📚 Library", "👤 Character", "🎮 Roleplay"])

# ==================== LIBRARY PAGE ====================
if page == "📚 Library":
    st.title("📚 Your Book Library")
    
    uploaded_files = st.file_uploader(
        "Drop your books here (PDF only)",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for file in uploaded_files:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📖 {file.name}")
            with col2:
                if st.button(f"Process", key=file.name):
                    with st.spinner(f"Reading {file.name}..."):
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                            tmp.write(file.getvalue())
                            tmp_path = tmp.name
                        
                        st.session_state.books_processed.append({
                            "name": file.name,
                            "path": tmp_path
                        })
                        time.sleep(1)
                    st.success(f"✅ {file.name} ready!")
    
    if st.session_state.books_processed:
        st.subheader("📚 Your Library")
        for book in st.session_state.books_processed:
            st.write(f"✅ {book['name']}")

# ==================== CHARACTER PAGE ====================
elif page == "👤 Character":
    st.title("👤 Create Your Character")
    
    with st.form("character_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Character Name")
            age = st.number_input("Age", min_value=1, max_value=1000, value=16)
            
            parent = st.selectbox(
                "Godly Parent",
                ["None", "Zeus", "Poseidon", "Hades", "Athena", "Apollo",
                 "Artemis", "Ares", "Aphrodite", "Hermes", "Dionysus", "Demeter"]
            )
            
            abilities = st.text_area("Abilities (one per line)")
        
        with col2:
            personality = st.text_area("Personality (traits one per line)")
            backstory = st.text_area("Backstory (short)")
        
        submitted = st.form_submit_button("Save Character")
        
        if submitted and name:
            character = {
                "name": name,
                "age": age,
                "parent": parent if parent != "None" else None,
                "abilities": [a.strip() for a in abilities.split('\n') if a.strip()],
                "personality": [p.strip() for p in personality.split('\n') if p.strip()],
                "backstory": backstory
            }
            
            st.session_state.current_character = character
            
            save_path = Path(f"character_{name.lower().replace(' ', '_')}.json")
            with open(save_path, 'w') as f:
                json.dump(character, f, indent=2)
            
            st.success(f"✅ {name} saved!")
    
    if st.session_state.current_character:
        st.subheader("Current Character")
        st.json(st.session_state.current_character)

# ==================== ROLEPLAY PAGE ====================
else:
    st.title("🎮 Roleplay")
    
    if not st.session_state.current_character:
        st.warning("⚠️ Create a character first!")
        st.stop()
    
    with st.expander("Your Character"):
        st.json(st.session_state.current_character)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What do you do/say?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                time.sleep(1)
                
                responses = [
                    f"You {prompt.lower()}. The scene unfolds before you...",
                    f"As you {prompt.lower()}, something catches your attention.",
                    f"The world responds to your action. What happens next?"
                ]
                ai_text = random.choice(responses)
                st.markdown(ai_text)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_text})
        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Visual RP Engine v1.0")
