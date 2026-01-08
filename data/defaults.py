import datetime

def get_default_user_data():
    
    today = datetime.date.today().isoformat()
    return {

        "gender": "male",
        "age": 30,
        "height": 175,
        "weight": 70,
        "activity_level": "medium",
        "goal": "maintain",
        

        "theme_mode": "system",
        "close_mode": "ask",
        "language": "zh_CN",
        "china_ai_mode": False,
        "use_china_ai_mode": False,
        "reminder_active": False,
        

        "water_intake": 0,
        "water_records": {"date": today, "records": []},
        "daily_meals": {"date": today, "meals": []},
        "daily_sleep": {"date": today, "records": []},
        "daily_exercises": {"date": today, "records": []},
        

        "last_drink_timestamp": None,
        "environment": "default",
        "cycle_state": None,
        "exercise_intensity": "moderate",
    }
