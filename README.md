# y-cruncher StressTest GUI

Just a (lightweight) GUI for the StressTest part of y-cruncher, mainly for testing purposes.

DISCLAIMER: the code has been cleaned and the UI made graphically appealing by AI.
Take this as a quick personal project.

<img width="799" height="931" alt="{7CC94B43-357C-4482-9F38-9AE140EE22FA}" src="https://github.com/user-attachments/assets/6bff379e-a4c2-477b-87f4-ac50cda0ed04" />




### Requirements

- **Python 3.6+**
- **y-cruncher v0.8.6 Build 9545+** ([Download](https://www.numberworld.org/y-cruncher/))
- **Required Python packages**: 
    - `tkinter`
    - `psutil`

### Installation - How to Use

- Download the latest release .zip file
- Extract y-cruncher_gui.exe inside the y-cruncher folder (or wherever if you add y-cruncher to system PATH)
- Start the GUI , select tests or use presets , select test duration or leave auto values. Then start the stress test.


  
### Run the .py file

1. Install required Python package:
    ```bash
    pip install psutil
    ```
2. Optional:
    ```bash
    pip install ttkthemes
    ```
3. Execute the application:
    ```bash
    python y-cruncher_gui.py
    ```

	
### Features

1. CPU , CPU+RAM , and RAM-focused test presets
2. Checkbox interface with CPU-RAM load indicators for all tests
3. Select All/Deselect All toggles
4. Time Limit automatically calculates based on selected tests (1800s × test count) - Manual settings maintained when feasible
5. Console Output
6. A decently looking - lightweight user interface
   

### Known Issues

1. In rare cases the y-cruncher process might not close correctly, requiring the user hard-killing it
2. y-cruncher test process won't get killed if the GUI process gets force-closed
3. Tests selection is hardcoded







