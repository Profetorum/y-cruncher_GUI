"""ANSI-enabled text widget"""
import re
import tkinter as tk
from tkinter import scrolledtext

from config.settings import UI_CONFIG, ANSI_COLORS

class AnsiTextWidget:
    """Scrolled text widget with ANSI color code support"""
    
    def __init__(self, parent):
        self.widget = self._create_widget(parent)
        self._setup_tags()
    
    def _create_widget(self, parent):
        return scrolledtext.ScrolledText(
            parent, 
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
            self.widget.tag_configure(f'ansi_{color}', foreground=self._get_color_value(color))
        
        self.widget.tag_configure('command', foreground=UI_CONFIG['colors']['command_text'])
        self.widget.tag_configure('info', foreground=UI_CONFIG['colors']['info_text'])
        self.widget.tag_configure('error', foreground=UI_CONFIG['colors']['error_text'])
    
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
    
    def write_ansi(self, text: str):
        """Write text with ANSI color code parsing"""
        ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')
        parts = ansi_pattern.split(text)
        
        current_tag = None
        self.widget.config(state='normal')
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Text part
                if part:
                    self.widget.insert(tk.END, part, current_tag)
            else:  # ANSI code part
                codes = part.split(';')
                for code in codes:
                    if code in ANSI_COLORS:
                        current_tag = f'ansi_{ANSI_COLORS[code]}'
                    elif code == '0':  # Reset
                        current_tag = None
        
        self.widget.insert(tk.END, '\n')
        self.widget.see(tk.END)
        self.widget.config(state='disabled')
        self.widget.update_idletasks()
    
    def write(self, text: str, tag: str = None):
        self.widget.config(state='normal')
        self.widget.insert(tk.END, text + '\n', tag)
        self.widget.see(tk.END)
        self.widget.config(state='disabled')
        self.widget.update_idletasks()
    
    def clear(self):
        self.widget.config(state='normal')
        self.widget.delete(1.0, tk.END)
        self.widget.config(state='disabled')
    
    def grid(self, **kwargs):
        self.widget.grid(**kwargs)