from app.storage import WORKOUTS

def calc_norm_water(weight, activity, temperature):
    result = weight * 30 + (activity / 30) * 500 + (1000 if temperature >= 25 else 0)
    return round(result / 50) * 50


def calc_norm_food(weight, hight, age, activity):
    result = 10 * weight + 6.25 * hight - 5 * age + 10 * activity
    return round(result / 50) * 50


def calc_workout_calories(workout_type, duration):
    met_value = WORKOUTS.get(workout_type, 0)
    return int(met_value * duration)