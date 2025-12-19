import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, ttk
import json
import os

from src.utils.translator import T
from src.models.character import Character

SETTINGS_FILE = "settings.json"

class RenPyManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ren'Py Project Manager") 
        self.root.geometry("900x600")
        
        self.settings = {}
        self.current_project_path = None
        self.project_data = {"characters": []}

        self.load_settings()
        self.show_start_screen()

    # --- SETTINGS & LOGICA ---
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

        lang = self.settings.get("language", "en")
        T.load_language(lang)
        self.root.title(T.get("app_title"))

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)

    def change_language(self, event):
        new_lang = self.lang_combobox.get()
        self.settings["language"] = new_lang
        self.save_settings()
        T.load_language(new_lang)
        self.root.title(T.get("app_title"))
        self.show_start_screen()

    def add_to_recents(self, path):
        recents = self.settings.get("recents", [])
        if path in recents: recents.remove(path)
        recents.insert(0, path)
        self.settings["recents"] = recents[:3]
        self.save_settings()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # --- GESTIONE DATI PROGETTO ---
    def load_project_data(self):
        char_file = os.path.join(self.current_project_path, ".manager", "characters.json")
        self.project_data["characters"] = []
        if os.path.exists(char_file):
            try:
                with open(char_file, "r") as f:
                    data = json.load(f)
                    for char_dict in data:
                        self.project_data["characters"].append(Character.from_dict(char_dict))
            except Exception as e:
                print(f"Errore caricamento: {e}")

    def save_project_data(self):
        char_file = os.path.join(self.current_project_path, ".manager", "characters.json")
        data_to_save = [c.to_dict() for c in self.project_data["characters"]]
        with open(char_file, "w") as f:
            json.dump(data_to_save, f, indent=4)

    def generate_rpy_characters(self):
        try:
            rpy_path = os.path.join(self.current_project_path, "game", "characters.rpy")
            with open(rpy_path, "w", encoding="utf-8") as f:
                f.write(T.get("generated_1"))
                f.write(T.get("generated_2"))
                for char in self.project_data["characters"]:
                    f.write(char.to_renpy_code() + "\n")
            messagebox.showinfo("Success", T.get("export_success"))
        except Exception as e:
            messagebox.showerror("Error", f"{T.get('export_error')} {e}")

    # --- INTERFACCIA: START SCREEN ---
    def show_start_screen(self):
        self.clear_window()
        
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(top_frame, text="Language:").pack(side=tk.RIGHT, padx=5)
        self.lang_combobox = ttk.Combobox(top_frame, values=["en", "it"], state="readonly", width=5)
        self.lang_combobox.set(self.settings.get("language", "en"))
        self.lang_combobox.pack(side=tk.RIGHT)
        self.lang_combobox.bind("<<ComboboxSelected>>", self.change_language)

        tk.Label(self.root, text=T.get("app_title"), font=("Arial", 20)).pack(pady=30)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text=T.get("load_project"), command=self.open_project_dialog, width=20, height=2).pack(side=tk.LEFT, padx=10)
        
        tk.Label(self.root, text=T.get("recents"), font=("Arial", 10, "bold")).pack(pady=(40, 5))
        for path in self.settings.get("recents", []):
            tk.Button(self.root, text=path, command=lambda p=path: self.load_project(p)).pack(fill=tk.X, padx=100, pady=2)

    def open_project_dialog(self):
        path = filedialog.askdirectory()
        if path: self.load_project(path)

    def load_project(self, path):
        if not os.path.isdir(os.path.join(path, "game")):
            messagebox.showerror("Error", T.get("error_no_game"))
            return
        
        manager_dir = os.path.join(path, ".manager")
        if not os.path.exists(manager_dir): os.makedirs(manager_dir)

        self.current_project_path = path
        self.add_to_recents(path)
        self.load_project_data()
        self.show_dashboard()

    # --- INTERFACCIA: DASHBOARD ---
    def show_dashboard(self):
        self.clear_window()
        
        header = tk.Frame(self.root, bg="#333", height=40)
        header.pack(fill=tk.X)
        tk.Label(header, text=f"{T.get('project')}: {os.path.basename(self.current_project_path)}", bg="#333", fg="white").pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(header, text=T.get("exit"), command=self.show_start_screen, bg="#555", fg="white", bd=0).pack(side=tk.RIGHT, padx=10, pady=5)

        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        sidebar = tk.Frame(main_container, bg="#444", width=150)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Button(sidebar, text=T.get("scenes"), state=tk.DISABLED, bg="#444", fg="gray", bd=0).pack(fill=tk.X, pady=1)

        tk.Button(sidebar, text=T.get("characters"), command=lambda: self.open_character_tab(content_area),
                  bg="#666", fg="white", font=("Arial", 10, "bold"), height=2, bd=0).pack(fill=tk.X, pady=1)
        
        tk.Button(sidebar, text=T.get("assets"), state=tk.DISABLED, bg="#444", fg="gray", bd=0).pack(fill=tk.X, pady=1)
        
        tk.Button(sidebar, text=T.get("quests"), state=tk.DISABLED, bg="#444", fg="gray", bd=0).pack(fill=tk.X, pady=1)

        content_area = tk.Frame(main_container, bg="#f0f0f0")
        content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.open_character_tab(content_area)

    # --- INTERFACCIA: TAB CHARACTER ---
    def open_character_tab(self, parent_frame):
        for widget in parent_frame.winfo_children(): widget.destroy()

        list_frame = tk.Frame(parent_frame, bg="#e0e0e0", width=200)
        list_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        details_frame = tk.Frame(parent_frame, bg="white")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(list_frame, text=T.get("list_header"), bg="#e0e0e0", font=("Arial", 10, "bold")).pack(pady=5)
        self.char_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, bd=0)
        self.char_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.char_listbox.bind("<<ListboxSelect>>", lambda e: self.load_char_details(details_frame))

        tk.Button(list_frame, text=T.get("new_btn"), command=lambda: self.add_character(details_frame), 
                  bg="#4CAF50", fg="white").pack(fill=tk.X, padx=5, pady=5)

        tk.Button(list_frame, text=T.get("export_btn"), command=self.generate_rpy_characters, 
                  bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, padx=5, pady=(20, 10))

        self.refresh_char_list()
        self.details_label = tk.Label(details_frame, text=T.get("select_or_create"), fg="gray", bg="white")
        self.details_label.pack(expand=True)

    def refresh_char_list(self):
        self.char_listbox.delete(0, tk.END)
        for char in self.project_data["characters"]:
            self.char_listbox.insert(tk.END, char.name)

    def add_character(self, details_frame):
        new_char = Character("new", "New Character", "#000000")
        self.project_data["characters"].append(new_char)
        self.save_project_data()
        self.refresh_char_list()
        self.char_listbox.selection_clear(0, tk.END)
        self.char_listbox.selection_set(tk.END)
        self.load_char_details(details_frame)

    def load_char_details(self, parent_frame):
        selection = self.char_listbox.curselection()
        if not selection: return
        index = selection[0]
        char_obj = self.project_data["characters"][index]

        for widget in parent_frame.winfo_children(): widget.destroy()

        tk.Label(parent_frame, text=T.get("edit_char_title"), font=("Arial", 14, "bold"), bg="white").pack(pady=10, anchor="w", padx=20)
        form = tk.Frame(parent_frame, bg="white")
        form.pack(fill=tk.BOTH, expand=True, padx=20)

        tk.Label(form, text=T.get("var_label"), bg="white").pack(anchor="w")
        entry_id = tk.Entry(form)
        entry_id.insert(0, char_obj.id_name)
        entry_id.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text=T.get("name_label"), bg="white").pack(anchor="w")
        entry_name = tk.Entry(form)
        entry_name.insert(0, char_obj.name)
        entry_name.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text=T.get("color_label"), bg="white").pack(anchor="w")
        color_btn = tk.Button(form, text=char_obj.color, bg=char_obj.color, width=10)
        
        def pick_color():
            c = colorchooser.askcolor(color=char_obj.color)[1]
            if c:
                color_btn.config(bg=c, text=c)
                save_changes()

        color_btn.config(command=pick_color)
        color_btn.pack(anchor="w", pady=(0, 10))

        def save_changes(event=None):
            char_obj.id_name = entry_id.get()
            char_obj.name = entry_name.get()
            char_obj.color = color_btn.cget("text")
            self.save_project_data()
            self.refresh_char_list()
            self.char_listbox.selection_clear(0, tk.END)
            self.char_listbox.selection_set(index)

        tk.Button(form, text=T.get("save_btn"), command=save_changes, bg="#2196F3", fg="white").pack(pady=20, anchor="e")