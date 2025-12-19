import json
import os
from src.utils.translator import T
from src.models.character import Character

SETTINGS_FILE = "settings.json"


class AppState:
    def __init__(self):
        self.settings = {}
        self.current_project_path = None
        self.project_data = {"characters": []}
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

        char_file = os.path.join(path, ".manager", "characters.json")
        self.project_data["characters"] = []

        # Assicura che la cartella .manager esista
        manager_dir = os.path.join(path, ".manager")
        if not os.path.exists(manager_dir): os.makedirs(manager_dir)

        if os.path.exists(char_file):
            try:
                with open(char_file, "r") as f:
                    data = json.load(f)
                    for char_dict in data:
                        self.project_data["characters"].append(Character.from_dict(char_dict))
            except Exception as e:
                print(f"Errore caricamento: {e}")

    def save_project_data(self):
        if not self.current_project_path: return
        char_file = os.path.join(self.current_project_path, ".manager", "characters.json")
        data_to_save = [c.to_dict() for c in self.project_data["characters"]]
        with open(char_file, "w") as f:
            json.dump(data_to_save, f, indent=4)

    def generate_rpy_characters(self):
        if not self.current_project_path: return
        rpy_path = os.path.join(self.current_project_path, "game", "characters.rpy")
        with open(rpy_path, "w", encoding="utf-8") as f:
            f.write("# File generato automaticamente da Ren'Py Project Manager\n")
            f.write("# Non modificare manualmente.\n\n")
            for char in self.project_data["characters"]:
                f.write(char.to_renpy_code() + "\n")