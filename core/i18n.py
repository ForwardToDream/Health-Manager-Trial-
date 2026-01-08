import flet as ft
import json
import os
import locale
from data.storage import load_user_data

def _detect_system_language():
    try:
        system_lang, _ = locale.getdefaultlocale()
        if system_lang:
            if system_lang.startswith('zh'):
                return 'zh_CN'
            elif system_lang.startswith('en'):
                return 'en_US'
    except Exception:
        pass
    return 'en_US'

class I18nManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(I18nManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, default_lang=None, fallback_lang="en_US"):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        

        user_data = load_user_data()
        saved_lang = user_data.get("language")
        
        if saved_lang:
            default_lang = saved_lang
        elif default_lang is None:
            default_lang = _detect_system_language()
        
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_dir = os.path.join(project_root, 'assests', 'i18n')
        
        self.default_lang = default_lang
        self.fallback_lang = fallback_lang
        self.current_lang = default_lang
        self.translations = {}
        self._subscribers = set()
        self.load_all_languages()

    def load_all_languages(self):
        if not os.path.isdir(self.base_dir):
            print(f"Error: Language directory not found at {self.base_dir}")
            return
            
        try:
            for filename in os.listdir(self.base_dir):
                if filename.endswith(".json"):
                    lang_code = filename.split(".")[0]
                    filepath = os.path.join(self.base_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.translations[lang_code] = json.load(f)
        except Exception as e:
            print(f"Error loading languages from {self.base_dir}: {e}")

    def set_language(self, lang_code: str):
        if lang_code in self.translations and self.current_lang != lang_code:
            self.current_lang = lang_code
            self._notify_subscribers()
            print(f"Language changed to: {lang_code}")

    def get(self, key: str, **kwargs) -> str:
        translation = self.translations.get(self.current_lang, {}).get(key)
        if translation is None:
            translation = self.translations.get(self.fallback_lang, {}).get(key)
        if translation is None:
            return key
        try:
            return translation.format(**kwargs)
        except KeyError:
            return translation

    def t(self, key: str, **kwargs) -> str:
        return self.get(key, **kwargs)

    def subscribe(self, callback):
        self._subscribers.add(callback)

    def unsubscribe(self, callback):
        self._subscribers.discard(callback)

    def _notify_subscribers(self):
        for callback in self._subscribers:
            try:
                callback()
            except Exception as e:
                print(f"Error in subscriber callback: {e}")

i18n_manager = I18nManager()

class I18nText(ft.Text):
    def __init__(self, key: str, **kwargs):
        self.key = key
        self.format_args = {k: v for k, v in kwargs.items() if k not in ft.Text.__dataclass_fields__}
        text_kwargs = {k: v for k, v in kwargs.items() if k not in self.format_args}

        super().__init__(value=i18n_manager.t(self.key, **self.format_args), **text_kwargs)

    def will_mount(self):
        i18n_manager.subscribe(self.update_ui)
        self.update_ui()

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)

    def update_ui(self):
        self.value = i18n_manager.t(self.key, **self.format_args)
        if self.page:
            self.update()
