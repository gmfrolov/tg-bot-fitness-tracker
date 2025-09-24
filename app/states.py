from aiogram.fsm.state import State, StatesGroup

class UserProfile(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    water_goal = State()
    calorie_goal = State()

class WaterLog(StatesGroup):
    water = State()

class FoodLog(StatesGroup):
    product_name = State()
    product_weight = State()
    