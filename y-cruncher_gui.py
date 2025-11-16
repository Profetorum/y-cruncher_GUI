import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import sys
import psutil
import os
import time
from typing import List, Dict, Tuple, Optional

# =============================================================================
# CONFIGURATION - EASILY CUSTOMIZABLE PARAMETERS
# =============================================================================

# Test Behavior Configuration
TEST_CONFIG = {
    'auto_time_limit_per_test': 1800,  # Base time per test when Time Limit is Auto (seconds)
    'default_per_test_duration': 120,   # Default duration when Per Test is Auto (seconds)
    'default_values': {
        'time_limit': "Auto",
        'duration_per_test': "Auto", 
        'memory': "Auto"
    }
}

# Test Components Configuration
TEST_COMPONENTS = {
    "BKT": {"name": "Scalar Integer", "ram_intensity": 0.2},
    "BBP": {"name": "AVX2 Float", "ram_intensity": 0.1},
    "SFTv4": {"name": "AVX2 Float", "ram_intensity": 0.2},
    "SNT": {"name": "AVX2 Integer", "ram_intensity": 0.3},
    "SVT": {"name": "AVX2 Float", "ram_intensity": 0.3},
    "FFTv4": {"name": "AVX2 Float", "ram_intensity": 0.9},
    "N63": {"name": "AVX2 Integer", "ram_intensity": 0.4},
    "VT3": {"name": "AVX2 Float", "ram_intensity": 0.5}
}

# Test Presets
TEST_PRESETS = {
    "CPU": {
        "description": "CPU-focused tests", 
        "criteria": {"max_ram_intensity": 0.3}
    },
    "CPU+RAM": {
        "description": "IMC/SA/FCLK/signaling-focused tests", 
        "criteria": {"min_ram_intensity": 0.4, "max_ram_intensity": 0.7}
    },
    "RAM": {
        "description": "RAM-focused tests", 
        "criteria": {"min_ram_intensity": 0.8}
    }
}

# UI Appearance Configuration
UI_CONFIG = {
    'window': {
        'title': "y-cruncher StressTest GUI",
        'size': "800x900",
        'min_size': (800, 600)
    },
    'fonts': {
        'header': ('Arial', 16, 'bold'),
        'label': ('Arial', 9, 'bold'),
        'entry': ('Arial', 10),
        'small': ('Arial', 8),
        'console': ('Consolas', 9),
        'button': ('Arial', 9)
    },
    'colors': {
        'console_bg': '#1e1e1e',
        'console_fg': '#d4d4d4',
        'command_text': '#569cd6',
        'info_text': '#6a9955',
        'error_text': '#f44747',
        'warning_text': '#cc0000'
    },
    'layout': {
        'frame_padding': 5,
        'widget_padding': 2,
        'section_padding': (10, 5)
    }
}

# Treeview Configuration
TREEVIEW_CONFIG = {
    'height': len(TEST_COMPONENTS),
    'selectmode': 'none',
    'columns': ('Select', 'Tag', 'Component', 'CPU-RAM'),
    'column_config': {
        'Select': {'width': 50, 'anchor': 'center', 'text': '✓'},
        'Tag': {'width': 60, 'anchor': 'center', 'text': 'Test'},
        'Component': {'width': 120, 'anchor': 'center', 'text': 'Component'},
        'CPU-RAM': {'width': 180, 'anchor': 'center', 'text': 'CPU-RAM Load'}
    }
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def check_ycruncher_present() -> bool:
    """Check if y-cruncher.exe is available"""
    if os.path.exists("y-cruncher.exe"):
        return True
    
    try:
        if sys.platform == "win32":
            result = subprocess.run(["where", "y-cruncher.exe"], 
                                  capture_output=True, text=True, timeout=5)
        else:
            result = subprocess.run(["which", "y-cruncher"], 
                                  capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False

# =============================================================================
# CORE BUSINESS LOGIC
# =============================================================================

class TestComponent:
    """Represents a single stress test component with its properties"""
    
    __slots__ = ('tag', 'name', 'ram_intensity', 'enabled')
    
    def __init__(self, tag: str, name: str, ram_intensity: float):
        self.tag = tag
        self.name = name
        self.ram_intensity = ram_intensity
        self.enabled = False
    
    def get_cpu_mem_visual(self) -> str:
        """Generate visual indicator of CPU-MEM balance"""
        line_length = 10
        dot_position = min(int(self.ram_intensity * line_length), line_length - 1)
        line = ['─'] * line_length
        line[dot_position] = '●'
        return f"CPU [{''.join(line)}] MEM"

class TestManager:
    """Manages test components and selection state"""
    
    def __init__(self):
        self.components = self._load_components()
    
    def _load_components(self) -> Dict[str, TestComponent]:
        """Initialize test components from configuration"""
        return {
            tag: TestComponent(tag, data["name"], data["ram_intensity"])
            for tag, data in TEST_COMPONENTS.items()
        }
    
    def get_enabled_components(self) -> List[str]:
        """Get list of enabled component tags"""
        return [tag for tag, comp in self.components.items() if comp.enabled]
    
    def enable_all(self) -> None:
        """Enable all components"""
        for comp in self.components.values():
            comp.enabled = True
    
    def disable_all(self) -> None:
        """Disable all components"""
        for comp in self.components.values():
            comp.enabled = False
    
    def apply_preset(self, preset_name: str) -> None:
        """Apply a test preset based on RAM intensity criteria"""
        self.disable_all()
        preset = TEST_PRESETS[preset_name]
        criteria = preset["criteria"]
        
        min_intensity = criteria.get('min_ram_intensity', 0.0)
        max_intensity = criteria.get('max_ram_intensity', 1.0)
        
        for component in self.components.values():
            if min_intensity <= component.ram_intensity <= max_intensity:
                component.enabled = True

class ProcessController:
    """Handles y-cruncher process execution and control"""
    
    __slots__ = ('process', 'pid', 'is_running')
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.is_running = False
    
    def start_test(self, config, enabled_components: List[str], 
                   output_callback, status_callback) -> Tuple[bool, str]:
        """Start the stress test process"""
        if self.is_running:
            return False, "Test is already running!"
        
        if not enabled_components:
            return False, "Please select at least one component!"
        
        if not check_ycruncher_present():
            return False, "y-cruncher.exe not found! Please download from https://www.numberworld.org/y-cruncher/"
        
        cmd = self._build_command(config, enabled_components)
        
        try:
            startupinfo = self._get_startup_info()
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                startupinfo=startupinfo
            )
            self.pid = self.process.pid
            self.is_running = True
            
            self._start_monitoring_threads(output_callback, status_callback)
            return True, "Test started successfully"
            
        except FileNotFoundError:
            return False, "y-cruncher.exe not found!"
        except Exception as e:
            return False, f"Failed to start: {str(e)}"
    
    def _get_startup_info(self):
        """Get platform-specific startup info to hide console window"""
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
            return startupinfo
        return None
    
    def _start_monitoring_threads(self, output_callback, status_callback):
        """Start threads to monitor process output and completion"""
        threads = [
            threading.Thread(target=self._monitor_output, 
                           args=(self.process.stdout, output_callback), daemon=True),
            threading.Thread(target=self._monitor_output,
                           args=(self.process.stderr, output_callback), daemon=True),
            threading.Thread(target=self._wait_for_completion,
                           args=(output_callback, status_callback), daemon=True)
        ]
        
        for thread in threads:
            thread.start()
    
    def _build_command(self, config, enabled_components: List[str]) -> List[str]:
        """Build the y-cruncher command with parameters"""
        cmd = ["y-cruncher.exe", "stress"]
        
        # Add memory parameter if specified
        if config.memory.strip() and config.memory.lower() != "auto":
            cmd.append(f"-M:{config.memory}")
        
        # Add duration parameter (use default if Auto)
        duration = config.duration_per_test
        if duration and str(duration).lower() != "auto":
            cmd.append(f"-D:{duration}")
        else:
            cmd.append(f"-D:{TEST_CONFIG['default_per_test_duration']}")
        
        # Add time limit parameter (calculate if Auto)
        time_limit = config.time_limit
        if time_limit and str(time_limit).lower() != "auto":
            cmd.append(f"-TL:{time_limit}")
        else:
            auto_time = TEST_CONFIG['auto_time_limit_per_test'] * len(enabled_components)
            cmd.append(f"-TL:{auto_time}")
        
        cmd.extend(enabled_components)
        return cmd
    
    def _monitor_output(self, pipe, callback) -> None:
        """Monitor process output stream"""
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    callback(line.rstrip())
        except (ValueError, OSError):
            pass
        finally:
            try:
                pipe.close()
            except OSError:
                pass
    
    def _wait_for_completion(self, output_callback, status_callback) -> None:
        """Wait for process completion and cleanup"""
        try:
            return_code = self.process.wait()
            if return_code != 0:
                output_callback(f"\n> Process exited with code: {return_code}\n")
        except Exception:
            pass
        finally:
            self.is_running = False
            output_callback("\n> Test completed or stopped.\n")
            status_callback("Test completed")
            self._cleanup()
    
    def stop_test(self) -> Tuple[bool, str]:
        """Stop the running test process"""
        if not self.is_running or not self.process:
            return False, "No test is running!"
        
        try:
            if not psutil.pid_exists(self.pid):
                self._cleanup()
                return True, "Process already terminated"
            
            self._terminate_process_tree()
            self._cleanup()
            return True, "Test stopped by user"
            
        except psutil.NoSuchProcess:
            self._cleanup()
            return True, "Process already terminated"
        except Exception as e:
            return False, f"Error stopping test: {str(e)}"
    
    def _terminate_process_tree(self):
        """Terminate process and all its children"""
        try:
            process = psutil.Process(self.pid)
            
            # Terminate children first
            for child in process.children(recursive=True):
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    continue
            
            # Terminate main process
            process.terminate()
            
            # Wait for termination
            gone, alive = psutil.wait_procs([process] + process.children(recursive=True), timeout=3)
            
            # Force kill if still alive
            for proc in alive:
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    continue
            
            # Windows fallback
            if sys.platform == "win32" and alive:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.pid)], 
                             capture_output=True, timeout=5, check=False)
                
        except psutil.NoSuchProcess:
            pass
    
    def _cleanup(self) -> None:
        """Clean up process resources"""
        self.is_running = False
        self.process = None
        self.pid = None

class TestConfig:
    """Stores test configuration parameters"""
    
    __slots__ = ('time_limit', 'duration_per_test', 'memory')
    
    def __init__(self):
        defaults = TEST_CONFIG['default_values']
        self.time_limit = defaults['time_limit']
        self.duration_per_test = defaults['duration_per_test']
        self.memory = defaults['memory']

# =============================================================================
# UI COMPONENTS
# =============================================================================

class ComponentTreeView:
    """Treeview for test component selection with visual indicators"""
    
    def __init__(self, parent, test_manager):
        self.frame = ttk.LabelFrame(parent, text="Stress Test Components")
        self.test_manager = test_manager
        self.tree = self._create_treeview()
        self._setup_layout()
    
    def _create_treeview(self):
        """Create and configure the treeview"""
        tree = ttk.Treeview(
            self.frame, 
            columns=TREEVIEW_CONFIG['columns'], 
            show='headings', 
            height=TREEVIEW_CONFIG['height'],
            selectmode=TREEVIEW_CONFIG['selectmode']
        )
        
        # Configure columns
        for col, config in TREEVIEW_CONFIG['column_config'].items():
            tree.heading(col, text=config['text'])
            tree.column(col, width=config['width'], anchor=config['anchor'])
        
        # Populate with data
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
        self.tree.grid(row=0, column=0, sticky='nsew', 
                      padx=UI_CONFIG['layout']['frame_padding'], 
                      pady=UI_CONFIG['layout']['frame_padding'])
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def bind_events(self, callback):
        """Bind click events for checkbox toggling"""
        self.tree.bind('<Button-1>', callback)
    
    def toggle_selection(self, event):
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
    
    def __init__(self, parent, config):
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
        # Time Limit
        ttk.Label(self.frame, text="Time Limit:", 
                 font=UI_CONFIG['fonts']['label']).grid(
            row=0, column=0, padx=(5, 3), pady=UI_CONFIG['layout']['frame_padding'], sticky='e')
        
        self.tl_entry = ttk.Entry(self.frame, width=8, font=UI_CONFIG['fonts']['entry'])
        self.tl_entry.insert(0, self.config.time_limit)
        self.tl_entry.grid(row=0, column=1, padx=3, pady=UI_CONFIG['layout']['frame_padding'], sticky='w')
        
        ttk.Label(self.frame, text="sec", font=UI_CONFIG['fonts']['small']).grid(
            row=0, column=2, padx=(0, 15), pady=UI_CONFIG['layout']['frame_padding'], sticky='w')
        
        # Duration per Test
        ttk.Label(self.frame, text="Per Test:", 
                 font=UI_CONFIG['fonts']['label']).grid(
            row=0, column=3, padx=(0, 3), pady=UI_CONFIG['layout']['frame_padding'], sticky='e')
        
        self.d_entry = ttk.Entry(self.frame, width=8, font=UI_CONFIG['fonts']['entry'])
        self.d_entry.insert(0, self.config.duration_per_test)
        self.d_entry.grid(row=0, column=4, padx=3, pady=UI_CONFIG['layout']['frame_padding'], sticky='w')
        
        ttk.Label(self.frame, text="sec", font=UI_CONFIG['fonts']['small']).grid(
            row=0, column=5, padx=(0, 15), pady=UI_CONFIG['layout']['frame_padding'], sticky='w')
        
        # Memory Allocation
        ttk.Label(self.frame, text="Memory:", 
                 font=UI_CONFIG['fonts']['label']).grid(
            row=0, column=6, padx=(0, 3), pady=UI_CONFIG['layout']['frame_padding'], sticky='e')
        
        self.m_entry = ttk.Entry(self.frame, width=6, font=UI_CONFIG['fonts']['entry'])
        self.m_entry.insert(0, self.config.memory)
        self.m_entry.grid(row=0, column=7, padx=3, pady=UI_CONFIG['layout']['frame_padding'], sticky='w')
        
        ttk.Label(self.frame, text="example: 64M,128M ... 8G,16G", 
                 font=UI_CONFIG['fonts']['small']).grid(
            row=0, column=8, padx=(0, 5), pady=UI_CONFIG['layout']['frame_padding'], sticky='w')
        
        # Information labels
        self.info_label = ttk.Label(
            self.frame, text="", font=UI_CONFIG['fonts']['small'], foreground='#666666'
        )
        self.info_label.grid(row=1, column=0, columnspan=9, padx=5, pady=(0, 5), sticky='w')
        
        self.validation_label = ttk.Label(
            self.frame, text="", font=UI_CONFIG['fonts']['small'], 
            foreground=UI_CONFIG['colors']['warning_text']
        )
        self.validation_label.grid(row=2, column=0, columnspan=9, padx=5, pady=(0, 5), sticky='w')
    
    def _setup_bindings(self):
        """Setup event bindings"""
        self.tl_entry.bind('<KeyRelease>', self._on_time_limit_change)
        self.tl_entry.bind('<FocusOut>', self._validate_time_limit)
        self.d_entry.bind('<FocusOut>', self._validate_time_limit)
    
    def _on_time_limit_change(self, event):
        """Handle time limit manual input"""
        if self._correcting_time_limit:
            return
            
        current_value = self.tl_entry.get().strip()
        if current_value.lower() == "auto":
            self.time_limit_manual = False
            self._update_auto_values()
        else:
            self.time_limit_manual = True
    
    def _validate_time_limit(self, event=None):
        """Validate and auto-correct time limit if needed"""
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
        """Get the effective per test value (handles Auto)"""
        per_test_str = self.d_entry.get().strip()
        if per_test_str.lower() == "auto":
            return TEST_CONFIG['default_per_test_duration']
        return int(per_test_str)
    
    def _correct_time_limit(self, min_required):
        """Auto-correct time limit to minimum required"""
        self._correcting_time_limit = True
        self.tl_entry.delete(0, tk.END)
        self.tl_entry.insert(0, str(min_required))
        self._correcting_time_limit = False
        
        self.validation_label.config(
            text=f"Time Limit auto-corrected to {min_required} sec (minimum required for {self.enabled_count} tests)"
        )
        self.frame.after(5000, lambda: self.validation_label.config(text=""))
    
    def update_enabled_count(self, enabled_count):
        """Update enabled test count and recalculate values"""
        self.enabled_count = enabled_count
        self._update_auto_values()
        self._validate_time_limit()
    
    def _update_auto_values(self):
        """Update auto-calculated values"""
        if not self.time_limit_manual and self.enabled_count > 0:
            total_time = TEST_CONFIG['auto_time_limit_per_test'] * self.enabled_count
            self.tl_entry.delete(0, tk.END)
            self.tl_entry.insert(0, str(total_time))
        
        self._update_display()
    
    def _update_display(self):
        """Update information display"""
        if self.enabled_count > 0:
            time_limit = self.tl_entry.get().strip()
            duration = self.d_entry.get().strip()
            
            # Check for validation issues
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
    
    def get_config(self):
        """Get current configuration"""
        self.config.time_limit = self.tl_entry.get().strip()
        self.config.duration_per_test = self.d_entry.get().strip()
        self.config.memory = self.m_entry.get().strip()
        return self.config
    
    def validate(self) -> Tuple[bool, str]:
        """Validate configuration"""
        config = self.get_config()
        
        # Validate numeric fields
        for field, value in [("Time limit", config.time_limit), 
                           ("Duration per test", config.duration_per_test)]:
            if value and value.lower() != "auto" and not value.isdigit():
                return False, f"{field} must be a number or 'Auto'!"
        
        # Validate time limit sufficiency
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
    
    def __init__(self, parent, callbacks):
        self.frame = ttk.Frame(parent)
        self.callbacks = callbacks
        self._create_widgets()
    
    def _create_widgets(self):
        """Create control buttons"""
        # Selection controls
        ttk.Button(self.frame, text="Select All", 
                  command=self.callbacks['select_all']).grid(
            row=0, column=0, padx=UI_CONFIG['layout']['widget_padding'], 
            pady=UI_CONFIG['layout']['widget_padding'])
        
        ttk.Button(self.frame, text="Deselect All", 
                  command=self.callbacks['deselect_all']).grid(
            row=0, column=1, padx=UI_CONFIG['layout']['widget_padding'], 
            pady=UI_CONFIG['layout']['widget_padding'])
        
        # Presets
        ttk.Label(self.frame, text="Presets:", 
                 font=UI_CONFIG['fonts']['label']).grid(
            row=0, column=2, padx=(15, 5), pady=UI_CONFIG['layout']['widget_padding'])
        
        for i, preset in enumerate(TEST_PRESETS.keys(), 3):
            ttk.Button(self.frame, text=preset, 
                      command=lambda p=preset: self.callbacks['apply_preset'](p)).grid(
                row=0, column=i, padx=UI_CONFIG['layout']['widget_padding'], 
                pady=UI_CONFIG['layout']['widget_padding'])
        
        # Test controls
        self.start_btn = ttk.Button(self.frame, text="Start Stress Test", 
                                   command=self.callbacks['start_test'])
        self.start_btn.grid(row=0, column=7, padx=(20, 5), 
                           pady=UI_CONFIG['layout']['widget_padding'])
        
        self.stop_btn = ttk.Button(self.frame, text="Stop Test", 
                                  command=self.callbacks['stop_test'], state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=8, padx=5, 
                          pady=UI_CONFIG['layout']['widget_padding'])
    
    def set_test_state(self, running):
        """Update button states based on test state"""
        self.start_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL if running else tk.DISABLED)
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

class ConsoleOutput:
    """Console output display with colored text support"""
    
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Console Output")
        self.console = self._create_console()
        self._setup_tags()
        self._setup_layout()
    
    def _create_console(self):
        """Create the console widget"""
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
        """Configure text color tags"""
        self.console.tag_configure('command', foreground=UI_CONFIG['colors']['command_text'])
        self.console.tag_configure('info', foreground=UI_CONFIG['colors']['info_text'])
        self.console.tag_configure('error', foreground=UI_CONFIG['colors']['error_text'])
    
    def _setup_layout(self):
        """Setup console layout"""
        self.console.grid(row=0, column=0, sticky='nsew', 
                         padx=UI_CONFIG['layout']['frame_padding'], 
                         pady=UI_CONFIG['layout']['frame_padding'])
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
    
    def write(self, text, tag=None):
        """Write text to console with optional coloring"""
        self.console.insert(tk.END, text + '\n', tag)
        self.console.see(tk.END)
        self.console.update_idletasks()
    
    def clear(self):
        """Clear console content"""
        self.console.delete(1.0, tk.END)
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

class StatusBar:
    """Status bar for displaying application status"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.status_var = tk.StringVar(value="Ready - Select tests and click Start")
        
        self.label = ttk.Label(
            self.frame, 
            textvariable=self.status_var,
            font=UI_CONFIG['fonts']['label'],
            relief=tk.SUNKEN, 
            anchor=tk.W, 
            padding=(10, 6)
        )
        self.label.grid(row=0, column=0, sticky='ew')
        self.frame.grid_columnconfigure(0, weight=1)
    
    def set_text(self, text):
        self.status_var.set(text)
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

class YCruncherGUI:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self._initialize_components()
        self._create_ui()
        self._setup_bindings()
    
    def _setup_window(self):
        """Configure main window"""
        self.root.title(UI_CONFIG['window']['title'])
        self.root.geometry(UI_CONFIG['window']['size'])
        self.root.minsize(*UI_CONFIG['window']['min_size'])
    
    def _initialize_components(self):
        """Initialize core components"""
        self.test_manager = TestManager()
        self.process_controller = ProcessController()
        self.test_config = TestConfig()
    
    def _create_ui(self):
        """Create the user interface"""
        # Header
        ttk.Label(self.root, text=UI_CONFIG['window']['title'], 
                 font=UI_CONFIG['fonts']['header']).grid(
            row=0, column=0, padx=UI_CONFIG['layout']['section_padding'][0], 
            pady=(10, 5), sticky='w')
        
        # Configuration
        self.config_panel = ConfigurationPanel(self.root, self.test_config)
        self.config_panel.grid(row=1, column=0, 
                              padx=UI_CONFIG['layout']['section_padding'][0], 
                              pady=UI_CONFIG['layout']['section_padding'][1], sticky='ew')
        
        # Component selection
        self.tree_view = ComponentTreeView(self.root, self.test_manager)
        self.tree_view.grid(row=2, column=0, 
                           padx=UI_CONFIG['layout']['section_padding'][0], 
                           pady=UI_CONFIG['layout']['section_padding'][1], sticky='nsew')
        
        # Controls
        callbacks = {
            'select_all': self._on_select_all,
            'deselect_all': self._on_deselect_all,
            'apply_preset': self._on_apply_preset,
            'start_test': self._on_start_test,
            'stop_test': self._on_stop_test
        }
        self.control_panel = ControlPanel(self.root, callbacks)
        self.control_panel.grid(row=3, column=0, 
                               padx=UI_CONFIG['layout']['section_padding'][0], 
                               pady=UI_CONFIG['layout']['section_padding'][1], sticky='ew')
        
        # Console
        self.console = ConsoleOutput(self.root)
        self.console.grid(row=4, column=0, 
                         padx=UI_CONFIG['layout']['section_padding'][0], 
                         pady=UI_CONFIG['layout']['section_padding'][1], sticky='nsew')
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=5, column=0, 
                            padx=UI_CONFIG['layout']['section_padding'][0], 
                            pady=(5, 10), sticky='ew')
        
        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)  # Treeview
        self.root.grid_rowconfigure(4, weight=3)  # Console
        self.root.grid_columnconfigure(0, weight=1)
    
    def _setup_bindings(self):
        """Setup event bindings"""
        self.tree_view.bind_events(self._on_tree_click)
        self.root.protocol("WM_DELETE_WINDOW", self.safe_shutdown)
    
    def safe_shutdown(self):
        """Safely shutdown the application"""
        if self.process_controller.is_running:
            self.console.write("Stopping running test before exit...", 'info')
            success, message = self.process_controller.stop_test()
            if not success:
                self.console.write(f"Warning: {message}", 'error')
        self.root.destroy()
    
    def _on_tree_click(self, event):
        """Handle treeview selection changes"""
        if self.tree_view.toggle_selection(event):
            enabled_count = len(self.test_manager.get_enabled_components())
            self.config_panel.update_enabled_count(enabled_count)
            status = f"Ready - {enabled_count} test(s) selected" if enabled_count > 0 else "Ready - Select tests and click Start"
            self.status_bar.set_text(status)
    
    def _on_select_all(self):
        """Select all tests"""
        self.test_manager.enable_all()
        self.tree_view.refresh()
        enabled_count = len(self.test_manager.get_enabled_components())
        self.config_panel.update_enabled_count(enabled_count)
        self.status_bar.set_text(f"Ready - {enabled_count} test(s) selected")
    
    def _on_deselect_all(self):
        """Deselect all tests"""
        self.test_manager.disable_all()
        self.tree_view.refresh()
        self.config_panel.update_enabled_count(0)
        self.status_bar.set_text("Ready - Select tests and click Start")
    
    def _on_apply_preset(self, preset_name):
        """Apply test preset"""
        self.test_manager.apply_preset(preset_name)
        self.tree_view.refresh()
        enabled_count = len(self.test_manager.get_enabled_components())
        self.config_panel.update_enabled_count(enabled_count)
        description = TEST_PRESETS[preset_name]["description"]
        self.status_bar.set_text(f"Applied {preset_name} preset: {description} ({enabled_count} tests selected)")
    
    def _on_start_test(self):
        """Start stress test"""
        # Validate configuration
        valid, message = self.config_panel.validate()
        if not valid:
            messagebox.showwarning("Configuration Error", message)
            return
        
        enabled_components = self.test_manager.get_enabled_components()
        if not enabled_components:
            messagebox.showwarning("Selection Error", "Please select at least one component!")
            return
        
        # Get configuration and build command
        config = self.config_panel.get_config()
        cmd = self._build_command_display(config, enabled_components)
        
        self.console.write(f"Starting: {cmd}", 'command')
        self.console.write(f"Using calculated values based on {len(enabled_components)} selected tests", 'info')
        
        # Start test
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
    
    def _build_command_display(self, config, enabled_components):
        """Build command string for display"""
        cmd = ["y-cruncher.exe", "stress"]
        
        if config.memory.strip() and config.memory.lower() != "auto":
            cmd.append(f"-M:{config.memory}")
        
        cmd.append(f"-D:{config.duration_per_test}")
        cmd.append(f"-TL:{config.time_limit}")
        cmd.extend(enabled_components)
        
        return ' '.join(cmd)
    
    def _on_stop_test(self):
        """Stop running test"""
        success, message = self.process_controller.stop_test()
        
        if success:
            self.control_panel.set_test_state(False)
            self.console.write(message, 'info')
            self.status_bar.set_text(f"{message} - Ready for new test")
        else:
            self.console.write(f"Error: {message}", 'error')
            self.status_bar.set_text(f"Error: {message}")
            messagebox.showerror("Error", message)
    
    def _on_console_output(self, text):
        """Handle console output from process"""
        self.console.write(text)
    
    def _on_status_update(self, status):
        """Handle status updates"""
        self.control_panel.set_test_state(False)
        self.status_bar.set_text(status)

def main():
    """Application entry point"""
    # Check for y-cruncher before creating UI
    if not check_ycruncher_present():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "y-cruncher Not Found", 
            "y-cruncher.exe was not found in the current directory or system PATH.\n\n"
            "Please download y-cruncher from:\n"
            "https://www.numberworld.org/y-cruncher/\n\n"
            "Extract and place y-cruncher.exe in this directory or add to PATH."
        )
        root.destroy()
        return
    
    # Create themed window if available
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
    except ImportError:
        root = tk.Tk()
    
    # Create and run application
    app = YCruncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()