import tkinter as tk
from src.ui.app import RenPyManagerApp

# Assicura che l'app parta correttamente
if __name__ == "__main__":
    root = tk.Tk()
    app = RenPyManagerApp(root)
    root.mainloop()