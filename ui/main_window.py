"""Main application window"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Callable

from config.settings import UI_CONFIG
from core.manager import TestManager
from core.controller import ProcessController
from core.models import TestConfig
from utils.settings_manager import SettingsManager

# Absolute imports for all frames
from ui.frames.header import HeaderFrame
from ui.frames.configuration import ConfigurationFrame
from ui.frames.components import ComponentsFrame
from ui.frames.controls import ControlsFrame
from ui.frames.console import ConsoleFrame

class YCruncherGUI:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self._initialize_components()
        self._load_settings()
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
        self.settings_manager = SettingsManager()
    
    def _load_settings(self):
        """Load settings from INI file or create default"""
        if not self.settings_manager.load_settings(self.test_config, self.test_manager):
            # Create default settings file if it doesn't exist
            self.settings_manager.create_default_settings(self.test_config, self.test_manager)
            print("Created default settings file")
        else:
            print("Loaded settings from file")
    
    def _save_settings(self):
        """Save current settings to INI file"""
        # Update test_config from UI before saving
        if hasattr(self, 'config_panel'):
            self.config_panel.get_config()
        self.settings_manager.save_settings(self.test_config, self.test_manager)
        print("Settings saved")
    
    def _create_ui(self):
        """Create the user interface using modular frames"""
        section_padding = UI_CONFIG['layout']['section_padding']
        
        # Create frames using absolute imports
        self.header = HeaderFrame(self.root)
        self.config_panel = ConfigurationFrame(self.root, self.test_config)
        self.components_frame = ComponentsFrame(self.root, self.test_manager)
        self.controls_frame = ControlsFrame(self.root, self._get_callbacks())
        self.console = ConsoleFrame(self.root)
        
        # Set save callback for configuration panel
        self.config_panel.set_save_callback(self._save_settings)
        
        # Layout frames
        self.header.grid(row=0, column=0, padx=section_padding[0], pady=(10, 5), sticky='w')
        self.config_panel.grid(row=1, column=0, padx=section_padding[0], pady=section_padding[1], sticky='ew')
        self.components_frame.grid(row=2, column=0, padx=section_padding[0], pady=section_padding[1], sticky='nsew')
        self.controls_frame.grid(row=3, column=0, padx=section_padding[0], pady=section_padding[1], sticky='ew')
        self.console.grid(row=4, column=0, padx=section_padding[0], pady=section_padding[1], sticky='nsew')
        
        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(4, weight=3)  # Console gets more space
        self.root.grid_columnconfigure(0, weight=1)
    
    def _get_callbacks(self) -> Dict[str, Callable]:
        """Return dictionary of callback functions"""
        return {
            'select_all': self._on_select_all,
            'deselect_all': self._on_deselect_all,
            'apply_preset': self._on_apply_preset,
            'start_test': self._on_start_test,
            'stop_test': self._on_stop_test
        }
    
    def _setup_bindings(self):
        self.components_frame.bind_events(self._on_tree_click)
        self.root.protocol("WM_DELETE_WINDOW", self.safe_shutdown)
    
    def safe_shutdown(self):
        """Safely shutdown the application"""
        # Save settings before exit
        self._save_settings()
        
        if self.process_controller.is_running:
            self.console.write("Stopping running test before exit...", 'info')
            success, message = self.process_controller.stop_test()
            if not success:
                self.console.write(f"Warning: {message}", 'error')
        self.root.destroy()
    
    def _on_tree_click(self, event):
        if self.components_frame.toggle_selection(event):
            enabled_count = self.components_frame.get_enabled_count()
            self.config_panel.update_enabled_count(enabled_count)
            # Save settings when selection changes
            self._save_settings()
    
    def _on_select_all(self):
        self.test_manager.enable_all()
        self.components_frame.refresh()
        enabled_count = self.components_frame.get_enabled_count()
        self.config_panel.update_enabled_count(enabled_count)
        self.console.write("All components selected", 'info')
        # Save settings
        self._save_settings()
    
    def _on_deselect_all(self):
        self.test_manager.disable_all()
        self.components_frame.refresh()
        self.config_panel.update_enabled_count(0)
        self.console.write("All components deselected", 'info')
        # Save settings
        self._save_settings()
    
    def _on_apply_preset(self, preset_name):
        from config.presets import TEST_PRESETS
        
        if preset_name not in TEST_PRESETS:
            self.console.write(f"Error: Preset '{preset_name}' not found", 'error')
            return
            
        self.test_manager.apply_preset(preset_name)
        self.components_frame.refresh()
        enabled_count = self.components_frame.get_enabled_count()
        self.config_panel.update_enabled_count(enabled_count)
        
        description = TEST_PRESETS[preset_name]["description"]
        self.console.write(f"Applied preset '{preset_name}': {description}", 'info')
        # Save settings
        self._save_settings()
    
    def _on_start_test(self):
        # Validate configuration
        valid, message = self.config_panel.validate()
        if not valid:
            messagebox.showwarning("Configuration Error", message)
            return
        
        # Check if components are selected
        enabled_components = self.test_manager.get_enabled_components()
        if not enabled_components:
            messagebox.showwarning("Selection Error", "Please select at least one component!")
            return
        
        # Get configuration and build command
        config = self.config_panel.get_config()
        cmd = self._build_command_display(config, enabled_components)
        
        # Show start information
        self.console.write("=" * 60, 'info')
        self.console.write("STARTING STRESS TEST", 'info')
        self.console.write("=" * 60, 'info')
        self.console.write(f"Command: {cmd}", 'command')
        self.console.write(f"Configuration: {len(enabled_components)} tests selected", 'info')
        self.console.write("", 'info')
        
        # Start the test
        success, message = self.process_controller.start_test(
            config, enabled_components, self._on_console_output, self._on_test_completion
        )
        
        if success:
            self.controls_frame.set_test_state(True)
            self.console.write("Test process started successfully", 'info')
        else:
            self.console.write(f"Error starting test: {message}", 'error')
            messagebox.showerror("Start Error", message)
    
    def _build_command_display(self, config: TestConfig, enabled_components: list) -> str:
        """Build command string for display purposes"""
        cmd = ["y-cruncher.exe", "colors:1", "console:linux-vterm", "stress"]
        
        if config.memory.strip() and config.memory.lower() != "auto":
            cmd.append(f"-M:{config.memory}")
        
        cmd.append(f"-D:{config.duration_per_test}")
        cmd.append(f"-TL:{config.time_limit}")
        cmd.extend(enabled_components)
        
        return ' '.join(cmd)
    
    def _on_stop_test(self):
        """Stop the currently running test"""
        if not self.process_controller.is_running:
            self.console.write("No test is currently running", 'info')
            return
            
        self.console.write("Stopping test...", 'info')
        success, message = self.process_controller.stop_test()
        
        if success:
            self.controls_frame.set_test_state(False)
            self.console.write("Test stopped successfully", 'info')
        else:
            self.console.write(f"Error stopping test: {message}", 'error')
            messagebox.showerror("Stop Error", message)
    
    def _on_console_output(self, text: str):
        """Handle console output from the test process"""
        self.console.write_ansi(text)
    
    def _on_test_completion(self, return_code, exit_code):
        """Called when the test process completes"""
        # Schedule GUI update on main thread
        self.root.after(0, self._handle_test_completion, return_code, exit_code)
    
    def _handle_test_completion(self, return_code, exit_code):
        """Handle test completion on the main GUI thread"""
        self.controls_frame.set_test_state(False)