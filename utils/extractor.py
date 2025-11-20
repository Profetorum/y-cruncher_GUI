"""Y-cruncher zip extraction utilities"""
import os
import zipfile
import glob
import shutil
import tempfile
from typing import Optional, List

class YCruncherExtractor:
    """Handles extraction of y-cruncher from zip files"""
    
    # Common y-cruncher file patterns to look for
    YCRUNCHER_PATTERNS = ["y-cruncher*.zip", "y_cruncher*.zip"]
    
    def __init__(self):
        self.extracted_files = []
    
    def find_zip_file(self) -> Optional[str]:
        """Look for y-cruncher zip files in current directory"""
        print(f"Looking for zip files in: {os.getcwd()}")
        for pattern in self.YCRUNCHER_PATTERNS:
            zip_files = glob.glob(pattern)
            print(f"Pattern '{pattern}' found: {zip_files}")
            if zip_files:
                return zip_files[0]
        return None
    
    def extract_zip(self, zip_path: str) -> bool:
        """Extract y-cruncher zip file with proper structure handling"""
        try:
            print(f"Starting extraction from: {zip_path}")
            
            # First, extract to a temporary directory to analyze structure
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"Extracting to temp dir: {temp_dir}")
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                    print(f"Extracted {len(zip_ref.namelist())} items to temp dir")
                
                # Analyze the structure
                source_dir = self._find_extraction_source(temp_dir)
                if not source_dir:
                    print("Could not find valid extraction source")
                    return False
                
                print(f"Source directory for copy: {source_dir}")
                
                # Copy all contents to current directory
                return self._copy_contents(source_dir, ".")
                    
        except Exception as e:
            print(f"Error extracting zip: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _find_extraction_source(self, temp_dir: str) -> Optional[str]:
        """Find the correct source directory within extracted contents"""
        items = os.listdir(temp_dir)
        print(f"Items in temp directory: {items}")
        
        # If there's only one item and it's a directory, use that
        if len(items) == 1:
            single_item = os.path.join(temp_dir, items[0])
            if os.path.isdir(single_item):
                print(f"Single directory found: {single_item}")
                # Check if this directory contains y-cruncher files
                if self._contains_ycruncher_files(single_item):
                    return single_item
                else:
                    # Maybe the single directory contains another directory with the files
                    sub_items = os.listdir(single_item)
                    if len(sub_items) == 1:
                        sub_item = os.path.join(single_item, sub_items[0])
                        if os.path.isdir(sub_item) and self._contains_ycruncher_files(sub_item):
                            return sub_item
        
        # Check if temp directory directly contains y-cruncher files
        if self._contains_ycruncher_files(temp_dir):
            return temp_dir
        
        # Look for any directory that contains y-cruncher files
        for item in items:
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path) and self._contains_ycruncher_files(item_path):
                return item_path
        
        return None
    
    def _contains_ycruncher_files(self, directory: str) -> bool:
        """Check if directory contains y-cruncher files"""
        try:
            items = os.listdir(directory)
            # Look for y-cruncher executable or common files
            ycruncher_files = [
                "y-cruncher.exe", "y-cruncher",
                "Components", "Config", "Numbers"
            ]
            
            for expected in ycruncher_files:
                if expected in items:
                    print(f"Found y-cruncher file/dir: {expected} in {directory}")
                    return True
        except Exception as e:
            print(f"Error checking directory {directory}: {e}")
        
        return False
    
    def _copy_contents(self, source_dir: str, target_dir: str) -> bool:
        """Copy all contents from source to target directory"""
        try:
            print(f"Copying contents from {source_dir} to {target_dir}")
            
            for item in os.listdir(source_dir):
                source_path = os.path.join(source_dir, item)
                target_path = os.path.join(target_dir, item)
                
                print(f"Copying: {item}")
                
                if os.path.isdir(source_path):
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
                else:
                    shutil.copy2(source_path, target_path)
                
                self.extracted_files.append(target_path)
            
            print("Copy completed successfully")
            return True
            
        except Exception as e:
            print(f"Error copying contents: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_extraction(self) -> bool:
        """Verify that extraction was successful"""
        print("Verifying extraction...")
        
        # Check for main executable
        exe_found = os.path.exists("y-cruncher.exe") or os.path.exists("y-cruncher")
        print(f"Executable found: {exe_found}")
        
        # Check for expected directories
        expected_dirs = ["Components", "Config", "Numbers"]
        for directory in expected_dirs:
            exists = os.path.exists(directory) and os.path.isdir(directory)
            print(f"Directory {directory} found: {exists}")
        
        # For now, just check if executable exists
        return exe_found
    
    def cleanup_failed_extraction(self) -> bool:
        """Clean up files from a failed or incomplete extraction"""
        try:
            print("Cleaning up failed extraction...")
            for file_path in self.extracted_files:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        print(f"Removed directory: {file_path}")
                    else:
                        os.remove(file_path)
                        print(f"Removed file: {file_path}")
            
            self.extracted_files.clear()
            return True
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return False