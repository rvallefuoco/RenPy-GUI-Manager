import json
import os

LOCALES_DIR = "locales"

class Translator:
    def __init__(self):
        self.translations = {}
        self.current_lang = "en"

    def load_language(self, lang_code):
        path = os.path.join(LOCALES_DIR, f"{lang_code}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
                self.current_lang = lang_code
            except Exception as e:
                print(f"Errore caricamento lingua {lang_code}: {e}")
                self.translations = {}
        else:
            print(f"Lingua non trovata: {path}")
            self.translations = {}

    def get(self, key):
        return self.translations.get(key, key)

T = Translator()