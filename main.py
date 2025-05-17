from file_functions import save_file, open_file, list_files
from logging_config import setup_logging, get_logger
from toon import Toon
import os

logger = get_logger(__name__)

class ToonManager:
    def main():
        # Initialize logging
        setup_logging()
        logger.info("ToonManager application started")
        
        try:
            # 1. Create a new character
            character = Toon()
            
            # 2. Set basic character information
            character.set_name("Gandalf")
            character.set_race("elf")  # Using high elf subrace
            
            # 3. Set ability scores
            character.set_ability_scores({
                "strength": 10,
                "dexterity": 14,
                "constitution": 12,
                "intelligence": 18,
                "wisdom": 16,
                "charisma": 14
            })
            
            # 4. Add class levels
            character.add_class("wizard", 19)
            
            # 5. Export character sheet to PDF
            try:
                pdf_path = character.export_character_sheet(format="pdf")
                logger.info(f"Character sheet exported to PDF: {pdf_path}")
            except Exception as e:
                logger.error(f"Failed to export PDF: {e}")
                # Fallback to HTML if PDF export fails
                html = character.export_character_sheet(format="html")
                with open("characters/character_sheet.html", "w") as f:
                    f.write(html)
                logger.info("Character sheet exported to HTML as fallback")
                
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}", exc_info=True)
            raise
        
        finally:
            logger.info("ToonManager application finished")

if __name__ == "__main__":
    tm = ToonManager
    tm.main()