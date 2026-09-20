"""
Double-click launcher.

On Windows, a .pyw file is opened by "pythonw.exe" automatically when you
double-click it in File Explorer -- no console window, no need to type
"python main.py" in a terminal every time.

This just re-uses main.py's startup logic, so there is exactly one place
(main.py) that owns the actual startup sequence.
"""
from main import main

if __name__ == "__main__":
    main()
