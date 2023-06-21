# ScreenManager

ScreenManager is a Python class that retrieves information about display screens connected to a Windows system using the ctypes library. It provides methods to obtain the device name, coordinates, dimensions, and primary status of a specified screen.

## Persistence of Screen Identification
The ScreenManager class uses the device name of the screen to consistently identify the same screen even after a system restart. This ensures that the screen with a specific device name will be recognized consistently across different system sessions.

Please note that the device name may change if the display configuration is modified (e.g., connecting or disconnecting displays).

## Prerequisites

- Python 3.x
- Windows operating system

## Usage

```python
from screen_manager import GetScreen, InvalidScreenNumberError
import numpy as np
import cv2

screen = 1

try:
    screen = GetScreen(screen)
    display_info = screen.display_name
    print(display_info)

    left, top, right, bottom = screen.left_top_right_bottom
    print(f"Left: {left}, Top: {top}, Right: {right}, Bottom: {bottom}")

    x, y, width, height = screen.x_y_width_height
    print(f"X: {x}, Y: {y}, Width: {width}, Height: {height}")

    is_primary = screen.is_primary_screen
    print(f"Is Primary: {is_primary}")
    
    screen.capture_screen_to_file()
    bitmap_data = screen.capture_screen_to_data()

    # Convert the bitmap_data into a NumPy array
    image_data = np.frombuffer(bitmap_data, dtype=np.uint8)

    # Reshape the image_data array to match the dimensions of the image
    image = image_data.reshape((height, width, 3))

    # Convert the image data to the correct data type
    cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
   


except InvalidScreenNumberError  as e:
    print(str(e))




```

```text
$ python main.py
DISPLAY3
Left: 0, Top: 0, Right: 1920, Bottom: 1080
X: 0, Y: 0, Width: 1920, Height: 1080
Is Primary: True
```

### DOC
https://learn.microsoft.com/en-us/windows/win32/api/_gdi/
