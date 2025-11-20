"""Utility functions"""
import os
import subprocess
import sys

def check_ycruncher_present() -> bool:
    """Check if y-cruncher executable is available"""
    # Check current directory first
    if os.path.exists("y-cruncher.exe") or os.path.exists("y-cruncher"):
        return True
    
    # Check system PATH
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

def get_ycruncher_executable_name() -> str:
    """Get the appropriate y-cruncher executable name for the current platform"""
    return "y-cruncher.exe" if os.name == 'nt' else "y-cruncher"