# Screen Capture Utility in Python

This is a Python utility for capturing screens and managing screen information using the Windows API. The utility provides a way to capture screen data and handle screen information in a multi-screen setup.

## Features

- Capture screen data and save it as a BMP image.
- Retrieve information about the display monitors, such as monitor dimensions and positions.
- Identify primary screens.
- Handle multiple screens.

## How to Use

1. Ensure you have Python installed on your system.

2. Clone this repository or copy the provided code.

3. Import the necessary modules in your Python script or interactive session.

```python
import ctypes
from ctypes import wintypes
import threading
from screen_manager import GetScreen, ScreenCapture
```
1. The code provides two main classes: GetScreen and ScreenCapture. The GetScreen class retrieves information about display monitors, while the ScreenCapture class captures screen data.
2. To use the GetScreen class, you can create an instance by providing the screen number:
```python
screen_number = 0  # Change this to the desired screen number
screen = GetScreen(screen_number)
print("Display Name:", screen.display_name)
print("Primary Screen:", screen.is_primary_screen)
```
1. To capture screen data using the ScreenCapture class, create an instance and start capturing:
```python
screen_to_capture = GetScreen(0)  # Change this to the desired screen number
capture = ScreenCapture(screen_to_capture)

# Wait for data to be captured
captured_data = capture.get_captured_data()
```

## Note 
- This utility is specific to Windows and uses the Windows API to interact with display monitors and capture screen data.
- The code focuses on the functionality of capturing screen data and managing screen information. It does not provide error handling for all possible scenarios.

## License
This code is provided under the MIT License.
