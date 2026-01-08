import flet as ft
from core.i18n import i18n_manager
from ui.styles import theme_manager, AppColors

class AppNavigationRail(ft.Container):
    def __init__(self, on_destination_selected):
        self.on_destination_selected = on_destination_selected
        self.selected_index = 0
        self.nav_buttons = {}
        
        super().__init__(
            width=100,
            bgcolor=theme_manager.current_colors.CARD_BG,
            padding=ft.padding.symmetric(vertical=20),
        )
        

        self.nav_configs = [

            {"index": 0, "key": "nav_home", "icon": ft.Icons.DASHBOARD_OUTLINED, "selected_icon": ft.Icons.DASHBOARD},
            {"index": 1, "key": "nav_water", "icon": ft.Icons.WATER_DROP_OUTLINED, "selected_icon": ft.Icons.WATER_DROP},
            {"index": 2, "key": "nav_food", "icon": ft.Icons.RESTAURANT_OUTLINED, "selected_icon": ft.Icons.RESTAURANT},
            {"index": 3, "key": "nav_sleep", "icon": ft.Icons.BEDTIME_OUTLINED, "selected_icon": ft.Icons.BEDTIME},
            {"index": 4, "key": "nav_exercise", "icon": ft.Icons.FITNESS_CENTER_OUTLINED, "selected_icon": ft.Icons.FITNESS_CENTER},

            {"index": 5, "key": "nav_calendar", "icon": ft.Icons.CALENDAR_MONTH_OUTLINED, "selected_icon": ft.Icons.CALENDAR_MONTH},
            {"index": 6, "key": "nav_settings", "icon": ft.Icons.SETTINGS_OUTLINED, "selected_icon": ft.Icons.SETTINGS},
        ]

        self._build_layout()
        
        i18n_manager.subscribe(self.update_ui)
        theme_manager.subscribe(self.update_theme)

    def will_unmount(self):
        i18n_manager.unsubscribe(self.update_ui)
        theme_manager.unsubscribe(self.update_theme)

    def update_theme(self):
        self.bgcolor = theme_manager.current_colors.CARD_BG
        self._update_selection_visuals()
        self.update()

    def update_ui(self):
        
        for config in self.nav_configs:
            idx = config["index"]
            if idx in self.nav_buttons:
                _, text_control, _ = self.nav_buttons[idx]
                text_control.value = i18n_manager.t(config["key"])
        self.update()

    def _build_nav_item(self, config):
        idx = config["index"]
        key = config["key"]
        icon = config["icon"]
        selected_icon = config["selected_icon"]
        
        is_selected = (idx == self.selected_index)
        
        current_icon = selected_icon if is_selected else icon
        color = theme_manager.current_colors.PRIMARY if is_selected else ft.Colors.ON_SURFACE_VARIANT
        bgcolor = theme_manager.current_colors.PRIMARY_CONTAINER if is_selected else ft.Colors.TRANSPARENT
        
        icon_control = ft.Icon(current_icon, color=color, size=24)
        text_control = ft.Text(
            i18n_manager.t(key),
            size=12,
            color=color,
            text_align=ft.TextAlign.CENTER
        )
        

        item_container = ft.Container(
            content=ft.Column(
                [icon_control, text_control],
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.all(10),
            border_radius=10,
            bgcolor=bgcolor,
            on_click=lambda e, i=idx: self._handle_click(i),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            tooltip=i18n_manager.t(key)
        )
        
        self.nav_buttons[idx] = (icon_control, text_control, item_container)
        return item_container

    def _build_layout(self):

        column_controls = []
        

        column_controls.append(ft.Container(expand=1))
        

        for i in range(5):
            config = self.nav_configs[i]
            column_controls.append(self._build_nav_item(config))
            column_controls.append(ft.Container(expand=1))
            

        

        column_controls = []
        column_controls.append(ft.Container(expand=1))
        
        for i in range(7):
            config = self.nav_configs[i]
            column_controls.append(self._build_nav_item(config))
            

            if i == 4:
                column_controls.append(ft.Container(expand=2))
            elif i == 6:
                column_controls.append(ft.Container(expand=1))
            else:
                column_controls.append(ft.Container(expand=1))
                
        self.content = ft.Column(
            controls=column_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

    def _handle_click(self, index):
        if index != self.selected_index:
            self.selected_index = index
            self._update_selection_visuals()
            self.on_destination_selected(index)

    def _update_selection_visuals(self):
        for idx, controls in self.nav_buttons.items():
            icon_control, text_control, container = controls
            config = next(c for c in self.nav_configs if c["index"] == idx)
            
            is_selected = (idx == self.selected_index)
            
            current_icon = config["selected_icon"] if is_selected else config["icon"]
            color = theme_manager.current_colors.PRIMARY if is_selected else ft.Colors.ON_SURFACE_VARIANT
            bgcolor = theme_manager.current_colors.PRIMARY_CONTAINER if is_selected else ft.Colors.TRANSPARENT
            
            icon_control.name = current_icon
            icon_control.color = color
            text_control.color = color
            container.bgcolor = bgcolor
            
            container.update()

    def set_selection(self, index):
        
        if index != self.selected_index:
            self.selected_index = index
            self._update_selection_visuals()
