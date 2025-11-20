# y-cruncher StressTest GUI

Just a (lightweight) GUI for the StressTest part of y-cruncher, mainly for testing purposes.

DISCLAIMER: the code has been cleaned and the UI made graphically appealing by AI.
Take this as a quick personal project.


<img width="798" height="927" alt="{9FC62A4F-028F-4104-AACB-AEDA137832BE}" src="https://github.com/user-attachments/assets/37435f5a-d7dd-4d93-9046-efc9a657b70d" />





### Requirements

- **Python 3.6+**
- **y-cruncher v0.8.6 Build 9545+** ([Download](https://www.numberworld.org/y-cruncher/))
- **Required Python packages**: 
    - `tkinter`
    - `psutil`

### Installation - How to Use

- Download the [latest release](https://github.com/Profetorum/y-cruncher_GUI/releases) .zip file ( [y-cruncher 0.8.6](https://www.numberworld.org/y-cruncher/) required or prompted to download )
- Extract y-cruncher_gui.exe
- Start the GUI , select tests or use presets , select test duration or leave auto values. Then start the stress test.


  
### Compile

1. Install required Python package:
    ```bash
    pip install psutil
    ```
2. Optional:
    ```bash
    pip install ttkthemes
    ```
3. Compile:
    ```bash
    pyinstaller --windowed --onefile main.py
    ```

	
### Features

1. CPU , CPU+RAM , and RAM-focused stresstest presets
2. Checkbox interface with CPU-RAM load indicators for all tests
3. Select All/Deselect All toggles
4. Time Limit automatically calculates based on selected tests (1800s × test count) - Manual settings maintained when feasible
5. Console Output
6. A decently looking - lightweight user interface
7. .ini file saving tests selection / loading them on startup
8. Automatic y-cruncher download if not present
   

### Known Issues

1. In rare cases the y-cruncher process might not close correctly, requiring the user hard-killing it
2. y-cruncher test process won't get killed if the GUI process gets force-closed
3. Tests selection is hardcoded

















