import requests
import streamlit as st
import json

class GroqLLM:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def generate_response(self, user_input, character_info, chat_history, book_context=""):
        """
        Generate a smart roleplay response using Groq
        """
        try:
            # Build the conversation history for context
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
            
            # Add chat history (last 6 messages for context)
            for msg in chat_history[-6:]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add the current user input
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Call Groq API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama3-70b-8192",  # Smart and fast
                "messages": messages,
                "temperature": 0.8,  # Creative but not crazy
                "max_tokens": 150
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                st.error(f"Groq API error: {response.status_code}")
                return self._fallback_response(user_input)
                
        except Exception as e:
            st.error(f"Error with Groq: {e}")
            return self._fallback_response(user_input)
    
    def _fallback_response(self, user_input):
        """Simple fallback if API fails"""
        return f"You {user_input.lower()}. The scene continues around you."
