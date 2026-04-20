from aiogram.fsm.state import State, StatesGroup


class SettingsState(StatesGroup):
    waiting_min_profit = State()
    waiting_min_volume = State()
    waiting_capital = State()
    waiting_min_exec = State()
    waiting_max_age = State()
