import streamlit as st
import tempfile
from pathlib import Path
import json
import time
import random

# IMPORT your separate files
from character_creator import CharacterCreator
from image_generator import ImageGenerator
from scene_detector import PercyJacksonDetector

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

# Initialize your tools (from separate files)
@st.cache_resource
def init_tools():
    character_creator = CharacterCreator()
    image_gen = ImageGenerator()
    detector = PercyJacksonDetector()
    return character_creator, image_gen, detector

character_creator, image_gen, detector = init_tools()

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
    
    # Use character_creator from separate file
    character = character_creator.render_form()
    if character:
        st.session_state.current_character = character
    
    character_creator.display_character()

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
        # Show image if this message has one
        if message.get("image"):
            st.image(message["image"], use_column_width=True)
        
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What do you do/say?"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
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
        
        # Add AI message
        st.session_state.messages.append({"role": "assistant", "content": ai_text})
        
        # ========== AUTO-IMAGE GENERATION ==========
        # Use detector to decide if we need an image
        should_gen, reason = detector.should_generate(
            prompt, 
            ai_text, 
            len(st.session_state.messages)
        )
        
        if should_gen:
            with st.spinner(f"🎨 Painting scene..."):
                # Use detector to extract scene description
                char_name = st.session_state.current_character.get('name', '')
                scene_desc = detector.extract_scene(prompt, ai_text, char_name)
                
                # Generate image
                image = image_gen.generate(scene_desc)
                
                if image:
                    st.image(image, use_column_width=True)
                    st.session_state.messages[-1]["image"] = image
                    st.caption("✨ Scene visualized!")
        
        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Visual RP Engine v1.0")
