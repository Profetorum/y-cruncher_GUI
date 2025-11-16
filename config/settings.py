"""Application configuration settings"""

# UI Appearance Configuration
UI_CONFIG = {
    'window': {
        'title': "y-cruncher StressTest GUI",
        'size': "800x900",
        'min_size': (800, 600)
    },
    'fonts': {
        'header': ('Arial', 16, 'bold'),
        'label': ('Arial', 9, 'bold'),
        'entry': ('Arial', 10),
        'small': ('Arial', 8),
        'console': ('Consolas', 9),
        'button': ('Arial', 9)
    },
    'colors': {
        'console_bg': '#1e1e1e',
        'console_fg': '#d4d4d4',
        'command_text': '#569cd6',
        'info_text': '#6a9955',
        'error_text': '#f44747',
        'warning_text': '#cc0000'
    },
    'layout': {
        'frame_padding': 5,
        'widget_padding': 2,
        'section_padding': (10, 5)
    }
}

# Test Behavior Configuration
TEST_CONFIG = {
    'auto_time_limit_per_test': 1800,
    'default_per_test_duration': 120,
    'default_values': {
        'time_limit': "Auto",
        'duration_per_test': "Auto", 
        'memory': "Auto"
    }
}

# ANSI Color Codes
ANSI_COLORS = {
    '30': 'black', '31': 'red', '32': 'green', '33': 'yellow',
    '34': 'blue', '35': 'magenta', '36': 'cyan', '37': 'white',
    '90': 'bright_black', '91': 'bright_red', '92': 'bright_green', '93': 'bright_yellow',
    '94': 'bright_blue', '95': 'bright_magenta', '96': 'bright_cyan', '97': 'bright_white'
}