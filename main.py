"""Main entry point for the y-cruncher GUI application"""
import tkinter as tk
from tkinter import messagebox

from utils.helpers import check_ycruncher_present
from ui.main_window import YCruncherGUI

def main():
    """Application entry point"""
    if not check_ycruncher_present():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "y-cruncher Not Found", 
            "y-cruncher.exe was not found in the current directory or system PATH.\n\n"
            "Please download y-cruncher from:\n"
            "https://www.numberworld.org/y-cruncher/\n\n"
            "Extract and place y-cruncher.exe in this directory or add to PATH."
        )
        root.destroy()
        return
    
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
    except ImportError:
        root = tk.Tk()
    
    app = YCruncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()