# y-cruncher StressTest GUI

Just a (lightweight) GUI for the StressTest part of y-cruncher, mainly for testing purposes.

DISCLAIMER: the code has been cleaned and the UI made graphically appealing by AI.
Take this as a quick personal project.


### Requirements

- **Python 3.6+**
- **y-cruncher v0.8.6 Build 9545+** ([Download](https://www.numberworld.org/y-cruncher/))
- **Required Python packages**: 
    - `tkinter`
    - `psutil`

### Installation - How to Use

- Compile or download the latest release .zip file
- Extract y-cruncher_gui.exe inside the y-cruncher folder (or wherever if you add y-cruncher to system PATH)
- Start the GUI , select tests or use presets , select test duration or leave auto values. Then start the stress test.


  
### Compile

1. Download y-cruncher from the official repository and extract to desired location
2. Place `y-cruncher.exe` in the same directory as the GUI script
3. Install required Python package:
    ```bash
    pip install psutil
    ```
4. Optional:
    ```bash
    pip install ttkthemes
    ```
5. Execute the application:
    ```bash
    python y-cruncher_gui.py
    ```
	
### Features

1. One-Click Presets: CPU-focused, CPU+RAM balanced, and RAM-focused test configurations
2. Component Selection: Checkbox interface with CPU-RAM load indicators for all tests
3. Select All/Deselect All for rapid test configuration
4. Time Limit automatically calculates based on selected tests (1800s × test count) - Manual settings maintained when technically feasible
5. Console Output
6. A decently looking - lightweight user interface

### Known Issues

1. In rare cases the y-cruncher process might not close correctly, requiring the user hard-killing it
2. y-cruncher test process won't get killed if the GUI process gets force-closed


