"""Controls frame with action buttons"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable

from config.settings import UI_CONFIG
from config.presets import TEST_PRESETS

class ControlsFrame:
    """Control panel with test management buttons"""
    
    def __init__(self, parent, callbacks: Dict[str, Callable]):
        self.frame = ttk.Frame(parent)
        self.callbacks = callbacks
        self._create_widgets()
    
    def _create_widgets(self):
        """Create control buttons with Start/Stop on the right"""
        padding = UI_CONFIG['layout']['widget_padding']
        
        # Left side: Selection controls and presets
        ttk.Button(self.frame, text="Select All", command=self.callbacks['select_all']).grid(
            row=0, column=0, padx=padding, pady=padding, sticky='w')
        
        ttk.Button(self.frame, text="Deselect All", command=self.callbacks['deselect_all']).grid(
            row=0, column=1, padx=padding, pady=padding, sticky='w')
        
        # Presets label and buttons
        ttk.Label(self.frame, text="Presets:", font=UI_CONFIG['fonts']['label']).grid(
            row=0, column=2, padx=(15, 5), pady=padding, sticky='w')
        
        for i, preset in enumerate(TEST_PRESETS.keys(), 3):
            ttk.Button(self.frame, text=preset, command=lambda p=preset: self.callbacks['apply_preset'](p)).grid(
                row=0, column=i, padx=padding, pady=padding, sticky='w')
        
        # Right side: Test controls - use a spacer column to push them to the right
        # Add an empty column that expands to take up all extra space
        self.frame.columnconfigure(6, weight=1)
        
        # Start and Stop buttons on the right
        self.start_btn = ttk.Button(self.frame, text="Start Stress Test", command=self.callbacks['start_test'])
        self.start_btn.grid(row=0, column=7, padx=(20, 5), pady=padding, sticky='e')
        
        self.stop_btn = ttk.Button(self.frame, text="Stop Test", command=self.callbacks['stop_test'], state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=8, padx=(0, 5), pady=padding, sticky='e')
    
    def set_test_state(self, running: bool):
        self.start_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL if running else tk.DISABLED)
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)