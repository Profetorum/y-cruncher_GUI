"""Y-cruncher download utilities"""
import os
import urllib.request
import urllib.error
from typing import Optional

class YCruncherDownloader:
    """Handles downloading of y-cruncher"""
    
    # Download URL for y-cruncher - exposed as a class variable for easy modification
    DOWNLOAD_URL = "https://cdn.numberworld.org/y-cruncher-downloads/y-cruncher%20v0.8.6.9545b.zip"
    DOWNLOAD_FILENAME = "y-cruncher-v0.8.6.9545b.zip"
    
    def __init__(self):
        self.downloaded_size = 0
        self.total_size = 0
    
    def download_ycruncher(self, progress_callback: Optional[callable] = None) -> bool:
        """Download y-cruncher from the official website"""
        try:
            print(f"Downloading y-cruncher from: {self.DOWNLOAD_URL}")
            print("This may take a few moments...")
            
            # Download the file
            if progress_callback:
                urllib.request.urlretrieve(
                    self.DOWNLOAD_URL, 
                    self.DOWNLOAD_FILENAME,
                    reporthook=progress_callback
                )
            else:
                urllib.request.urlretrieve(self.DOWNLOAD_URL, self.DOWNLOAD_FILENAME)
            
            # Verify the download
            if os.path.exists(self.DOWNLOAD_FILENAME) and os.path.getsize(self.DOWNLOAD_FILENAME) > 0:
                print(f"Successfully downloaded: {self.DOWNLOAD_FILENAME}")
                return True
            else:
                print("Download failed - file is empty or doesn't exist")
                return False
                
        except urllib.error.URLError as e:
            print(f"Download error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error during download: {e}")
            return False
    
    def get_download_info(self) -> dict:
        """Get information about the download"""
        return {
            'url': self.DOWNLOAD_URL,
            'filename': self.DOWNLOAD_FILENAME,
            'version': 'v0.8.6.9545b',
            'source': 'https://www.numberworld.org/y-cruncher/'
        }
    
    def cleanup_download(self) -> bool:
        """Remove downloaded zip file"""
        try:
            if os.path.exists(self.DOWNLOAD_FILENAME):
                os.remove(self.DOWNLOAD_FILENAME)
                print(f"Removed downloaded file: {self.DOWNLOAD_FILENAME}")
                return True
            return True  # Already doesn't exist
        except Exception as e:
            print(f"Error cleaning up download: {e}")
            return False