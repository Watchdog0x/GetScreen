import ctypes
from ctypes import wintypes

class MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcMonitor', wintypes.RECT),
        ('rcWork', wintypes.RECT),
        ('dwFlags', wintypes.DWORD),
        ('szDevice', wintypes.WCHAR * 32),
    ]

class GetScreen:
    def __init__(self, screen: int):
        self.__monitor_handles = self.__get_display_monitors()
        self.__monitor_info_dict = {}

        if screen < len(self.__monitor_handles):
            monitor_info = self.__get_monitor_info(screen)
            self.__monitor_info_dict[screen] = monitor_info
            self.__monitor = monitor_info.rcMonitor
            self.display_name = self.__get_device_name(screen)
            self.is_primary_screen = self.__is_primary_screen(screen)
        else:
            raise ValueError("Invalid screen number")

    def __get_monitor_info(self, screen: int) -> MONITORINFOEX:
        monitor_info = MONITORINFOEX()
        monitor_info.cbSize = ctypes.sizeof(monitor_info)
        ctypes.windll.user32.GetMonitorInfoW(self.__monitor_handles[screen], ctypes.byref(monitor_info))
        return monitor_info

    def __get_device_name(self, screen: int) -> str:
        monitor_info = self.__monitor_info_dict.get(screen)
        if monitor_info:
            device_name = monitor_info.szDevice.replace('\\\\.\\', '')
            return device_name
        else:
            raise ValueError("Invalid screen number")

    def __get_display_monitors(self) -> list:
        monitors = []

        EnumDisplayMonitorsProc = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.POINTER(wintypes.RECT),
            ctypes.c_double,
        )

        def callback(hMonitor: ctypes.c_ulong, hdcMonitor: ctypes.c_ulong, lprcMonitor: ctypes.POINTER(wintypes.RECT),
                     dwData: ctypes.c_double) -> bool:
            monitors.append(hMonitor)
            return True

        enum_proc = EnumDisplayMonitorsProc(callback)
        ctypes.windll.user32.EnumDisplayMonitors(None, None, enum_proc, 0)
        return monitors

    @property
    def left_top_right_bottom(self) -> tuple:
        return self.__monitor.left, self.__monitor.top, self.__monitor.right, self.__monitor.bottom

    @property
    def x_y_width_height(self) -> tuple:
        return self.__monitor.left, self.__monitor.top, self.__monitor.right - self.__monitor.left, self.__monitor.bottom - self.__monitor.top

    def __is_primary_screen(self, screen: int) -> bool:
        monitor_info = self.__monitor_info_dict.get(screen)
        if monitor_info:
            return monitor_info.dwFlags & 1 == 1  # MONITORINFOF_PRIMARY
        else:
            raise ValueError("Invalid screen number")

