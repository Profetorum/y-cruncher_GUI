"""Main entry point for the y-cruncher GUI application"""
import tkinter as tk
from tkinter import messagebox
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def ask_download_consent(download_info: dict) -> bool:
    """Ask user for consent to download y-cruncher"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    result = messagebox.askyesno(
        "y-cruncher Not Found",
        f"y-cruncher was not found in the current directory or system PATH.\n\n"
        f"Would you like to automatically download and extract the latest version?\n\n"
        f"File: {download_info['filename']}\n"
        f"Version: {download_info['version']}\n"
        f"Source: {download_info['source']}\n\n"
        "If you choose 'No', you will need to manually download and place y-cruncher in this directory."
    )
    
    root.destroy()
    return result

def auto_setup_ycruncher() -> bool:
    """Automatically set up y-cruncher by extracting from zip if needed"""
    # Import locally to avoid circular imports
    from utils.helpers import check_ycruncher_present
    from utils.extractor import YCruncherExtractor
    
    # Check if already present
    if check_ycruncher_present():
        print("y-cruncher already present")
        return True
        
    extractor = YCruncherExtractor()
    
    # Look for zip file
    zip_path = extractor.find_zip_file()
    if zip_path:
        print(f"Found y-cruncher zip: {zip_path}")
    else:
        # No zip file found, ask user if they want to download
        print("No y-cruncher zip file found locally")
        return False
    
    # Try to extract
    success = extractor.extract_zip(zip_path)
    
    if success:
        # Verify extraction worked
        if extractor.verify_extraction():
            print("y-cruncher setup successful!")
            return True
        else:
            print("Extraction completed but verification failed")
            extractor.cleanup_failed_extraction()
            return False
    
    return False

def download_and_setup_ycruncher() -> bool:
    """Download y-cruncher and set it up"""
    from utils.downloader import YCruncherDownloader
    from utils.extractor import YCruncherExtractor
    
    downloader = YCruncherDownloader()
    extractor = YCruncherExtractor()
    
    # Download the file
    success = downloader.download_ycruncher()
    if not success:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Download Failed",
            "Failed to download y-cruncher.\n\n"
            "Please check your internet connection and try again, "
            "or manually download from:\n"
            "https://www.numberworld.org/y-cruncher/"
        )
        root.destroy()
        return False
    
    # Extract the downloaded file
    zip_path = downloader.DOWNLOAD_FILENAME
    success = extractor.extract_zip(zip_path)
    
    if success:
        # Verify extraction worked
        if extractor.verify_extraction():
            print("y-cruncher download and setup successful!")
            
            # Optionally clean up the downloaded zip file to save space
            downloader.cleanup_download()
            
            return True
        else:
            print("Download completed but extraction verification failed")
            extractor.cleanup_failed_extraction()
            return False
    
    return False

def main():
    """Application entry point"""
    # Import locally to avoid circular imports
    from utils.helpers import check_ycruncher_present
    from utils.downloader import YCruncherDownloader
    
    # Try auto-setup first
    if not check_ycruncher_present():
        print("y-cruncher not found, attempting auto-setup...")
        
        # First try local extraction
        local_success = auto_setup_ycruncher()
        
        if not local_success:
            # No local zip found, ask about downloading
            downloader = YCruncherDownloader()
            download_info = downloader.get_download_info()
            
            if ask_download_consent(download_info):
                # User consented to download
                download_success = download_and_setup_ycruncher()
                
                if download_success:
                    # Successfully downloaded and extracted
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showinfo(
                        "y-cruncher Auto-Setup",
                        "y-cruncher was successfully downloaded and extracted!\n"
                        "The application will now start."
                    )
                    root.destroy()
                else:
                    # Download failed
                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showerror(
                        "Setup Failed",
                        "Failed to download and setup y-cruncher.\n\n"
                        "Please manually download y-cruncher from:\n"
                        "https://www.numberworld.org/y-cruncher/\n\n"
                        "Extract the contents to this directory and run the application again."
                    )
                    root.destroy()
                    return
            else:
                # User declined download
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo(
                    "Manual Setup Required",
                    "Please download y-cruncher from:\n"
                    "https://www.numberworld.org/y-cruncher/\n\n"
                    "Extract the contents to this directory and run the application again."
                )
                root.destroy()
                return
    
    try:
        from ttkthemes import ThemedTk
        root = ThemedTk(theme="arc")
    except ImportError:
        root = tk.Tk()
    
    # Import locally to avoid circular imports
    from ui.main_window import YCruncherGUI
    app = YCruncherGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()