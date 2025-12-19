import tkinter as tk
from src.utils.translator import T
from src.ui.tabs.characters import CharactersTab
from src.ui.tabs.locations import LocationsTab
from src.ui.tabs.story import StoryTab
import os

class Dashboard(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.controller = app_controller
        self.state = app_controller.state

        # Header
        header = tk.Frame(self, bg="#333", height=40)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"{T.get('project')}: {os.path.basename(self.state.current_project_path)}", bg="#333", fg="white").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(header, text=T.get("exit"), command=self.controller.show_start, bg="#555", fg="white", bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

        # Body
        body = tk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(body, bg="#444", width=150)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.content_area = tk.Frame(body, bg="#f0f0f0")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Sidebar Buttons
        self._sidebar_btn(sidebar, T.get("characters"), lambda: self.show_tab(CharactersTab))
        self._sidebar_btn(sidebar, T.get("locations"), lambda: self.show_tab(LocationsTab))
        self._sidebar_btn(sidebar, T.get("story"), lambda: self.show_tab(StoryTab))

        # Default Tab
        self.show_tab(CharactersTab)

    def _sidebar_btn(self, parent, text, command, state=tk.NORMAL):
        tk.Button(parent, text=text, command=command, state=state,
                  bg="#666", fg="white", font=("Arial", 10, "bold"), height=2, bd=0).pack(fill=tk.X, pady=1)

    def show_tab(self, TabClass):
        for w in self.content_area.winfo_children(): w.destroy()
        if TabClass:
            # Passiamo l'app_state al Tab
            TabClass(self.content_area, self.state).pack(fill=tk.BOTH, expand=True)