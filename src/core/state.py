import json
import os
from src.utils.translator import T
from src.models.character import Character
from src.models.location import Location
from src.models.story import StoryLabel

SETTINGS_FILE = "settings.json"

class AppState:
    def __init__(self):
        self.settings = {}
        self.current_project_path = None
        self.project_data = {"characters": [], "locations": [], "story": []}
        self.load_settings()

    def load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            self.settings = {"recents": [], "language": "en"}
            self.save_settings()
        else:
            try:
                with open(SETTINGS_FILE, "r") as f:
                    self.settings = json.load(f)
            except:
                self.settings = {"recents": [], "language": "en"}

        # Carica la lingua
        lang = self.settings.get("language", "en")
        T.load_language(lang)

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)

    def add_to_recents(self, path):
        recents = self.settings.get("recents", [])
        if path in recents: recents.remove(path)
        recents.insert(0, path)
        self.settings["recents"] = recents[:3]
        self.save_settings()

    def load_project_data(self, path):
        self.current_project_path = path
        self.add_to_recents(path)

        manager_dir = os.path.join(path, ".manager")
        if not os.path.exists(manager_dir): os.makedirs(manager_dir)

        # --- CARICAMENTO PERSONAGGI  ---
        self.project_data["characters"] = []
        char_file = os.path.join(path, ".manager", "characters.json")
        if os.path.exists(char_file):
            try:
                with open(char_file, "r") as f:
                    data = json.load(f)
                    for d in data: self.project_data["characters"].append(Character.from_dict(d))
            except Exception as e:
                print(f"Err Char: {e}")

        # --- CARICAMENTO LUOGHI  ---
        self.project_data["locations"] = []
        loc_file = os.path.join(path, ".manager", "locations.json")
        if os.path.exists(loc_file):
            try:
                with open(loc_file, "r") as f:
                    data = json.load(f)
                    for d in data: self.project_data["locations"].append(Location.from_dict(d))
            except Exception as e:
                print(f"Err Loc: {e}")

        # --- CARICAMENTO STORIA ---
        self.project_data["story"] = []
        story_file = os.path.join(path, ".manager", "story.json")
        if os.path.exists(story_file):
            try:
                with open(story_file, "r") as f:
                    data = json.load(f)
                    for d in data:
                        self.project_data["story"].append(StoryLabel.from_dict(d))
            except Exception as e:
                print(f"Err Story: {e}")

    def save_project_data(self):
        if not self.current_project_path: return
        manager_dir = os.path.join(self.current_project_path, ".manager")

        # Salva Personaggi
        char_file = os.path.join(manager_dir, "characters.json")
        with open(char_file, "w") as f:
            json.dump([c.to_dict() for c in self.project_data["characters"]], f, indent=4)

        # Salva Luoghi
        manager_dir = os.path.join(self.current_project_path, ".manager")
        loc_file = os.path.join(manager_dir, "locations.json")
        with open(loc_file, "w") as f:
            json.dump([l.to_dict() for l in self.project_data["locations"]], f, indent=4)

        # Salva Storia
        manager_dir = os.path.join(self.current_project_path, ".manager")
        story_file = os.path.join(manager_dir, "story.json")
        with open(story_file, "w") as f:
            # Serializza la lista di StoryLabel
            json.dump([s.to_dict() for s in self.project_data["story"]], f, indent=4)

    def generate_rpy_characters(self):
        if not self.current_project_path: return
        rpy_path = os.path.join(self.current_project_path, "game", "locations.rpy")
        with open(rpy_path, "w", encoding="utf-8") as f:
            f.write("# Characters definitions\n\n")
            for chara in self.project_data["characters"]:
                f.write(chara.to_renpy_code() + "\n")

    def generate_rpy_locations(self):
        """Genera locations.rpy"""
        if not self.current_project_path: return
        rpy_path = os.path.join(self.current_project_path, "game", "locations.rpy")
        with open(rpy_path, "w", encoding="utf-8") as f:
            f.write("# Backgrounds definitions\n\n")
            for loc in self.project_data["locations"]:
                f.write(loc.to_renpy_code() + "\n")

    def generate_rpy_script(self):
        """Genera il file script.rpy principale (o story.rpy)"""
        if not self.current_project_path: return
        rpy_path = os.path.join(self.current_project_path, "game", "story.rpy")
        with open(rpy_path, "w", encoding="utf-8") as f:
            f.write("# Generated by Ren'Py GUI Manager\n\n")
            for label in self.project_data["story"]:
                f.write(label.to_renpy() + "\n\n")