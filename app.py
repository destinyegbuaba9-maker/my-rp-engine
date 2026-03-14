import streamlit as st
import tempfile
from pathlib import Path
import json
import os
import requests
import base64
from io import BytesIO
from PIL import Image
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
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        background-color: #16213e;
    }
    .user-message {
        background-color: #0f3460;
    }
    .assistant-message {
        background-color: #1a1a2e;
        border: 1px solid #0f3460;
    }
    .image-container {
        border-radius: 15px;
        overflow: hidden;
        margin: 1rem 0;
        border: 2px solid #e94560;
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
if 'scene_context' not in st.session_state:
    st.session_state.scene_context = []
if 'last_image' not in st.session_state:
    st.session_state.last_image = None

# Sidebar navigation
st.sidebar.title("🎭 Visual RP")
page = st.sidebar.radio("Go to", ["📚 Library", "👤 Character", "🎮 Roleplay"])

# Image generator (connects to Cloudflare)
class ImageGenerator:
    def __init__(self):
        self.api_url = "https://fragrant-lab-3fda.destinyegbuaba9.workers.dev"
    
    def generate(self, scene_description):
        """Send scene to Cloudflare and get image back"""
        try:
            # Enhance description for better images
            enhanced_prompt = f"{scene_description}, fantasy art style, detailed, dramatic lighting, digital painting"
            
            response = requests.post(
                f"{self.api_url}/generate",
                json={"prompt": enhanced_prompt}
            )
            
            if response.status_code == 200:
                # Return image data
                return Image.open(BytesIO(response.content))
            else:
                st.error(f"Image generation failed: {response.status_code}")
        except Exception as e:
            st.error(f"Error generating image: {e}")
        return None

# Initialize image generator
image_gen = ImageGenerator()

# ==================== LIBRARY PAGE ====================
if page == "📚 Library":
    st.title("📚 Your Book Library")
    
    # Drag drop area
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
                        # Save temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                            tmp.write(file.getvalue())
                            tmp_path = tmp.name
                        
                        # Add to processed list
                        st.session_state.books_processed.append({
                            "name": file.name,
                            "path": tmp_path
                        })
                        time.sleep(1)
                    st.success(f"✅ {file.name} ready!")
    
    # Show processed books
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
            
            # For Percy Jackson world
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
            
            # Save to session
            st.session_state.current_character = character
            
            # Also save to file (so it persists)
            save_path = Path(f"character_{name.lower().replace(' ', '_')}.json")
            with open(save_path, 'w') as f:
                json.dump(character, f, indent=2)
            
            st.success(f"✅ {name} saved!")
    
    # Show current character if exists
    if st.session_state.current_character:
        st.subheader("Current Character")
        char = st.session_state.current_character
        st.json(char)

# ==================== ROLEPLAY PAGE ====================
else:  # Roleplay page
    st.title("🎮 Roleplay")
    
    # Check if character is loaded
    if not st.session_state.current_character:
        st.warning("⚠️ Create a character first!")
        st.stop()
    
    # Show current character
    with st.expander("Your Character"):
        st.json(st.session_state.current_character)
    
    # ========== SCENE DETECTOR (The Magic Part) ==========
    def should_generate_image(user_input, ai_response=""):
        """Automatically decides if scene needs an image"""
        
        # Scene change keywords
        visual_triggers = [
            'walk into', 'enter', 'arrive', 'approach', 'see',
            'look at', 'appears', 'emerges', 'suddenly', 'then',
            'attack', 'fight', 'cast', 'summon', 'monster',
            'forest', 'camp', 'underworld', 'mountain', 'sea',
            'night', 'storm', 'dark', 'light', 'shadow'
        ]
        
        # Check user input
        text_to_check = f"{user_input} {ai_response}".lower()
        
        for trigger in visual_triggers:
            if trigger in text_to_check:
                return True
        
        # Also generate every 5 messages for variety
        if len(st.session_state.messages) > 0 and len(st.session_state.messages) % 5 == 0:
            return True
        
        return False
    
    def extract_scene_description(text):
        """Extract what should be visualized"""
        
        # Look for location words
        locations = {
            'camp': 'Camp Half-Blood, Greek columns, strawberry fields, demigods',
            'forest': 'dark magical forest, ancient trees, mist, moonlight',
            'underworld': 'dark realm, souls of the dead, asphodel fields, blue mist',
            'sea': 'ocean, waves, stormy water, beach',
            'olympus': 'marble palace, golden light, gods, clouds'
        }
        
        # Find which location is mentioned
        scene = "fantasy scene, detailed, atmospheric"
        for word, desc in locations.items():
            if word in text.lower():
                scene = desc
                break
        
        # Add character if mentioned
        char = st.session_state.current_character['name']
        
        return f"{char} in {scene}, {text[:100]}, fantasy art, digital painting"
    
    # ========== MESSAGE DISPLAY ==========
    
    # Display chat history with images
    for message in st.session_state.messages:
        # Show image if this message has one
        if message.get("image"):
            st.image(message["image"], use_column_width=True)
        
        # Show text
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # ========== CHAT INPUT ==========
    
    # User input
    if prompt := st.chat_input("What do you do/say?"):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response (simple for now)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                time.sleep(1)  # Simulate thinking
                
                # Simple response logic
                responses = [
                    f"You {prompt.lower()}. The scene unfolds before you...",
                    f"As you {prompt.lower()}, something catches your attention.",
                    f"The world responds to your action. What happens next?"
                ]
                ai_text = random.choice(responses)
                
                st.markdown(ai_text)
        
        # Add AI message
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_text
        })
        
        # ========== AUTO-IMAGE GENERATION ==========
        # Check if we should generate an image
        if should_generate_image(prompt, ai_text):
            with st.spinner("🎨 Painting the scene..."):
                # Create scene description
                scene_desc = extract_scene_description(f"{prompt} {ai_text}")
                
                # Generate image
                image = image_gen.generate(scene_desc)
                
                if image:
                    # Display image
                    st.image(image, use_column_width=True)
                    
                    # Save to last message
                    st.session_state.messages[-1]["image"] = image
                    
                    # Success message
                    st.caption("✨ Scene visualized!")
        
        # Force rerun to update display
        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Visual RP Engine v1.0")
