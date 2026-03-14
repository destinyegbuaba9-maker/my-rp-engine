import streamlit as st
from pathlib import Path
import json

class CharacterCreator:
    def __init__(self):
        self.character = None
    
    def render_form(self):
        """Display the character creation form"""
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
                self.character = {
                    "name": name,
                    "age": age,
                    "parent": parent if parent != "None" else None,
                    "abilities": [a.strip() for a in abilities.split('\n') if a.strip()],
                    "personality": [p.strip() for p in personality.split('\n') if p.strip()],
                    "backstory": backstory
                }
                
                # Save to file
                self.save_character()
                
                st.success(f"✅ {name} saved!")
                return self.character
        
        return None
    
    def save_character(self):
        """Save character to JSON file"""
        if self.character:
            name = self.character['name']
            save_path = Path(f"character_{name.lower().replace(' ', '_')}.json")
            with open(save_path, 'w') as f:
                json.dump(self.character, f, indent=2)
    
    def load_character(self, name):
        """Load character from JSON file"""
        try:
            save_path = Path(f"character_{name.lower().replace(' ', '_')}.json")
            with open(save_path, 'r') as f:
                self.character = json.load(f)
            return self.character
        except:
            return None
    
    def display_character(self):
        """Display current character"""
        if self.character:
            st.subheader("Current Character")
            st.json(self.character)
    
    def get_character_name(self):
        """Return character name if exists"""
        return self.character['name'] if self.character else None
