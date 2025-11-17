"""Configuration frame with settings panel"""
import tkinter as tk
from tkinter import ttk
from typing import Tuple

from config.settings import UI_CONFIG, TEST_CONFIG
from core.models import TestConfig

class ConfigurationFrame:
    """Configuration panel with real-time validation and auto-calculation"""
    
    def __init__(self, parent, config: TestConfig):
        self.frame = ttk.LabelFrame(parent, text="Test Configuration")
        self.config = config
        self.enabled_count = 0
        self.time_limit_manual = False
        self._correcting_time_limit = False
        
        self._create_widgets()
        self._setup_bindings()
        self._update_display()
    
    def _create_widgets(self):
        """Create configuration widgets"""
        padding = UI_CONFIG['layout']['frame_padding']
        label_font = UI_CONFIG['fonts']['label']
        entry_font = UI_CONFIG['fonts']['entry']
        small_font = UI_CONFIG['fonts']['small']
        
        # Time Limit
        ttk.Label(self.frame, text="Time Limit:", font=label_font).grid(
            row=0, column=0, padx=(5, 3), pady=padding, sticky='e')
        
        self.tl_entry = ttk.Entry(self.frame, width=8, font=entry_font)
        self.tl_entry.insert(0, self.config.time_limit)
        self.tl_entry.grid(row=0, column=1, padx=3, pady=padding, sticky='w')
        
        ttk.Label(self.frame, text="sec", font=small_font).grid(
            row=0, column=2, padx=(0, 15), pady=padding, sticky='w')
        
        # Duration per Test
        ttk.Label(self.frame, text="Per Test:", font=label_font).grid(
            row=0, column=3, padx=(0, 3), pady=padding, sticky='e')
        
        self.d_entry = ttk.Entry(self.frame, width=8, font=entry_font)
        self.d_entry.insert(0, self.config.duration_per_test)
        self.d_entry.grid(row=0, column=4, padx=3, pady=padding, sticky='w')
        
        ttk.Label(self.frame, text="sec", font=small_font).grid(
            row=0, column=5, padx=(0, 15), pady=padding, sticky='w')
        
        # Memory Allocation
        ttk.Label(self.frame, text="Memory:", font=label_font).grid(
            row=0, column=6, padx=(0, 3), pady=padding, sticky='e')
        
        self.m_entry = ttk.Entry(self.frame, width=6, font=entry_font)
        self.m_entry.insert(0, self.config.memory)
        self.m_entry.grid(row=0, column=7, padx=3, pady=padding, sticky='w')
        
        ttk.Label(self.frame, text="example: 64M,128M ... 8G,16G", font=small_font).grid(
            row=0, column=8, padx=(0, 5), pady=padding, sticky='w')
        
        # Information labels
        self.info_label = ttk.Label(self.frame, text="", font=small_font, foreground='#666666')
        self.info_label.grid(row=1, column=0, columnspan=9, padx=5, pady=(0, 5), sticky='w')
        
        self.validation_label = ttk.Label(
            self.frame, text="", font=small_font, foreground=UI_CONFIG['colors']['warning_text']
        )
        self.validation_label.grid(row=2, column=0, columnspan=9, padx=5, pady=(0, 5), sticky='w')
    
    def _setup_bindings(self):
        self.tl_entry.bind('<KeyRelease>', self._on_time_limit_change)
        self.tl_entry.bind('<FocusOut>', self._validate_time_limit)
        self.d_entry.bind('<FocusOut>', self._validate_time_limit)
    
    def _on_time_limit_change(self, event):
        if self._correcting_time_limit:
            return
            
        current_value = self.tl_entry.get().strip()
        if current_value.lower() == "auto":
            self.time_limit_manual = False
            self._update_auto_values()
        else:
            self.time_limit_manual = True
    
    def _validate_time_limit(self, event=None):
        if self._correcting_time_limit or self.enabled_count == 0:
            return
            
        try:
            time_limit = int(self.tl_entry.get().strip())
            per_test = self._get_per_test_value()
            min_required = per_test * self.enabled_count
            
            if time_limit < min_required:
                self._correct_time_limit(min_required)
            else:
                self.validation_label.config(text="")
                
        except ValueError:
            pass
    
    def _get_per_test_value(self):
        per_test_str = self.d_entry.get().strip()
        if per_test_str.lower() == "auto":
            return TEST_CONFIG['default_per_test_duration']
        return int(per_test_str)
    
    def _correct_time_limit(self, min_required):
        self._correcting_time_limit = True
        self.tl_entry.delete(0, tk.END)
        self.tl_entry.insert(0, str(min_required))
        self._correcting_time_limit = False
        
        self.validation_label.config(
            text=f"Time Limit auto-corrected to {min_required} sec (minimum required for {self.enabled_count} tests)"
        )
        self.frame.after(5000, lambda: self.validation_label.config(text=""))
    
    def update_enabled_count(self, enabled_count: int):
        self.enabled_count = enabled_count
        self._update_auto_values()
        self._validate_time_limit()
    
    def _update_auto_values(self):
        if not self.time_limit_manual and self.enabled_count > 0:
            total_time = TEST_CONFIG['auto_time_limit_per_test'] * self.enabled_count
            self.tl_entry.delete(0, tk.END)
            self.tl_entry.insert(0, str(total_time))
        
        self._update_display()
    
    def _update_display(self):
        if self.enabled_count > 0:
            time_limit = self.tl_entry.get().strip()
            duration = self.d_entry.get().strip()
            
            try:
                time_int = int(time_limit)
                per_test = self._get_per_test_value()
                min_req = per_test * self.enabled_count
                status_note = f" (⚠️ needs at least {min_req} sec)" if time_int < min_req else ""
            except ValueError:
                status_note = ""
            
            time_info = f"Time Limit: {time_limit} sec{status_note}"
            duration_info = f"Per Test: {duration} sec" if duration.lower() != "auto" else f"Per Test: Auto (default: {TEST_CONFIG['default_per_test_duration']} sec)"
            
            self.info_label.config(
                text=f"{time_info} | {duration_info} | Based on {self.enabled_count} selected tests"
            )
        else:
            self.info_label.config(text="Select tests to see calculated values")
    
    def get_config(self) -> TestConfig:
        self.config.time_limit = self.tl_entry.get().strip()
        self.config.duration_per_test = self.d_entry.get().strip()
        self.config.memory = self.m_entry.get().strip()
        return self.config
    
    def validate(self) -> Tuple[bool, str]:
        config = self.get_config()
        
        for field, value in [("Time limit", config.time_limit), ("Duration per test", config.duration_per_test)]:
            if value and value.lower() != "auto" and not value.isdigit():
                return False, f"{field} must be a number or 'Auto'!"
        
        if (config.time_limit and config.time_limit.isdigit() and self.enabled_count > 0):
            time_limit = int(config.time_limit)
            per_test = self._get_per_test_value()
            min_required = per_test * self.enabled_count
            
            if time_limit < min_required:
                return False, (f"Time limit ({time_limit} sec) is too low! "
                             f"Minimum required: {min_required} sec ({per_test} sec × {self.enabled_count} tests)")
        
        return True, "Configuration valid"
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)