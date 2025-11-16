"""Test management and business logic"""
from typing import List, Dict
from .models import TestComponent
from config.presets import TEST_COMPONENTS, TEST_PRESETS

class TestManager:
    """Manages test components and selection state"""
    
    def __init__(self):
        self.components = self._load_components()
    
    def _load_components(self) -> Dict[str, TestComponent]:
        return {
            tag: TestComponent(tag, data["name"], data["ram_intensity"])
            for tag, data in TEST_COMPONENTS.items()
        }
    
    def get_enabled_components(self) -> List[str]:
        return [tag for tag, comp in self.components.items() if comp.enabled]
    
    def enable_all(self) -> None:
        for comp in self.components.values():
            comp.enabled = True
    
    def disable_all(self) -> None:
        for comp in self.components.values():
            comp.enabled = False
    
    def apply_preset(self, preset_name: str) -> None:
        """Apply a test preset based on RAM intensity criteria"""
        self.disable_all()
        criteria = TEST_PRESETS[preset_name]["criteria"]
        
        min_intensity = criteria.get('min_ram_intensity', 0.0)
        max_intensity = criteria.get('max_ram_intensity', 1.0)
        
        for component in self.components.values():
            if min_intensity <= component.ram_intensity <= max_intensity:
                component.enabled = True