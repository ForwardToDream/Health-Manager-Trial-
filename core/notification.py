
import os
import platform
from core.i18n import i18n_manager

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_PATH = os.path.join(PROJECT_ROOT, 'assests', 'resource', 'icon', 'Health_App.ico')
ICON_PATH_PNG = os.path.join(PROJECT_ROOT, 'assests', 'resource', 'icon', 'Health_App.png')

SYSTEM = platform.system()

def send_notification(
    title_key: str = "app_title", 
    message_key: str = "reminder_warning", 
    duration: str = "short"
):
    
    title = i18n_manager.t(title_key)
    message = i18n_manager.t(message_key)
    
    if SYSTEM == "Windows":
        return _send_windows_notification(title, message, duration)
    elif SYSTEM == "Darwin":
        return _send_macos_notification(title, message)
    else:
        return _send_linux_notification(title, message)

def _send_windows_notification(title: str, message: str, duration: str) -> bool:
    
    try:
        from win11toast import toast
        
        icon_dict = None
        if os.path.exists(ICON_PATH):
            icon_dict = {'src': ICON_PATH, 'placement': 'appLogoOverride', 'hint-crop': 'circle'}
        
        toast(
            title=message,
            body='',
            app_id=title,
            duration=duration,
        )
        return True
        
    except ImportError:

        return _send_plyer_notification(title, message)
    except Exception as e:
        print(f"[Notification] Windows error: {e}")
        _play_beep()
        return False

def _send_macos_notification(title: str, message: str) -> bool:
    
    try:

        import subprocess
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except Exception:

        return _send_plyer_notification(title, message)

def _send_linux_notification(title: str, message: str) -> bool:
    
    try:

        import subprocess
        icon = ICON_PATH_PNG if os.path.exists(ICON_PATH_PNG) else ICON_PATH
        subprocess.run(['notify-send', title, message, '-i', icon], check=True)
        return True
    except Exception:

        return _send_plyer_notification(title, message)

def _send_plyer_notification(title: str, message: str) -> bool:
    
    try:
        from plyer import notification
        
        icon = ICON_PATH if os.path.exists(ICON_PATH) else None
        notification.notify(
            title=title,
            message=message,
            app_icon=icon,
            timeout=5
        )
        return True
    except ImportError:
        print("[Notification] plyer not installed")
        _play_beep()
        return False
    except Exception as e:
        print(f"[Notification] plyer error: {e}")
        _play_beep()
        return False

def _play_beep():
    
    try:
        if SYSTEM == "Windows":
            import ctypes
            ctypes.windll.user32.MessageBeep(0)
        elif SYSTEM == "Darwin":
            os.system('afplay /System/Library/Sounds/Ping.aiff &')
        else:
            print('\a', end='', flush=True)
    except Exception:
        pass

def flash_window(window_title: str):
    
    if SYSTEM != "Windows":
        return False
        
    try:
        import win32gui
        import win32con
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.FlashWindowEx(hwnd, win32con.FLASHW_ALL | win32con.FLASHW_TIMERNOFG, 3, 0)
            return True
        return False
    except ImportError:
        return False
    except Exception:
        return False
