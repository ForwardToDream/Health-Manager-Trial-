def calculate_water_goal(user_data: dict) -> int:
    try:
        weight = float(user_data.get("weight", 0))
        age = int(user_data.get("age", 0))
        height = float(user_data.get("height", 0))
        exercise = user_data.get("exercise_intensity", "")
        environment = user_data.get("environment", "")

        if weight <= 0:
            return 2000

        coefficient = 30
        if 3 <= age <= 12:
            coefficient = 50
        elif 13 <= age <= 17:
            coefficient = 40
        elif 18 <= age <= 55:
            coefficient = 33
        elif 56 <= age <= 65:
            coefficient = 28
        elif age >= 66:
            coefficient = 23
        
        base_intake = weight * coefficient

        if height >= 175:
            base_intake += 250
        elif height <= 155:
            base_intake -= 150

        extra_intake = 0
        if "light_active" in exercise:
            extra_intake += 400
        elif "moderately_active" in exercise:
            extra_intake += 750
        elif "very_active" in exercise or "high_active" in exercise or "extra_active" in exercise:
            extra_intake += 1000
        
        if "hot_env" in environment:
            extra_intake += 400
        elif "ac_env" in environment:
            extra_intake += 200

        total_intake = base_intake + extra_intake
        
        return int(round(total_intake / 10) * 10)

    except (ValueError, TypeError):
        return 2000

def _calculate_adult_nutrition(weight, height, age, exercise_level, environment, sex="male"):
    bmr = 10 * weight + 6.25 * height - 5 * age
    if sex == "male":
        bmr += 5
    else:
        bmr -= 161
    
    activity_factors = {
        "sedentary": 1.2,
        "light_active": 1.375,
        "moderately_active": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9,
    }
    
    factor = 1.2
    

    for key, val in activity_factors.items():
        if key in exercise_level:
            factor = val
            if key in ["sedentary", "light_active", "moderately_active", "very_active", "extra_active"]:
                break
            
    tdee = bmr * factor
    
    if "cold_env" in environment or "hot_env" in environment:
        tdee *= 1.1
        
    return {
        "calories": {"min": round(tdee * 0.9), "max": round(tdee * 1.1), "unit": "kcal"},
        "protein": {"min": round(weight * 0.8, 1), "max": round(weight * 2.0, 1), "unit": "g"},
        "total_fat": {"min": round((tdee * 0.2) / 9, 1), "max": round((tdee * 0.35) / 9, 1), "unit": "g"},
        "total_carbs": {"min": round((tdee * 0.45) / 4, 1), "max": round((tdee * 0.65) / 4, 1), "unit": "g"},
        "fiber": {"min": 25, "max": 38, "unit": "g"},
        "sugars": {"min": 0, "max": round((tdee * 0.1) / 4, 1), "unit": "g"},
        "sodium": {"min": 1500, "max": 2300, "unit": "mg"},
        "calcium": {"min": 800, "max": 2000, "unit": "mg"},
        "vitamin_c": {"min": 100, "max": 2000, "unit": "mg"},
        "vitamin_d": {"min": 15, "max": 100, "unit": "µg"}
    }

def _calculate_youth_nutrition(weight, height, age, exercise_level, environment, sex="male"):
    if 3 <= age < 10:
        bmr = (22.7 * weight + 495) if sex == "male" else (22.5 * weight + 499)
    elif 10 <= age <= 18:
        bmr = (17.5 * weight + 651) if sex == "male" else (12.2 * weight + 746)
    else:
        return _calculate_adult_nutrition(weight, height, age, exercise_level, environment, sex)

    tdee = bmr * 1.5  
    growth_surplus = tdee * 0.1
    target_calories = tdee + growth_surplus

    calcium_min = 1300 if age >= 9 else 1000

    return {
        "calories": {"min": round(target_calories * 0.95), "max": round(target_calories * 1.05), "unit": "kcal"},
        "protein": {"min": round(weight * 1.2, 1), "max": round(weight * 1.8, 1), "unit": "g"},
        "total_fat": {"min": round((target_calories * 0.25) / 9, 1), "max": round((target_calories * 0.35) / 9, 1), "unit": "g"},
        "total_carbs": {"min": round((target_calories * 0.45) / 4, 1), "max": round((target_calories * 0.65) / 4, 1), "unit": "g"},
        "fiber": {"min": 25, "max": 38, "unit": "g"},
        "sugars": {"min": 0, "max": round((target_calories * 0.08) / 4, 1), "unit": "g"},
        "sodium": {"min": 1500, "max": 2300, "unit": "mg"},
        "calcium": {"min": calcium_min, "max": 2500, "unit": "mg"},
        "vitamin_c": {"min": 100, "max": 2000, "unit": "mg"},
        "vitamin_d": {"min": 15, "max": 100, "unit": "µg"}
    }

def calculate_nutrition_goals(user_data: dict) -> dict:
    try:
        weight = float(user_data.get("weight", 70))
        height = float(user_data.get("height", 175))
        age = int(user_data.get("age", 30))
        exercise = user_data.get("exercise_intensity", "sedentary")
        environment = user_data.get("environment", "")
        sex = user_data.get("gender", "male").lower()
        if sex not in ["male", "female"]:
            sex = "male"

        if age < 18:
            raw_goals = _calculate_youth_nutrition(weight, height, age, exercise, environment, sex)
        else:
            raw_goals = _calculate_adult_nutrition(weight, height, age, exercise, environment, sex)

        formatted_goals = {}
        for key, data in raw_goals.items():
            min_val = data["min"]
            max_val = data["max"]
            ideal_val = (min_val + max_val) / 2
            formatted_goals[key] = {
                "ideal": ideal_val,
                "unit": data["unit"],
                "range": [min_val, ideal_val, max_val]
            }
            
        return formatted_goals

    except (ValueError, TypeError):
        return {
            "calories": {"ideal": 2000, "unit": "kcal", "range": [1800, 2000, 2200]},
            "protein": {"ideal": 100, "unit": "g", "range": [56, 100, 140]},
            "total_fat": {"ideal": 60, "unit": "g", "range": [44, 60, 77]},
            "total_carbs": {"ideal": 260, "unit": "g", "range": [225, 260, 325]},
            "fiber": {"ideal": 30, "unit": "g", "range": [25, 30, 38]},
            "sugars": {"ideal": 25, "unit": "g", "range": [0, 25, 50]},
            "sodium": {"ideal": 1500, "unit": "mg", "range": [1500, 1900, 2300]},
            "calcium": {"ideal": 1000, "unit": "mg", "range": [800, 1000, 2000]},
            "vitamin_c": {"ideal": 90, "unit": "mg", "range": [100, 1000, 2000]},
            "vitamin_d": {"ideal": 15, "unit": "µg", "range": [15, 50, 100]},
        }

def calculate_nutrition_score(actual_intake: dict, goals: dict) -> int:
    if not goals or not actual_intake:
        return 0
    
    nutrients = ["calories", "protein", "total_fat", "total_carbs", "fiber", 
                 "sugars", "sodium", "calcium", "vitamin_c", "vitamin_d"]
    
    total_score = 0
    counted = 0
    
    for nutrient in nutrients:
        if nutrient not in goals:
            continue
        
        goal_data = goals[nutrient]
        goal_range = goal_data.get("range", [0, 0, 0])
        min_val, ideal_val, max_val = goal_range[0], goal_range[1], goal_range[2]
        
        actual = actual_intake.get(nutrient, 0)
        if not isinstance(actual, (int, float)):
            actual = 0
        
        counted += 1
        
        if min_val <= actual <= max_val:
            if actual <= ideal_val:
                if min_val == ideal_val:
                    ratio = 1.0
                else:
                    ratio = (actual - min_val) / (ideal_val - min_val)
                total_score += 8 + 2 * ratio
            else:
                if max_val == ideal_val:
                    ratio = 1.0
                else:
                    ratio = 1 - (actual - ideal_val) / (max_val - ideal_val)
                total_score += 8 + 2 * ratio
        elif actual < min_val:
            if min_val == 0:
                total_score += 0
            else:
                ratio = actual / min_val
                total_score += min(8 * ratio, 8)
        else:
            excess_ratio = (actual - max_val) / max_val if max_val > 0 else 1
            penalty = min(excess_ratio * 5, 8)
            total_score += max(8 - penalty, 0)
    
    if counted == 0:
        return 0
    
    return int(round(total_score * 10 / counted))

def calculate_sleep_score(duration_minutes: int, quality: str) -> str:
    if duration_minutes <= 0:
        return "F"
    
    hours = duration_minutes / 60
    quality_scores = {"excellent": 4, "good": 3, "fair": 2, "poor": 1}
    quality_score = quality_scores.get(quality, 2)
    
    if 7 <= hours <= 9:
        duration_score = 4
    elif 6 <= hours < 7 or 9 < hours <= 10:
        duration_score = 3
    elif 5 <= hours < 6:
        duration_score = 2
    elif 4 <= hours < 5:
        duration_score = 1
    else:
        duration_score = 0
    
    combined = (duration_score + quality_score) / 2
    
    if combined >= 3.5:
        return "A"
    elif combined >= 2.5:
        return "B"
    elif combined >= 1.5:
        return "C"
    elif combined >= 0.5:
        return "D"
    else:
        return "F"

def calculate_exercise_score(records: list, user_data: dict = None) -> int:
    if not records:
        return 0
    
    total_duration = sum(r.get("duration_minutes", 0) for r in records)
    total_calories = sum(r.get("calories", 0) for r in records)
    unique_types = set(r.get("type", "other") for r in records)
    
    if total_duration >= 30:
        duration_score = 50
    else:
        duration_score = int(50 * total_duration / 30)
    
    if total_calories >= 150:
        calories_score = 30
    else:
        calories_score = int(30 * total_calories / 150)
    
    if len(unique_types) >= 2:
        variety_score = 20
    elif len(unique_types) == 1:
        variety_score = 10
    else:
        variety_score = 0
    
    return min(duration_score + calories_score + variety_score, 100)

EXERCISE_METS = {
    "running": 9.8,
    "walking": 3.5,
    "cycling": 7.5,
    "swimming": 8.0,
    "yoga": 3.0,
    "strength": 6.0,
    "weightlifting": 6.0,
    "hiit": 12.0,
    "pilates": 3.0,
    "crossfit": 12.0,
    "elliptical": 5.0,
    "rowing": 7.0,
    "stair_climber": 9.0,
    "jump_rope": 10.0,
    "aerobics": 7.3,
    "calisthenics": 8.0,
    "basketball": 8.0,
    "football": 10.0,
    "badminton": 5.5,
    "tennis": 7.3,
    "volleyball": 4.0,
    "table_tennis": 4.0,
    "soccer": 10.0,
    "rugby": 10.0,
    "baseball": 5.0,
    "golf": 4.8,
    "bowling": 3.0,
    "dance": 5.0,
    "zumba": 6.5,
    "ballet": 6.0,
    "hiking": 6.0,
    "climbing": 8.0,
    "skiing": 7.0,
    "snowboarding": 5.0,
    "skating": 5.5,
    "surfing": 3.0,
    "kayaking": 5.0,
    "boxing": 12.0,
    "martial_arts": 10.0,
    "kickboxing": 10.0,
    "taekwondo": 10.0,
    "judo": 10.0,
    "other": 0.0
}

INTENSITY_FACTORS = {
    "low": 0.8,
    "medium": 1.0,
    "high": 1.2
}

def get_calories_for_exercise(exercise_type: str, duration_minutes: float, intensity: str, user_weight: float) -> int:
    met = EXERCISE_METS.get(exercise_type, 5.0)
    intensity_factor = INTENSITY_FACTORS.get(intensity, 1.0)
    duration_hours = duration_minutes / 60
    
    calories = met * user_weight * duration_hours * intensity_factor
    return int(round(calories))

def get_hourly_calories(exercise_type: str, intensity: str, user_weight: float) -> int:
    return get_calories_for_exercise(exercise_type, 60, intensity, user_weight)
