"""Header frame for the application"""
import tkinter as tk
from tkinter import ttk

from config.settings import UI_CONFIG

class HeaderFrame:
    """Application header with title"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create header widgets"""
        ttk.Label(
            self.frame, 
            text=UI_CONFIG['window']['title'], 
            font=UI_CONFIG['fonts']['header']
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky='w')
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)