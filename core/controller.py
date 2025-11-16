"""Process control and execution"""
import subprocess
import threading
import sys
import psutil
import os
from typing import List, Tuple, Optional
from .models import TestConfig
from config.settings import TEST_CONFIG
from utils.helpers import check_ycruncher_present

class ProcessController:
    """Handles y-cruncher process execution and control"""
    
    __slots__ = ('process', 'pid', 'is_running')
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.is_running = False
    
    def start_test(self, config: TestConfig, enabled_components: List[str], 
                   output_callback) -> Tuple[bool, str]: 
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
            
            self._start_monitoring_threads(output_callback)
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
    
    def _start_monitoring_threads(self, output_callback): 
        """Start threads to monitor process output and completion"""
        threads = [
            threading.Thread(target=self._monitor_output, args=(self.process.stdout, output_callback), daemon=True),
            threading.Thread(target=self._monitor_output, args=(self.process.stderr, output_callback), daemon=True),
            threading.Thread(target=self._wait_for_completion, args=(output_callback,), daemon=True)
        ]
        
        for thread in threads:
            thread.start()
    
    def _build_command(self, config: TestConfig, enabled_components: List[str]) -> List[str]:
        """Build the y-cruncher command with parameters"""
        cmd = ["y-cruncher.exe", "colors:1", "console:linux-vterm", "stress"]
        
        if config.memory.strip() and config.memory.lower() != "auto":
            cmd.append(f"-M:{config.memory}")
        
        duration = config.duration_per_test
        if duration and str(duration).lower() != "auto":
            cmd.append(f"-D:{duration}")
        else:
            cmd.append(f"-D:{TEST_CONFIG['default_per_test_duration']}")
        
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
    
    def _wait_for_completion(self, output_callback) -> None:
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
            
            for child in process.children(recursive=True):
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    continue
            
            process.terminate()
            
            gone, alive = psutil.wait_procs([process] + process.children(recursive=True), timeout=3)
            
            for proc in alive:
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    continue
            
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