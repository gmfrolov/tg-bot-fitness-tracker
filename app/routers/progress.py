from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from app.states import WaterLog, FoodLog
from app.utils.food_api import get_food_info
from app.storage import users, WORKOUTS
from app.utils.calculations import calc_workout_calories

router = Router()

@router.message(Command('log_water'))
async def start_log_water(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        try:
            amount = float(parts[1])
            if "logged_water" not in users[message.from_user.id]:
                users[message.from_user.id]["logged_water"] = int(amount)
            else:
                users[message.from_user.id]["logged_water"] += int(amount)
            
            await message.reply(
                    f"Записано {amount} мл воды\n"
                    f'Вам осталось выпить: {users[message.from_user.id]["water_goal"] - users[message.from_user.id]["logged_water"]}'
                )
        
        except ValueError:
            await message.reply("Пожалуйста, укажите число: /log_water <количество>")
    else:
        await message.reply("Сколько воды выпито?")
        await state.set_state(WaterLog.water)

@router.message(WaterLog.water)
async def end_log_water(message: Message, state: FSMContext):
    if "logged_water" not in users[message.from_user.id]:
         users[message.from_user.id]["logged_water"] = int(message.text)
    else:
        users[message.from_user.id]["logged_water"] += int(message.text)
    await message.reply(
        f"Записано {int(message.text)} мл воды\n"
        f'Вам осталось выпить: {users[message.from_user.id]["water_goal"] - users[message.from_user.id]["logged_water"]}'
        )
    await state.clear()

# Ввод наименования продукта
@router.message(Command('log_food'))
async def start_log_food(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        product_name = parts[1]
        info_product = await get_food_info(product_name)
        if info_product:
            await state.update_data(calories=info_product["calories"])
            await message.reply(f'{info_product["name"]} — {info_product["calories"]} ккал на 100 г.\nСколько грамм вы съели?')
            await state.set_state(FoodLog.product_weight)
        else:
            await message.reply(f'Такого продукта не нашлось :(\n Попробуйте еще раз!')
            await state.set_state(FoodLog.product_name)

    else:
        await message.reply('Введите название продукта/блюда:')
        await state.set_state(FoodLog.product_name)

# Поиск продукта
@router.message(FoodLog.product_name)
async def end_log_name_food(message: Message, state: FSMContext):
    product_name = message.text
    info_product = await get_food_info(product_name)
    if info_product:
        await state.update_data(calories=info_product["calories"])
        await message.reply(f'{info_product["name"]} — {info_product["calories"]} ккал на 100 г.\nСколько грамм вы съели?')
        await state.set_state(FoodLog.product_weight)
    else:
        await message.reply(f'Такого продукта не нашлось :(\n Попробуйте еще раз!')
        await state.set_state(FoodLog.product_name)


@router.message(FoodLog.product_weight)
async def end_log_weight_food(message: Message, state: FSMContext):
    data = await state.get_data()
    if "logged_calories" not in users[message.from_user.id]:
         users[message.from_user.id]["logged_calories"] = data['calories'] * int(message.text) / 100
    else:
        users[message.from_user.id]["logged_calories"] += data['calories'] * int(message.text) / 100
    await message.reply(f'Записано: {data["calories"] * int(message.text) / 100} ккал')
    await state.clear()


@router.message(Command("log_workout"))
async def log_workout_cmd(message: Message, command: CommandObject):
    if command.args:
        try:
            parts = command.args.rsplit(" ", maxsplit=1)
            workout_type = parts[0].lower()
            duration = int(parts[1])

            if workout_type not in WORKOUTS:
                await message.answer(
                    f"Неверный тип тренировки.\nДоступные тренировки: {', '.join(WORKOUTS)}"
                )
                return

            calories = calc_workout_calories(workout_type, duration)
            users[message.from_user.id]["burned_calories"] = users[message.from_user.id].get("burned_calories", 0) + calories
            await message.answer(f"Вы сожгли {calories} ккал за {duration} минут")
        except (IndexError, ValueError):
            await message.answer(
                "Неправильный формат команды. Используйте: /log_workout <тип> <время>\n"
                f"Доступные тренировки: {', '.join(WORKOUTS)}"
            )
    else:
        # если параметры не указаны
        await message.answer(
            "Вы не указали параметры.\n"
            f"Доступные тренировки: {', '.join(WORKOUTS)}\n"
            "Пример команды: /log_workout бег 30"
        )


@router.message(Command("check_progress"))
async def check_progress_cmd(message: Message):
    data = users[message.from_user.id]
    await message.reply(
            f'📊 Прогресс:\n'
            f'Вода:\n'
            f'- Выпито: {data["logged_water"]} мл из {data["calorie_goal"]} мл.\n'
            f'- Осталось: {data["calorie_goal"] - data["logged_water"]} мл.\n\n'
            f'Калории:\n'
            f'- Потреблено: {data["logged_calories"]} ккал из {data["calorie_goal"]} ккал.\n'
            f'- Сожжено: {data["burned_calories"]} ккал.\n'
            f'- Баланс: {data["logged_calories"] - data["burned_calories"]} ккал.'
        )
