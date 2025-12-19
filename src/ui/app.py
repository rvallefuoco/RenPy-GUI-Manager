from src.core.state import AppState
from src.ui.screens.start import StartScreen
from src.ui.screens.dashboard import Dashboard
from src.utils.translator import T


class RenPyManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x600")

        # Inizializza il "Cervello"
        self.state = AppState()
        self.reload_ui()

    def reload_ui(self):
        """Ricarica l'interfaccia (utile per cambio lingua)"""
        self.root.title(T.get("app_title"))
        self.show_start()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_start(self):
        self.clear_window()
        StartScreen(self.root, self).pack(fill="both", expand=True)

    def show_dashboard(self):
        self.clear_window()
        Dashboard(self.root, self).pack(fill="both", expand=True)