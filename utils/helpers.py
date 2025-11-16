"""Utility functions"""
import os
import subprocess
import sys

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