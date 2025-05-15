import logging
logger = logging.getLogger(__name__)
logging.basicConfig(filename="logs/toonmng.log", level=logging.INFO)


class Toon:
    def __init__(self):
        self.properties = {
            "name": "",
            "race": "",
            "classes" : [{
                "clsname": "",
                "level": 0,
            }],
            "background": "",
            "spells" : [{
                "spellname": "",
                "spellschool": "",
            }],
            "stats": {
                "str": 0,
                "chr": 0,
                "wis": 0,
                "dex": 0,
                "int": 0,
                "con": 0,
            }
        }
    
    def get_name(self):
        return self.properties["name"]
    
    def set_name(self, name):
        try:
            self.properties["name"] = name
        except KeyError as e:
            logger.info(f"Could not set the name to {name}: {e}")
    
    def get_race(self):
        return self.properties["race"]
    
    def set_race(self, race):
        try:
            self.properties["race"] = race
        except KeyError as e:
            logger.info(f"Could not set the name to {race}: {e}")

    def get_classes(self):
        return self.properties["classes"]
    
    def add_class(self, cls, level):
        try:
            self.properties["classes"].append({
                "clsname": cls,
                "level": level,
            })
        except Exception as e:
            logger.info(f"Could not add class {cls}: {e}")




