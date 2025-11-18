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
        self.test_running = False
        self.spinner_index = 0
        self.spinner_frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        self.spinner_after_id = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create control buttons with Start/Stop on the LEFT and selection controls on the RIGHT"""
        padding = UI_CONFIG['layout']['widget_padding']
        
        # LEFT side: Test controls (Start/Stop) 
        self.start_btn = ttk.Button(self.frame, text="Start Stress Test", 
                                   command=self.callbacks['start_test'])
        self.start_btn.grid(row=0, column=0, padx=(5, 5), pady=padding, sticky='w')
        
        self.stop_btn = ttk.Button(self.frame, text="Stop Test", 
                                  command=self.callbacks['stop_test'], state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=(0, 15), pady=padding, sticky='w')
        
        # Spinner indicator with fixed width
        self.spinner_label = ttk.Label(self.frame, text="", font=('Arial', 14), width=2,
                                      foreground=UI_CONFIG['colors']['info_text'])
        self.spinner_label.grid(row=0, column=2, padx=(0, 15), pady=padding, sticky='w')
        
        # Center: Presets
        ttk.Label(self.frame, text="Presets:", font=UI_CONFIG['fonts']['label']).grid(
            row=0, column=3, padx=(15, 5), pady=padding, sticky='w')
        
        # Create preset buttons dynamically
        preset_names = list(TEST_PRESETS.keys())
        for i, preset in enumerate(preset_names):
            ttk.Button(self.frame, text=preset, 
                      command=lambda p=preset: self.callbacks['apply_preset'](p)).grid(
                row=0, column=i+4, padx=padding, pady=padding, sticky='w')
        
        # RIGHT side: Selection controls - use a spacer column to push them to the right
        # Calculate spacer column position (after all preset buttons)
        spacer_col = len(preset_names) + 4
        self.frame.columnconfigure(spacer_col, weight=1)
        
        # Selection buttons on the right
        ttk.Button(self.frame, text="Select All", 
                  command=self.callbacks['select_all']).grid(
            row=0, column=spacer_col+1, padx=(5, 5), pady=padding, sticky='e')
        
        ttk.Button(self.frame, text="Deselect All", 
                  command=self.callbacks['deselect_all']).grid(
            row=0, column=spacer_col+2, padx=(0, 5), pady=padding, sticky='e')
    
    def set_test_state(self, running: bool):
        """Update button states and spinner based on test running status"""
        self.test_running = running
        self.start_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL if running else tk.DISABLED)
        
        # Start or stop spinner animation
        if running:
            self._start_spinner()
        else:
            self._stop_spinner()
    
    def _start_spinner(self):
        """Start the spinner animation"""
        self.spinner_index = 0
        self._update_spinner()
    
    def _stop_spinner(self):
        """Stop the spinner animation"""
        if self.spinner_after_id:
            self.frame.after_cancel(self.spinner_after_id)
            self.spinner_after_id = None
        self.spinner_label.config(text="")
    
    def _update_spinner(self):
        """Update spinner to next frame"""
        if not self.test_running:
            return
            
        self.spinner_label.config(text=self.spinner_frames[self.spinner_index])
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_frames)
        
        # Schedule next update
        self.spinner_after_id = self.frame.after(100, self._update_spinner)
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)