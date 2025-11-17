"""Console output frame"""
from tkinter import ttk

from config.settings import UI_CONFIG
from ui.widgets.ansi_text import AnsiTextWidget

class ConsoleFrame:
    """Console output display with ANSI color code support"""
    
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Console Output")
        self.console = AnsiTextWidget(self.frame)
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup console layout"""
        padding = UI_CONFIG['layout']['frame_padding']
        self.console.grid(row=0, column=0, sticky='nsew', padx=padding, pady=padding)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def write_ansi(self, text: str):
        """Write text with ANSI color code parsing"""
        self.console.write_ansi(text)
    
    def write(self, text: str, tag: str = None):
        self.console.write(text, tag)
    
    def clear(self):
        self.console.clear()
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)