import requests
from PIL import Image
from io import BytesIO
import streamlit as st

class ImageGenerator:
    def __init__(self):
        # Your Cloudflare worker URL
        self.api_url = "https://fragrant-lab-3fda.destinyegbuaba9.workers.dev"
    
    def generate(self, scene_description):
        """
        Send scene description to Cloudflare and get image back
        """
        try:
            # Enhance description for better fantasy images
            enhanced_prompt = self._enhance_prompt(scene_description)
            
            # Send to Cloudflare
            response = requests.post(
                f"{self.api_url}/generate",
                json={"prompt": enhanced_prompt},
                timeout=30
            )
            
            # Check if it worked
            if response.status_code == 200:
                # Convert response to image
                image = Image.open(BytesIO(response.content))
                return image
            else:
                st.error(f"Image generation failed: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error generating image: {e}")
            return None
    
    def _enhance_prompt(self, scene_description):
        """
        Make the prompt better for fantasy art
        """
        # Base style for fantasy images
        style = "fantasy art, digital painting, detailed, dramatic lighting, "
        
        # Add mood based on keywords
        if any(word in scene_description.lower() for word in ['dark', 'night', 'shadow', 'underworld']):
            style += "dark atmosphere, moody lighting, "
        elif any(word in scene_description.lower() for word in ['battle', 'fight', 'attack', 'monster']):
            style += "dynamic action, motion blur, epic, "
        elif any(word in scene_description.lower() for word in ['camp', 'half-blood']):
            style += "warm atmosphere, peaceful, magical, "
        
        # Add location-specific details
        if 'camp' in scene_description.lower():
            style += "Greek columns, strawberry fields, demigods, "
        elif 'underworld' in scene_description.lower():
            style += "souls of the dead, asphodel fields, dark realm, blue mist, "
        elif 'forest' in scene_description.lower():
            style += "ancient trees, magical forest, mist, moonlight, "
        elif 'sea' in scene_description.lower() or 'ocean' in scene_description.lower():
            style += "stormy sea, waves, beach, "
        
        # Combine everything
        final_prompt = f"{scene_description}, {style} high quality"
        
        # Keep it under 500 characters
        return final_prompt[:500]
