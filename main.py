import flet as ft
import sys
import os
from ui import main as flet_main

def check_single_instance():
    import tempfile
    import time
    
    lock_file = os.path.join(tempfile.gettempdir(), "health_companion_app.lock")
    
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                data = f.read().strip()
                if data:
                    last_time, pid = data.split(',')
                    last_time = float(last_time)
                    pid = int(pid)
                    
                    if time.time() - last_time < 10:
                        import platform
                        if platform.system() == "Windows":
                            try:
                                import win32gui
                                import win32con
                                
                                def callback(hwnd, results):
                                    if "Health Companion" in win32gui.GetWindowText(hwnd):
                                        results.append(hwnd)
                                    return True
                                
                                windows = []
                                win32gui.EnumWindows(callback, windows)
                                
                                if windows:
                                    hwnd = windows[0]
                                    if win32gui.IsIconic(hwnd):
                                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                                    win32gui.SetForegroundWindow(hwnd)
                                    win32gui.BringWindowToTop(hwnd)
                                    return False
                            except ImportError:
                                pass
                            except Exception:
                                pass
                        else:
                            print("Another instance is already running")
                        
                        return False
        except (ValueError, IOError, OSError):
            pass
    
    try:
        with open(lock_file, 'w') as f:
            f.write(f"{time.time()},{os.getpid()}")
    except IOError:
        pass
    
    return True

def update_lock_file():
    import tempfile
    import time
    import threading
    
    lock_file = os.path.join(tempfile.gettempdir(), "health_companion_app.lock")
    
    def update():
        while True:
            try:
                with open(lock_file, 'w') as f:
                    f.write(f"{time.time()},{os.getpid()}")
            except IOError:
                pass
            time.sleep(5)
    
    thread = threading.Thread(target=update, daemon=True)
    thread.start()

def cleanup_lock_file():
    import tempfile
    lock_file = os.path.join(tempfile.gettempdir(), "health_companion_app.lock")
    try:
        if os.path.exists(lock_file):
            os.remove(lock_file)
    except IOError:
        pass

if __name__ == "__main__":
    if not check_single_instance():
        print("Another instance is already running. Bringing it to front.")
        sys.exit(0)
    
    update_lock_file()
    
    import atexit
    atexit.register(cleanup_lock_file)
    
    ft.run(main=flet_main)