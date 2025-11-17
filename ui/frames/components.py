"""Components selection frame"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from config.settings import UI_CONFIG
from config.presets import TEST_COMPONENTS
from core.manager import TestManager
from ui.widgets.tree_view import ComponentTreeView  # Fixed import path

class ComponentsFrame:
    """Frame containing the component tree view"""
    
    def __init__(self, parent, test_manager: TestManager):
        self.frame = ttk.LabelFrame(parent, text="Stress Test Components")
        self.test_manager = test_manager
        self.tree_view = ComponentTreeView(self.frame, test_manager)
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup frame layout"""
        padding = UI_CONFIG['layout']['frame_padding']
        self.tree_view.grid(row=0, column=0, sticky='nsew', padx=padding, pady=padding)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def bind_events(self, callback: Callable):
        self.tree_view.bind_events(callback)
    
    def toggle_selection(self, event) -> bool:
        return self.tree_view.toggle_selection(event)
    
    def refresh(self):
        self.tree_view.refresh()
    
    def get_enabled_count(self) -> int:
        return len(self.test_manager.get_enabled_components())
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)