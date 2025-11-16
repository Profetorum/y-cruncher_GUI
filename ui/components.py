"""UI components and widgets"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import re
from typing import Tuple, Callable, Dict, List

from config.settings import UI_CONFIG, ANSI_COLORS
from config.presets import TEST_COMPONENTS
from core.manager import TestManager
from core.models import TestConfig

class ComponentTreeView:
    """Treeview for test component selection with visual indicators"""
    
    def __init__(self, parent, test_manager: TestManager):
        self.frame = ttk.LabelFrame(parent, text="Stress Test Components")
        self.test_manager = test_manager
        self.tree = self._create_treeview()
        self._setup_layout()
    
    def _create_treeview(self):
        """Create and configure the treeview"""
        columns = ('Select', 'Tag', 'Component', 'CPU-RAM')
        column_config = {
            'Select': {'width': 50, 'anchor': 'center', 'text': '✓'},
            'Tag': {'width': 60, 'anchor': 'center', 'text': 'Test'},
            'Component': {'width': 120, 'anchor': 'center', 'text': 'Component'},
            'CPU-RAM': {'width': 180, 'anchor': 'center', 'text': 'CPU-RAM Load'}
        }
        
        tree = ttk.Treeview(
            self.frame, 
            columns=columns, 
            show='headings', 
            height=len(TEST_COMPONENTS),
            selectmode='none'
        )
        
        for col, config in column_config.items():
            tree.heading(col, text=config['text'])
            tree.column(col, width=config['width'], anchor=config['anchor'])
        
        for tag, component in self.test_manager.components.items():
            tree.insert('', tk.END, values=(
                '☑' if component.enabled else '☐',
                tag,
                component.name,
                component.get_cpu_mem_visual()
            ), tags=(tag,))
        
        return tree
    
    def _setup_layout(self):
        """Setup treeview layout"""
        padding = UI_CONFIG['layout']['frame_padding']
        self.tree.grid(row=0, column=0, sticky='nsew', padx=padding, pady=padding)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def bind_events(self, callback: Callable):
        self.tree.bind('<Button-1>', callback)
    
    def toggle_selection(self, event) -> bool:
        """Handle checkbox toggling"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell" and self.tree.identify_column(event.x) == '#1':
            item = self.tree.identify_row(event.y)
            if item:
                self._toggle_item(item)
                return True
        return False
    
    def _toggle_item(self, item):
        """Toggle the selected item's enabled state"""
        values = self.tree.item(item, 'values')
        if len(values) >= 2:
            tag = values[1]
            current_value = values[0]
            
            if current_value == '☐':
                new_value = '☑'
                self.test_manager.components[tag].enabled = True
            else:
                new_value = '☐'
                self.test_manager.components[tag].enabled = False
            
            self.tree.set(item, 'Select', new_value)
    
    def refresh(self):
        """Refresh treeview data"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for tag, component in self.test_manager.components.items():
            self.tree.insert('', tk.END, values=(
                '☑' if component.enabled else '☐',
                tag,
                component.name,
                component.get_cpu_mem_visual()
            ), tags=(tag,))
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

class ConfigurationPanel:
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
        from config.settings import TEST_CONFIG
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
        from config.settings import TEST_CONFIG
        if not self.time_limit_manual and self.enabled_count > 0:
            total_time = TEST_CONFIG['auto_time_limit_per_test'] * self.enabled_count
            self.tl_entry.delete(0, tk.END)
            self.tl_entry.insert(0, str(total_time))
        
        self._update_display()
    
    def _update_display(self):
        from config.settings import TEST_CONFIG
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

class ControlPanel:
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
        
        from config.presets import TEST_PRESETS
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

class ConsoleOutput:
    """Console output display with ANSI color code support"""
    
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Console Output")
        self.console = self._create_console()
        self._setup_tags()
        self._setup_layout()
    
    def _create_console(self):
        return scrolledtext.ScrolledText(
            self.frame, 
            wrap=tk.WORD,
            font=UI_CONFIG['fonts']['console'], 
            bg=UI_CONFIG['colors']['console_bg'], 
            fg=UI_CONFIG['colors']['console_fg'],
            insertbackground='white',
            state='normal'
        )
    
    def _setup_tags(self):
        """Configure text color tags for ANSI colors"""
        for code, color in ANSI_COLORS.items():
            self.console.tag_configure(f'ansi_{color}', foreground=self._get_color_value(color))
        
        self.console.tag_configure('command', foreground=UI_CONFIG['colors']['command_text'])
        self.console.tag_configure('info', foreground=UI_CONFIG['colors']['info_text'])
        self.console.tag_configure('error', foreground=UI_CONFIG['colors']['error_text'])
    
    def _get_color_value(self, color_name: str) -> str:
        """Get hex color value for ANSI color names"""
        color_map = {
            'black': '#000000', 'red': '#CD3131', 'green': '#0DBC79', 'yellow': '#E5E510',
            'blue': '#2472C8', 'magenta': '#BC3FBC', 'cyan': '#11A8CD', 'white': '#E5E5E5',
            'bright_black': '#666666', 'bright_red': '#F14C4C', 'bright_green': '#23D18B',
            'bright_yellow': '#F5F543', 'bright_blue': '#3B8EEA', 'bright_magenta': '#D670D6',
            'bright_cyan': '#29B8DB', 'bright_white': '#FFFFFF'
        }
        return color_map.get(color_name, '#FFFFFF')
    
    def _setup_layout(self):
        padding = UI_CONFIG['layout']['frame_padding']
        self.console.grid(row=0, column=0, sticky='nsew', padx=padding, pady=padding)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def write_ansi(self, text: str):
        """Write text with ANSI color code parsing"""
        ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')
        parts = ansi_pattern.split(text)
        
        current_tag = None
        self.console.config(state='normal')
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Text part
                if part:
                    self.console.insert(tk.END, part, current_tag)
            else:  # ANSI code part
                codes = part.split(';')
                for code in codes:
                    if code in ANSI_COLORS:
                        current_tag = f'ansi_{ANSI_COLORS[code]}'
                    elif code == '0':  # Reset
                        current_tag = None
        
        self.console.insert(tk.END, '\n')
        self.console.see(tk.END)
        self.console.config(state='disabled')
        self.console.update_idletasks()
    
    def write(self, text: str, tag: str = None):
        self.console.config(state='normal')
        self.console.insert(tk.END, text + '\n', tag)
        self.console.see(tk.END)
        self.console.config(state='disabled')
        self.console.update_idletasks()
    
    def clear(self):
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.config(state='disabled')
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
