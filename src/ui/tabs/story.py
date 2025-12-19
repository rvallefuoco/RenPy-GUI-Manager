import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from src.utils.translator import T
from src.models.story import StoryLabel
from src.models.block import BlockDialogue, BlockScene
import os


class StoryTab(tk.Frame):
    def __init__(self, parent, app_state):
        super().__init__(parent, bg="#f0f0f0")
        self.app_state = app_state
        self.current_label = None  # La Label attualmente aperta
        self.current_block_index = None  # L'indice del blocco selezionato

        # --- LAYOUT A 3 COLONNE ---
        # 1. Sidebar (Labels)
        self.sidebar = tk.Frame(self, bg="#e0e0e0", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # 2. Timeline (Centro) - Scrollabile
        self.center_frame = tk.Frame(self, bg="#d0d0d0")
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 3. Inspector (Destra)
        self.inspector = tk.Frame(self, bg="white", width=250)
        self.inspector.pack(side=tk.RIGHT, fill=tk.Y)

        # Inizializza le aree
        self.setup_sidebar()
        self.setup_timeline_area()
        self.setup_inspector_placeholder()

        # Carica dati
        self.refresh_label_list()

    # ==========================================
    # COLONNA 1: SIDEBAR (LABELS)
    # ==========================================
    def setup_sidebar(self):
        tk.Label(self.sidebar, text=T.get("labels_list"), bg="#e0e0e0", font=("Arial", 10, "bold")).pack(pady=5)

        self.label_listbox = tk.Listbox(self.sidebar, selectmode=tk.SINGLE, bd=0)
        self.label_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.label_listbox.bind("<<ListboxSelect>>", self.on_label_select)

        tk.Button(self.sidebar, text=T.get("add_label"), command=self.add_label, bg="#4CAF50", fg="white").pack(
            fill=tk.X, padx=5, pady=5)
        tk.Button(self.sidebar, text=T.get("export_btn"), command=self.export_script, bg="#FF9800", fg="white").pack(
            fill=tk.X, padx=5, pady=(20, 10))

    def refresh_label_list(self):
        self.label_listbox.delete(0, tk.END)
        for label in self.app_state.project_data["story"]:
            self.label_listbox.insert(tk.END, label.id_name)

    def add_label(self):
        name = simpledialog.askstring("Nuova Label", "Nome della Label (es. start, capitolo1):")
        if name:
            # Pulisce il nome (niente spazi)
            safe_name = name.strip().replace(" ", "_")
            new_label = StoryLabel(safe_name)
            self.app_state.project_data["story"].append(new_label)
            self.app_state.save_project_data()
            self.refresh_label_list()

    def on_label_select(self, event):
        sel = self.label_listbox.curselection()
        if sel:
            index = sel[0]
            self.current_label = self.app_state.project_data["story"][index]
            self.refresh_timeline()
            self.setup_inspector_placeholder()  # Resetta ispettore

    # ==========================================
    # COLONNA 2: TIMELINE (CENTRO)
    # ==========================================
    def setup_timeline_area(self):
        # Header con bottoni azione
        action_bar = tk.Frame(self.center_frame, bg="#bbb", height=40)
        action_bar.pack(fill=tk.X)

        tk.Button(action_bar, text=T.get("add_dialogue"), command=self.add_block_dialogue, bg="#2196F3",
                  fg="white").pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(action_bar, text=T.get("add_scene"), command=self.add_block_scene, bg="#4CAF50", fg="white").pack(
            side=tk.LEFT, padx=5, pady=5)

        # Area scrollabile
        self.canvas = tk.Canvas(self.center_frame, bg="#d0d0d0")
        self.scrollbar = tk.Scrollbar(self.center_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#d0d0d0")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw",
                                  width=500)  # Width fissa o dinamica
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_timeline(self):
        # Pulisce i blocchi vecchi
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.current_label: return

        # Disegna ogni blocco
        for i, block in enumerate(self.current_label.blocks):
            self.draw_block_widget(i, block)

    def draw_block_widget(self, index, block):
        """Disegna il rettangolo colorato per un singolo blocco."""

        # Colore diverso in base al tipo
        bg_color = "white"
        text_summary = "Block"
        if block.block_type == "dialogue":
            bg_color = "#E3F2FD"  # Azzurrino
            # Cerca il nome del personaggio dall'ID
            char_name = block.char_id
            for c in self.app_state.project_data["characters"]:
                if c.id_name == block.char_id: char_name = c.name
            text_summary = f"👤 {char_name}: {block.text[:30]}..."
        elif block.block_type == "scene":
            bg_color = "#E8F5E9"  # Verdino
            text_summary = f"🖼 SCENE: {block.location_id} ({block.variation})"

        # Container del blocco
        frame = tk.Frame(self.scrollable_frame, bg=bg_color, bd=1, relief=tk.RAISED)
        frame.pack(fill=tk.X, pady=2, padx=5)

        # Evento Click per selezione
        frame.bind("<Button-1>", lambda e, idx=index: self.select_block(idx))

        # Contenuto visivo
        lbl = tk.Label(frame, text=text_summary, bg=bg_color, anchor="w", font=("Arial", 10))
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        lbl.bind("<Button-1>", lambda e, idx=index: self.select_block(idx))  # Click anche sulla label

        # Bottoncini rapidi (Su/Giù/Elimina)
        btn_del = tk.Label(frame, text="❌", bg=bg_color, cursor="hand2")
        btn_del.pack(side=tk.RIGHT, padx=5)
        btn_del.bind("<Button-1>", lambda e, idx=index: self.delete_block(idx))

    # --- LOGICA BLOCCHI ---
    def add_block_dialogue(self):
        if not self.current_label: return messagebox.showwarning("Warning", "Seleziona una Label prima!")
        # Default narratore
        blk = BlockDialogue("narrator", "Nuovo testo...")
        self.current_label.blocks.append(blk)
        self.save_and_refresh()

    def add_block_scene(self):
        if not self.current_label: return messagebox.showwarning("Warning", "Seleziona una Label prima!")
        blk = BlockScene("bg black", "")
        self.current_label.blocks.append(blk)
        self.save_and_refresh()

    def delete_block(self, index):
        if not self.current_label: return
        del self.current_label.blocks[index]
        self.save_and_refresh()
        self.setup_inspector_placeholder()

    def save_and_refresh(self):
        self.app_state.save_project_data()
        self.refresh_timeline()

    # ==========================================
    # COLONNA 3: INSPECTOR (DESTRA)
    # ==========================================
    def select_block(self, index):
        self.current_block_index = index
        block = self.current_label.blocks[index]
        self.show_inspector(block)

    def setup_inspector_placeholder(self):
        for w in self.inspector.winfo_children(): w.destroy()
        tk.Label(self.inspector, text=T.get("inspector"), bg="white", fg="gray").pack(pady=20)

    def show_inspector(self, block):
        for w in self.inspector.winfo_children(): w.destroy()

        tk.Label(self.inspector, text=T.get("inspector"), font=("Arial", 12, "bold"), bg="white").pack(pady=10)

        form = tk.Frame(self.inspector, bg="white")
        form.pack(fill=tk.BOTH, expand=True, padx=10)

        # Campi diversi in base al tipo
        if block.block_type == "dialogue":
            self._build_dialogue_inspector(form, block)
        elif block.block_type == "scene":
            self._build_scene_inspector(form, block)

        # Tasti Spostamento
        btn_frame = tk.Frame(self.inspector, bg="white")
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text=T.get("move_up"), command=self.move_block_up).pack(side=tk.LEFT, expand=True)
        tk.Button(btn_frame, text=T.get("move_down"), command=self.move_block_down).pack(side=tk.LEFT, expand=True)

    def _build_dialogue_inspector(self, parent, block):
        # Personaggio (Combobox)
        tk.Label(parent, text=T.get("block_char"), bg="white").pack(anchor="w")
        char_values = ["narrator"] + [c.id_name for c in self.app_state.project_data["characters"]]
        cb_char = ttk.Combobox(parent, values=char_values)
        cb_char.set(block.char_id)
        cb_char.pack(fill=tk.X, pady=(0, 5))

        # Espressione
        tk.Label(parent, text=T.get("block_expr"), bg="white").pack(anchor="w")
        entry_expr = tk.Entry(parent)
        entry_expr.insert(0, block.expression)
        entry_expr.pack(fill=tk.X, pady=(0, 5))

        # Testo (Text Area)
        tk.Label(parent, text=T.get("block_text"), bg="white").pack(anchor="w")
        txt_area = tk.Text(parent, height=5, width=20)
        txt_area.insert("1.0", block.text)
        txt_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Save Button
        def save():
            block.char_id = cb_char.get()
            block.expression = entry_expr.get()
            block.text = txt_area.get("1.0", tk.END).strip()
            self.save_and_refresh()

        tk.Button(parent, text="💾 Update", command=save, bg="#2196F3", fg="white").pack(fill=tk.X)

    def _build_scene_inspector(self, parent, block):
        # Luogo (Combobox)
        tk.Label(parent, text=T.get("block_loc"), bg="white").pack(anchor="w")
        loc_values = ["bg black"] + [l.id_name for l in self.app_state.project_data["locations"]]
        cb_loc = ttk.Combobox(parent, values=loc_values)
        cb_loc.set(block.location_id)
        cb_loc.pack(fill=tk.X, pady=(0, 5))

        # Variante (Combobox intelligente)
        tk.Label(parent, text=T.get("block_var"), bg="white").pack(anchor="w")
        cb_var = ttk.Combobox(parent)  # Valori popolati dinamicamente dopo? Per ora liberi
        cb_var.set(block.variation)
        cb_var.pack(fill=tk.X, pady=(0, 10))

        def save():
            block.location_id = cb_loc.get()
            block.variation = cb_var.get()
            self.save_and_refresh()

        tk.Button(parent, text="💾 Update", command=save, bg="#4CAF50", fg="white").pack(fill=tk.X)

    def move_block_up(self):
        idx = self.current_block_index
        if idx is not None and idx > 0:
            self.current_label.blocks[idx], self.current_label.blocks[idx - 1] = self.current_label.blocks[idx - 1], \
            self.current_label.blocks[idx]
            self.current_block_index -= 1  # Segui il blocco
            self.save_and_refresh()

    def move_block_down(self):
        idx = self.current_block_index
        if idx is not None and idx < len(self.current_label.blocks) - 1:
            self.current_label.blocks[idx], self.current_label.blocks[idx + 1] = self.current_label.blocks[idx + 1], \
            self.current_label.blocks[idx]
            self.current_block_index += 1
            self.save_and_refresh()

    def export_script(self):
        try:
            self.app_state.generate_rpy_script()
            messagebox.showinfo("Success", "File 'story.rpy' generated!")
        except Exception as e:
            messagebox.showerror("Error", str(e))