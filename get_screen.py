import ctypes
from ctypes import wintypes

# Define the MONITORINFOEX structure
class MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcMonitor', wintypes.RECT),
        ('rcWork', wintypes.RECT),
        ('dwFlags', wintypes.DWORD),
        ('szDevice', wintypes.WCHAR * 32),
    ]

class GetScreen:    
    def __init__(self, screen):
        self.monitor_handles = self.get_display_monitors()
        self.monitor_info_dict = {}

        if screen < len(self.monitor_handles):
            monitor_info = self.get_monitor_info(screen)
            self.monitor_info_dict[screen] = monitor_info
            self.monitor = monitor_info.rcMonitor
            self.display_name = self.get_device_name(screen)
        else:
            raise ValueError("Invalid screen number")

    def get_monitor_info(self, screen):
        monitor_info = MONITORINFOEX()
        monitor_info.cbSize = ctypes.sizeof(MONITORINFOEX)
        ctypes.windll.user32.GetMonitorInfoW(self.monitor_handles[screen], ctypes.byref(monitor_info))
        return monitor_info

    def get_monitor(self, screen):
        monitor_info = self.monitor_info_dict.get(screen)
        if monitor_info:
            return monitor_info.rcMonitor
        else:
            raise ValueError("Invalid screen number")

    def get_device_name(self, screen):
        monitor_info = self.monitor_info_dict.get(screen)
        if monitor_info:
            device_name = monitor_info.szDevice.replace('\\\\.\\', '')
            return device_name
        else:
            raise ValueError("Invalid screen number")

    def get_display_monitors(self):
        class RECT(ctypes.Structure):
            _fields_ = [
                ('left', ctypes.c_long),
                ('top', ctypes.c_long),
                ('right', ctypes.c_long),
                ('bottom', ctypes.c_long),
            ]

        EnumDisplayMonitorsProc = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.POINTER(RECT),
            ctypes.c_double,
        )

        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            monitors.append(hMonitor)
            return True

        monitors = []
        enum_proc = EnumDisplayMonitorsProc(callback)
        ctypes.windll.user32.EnumDisplayMonitors(None, None, enum_proc, 0)
        return monitors

    def left_top_right_bottom(self):
        return self.monitor.left, self.monitor.top, self.monitor.right, self.monitor.bottom

    def x_y_width_height(self):
        return self.monitor.left, self.monitor.top, self.monitor.right - self.monitor.left, self.monitor.bottom - self.monitor.top

    def is_primary_screen(self):
        monitor_info = self.monitor_info_dict.get(screen)
        if monitor_info:
            return monitor_info.dwFlags & 1  # MONITORINFOF_PRIMARY
        else:
            raise ValueError("Invalid screen number")

    # Alias
    ltrb = left_top_right_bottom
    xywh = x_y_width_height


# Example usage
screen = 1
get_screen = GetScreen(screen)
display_info = get_screen.display_name
print(display_info)

left, top, right, bottom = get_screen.left_top_right_bottom()
print(f"Left: {left}, Top: {top}, Right: {right}, Bottom: {bottom}")

x, y, width, height = get_screen.x_y_width_height()
print(f"X: {x}, Y: {y}, Width: {width}, Height: {height}")

is_primary = get_screen.is_primary_screen()
print(f"Is Primary: {is_primary}")

