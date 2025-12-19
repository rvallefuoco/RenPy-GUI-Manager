import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from src.utils.translator import T
from src.models.character import Character
import os


class CharactersTab(tk.Frame):
    def __init__(self, parent, app_state):
        super().__init__(parent, bg="#f0f0f0")
        self.app_state = app_state  # Riferimento ai dati condivisi

        # Layout principale
        self.list_frame = tk.Frame(self, bg="#e0e0e0", width=200)
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.details_frame = tk.Frame(self, bg="white")
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_list()
        self.show_placeholder()

    def setup_list(self):
        tk.Label(self.list_frame, text=T.get("list_header"), bg="#e0e0e0", font=("Arial", 10, "bold")).pack(pady=5)

        self.char_listbox = tk.Listbox(self.list_frame, selectmode=tk.SINGLE, bd=0)
        self.char_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.char_listbox.bind("<<ListboxSelect>>", self.on_select)

        tk.Button(self.list_frame, text=T.get("new_btn"), command=self.add_character, bg="#4CAF50", fg="white").pack(
            fill=tk.X, padx=5, pady=5)
        tk.Button(self.list_frame, text=T.get("export_btn"), command=self.export_rpy, bg="#FF9800", fg="white").pack(
            fill=tk.X, padx=5, pady=(20, 10))

        self.refresh_list()

    def show_placeholder(self):
        for widget in self.details_frame.winfo_children(): widget.destroy()
        tk.Label(self.details_frame, text=T.get("select_or_create"), fg="gray", bg="white").pack(expand=True)

    def refresh_list(self):
        self.char_listbox.delete(0, tk.END)
        for char in self.app_state.project_data["characters"]:
            self.char_listbox.insert(tk.END, char.name)

    def add_character(self):
        new_char = Character("new", "New Character", "#000000")
        self.app_state.project_data["characters"].append(new_char)
        self.app_state.save_project_data()
        self.refresh_list()
        self.char_listbox.selection_clear(0, tk.END)
        self.char_listbox.selection_set(tk.END)
        self.load_details(len(self.app_state.project_data["characters"]) - 1)

    def on_select(self, event):
        selection = self.char_listbox.curselection()
        if selection:
            self.load_details(selection[0])

    def load_details(self, index):
        char_obj = self.app_state.project_data["characters"][index]

        for widget in self.details_frame.winfo_children(): widget.destroy()

        # Header
        tk.Label(self.details_frame, text=T.get("edit_char_title"), font=("Arial", 14, "bold"), bg="white").pack(
            pady=10, anchor="w", padx=20)

        form = tk.Frame(self.details_frame, bg="white")
        form.pack(fill=tk.BOTH, expand=True, padx=20)

        # Campi
        self._create_entry(form, T.get("var_label"), char_obj.id_name, "id_name", char_obj)
        self._create_entry(form, T.get("name_label"), char_obj.name, "name", char_obj)

        # Colore
        tk.Label(form, text=T.get("color_label"), bg="white").pack(anchor="w")
        color_btn = tk.Button(form, text=char_obj.color, bg=char_obj.color, width=10)
        color_btn.pack(anchor="w", pady=(0, 10))
        color_btn.config(command=lambda: self.pick_color(char_obj, color_btn))

        # Side Images
        self._create_side_images_ui(form, char_obj)

        # Save Button
        tk.Button(form, text=T.get("save_btn"),
                  command=lambda: self.save_changes(char_obj, index),
                  bg="#2196F3", fg="white").pack(pady=10, anchor="e")

        # Conserviamo i riferimenti ai widget per leggere i valori dopo
        self.current_form_entries = form

    def _create_entry(self, parent, label, value, key, char_obj):
        tk.Label(parent, text=label, bg="white").pack(anchor="w")
        entry = tk.Entry(parent)
        entry.insert(0, value)
        entry.pack(fill=tk.X, pady=(0, 5))
        # Salviamo il riferimento all'entry nell'oggetto stesso temporaneamente o usiamo un dizionario lookup
        setattr(self, f"entry_{key}", entry)

    def pick_color(self, char_obj, btn):
        c = colorchooser.askcolor(color=char_obj.color)[1]
        if c:
            char_obj.color = c
            btn.config(bg=c, text=c)

    def _create_side_images_ui(self, parent, char_obj):
        tk.Label(parent, text="Image Tag:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 0))
        self.entry_img_tag = tk.Entry(parent)
        self.entry_img_tag.insert(0, char_obj.image_tag)
        self.entry_img_tag.pack(fill=tk.X)

        tk.Label(parent, text="Side Images:", bg="white").pack(anchor="w", pady=(5, 0))

        list_frame = tk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.sides_listbox = tk.Listbox(list_frame, height=5)
        self.sides_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(fill=tk.X)
        tk.Button(btn_frame, text="+ Add", command=lambda: self.add_side_image(char_obj)).pack(side=tk.LEFT)
        tk.Button(btn_frame, text="- Remove", command=lambda: self.remove_side_image(char_obj)).pack(side=tk.LEFT)

        self.refresh_sides_list(char_obj)

    def refresh_sides_list(self, char_obj):
        self.sides_listbox.delete(0, tk.END)
        for img in char_obj.side_images:
            self.sides_listbox.insert(tk.END, f"{img['tag']} -> {img['path']}")

    def add_side_image(self, char_obj):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.webp")])
        if not file_path: return

        # Logica path relativo
        game_dir = os.path.join(self.app_state.current_project_path, "game")
        if file_path.startswith(self.app_state.current_project_path):
            rel_path = os.path.relpath(file_path, game_dir).replace("\\", "/")
        else:
            rel_path = file_path  # Fallback assoluto

        from tkinter import simpledialog
        tag = simpledialog.askstring("Attribute", "Attribute (e.g. happy):")
        if tag is None: return

        char_obj.side_images.append({"tag": tag.strip(), "path": rel_path})
        self.refresh_sides_list(char_obj)

    def remove_side_image(self, char_obj):
        sel = self.sides_listbox.curselection()
        if not sel: return
        del char_obj.side_images[sel[0]]
        self.refresh_sides_list(char_obj)

    def save_changes(self, char_obj, index):
        # Recupera valori dalle entry salvate
        char_obj.id_name = self.entry_id_name.get()
        char_obj.name = self.entry_name.get()
        char_obj.image_tag = self.entry_img_tag.get()

        self.app_state.save_project_data()
        self.refresh_list()
        self.char_listbox.selection_set(index)

    def export_rpy(self):
        try:
            self.app_state.generate_rpy_characters()
            messagebox.showinfo("Success", T.get("export_success"))
        except Exception as e:
            messagebox.showerror("Error", str(e))