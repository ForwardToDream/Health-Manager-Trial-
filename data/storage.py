import datetime
from data import database
from core import event_bus
from data.defaults import get_default_user_data

DATA_FILE = "user_data.db"

def load_user_data():
    db_data = database.get_all_data()
    defaults = get_default_user_data()
    defaults.update(db_data)
    
    intensity = defaults.get("exercise_intensity", "")
    if intensity:
        if "almost no exercise" in intensity: defaults["exercise_intensity"] = "sedentary"
        elif "light activity" in intensity: defaults["exercise_intensity"] = "light_active"
        elif "moderate activity" in intensity: defaults["exercise_intensity"] = "moderately_active"
        elif "high activity" in intensity: defaults["exercise_intensity"] = "very_active"
        elif "extra active" in intensity: defaults["exercise_intensity"] = "extra_active"
        
    env = defaults.get("environment", "")
    if env:
        if "air conditioning" in env: defaults["environment"] = "ac_env"
        elif "cold" in env: defaults["environment"] = "cold_env"
        elif "hot" in env: defaults["environment"] = "hot_env"

    return defaults

def save_user_data(data, update_history=False):
    
    try:

        database.save_multiple_keys(data)
        

        event_bus.publish(event_bus.USER_DATA_SAVED, data)
        
        if update_history:

            try:
                update_today_summary()
            except Exception as e:
                print(f"Error updating summary: {e}")

        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def load_all_history() -> dict:
    
    if not database._db_initialized:
        database.init_db()
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    history = {}
    cursor.execute("SELECT date, summary FROM history")
    for row in cursor.fetchall():
        try:
            import json
            history[row['date']] = json.loads(row['summary'])
        except:
            pass
    
    conn.close()
    return history

def save_all_history(data: dict):
    
    for date_str, summary in data.items():
        database.save_history(date_str, summary)
    

    return save_user_data({}, update_history=False)

def save_daily_summary(date_str: str, summary: dict):
    
    database.save_history(date_str, summary)

    return save_user_data({}, update_history=False)

def load_daily_summary(date_str: str) -> dict:
    
    return database.get_daily_history(date_str)

def load_month_summaries(year: int, month: int) -> dict:
    
    return database.get_month_history(year, month)

def update_today_summary():
    
    from core.calculations import (
        calculate_water_goal, calculate_nutrition_goals,
        calculate_nutrition_score, calculate_sleep_score, calculate_exercise_score
    )
    
    user_data = load_user_data()
    today = datetime.date.today().isoformat()
    

    water_intake = user_data.get("water_intake", 0)
    water_goal = calculate_water_goal(user_data)
    water_achieved = water_intake >= water_goal
    

    daily_meals = user_data.get("daily_meals", {})
    actual_intake = {}
    if daily_meals.get("date") == today:
        meals = daily_meals.get("meals", [])
        for meal in meals:
            level1 = meal.get("level1", {})
            for key, value in level1.items():
                if isinstance(value, (int, float)):
                    actual_intake[key] = actual_intake.get(key, 0) + value
    
    nutrition_goals = calculate_nutrition_goals(user_data)
    nutrition_score = calculate_nutrition_score(actual_intake, nutrition_goals)
    

    daily_sleep = user_data.get("daily_sleep", {})
    sleep_duration = 0
    sleep_grade = "F"
    if daily_sleep.get("date") == today:
        records = daily_sleep.get("records", [])
        if records:
            sleep_duration = sum(r.get("duration_minutes", 0) for r in records)

            qualities = [r.get("quality", "fair") for r in records]
            quality_order = {"excellent": 0, "good": 1, "fair": 2, "poor": 3}
            best_quality = min(qualities, key=lambda q: quality_order.get(q, 2))
            sleep_grade = calculate_sleep_score(sleep_duration, best_quality)
    

    daily_exercises = user_data.get("daily_exercises", {})
    exercise_duration = 0
    exercise_calories = 0
    exercise_score = 0
    if daily_exercises.get("date") == today:
        records = daily_exercises.get("records", [])
        if records:
            exercise_duration = sum(r.get("duration_minutes", 0) for r in records)
            exercise_calories = sum(r.get("calories", 0) for r in records)
            exercise_score = calculate_exercise_score(records, user_data)
    

    summary = {
        "water_intake": water_intake,
        "water_goal": water_goal,
        "water_achieved": water_achieved,
        "nutrition_score": nutrition_score,
        "sleep_grade": sleep_grade,
        "sleep_duration": sleep_duration,
        "exercise_score": exercise_score,
        "exercise_duration": exercise_duration,
        "exercise_calories": exercise_calories
    }
    
    save_daily_summary(today, summary)
    return summary
