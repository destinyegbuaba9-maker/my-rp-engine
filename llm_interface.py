import requests
import streamlit as st
import json

class GroqLLM:
    def __init__(self):
        # Load key from Streamlit Secrets (this is what you just set)
        self.api_key = st.secrets.get("GROQ_API_KEY")
        
        if not self.api_key:
            st.error("❌ Groq API key is missing. Please add GROQ_API_KEY in App Settings → Secrets.")
            self.api_key = None
            
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_response(self, user_input, character_info, chat_history, book_context=""):
        """Generate a smart roleplay response using Groq"""
        if not self.api_key:
            return self._fallback_response(user_input)

        try:
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a roleplay master for a Percy Jackson game. 
                    The user is playing as: {json.dumps(character_info)}
                    
                    Rules:
                    - Stay true to Percy Jackson world and Greek mythology
                    - Only use characters, monsters, and places from the books
                    - Keep responses 2-4 sentences
                    - Be descriptive and immersive
                    - React to what the user does
                    """
                }
            ]
            
            # Add recent chat history
            for msg in chat_history[-6:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({"role": "user", "content": user_input})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 150
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                error_detail = ""
                try:
                    error_detail = response.json().get('error', {}).get('message', '')
                except:
                    error_detail = response.text[:200]
                
                st.error(f"Groq API error ({response.status_code}): {error_detail}")
                return self._fallback_response(user_input)
                
        except Exception as e:
            st.error(f"Error connecting to Groq: {str(e)}")
            return self._fallback_response(user_input)
    
    def _fallback_response(self, user_input):
        """Simple fallback if API fails"""
        return f"You {user_input.lower()}. The scene continues around you in Camp Half-Blood."
    
    def generate_opening(self, character_info):
        """Generate an opening scene when starting a new game"""
        if not self.api_key:
            return "You find yourself at Camp Half-Blood as the sun sets over the valley. The campers are gathering around the dining pavilion, and you hear Chiron's hoofsteps approaching."

        try:
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a roleplay master for a Percy Jackson game.
                    The user is playing as: {json.dumps(character_info)}
                    
                    Create an immersive opening scene for their character at Camp Half-Blood.
                    Describe where they are, what they see, and set up a small hook for adventure.
                    Be descriptive and atmospheric. 3-4 sentences.
                    """
                }
            ]
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": messages,
                "temperature": 0.9,
                "max_tokens": 200
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return "You find yourself at Camp Half-Blood as the sun sets over the valley. The campers are gathering around the dining pavilion, and you hear Chiron's hoofsteps approaching."
                
        except Exception as e:
            st.error(f"Error generating opening scene: {str(e)}")
            return "You find yourself at Camp Half-Blood as the sun sets over the valley."
