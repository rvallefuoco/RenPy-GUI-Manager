import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from src.utils.translator import T
import os


class StartScreen(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.controller = app_controller
        self.state = app_controller.state

        # Lingua
        top = tk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=5)
        self.cb = ttk.Combobox(top, values=["en", "it"], state="readonly", width=5)
        self.cb.set(self.state.settings.get("language", "en"))
        self.cb.pack(side=tk.RIGHT)
        self.cb.bind("<<ComboboxSelected>>", self.on_lang_change)

        # Contenuto
        tk.Label(self, text=T.get("app_title"), font=("Arial", 20)).pack(pady=30)

        tk.Button(self, text=T.get("load_project"), command=self.open_dialog, width=20, height=2).pack(pady=10)

        tk.Label(self, text=T.get("recents"), font=("Arial", 10, "bold")).pack(pady=(40, 5))
        for path in self.state.settings.get("recents", []):
            tk.Button(self, text=path, command=lambda p=path: self.load_recent(p)).pack(fill=tk.X, padx=100, pady=2)

    def open_dialog(self):
        path = filedialog.askdirectory()
        if path: self.load_recent(path)

    def load_recent(self, path):
        if not os.path.isdir(os.path.join(path, "game")):
            messagebox.showerror("Error", T.get("error_no_game"))
            return

        self.state.load_project_data(path)
        self.controller.show_dashboard()

    def on_lang_change(self, event):
        self.state.settings["language"] = self.cb.get()
        self.state.save_settings()
        self.controller.reload_ui()