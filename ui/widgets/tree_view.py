"""Tree view widget for component selection"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from config.settings import UI_CONFIG
from config.presets import TEST_COMPONENTS
from core.manager import TestManager

class ComponentTreeView:
    """Treeview for test component selection with visual indicators"""
    
    def __init__(self, parent, test_manager: TestManager):
        self.frame = ttk.Frame(parent)
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
        """Handle checkbox toggling - now works on entire row"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            # Toggle regardless of which column was clicked (entire row is clickable)
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