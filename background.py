from typing import Dict, List, Optional
import json
import os
from logging_config import get_logger

logger = get_logger(__name__)

class Background:
    def __init__(self, name: str):
        """Initialize a background from JSON data
        
        Args:
            name: Name of the background to load
        """
        self.name = name
        self.data = self._load_background_data()
        
    def _load_background_data(self) -> Dict:
        """Load background data from JSON file"""
        try:
            file_path = os.path.join("data", "backgrounds", f"{self.name.lower()}.json")
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Failed to load background data for {self.name}: {e}")
            raise ValueError(f"Invalid background: {self.name}")
    
    def apply_to_character(self, character) -> None:
        """Apply background benefits to a character
        
        Args:
            character: The character object to apply benefits to
        """
        try:
            # Apply proficiency grants
            self._apply_proficiencies(character)
            
            # Apply equipment grants
            self._apply_equipment(character)
            
            # Apply background feature
            self._apply_feature(character)
            
            # Set background name
            character.properties["background"] = self.name
            
            logger.info(f"Applied {self.name} background to character {character.get_name()}")
            
        except Exception as e:
            logger.error(f"Failed to apply background {self.name}: {e}")
            raise
    
    def _apply_proficiencies(self, character) -> None:
        """Apply proficiency grants to character"""
        proficiencies = self.data.get("proficiency_grants", {})
        
        # Apply skill proficiencies
        for skill in proficiencies.get("skills", []):
            skill_lc = skill.lower()
            if skill_lc not in character.properties["skills"]:
                character.properties["skills"][skill_lc] = True
        
        # Apply tool proficiencies
        for tool in proficiencies.get("tools", []):
            if tool not in character.properties["proficiencies"]["tools"]:
                character.properties["proficiencies"]["tools"].append(tool)
        
        # Handle language grants
        languages = proficiencies.get("languages", {})
        if languages:
            # For now, we'll just note that languages need to be chosen
            # This will be handled by the character creation UI
            character.properties["pending_choices"] = character.properties.get("pending_choices", {})
            character.properties["pending_choices"]["languages"] = {
                "count": languages.get("count", 0),
                "type": languages.get("type", "choice"),
                "description": languages.get("description", "")
            }
    
    def _apply_equipment(self, character) -> None:
        """Apply equipment grants to character"""
        equipment = self.data.get("equipment_grants", {})
        
        # Add fixed equipment
        for item in equipment.get("fixed", []):
            # Check if item already exists in inventory
            existing_items = [e for e in character.properties["equipment"] 
                            if e.get("item") == item["item"]]
            
            if existing_items:
                # Update quantity if item exists
                existing_items[0]["quantity"] += item["quantity"]
            else:
                # Add new item
                character.properties["equipment"].append({
                    "item": item["item"],
                    "quantity": item["quantity"],
                    "description": item.get("description", "")
                })
        
        # Add currency
        currency = equipment.get("currency", {})
        if currency:
            # Initialize currency if not present
            if "currency" not in character.properties:
                character.properties["currency"] = {"gold": 0, "silver": 0, "copper": 0}
            
            # Add currency
            for coin_type, amount in currency.items():
                character.properties["currency"][coin_type] = \
                    character.properties["currency"].get(coin_type, 0) + amount
    
    def _apply_feature(self, character) -> None:
        """Apply background feature to character"""
        feature = self.data.get("feature", {})
        if feature:
            # Add feature to character's feature list
            character.properties["features"].append({
                "name": feature["name"],
                "source": f"Background: {self.name}",
                "description": feature["description"]
            })
    
    def get_personality_options(self) -> Dict:
        """Get personality customization options
        
        Returns:
            Dictionary containing personality traits, ideals, bonds, and flaws
        """
        return self.data.get("personality", {})
    
    @staticmethod
    def list_available_backgrounds() -> List[str]:
        """List all available backgrounds
        
        Returns:
            List of background names
        """
        try:
            backgrounds_dir = os.path.join("data", "backgrounds")
            background_files = [f for f in os.listdir(backgrounds_dir) 
                              if f.endswith('.json')]
            return [os.path.splitext(f)[0] for f in background_files]
        except Exception as e:
            logger.error(f"Failed to list backgrounds: {e}")
            return [] 