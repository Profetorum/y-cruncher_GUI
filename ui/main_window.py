"""Main application window"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Callable

from config.settings import UI_CONFIG
from config.presets import TEST_PRESETS
from core.manager import TestManager
from core.controller import ProcessController
from core.models import TestConfig
from .components import (
    ComponentTreeView, ConfigurationPanel, ControlPanel, 
    ConsoleOutput, StatusBar
)

class YCruncherGUI:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self._initialize_components()
        self._create_ui()
        self._setup_bindings()
    
    def _setup_window(self):
        self.root.title(UI_CONFIG['window']['title'])
        self.root.geometry(UI_CONFIG['window']['size'])
        self.root.minsize(*UI_CONFIG['window']['min_size'])
    
    def _initialize_components(self):
        self.test_manager = TestManager()
        self.process_controller = ProcessController()
        self.test_config = TestConfig()
    
    def _create_ui(self):
        """Create the user interface"""
        section_padding = UI_CONFIG['layout']['section_padding']
        
        # Header
        ttk.Label(self.root, text=UI_CONFIG['window']['title'], font=UI_CONFIG['fonts']['header']).grid(
            row=0, column=0, padx=section_padding[0], pady=(10, 5), sticky='w')
        
        # Configuration
        self.config_panel = ConfigurationPanel(self.root, self.test_config)
        self.config_panel.grid(row=1, column=0, padx=section_padding[0], pady=section_padding[1], sticky='ew')
        
        # Component selection
        self.tree_view = ComponentTreeView(self.root, self.test_manager)
        self.tree_view.grid(row=2, column=0, padx=section_padding[0], pady=section_padding[1], sticky='nsew')
        
        # Controls
        callbacks = {
            'select_all': self._on_select_all,
            'deselect_all': self._on_deselect_all,
            'apply_preset': self._on_apply_preset,
            'start_test': self._on_start_test,
            'stop_test': self._on_stop_test
        }
        self.control_panel = ControlPanel(self.root, callbacks)
        self.control_panel.grid(row=3, column=0, padx=section_padding[0], pady=section_padding[1], sticky='ew')
        
        # Console
        self.console = ConsoleOutput(self.root)
        self.console.grid(row=4, column=0, padx=section_padding[0], pady=section_padding[1], sticky='nsew')
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=5, column=0, padx=section_padding[0], pady=(5, 10), sticky='ew')
        
        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(4, weight=3)
        self.root.grid_columnconfigure(0, weight=1)
    
    def _setup_bindings(self):
        self.tree_view.bind_events(self._on_tree_click)
        self.root.protocol("WM_DELETE_WINDOW", self.safe_shutdown)
    
    def safe_shutdown(self):
        if self.process_controller.is_running:
            self.console.write("Stopping running test before exit...", 'info')
            success, message = self.process_controller.stop_test()
            if not success:
                self.console.write(f"Warning: {message}", 'error')
        self.root.destroy()
    
    def _on_tree_click(self, event):
        if self.tree_view.toggle_selection(event):
            enabled_count = len(self.test_manager.get_enabled_components())
            self.config_panel.update_enabled_count(enabled_count)
            status = f"Ready - {enabled_count} test(s) selected" if enabled_count > 0 else "Ready - Select tests and click Start"
            self.status_bar.set_text(status)
    
    def _on_select_all(self):
        self.test_manager.enable_all()
        self.tree_view.refresh()
        enabled_count = len(self.test_manager.get_enabled_components())
        self.config_panel.update_enabled_count(enabled_count)
        self.status_bar.set_text(f"Ready - {enabled_count} test(s) selected")
    
    def _on_deselect_all(self):
        self.test_manager.disable_all()
        self.tree_view.refresh()
        self.config_panel.update_enabled_count(0)
        self.status_bar.set_text("Ready - Select tests and click Start")
    
    def _on_apply_preset(self, preset_name):
        self.test_manager.apply_preset(preset_name)
        self.tree_view.refresh()
        enabled_count = len(self.test_manager.get_enabled_components())
        self.config_panel.update_enabled_count(enabled_count)
        description = TEST_PRESETS[preset_name]["description"]
        self.status_bar.set_text(f"Applied {preset_name} preset: {description} ({enabled_count} tests selected)")
    
    def _on_start_test(self):
        valid, message = self.config_panel.validate()
        if not valid:
            messagebox.showwarning("Configuration Error", message)
            return
        
        enabled_components = self.test_manager.get_enabled_components()
        if not enabled_components:
            messagebox.showwarning("Selection Error", "Please select at least one component!")
            return
        
        config = self.config_panel.get_config()
        cmd = self._build_command_display(config, enabled_components)
        
        self.console.write(f"Starting: {cmd}", 'command')
        self.console.write(f"Using calculated values based on {len(enabled_components)} selected tests", 'info')
        
        success, message = self.process_controller.start_test(
            config, enabled_components, self._on_console_output, self._on_status_update
        )
        
        if success:
            self.control_panel.set_test_state(True)
            self.status_bar.set_text(f"Running stress test with {len(enabled_components)} components...")
        else:
            self.console.write(f"Error: {message}", 'error')
            self.status_bar.set_text(f"Error: {message}")
            messagebox.showerror("Error", message)
    
    def _build_command_display(self, config: TestConfig, enabled_components: list) -> str:
        cmd = ["y-cruncher.exe", "colors:1", "console:linux-vterm", "stress"]
        
        if config.memory.strip() and config.memory.lower() != "auto":
            cmd.append(f"-M:{config.memory}")
        
        cmd.append(f"-D:{config.duration_per_test}")
        cmd.append(f"-TL:{config.time_limit}")
        cmd.extend(enabled_components)
        
        return ' '.join(cmd)
    
    def _on_stop_test(self):
        success, message = self.process_controller.stop_test()
        
        if success:
            self.control_panel.set_test_state(False)
            self.console.write(message, 'info')
            self.status_bar.set_text(f"{message} - Ready for new test")
        else:
            self.console.write(f"Error: {message}", 'error')
            self.status_bar.set_text(f"Error: {message}")
            messagebox.showerror("Error", message)
    
    def _on_console_output(self, text: str):
        self.console.write_ansi(text)
    
    def _on_status_update(self, status: str):
        self.control_panel.set_test_state(False)
        self.status_bar.set_text(status)