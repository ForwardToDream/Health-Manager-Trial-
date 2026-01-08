import flet as ft
from ui.components.water_formula_card import WaterFormulaCard
from ui.components.reminder_card import ReminderCard

class WaterView(ft.Container):
    def __init__(self, water_card):
        super().__init__()
        self.expand = True
        
        self.reminder_card = ReminderCard()
        self.formula_card = WaterFormulaCard()
        
        self.content = ft.ListView(
            controls=[
                self.reminder_card,
                water_card,
                self.formula_card
            ],
            spacing=20,
            padding=ft.padding.only(left=20, top=20, right=35, bottom=20)
        )
