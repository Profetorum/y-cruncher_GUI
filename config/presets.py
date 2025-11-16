"""Test components and preset configurations"""

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