"""Settings management for saving and loading user preferences"""
import configparser
import os
from typing import Dict, List, Any
from core.models import TestConfig
from core.manager import TestManager

class SettingsManager:
    """Manages application settings using INI files"""
    
    def __init__(self, filename: str = "y-cruncher_gui.ini"):
        self.filename = filename
        self.config = configparser.ConfigParser()
    
    def load_settings(self, test_config: TestConfig, test_manager: TestManager) -> bool:
        """Load settings from INI file, return True if successful"""
        if not os.path.exists(self.filename):
            return False
        
        try:
            self.config.read(self.filename, encoding='utf-8')
            
            # Load test configuration
            if 'Configuration' in self.config:
                cfg_section = self.config['Configuration']
                test_config.time_limit = cfg_section.get('time_limit', test_config.time_limit)
                test_config.duration_per_test = cfg_section.get('duration_per_test', test_config.duration_per_test)
                test_config.memory = cfg_section.get('memory', test_config.memory)
            
            # Load component states
            if 'Components' in self.config:
                comp_section = self.config['Components']
                for tag in test_manager.components.keys():
                    enabled = comp_section.getboolean(tag, False)
                    test_manager.components[tag].enabled = enabled
            
            return True
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
    
    def save_settings(self, test_config: TestConfig, test_manager: TestManager) -> bool:
        """Save settings to INI file, return True if successful"""
        try:
            # Configuration section
            self.config['Configuration'] = {
                'time_limit': test_config.time_limit,
                'duration_per_test': test_config.duration_per_test,
                'memory': test_config.memory
            }
            
            # Components section
            comp_section = {}
            for tag, component in test_manager.components.items():
                comp_section[tag] = str(component.enabled)
            self.config['Components'] = comp_section
            
            # Write to file
            with open(self.filename, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
            
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def create_default_settings(self, test_config: TestConfig, test_manager: TestManager):
        """Create default settings file"""
        self.save_settings(test_config, test_manager)