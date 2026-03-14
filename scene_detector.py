class PercyJacksonDetector:
    def __init__(self):
        # Visual triggers that need images
        self.major_triggers = [
            'walk into', 'enter', 'arrive at', 'approach', 'reach',
            'emerges', 'appears', 'materializes', 'summons',
            'attack', 'fight', 'battle', 'strike', 'cast'
        ]
        
        # Locations that need images
        self.location_triggers = [
            'camp', 'forest', 'underworld', 'mountain', 'sea', 'ocean',
            'temple', 'cave', 'beach', 'woods', 'valley', 'olympus'
        ]
        
        # Atmosphere triggers
        self.atmosphere_triggers = [
            'night', 'dawn', 'dusk', 'storm', 'rain', 'thunder',
            'lightning', 'fog', 'mist', 'dark', 'shadow', 'light'
        ]
        
        # Percy Jackson specific locations with rich descriptions
        self.pj_locations = {
            'camp': 'Camp Half-Blood, Greek columns, strawberry fields, demigods in orange shirts, Big House',
            'underworld': 'Underworld, souls of the dead, asphodel fields, dark realm, blue mist, River Styx',
            'forest': 'magical forest, ancient trees, mist, moonlight, creatures watching',
            'sea': 'ocean, stormy waves, beach, sea foam, coastline',
            'olympus': 'Mount Olympus, marble palace, golden light, clouds, throne room',
            'cave': 'dark cave, rocky walls, shadows, echoing sounds'
        }
    
    def should_generate(self, user_input, ai_response, message_count):
        """
        Decide if this moment needs an image
        Returns: (bool, reason)
        """
        full_text = f"{user_input} {ai_response}".lower()
        
        # Check for major triggers (ALWAYS generate)
        for trigger in self.major_triggers:
            if trigger in full_text:
                return True, f"major event: {trigger}"
        
        # Check for new locations
        for trigger in self.location_triggers:
            if trigger in full_text:
                return True, f"location: {trigger}"
        
        # Check for atmosphere changes
        for trigger in self.atmosphere_triggers:
            if trigger in full_text:
                return True, f"atmosphere: {trigger}"
        
        # Generate every 6 messages for variety
        if message_count > 0 and message_count % 6 == 0:
            return True, "regular interval"
        
        return False, "no trigger"
    
    def extract_scene(self, user_input, ai_response, character_name=None):
        """
        Extract the key visual elements from the text
        Returns a description perfect for image generation
        """
        full_text = f"{user_input} {ai_response}".lower()
        
        # Start with character
        scene = ""
        if character_name:
            scene = f"{character_name} "
        
        # Check for Percy Jackson specific locations
        location_found = False
        for loc, desc in self.pj_locations.items():
            if loc in full_text:
                scene += f"at {desc}"
                location_found = True
                break
        
        # If no specific location, look for atmosphere
        if not location_found:
            for atm in self.atmosphere_triggers:
                if atm in full_text:
                    scene += f"in a {atm} setting"
                    break
            else:
                # Default to generic scene
                scene += "in a fantasy scene"
        
        # Add action if present
        for trigger in self.major_triggers:
            if trigger in full_text:
                scene += f", {trigger} action"
                break
        
        return scene.strip()
