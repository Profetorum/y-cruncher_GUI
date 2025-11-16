"""Data models for the application"""
from typing import List, Dict, Tuple, Optional

class TestComponent:
    """Represents a single stress test component"""
    
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

class TestConfig:
    """Stores test configuration parameters"""
    
    __slots__ = ('time_limit', 'duration_per_test', 'memory')
    
    def __init__(self):
        from config.settings import TEST_CONFIG
        defaults = TEST_CONFIG['default_values']
        self.time_limit = defaults['time_limit']
        self.duration_per_test = defaults['duration_per_test']
        self.memory = defaults['memory']