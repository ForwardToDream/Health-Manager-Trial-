import threading
import sys
import os
from core.i18n import i18n_manager

class SystemTray:
    def __init__(self, page, on_show_window, on_quit, on_navigate=None):
        self.page = page
        self.on_show_window = on_show_window
        self.on_quit = on_quit
        self.on_navigate = on_navigate
        self.tray_icon = None
        self._running = False
        
    def start(self):
        try:
            from pystray import Icon, Menu, MenuItem
            from PIL import Image
            
            def load_icon_image():
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                icon_path = os.path.join(project_root, 'assests', 'resource', 'icon', 'Health_App.png')
                if os.path.exists(icon_path):
                    return Image.open(icon_path)
                else:
                    width = 64
                    height = 64
                    image = Image.new('RGB', (width, height), color='white')
                    return image
            
            def toggle_window(icon, item):
                if self.page.window.visible:

                    if not self.page.web:
                        self.page.window.visible = False
                        self.page.window.skip_task_bar = True
                        self.page.update()
                else:

                    if self.on_show_window:
                        self.on_show_window()

            def navigate_to(index):
                def handler(icon, item):
                    if self.on_navigate:
                        self.on_navigate(index)
                return handler

            def get_toggle_label(item):
                if self.page.window.visible:
                    return i18n_manager.t("tray_hide_window")
                else:
                    return i18n_manager.t("tray_show_window")

            def quit_app(icon, item):
                self._running = False
                
                try:
                    icon.stop()
                except:
                    pass
                
                if self.on_quit:
                    self.on_quit()
            
            menu = Menu(
                MenuItem(
                    get_toggle_label,
                    toggle_window,
                    default=True
                ),
                Menu.SEPARATOR,
                MenuItem(i18n_manager.t("tray_nav_home"), navigate_to(0)),
                MenuItem(i18n_manager.t("tray_nav_water"), navigate_to(1)),
                MenuItem(i18n_manager.t("tray_nav_food"), navigate_to(2)),
                MenuItem(i18n_manager.t("tray_nav_sleep"), navigate_to(3)),
                MenuItem(i18n_manager.t("tray_nav_exercise"), navigate_to(4)),
                MenuItem(i18n_manager.t("tray_nav_calendar"), navigate_to(5)),
                MenuItem(i18n_manager.t("tray_nav_settings"), navigate_to(6)),
                Menu.SEPARATOR,
                MenuItem(
                    i18n_manager.t("tray_quit"),
                    quit_app
                )
            )
            
            self.tray_icon = Icon(
                i18n_manager.t("app_title"),
                load_icon_image(),
                menu=menu
            )
            
            def run_tray():
                self._running = True
                self.tray_icon.run()
            
            tray_thread = threading.Thread(target=run_tray, daemon=True)
            tray_thread.start()
            
            return True
            
        except ImportError:
            return False
        except Exception as e:
            return False
    
    def stop(self):
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
            self._running = False
    
    @property
    def is_running(self):
        return self._running
