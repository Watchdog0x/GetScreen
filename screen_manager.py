import ctypes
from ctypes import wintypes
import threading

class BITMAPFILEHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("bfType", wintypes.WORD),
        ("bfSize", wintypes.DWORD),
        ("bfReserved1", wintypes.WORD),
        ("bfReserved2", wintypes.WORD),
        ("bfOffBits", wintypes.DWORD),
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class MONITORINFOEX(ctypes.Structure):
    _fields_ = [
        ('cbSize', wintypes.DWORD),
        ('rcMonitor', wintypes.RECT),
        ('rcWork', wintypes.RECT),
        ('dwFlags', wintypes.DWORD),
        ('szDevice', wintypes.WCHAR * 32),
    ]


class InvalidScreenNumberError(Exception):
    def __init__(self, screen: int, available_screens: list):
        self.screen = screen
        self.available_screens = available_screens
        super().__init__(
            f"Invalid screen number: {screen}. Available screen numbers: {available_screens}")


class GetScreen:
    __monitor_info_dict = {}

    def __init__(self, screen: int):
        self.__monitor_handles = self.__get_display_monitors()

        if screen < len(self.__monitor_handles):
            if screen not in GetScreen.__monitor_info_dict:
                monitor_info = self.__get_monitor_info(screen)
                GetScreen.__monitor_info_dict[screen] = monitor_info
            else:
                monitor_info = GetScreen.__monitor_info_dict[screen]

            self.__monitor = monitor_info.rcMonitor
            self.__display_name = self.__get_device_name(screen)
            self.__is_primary_screen = self.__is_primary_screen(screen)
            self.__capture_lock = threading.Lock()
            self.__capture_data = None
        else:
            raise InvalidScreenNumberError(
                screen, list(range(len(self.__monitor_handles))))
    @property
    def get_monitor(self):
        return self.__monitor

    def __get_monitor_info(self, screen: int) -> MONITORINFOEX:
        monitor_info = MONITORINFOEX()
        monitor_info.cbSize = ctypes.sizeof(monitor_info)
        ctypes.windll.user32.GetMonitorInfoW(
            self.__monitor_handles[screen], ctypes.byref(monitor_info))
        return monitor_info

    def __get_device_name(self, screen: int) -> str:
        monitor_info = GetScreen.__monitor_info_dict.get(screen)
        if monitor_info:
            device_name = monitor_info.szDevice.replace('\\\\.\\', '')
            return device_name

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

    def __is_primary_screen(self, screen: int) -> bool:
        monitor_info = self.__monitor_info_dict.get(screen)
        if monitor_info:
            return monitor_info.dwFlags & 1 == 1  # MONITORINFOF_PRIMARY

    @property
    def display_name(self) -> str:
        """
        Get the display name of the monitor.

        Returns:
            str: The display name of the monitor.
        """
        return self.__display_name

    @property
    def is_primary_screen(self) -> bool:
        """
        Check if the monitor is the primary screen.

        Returns:
            bool: True if the monitor is the primary screen, False otherwise.
        """
        return self.__is_primary_screen

    @property
    def left_top_right_bottom(self) -> tuple:
        """
        Example:
            left, top, right, bottom = GetScreen(0).left_top_right_bottom

        Get the coordinates of the left, top, right, and bottom edges of the monitor's bounding rectangle.

        Returns:
            tuple: The left, top, right, and bottom coordinates.
        """
        return (
            self.__monitor.left,
            self.__monitor.top,
            self.__monitor.right,
            self.__monitor.bottom,
        )

    @property
    def x_y_width_height(self) -> tuple:
        """
        Example:
            x, y, width, height = GetScreen(0).left_top_right_bottom

        Get the coordinates of the top-left corner and the width and height of the monitor.

        Returns:
            tuple: The x-coordinate, y-coordinate, width, and height.
        """
        return (
            self.__monitor.left,
            self.__monitor.top,
            self.__monitor.right - self.__monitor.left,
            self.__monitor.bottom - self.__monitor.top,
        )

    def screenshot(self, bmp_filename="out.bmp"):
        width = self.__monitor.right - self.__monitor.left  # Get the width of the screen
        height = self.__monitor.bottom - self.__monitor.top  # Get the height of the screen

        screen_dc = ctypes.windll.user32.GetDC(0)
        mem_dc = ctypes.windll.gdi32.CreateCompatibleDC(screen_dc)
        bitmap = ctypes.windll.gdi32.CreateCompatibleBitmap(
            screen_dc, width, height)
        old_bitmap = ctypes.windll.gdi32.SelectObject(mem_dc, bitmap)
        SRCCOPY = 0x00CC0020
        ctypes.windll.gdi32.BitBlt(mem_dc, 0, 0, width, height, screen_dc,  self.__monitor.left,
                                   self.__monitor.top, SRCCOPY)

        bitmap_header = BITMAPFILEHEADER()
        bitmap_header.bfType = 0x4D42
        bitmap_header.bfSize = ctypes.sizeof(
            BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER) + width * height * 3
        bitmap_header.bfReserved1 = 0
        bitmap_header.bfReserved2 = 0
        bitmap_header.bfOffBits = ctypes.sizeof(
            BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER)

        bitmap_info = BITMAPINFOHEADER()
        bitmap_info.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bitmap_info.biWidth = width
        bitmap_info.biHeight = -height
        bitmap_info.biPlanes = 1
        bitmap_info.biBitCount = 24
        bitmap_info.biCompression = 0
        bitmap_info.biSizeImage = 0
        bitmap_info.biXPelsPerMeter = 0
        bitmap_info.biYPelsPerMeter = 0
        bitmap_info.biClrUsed = 0
        bitmap_info.biClrImportant = 0

        bitmap_data = ctypes.create_string_buffer(width * height * 3)
        ctypes.windll.gdi32.GetDIBits(
            mem_dc, bitmap, 0, height, bitmap_data, ctypes.byref(
                bitmap_info), 0
        )

        with open(bmp_filename, "wb") as bmp_file:
            bmp_file.write(bitmap_header)
            bmp_file.write(bitmap_info)
            bmp_file.write(bitmap_data)

        ctypes.windll.gdi32.SelectObject(mem_dc, old_bitmap)
        ctypes.windll.gdi32.DeleteObject(bitmap)
        ctypes.windll.gdi32.DeleteDC(mem_dc)
        ctypes.windll.user32.ReleaseDC(0, screen_dc)

class ScreenCapture:
    def __init__(self, monitor):
        self.__monitor = monitor
        self.__capture_data = None
        self.__capture_lock = threading.Lock()
        self.__data_available = threading.Event()
        self.__capture_thread = threading.Thread(target=self.__capture_screen_data)
        self.__capture_thread.daemon = True
        self.__capture_thread.start()

    def __capture_screen_data(self):
        while True:
            width = self.__monitor.right - self.__monitor.left
            height = self.__monitor.bottom - self.__monitor.top

            screen_dc = ctypes.windll.user32.GetDC(0)
            mem_dc = ctypes.windll.gdi32.CreateCompatibleDC(screen_dc)
            bitmap = ctypes.windll.gdi32.CreateCompatibleBitmap(screen_dc, width, height)
            old_bitmap = ctypes.windll.gdi32.SelectObject(mem_dc, bitmap)
            SRCCOPY = 0x00CC0020
            ctypes.windll.gdi32.BitBlt(mem_dc, 0, 0, width, height, screen_dc, self.__monitor.left,
                                        self.__monitor.top, SRCCOPY)

            bitmap_info = BITMAPINFOHEADER()
            bitmap_info.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bitmap_info.biWidth = width
            bitmap_info.biHeight = -height
            bitmap_info.biPlanes = 1
            bitmap_info.biBitCount = 24
            bitmap_info.biCompression = 0
            bitmap_info.biSizeImage = 0
            bitmap_info.biXPelsPerMeter = 0
            bitmap_info.biYPelsPerMeter = 0
            bitmap_info.biClrUsed = 0
            bitmap_info.biClrImportant = 0

            bitmap_data = ctypes.create_string_buffer(width * height * 3)
            ctypes.windll.gdi32.GetDIBits(mem_dc, bitmap, 0, height, bitmap_data, ctypes.byref(bitmap_info), 0)

            ctypes.windll.gdi32.SelectObject(mem_dc, old_bitmap)
            ctypes.windll.gdi32.DeleteObject(bitmap)
            ctypes.windll.gdi32.DeleteDC(mem_dc)
            ctypes.windll.user32.ReleaseDC(0, screen_dc)

            with self.__capture_lock:
                self.__capture_data = bitmap_data
                self.__data_available.set()
    
    def get_captured_data(self):
        self.__data_available.wait()
        with self.__capture_lock:
            return self.__capture_data