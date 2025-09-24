from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.states import UserProfile
from app.utils import calculations, weather_api
from app.storage import users

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Приветствие пользователя и краткая инструкция по боту.
    """
    await message.reply(
        "Привет! Я твой помощник для расчёта нормы воды и калорий.\n"
        "Я помогу отслеживать питание, тренировки и потребление воды.\n"
        "Чтобы начать, настрой свой профиль командой /set_profile.\n"
        "Если нужна помощь, введи /help."
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Показывает список всех доступных команд с кратким описанием.
    """
    await message.reply(
        "📌 Доступные команды:\n"
        "/set_profile — настроить профиль\n"
        "/change_calorie_goal — изменить цель по калориям\n"
        "/log_water <объем в мл> — записать выпитую воду (мл)\n"
        "/log_food <название> — записать съеденный продукт\n"
        "/log_workout <тип> <время> — записать тренировку\n"
        "/check_progress — посмотреть текущий прогресс\n"
    )
    

@router.message(Command('set_profile'))
async def start_set_profile(message: Message, state: FSMContext):
    await message.reply('Введите ваш вес (в кг):')
    await state.set_state(UserProfile.weight)

@router.message(UserProfile.weight)
async def process_weight(message: Message,state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(UserProfile.height)

@router.message(UserProfile.height)
async def process_height(message: Message,state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply("Введите ваш возраст:")
    await state.set_state(UserProfile.age)

@router.message(UserProfile.age)
async def process_age(message: Message,state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Сколько минут активности у вас в день?")
    await state.set_state(UserProfile.activity)

@router.message(UserProfile.activity)
async def process_activity(message: Message,state: FSMContext):
    await state.update_data(activity=message.text)
    await message.reply("В каком городе вы находитесь?")
    await state.set_state(UserProfile.city)

@router.message(UserProfile.city)
async def process_city(message: Message, state: FSMContext):
    data = await state.get_data()
    data["weight"] = int(data["weight"])
    data["height"] = int(data["height"])
    data["age"] = int(data["age"])
    data["activity"] = int(data["activity"])
    data["city"] = message.text
    data["temperature"] = await weather_api.fetch_temperature(data["city"])
    data["water_goal"] = calculations.calc_norm_water(data["weight"], data["activity"], data["temperature"])
    data["calorie_goal"] = calculations.calc_norm_food(data["weight"], data["height"], data["age"], data["activity"])
    users[message.from_user.id] = data
    await message.reply(
        f"✅ Профиль сохранён!\n"
        f"Вес: {data['weight']} кг\nРост: {data['height']} см\nВозраст: {data['age']}\nАктивность: {data['activity']} мин\nГород: {data['city']}\n"
        f"Ваша норма воды: {data['water_goal']} мл\nВаша норма каллорий: {data['calorie_goal']} ккал\n\n"
        f"Норму каллорий можно изменить командой: /change_calorie_goal"
    )
    await state.clear()

@router.message(Command('change_calorie_goal'))
async def cmd_change_calorie_goal(message: Message, state: FSMContext):
        await message.reply("Введите новую цель по каллориям:")
        await state.set_state(UserProfile.calorie_goal)


@router.message(UserProfile.calorie_goal)
async def process_calorie_goal(message: Message, state: FSMContext):
    users[message.from_user.id]["calorie_goal"] = int(message.text)
    await message.reply(
        f"✅ Норма каллорий изменена!\n"
        f"Новая цель: {users[message.from_user.id]['calorie_goal']}"
    )
    await state.clear()
