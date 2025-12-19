import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from src.utils.translator import T
from src.models.location import Location
import os


class LocationsTab(tk.Frame):
    def __init__(self, parent, app_state):
        super().__init__(parent, bg="#f0f0f0")
        self.app_state = app_state

        # --- LAYOUT PRINCIPALE ---
        # Lista Stanze (Sinistra)
        self.list_frame = tk.Frame(self, bg="#e0e0e0", width=200)
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Dettagli Stanza (Destra)
        self.details_frame = tk.Frame(self, bg="white")
        self.details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_sidebar()
        self.show_placeholder()

    def setup_sidebar(self):
        tk.Label(self.list_frame, text=T.get("list_header"), bg="#e0e0e0", font=("Arial", 10, "bold")).pack(pady=5)

        self.loc_listbox = tk.Listbox(self.list_frame, selectmode=tk.SINGLE, bd=0)
        self.loc_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.loc_listbox.bind("<<ListboxSelect>>", self.on_location_select)

        tk.Button(self.list_frame, text=T.get("new_btn"), command=self.add_location, bg="#4CAF50", fg="white").pack(
            fill=tk.X, padx=5, pady=5)
        tk.Button(self.list_frame, text=T.get("export_btn"), command=self.export_rpy, bg="#FF9800", fg="white").pack(
            fill=tk.X, padx=5, pady=(20, 10))

        self.refresh_loc_list()

    def show_placeholder(self):
        for w in self.details_frame.winfo_children(): w.destroy()
        tk.Label(self.details_frame, text="Seleziona o crea un Luogo", fg="gray", bg="white").pack(expand=True)

    def refresh_loc_list(self):
        self.loc_listbox.delete(0, tk.END)
        for loc in self.app_state.project_data["locations"]:
            self.loc_listbox.insert(tk.END, loc.name)

    def add_location(self):
        new_loc = Location("bg camera", "Nuova Stanza")
        self.app_state.project_data["locations"].append(new_loc)
        self.app_state.save_project_data()
        self.refresh_loc_list()
        self.loc_listbox.selection_clear(0, tk.END)
        self.loc_listbox.selection_set(tk.END)
        self.load_details(len(self.app_state.project_data["locations"]) - 1)

    def on_location_select(self, event):
        sel = self.loc_listbox.curselection()
        if sel: self.load_details(sel[0])

    def load_details(self, index):
        loc_obj = self.app_state.project_data["locations"][index]
        for w in self.details_frame.winfo_children(): w.destroy()

        # --- HEADER ---
        tk.Label(self.details_frame, text="Modifica Luogo", font=("Arial", 14, "bold"), bg="white").pack(pady=10,
                                                                                                         anchor="w",
                                                                                                         padx=20)

        # Container scrollabile o semplice frame
        form = tk.Frame(self.details_frame, bg="white")
        form.pack(fill=tk.BOTH, expand=True, padx=20)

        # --- DATI BASE ---
        tk.Label(form, text=T.get("loc_name_label"), bg="white").pack(anchor="w")
        entry_name = tk.Entry(form)
        entry_name.insert(0, loc_obj.name)
        entry_name.pack(fill=tk.X, pady=(0, 5))

        tk.Label(form, text=T.get("loc_id_label"), bg="white").pack(anchor="w")
        entry_id = tk.Entry(form)
        entry_id.insert(0, loc_obj.id_name)
        entry_id.pack(fill=tk.X, pady=(0, 10))

        # --- LISTA VARIANTI (Images) ---
        tk.Label(form, text=T.get("variations_label"), bg="white", font=("Arial", 10, "bold")).pack(anchor="w",
                                                                                                    pady=(10, 5))

        # Frame che contiene la lista a sinistra e l'anteprima a destra
        var_container = tk.Frame(form, bg="white", bd=1, relief=tk.SUNKEN)
        var_container.pack(fill=tk.BOTH, expand=True, pady=5)

        # > Lista Varianti
        self.vars_listbox = tk.Listbox(var_container, width=30)
        self.vars_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.vars_listbox.bind("<<ListboxSelect>>", lambda e: self.on_variant_select(loc_obj))

        # > Anteprima
        self.preview_lbl = tk.Label(var_container, text="No Preview", bg="#ddd", width=40)
        self.preview_lbl.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # > Bottoni Varianti
        btn_frame = tk.Frame(form, bg="white")
        btn_frame.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text=T.get("add_var_btn"), command=lambda: self.add_variant(loc_obj)).pack(side=tk.LEFT,
                                                                                                        padx=2)
        tk.Button(btn_frame, text="- Rimuovi", command=lambda: self.remove_variant(loc_obj)).pack(side=tk.LEFT, padx=2)

        self.refresh_vars_list(loc_obj)

        # --- SAVE BTN ---
        def save():
            loc_obj.name = entry_name.get()
            loc_obj.id_name = entry_id.get()
            self.app_state.save_project_data()
            self.refresh_loc_list()  # Aggiorna nome nella sidebar
            self.loc_listbox.selection_clear(0, tk.END)
            self.loc_listbox.selection_set(index)  # Mantiene selezione

        tk.Button(form, text=T.get("save_btn"), command=save, bg="#2196F3", fg="white").pack(pady=10, anchor="e")

    # --- LOGICA VARIANTI ---
    def refresh_vars_list(self, loc_obj):
        self.vars_listbox.delete(0, tk.END)
        for img in loc_obj.images:
            attr = img['attribute'] if img['attribute'] else "(base)"
            self.vars_listbox.insert(tk.END, attr)

    def add_variant(self, loc_obj):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.webp")])
        if not path: return

        # Path Relativo
        game_dir = os.path.join(self.app_state.current_project_path, "game")
        if path.startswith(self.app_state.current_project_path):
            rel_path = os.path.relpath(path, game_dir).replace("\\", "/")
        else:
            rel_path = path

        # Chiede nome variante
        attr = simpledialog.askstring("Variante",
                                      "Nome variante (es. day, night, rain):\nLascia vuoto per l'immagine di default.")
        if attr is None: return  # Annullato

        loc_obj.images.append({"attribute": attr.strip(), "path": rel_path})
        self.app_state.save_project_data()
        self.refresh_vars_list(loc_obj)

    def remove_variant(self, loc_obj):
        sel = self.vars_listbox.curselection()
        if not sel: return
        del loc_obj.images[sel[0]]
        self.app_state.save_project_data()
        self.refresh_vars_list(loc_obj)
        self.preview_lbl.config(image="", text="No Preview")

    def on_variant_select(self, loc_obj):
        sel = self.vars_listbox.curselection()
        if not sel: return

        index = sel[0]
        img_data = loc_obj.images[index]
        full_path = os.path.join(self.app_state.current_project_path, "game", img_data["path"])

        if os.path.exists(full_path):
            try:
                self.tk_img = tk.PhotoImage(file=full_path)
                # Ridimensiona per l'anteprima (molto grezzo ma funzionale)
                self.tk_img = self.tk_img.subsample(8, 8)
                self.preview_lbl.config(image=self.tk_img, text="")
            except:
                self.preview_lbl.config(image="", text="Format Error")
        else:
            self.preview_lbl.config(image="", text="File Not Found")

    def export_rpy(self):
        try:
            self.app_state.generate_rpy_locations()
            messagebox.showinfo("Success", "File 'locations.rpy' creato!")
        except Exception as e:
            messagebox.showerror("Error", str(e))