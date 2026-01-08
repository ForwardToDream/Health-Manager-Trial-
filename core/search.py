import json
import os
import sqlite3
import glob

try:
    from pypinyin import pinyin, Style
    PYPINYIN_AVAILABLE = True
except ImportError:
    PYPINYIN_AVAILABLE = False


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUTRITION_DIR = os.path.join(BASE_DIR, "assests", "database", "nutrition")
CUSTOM_DATA_FILE = os.path.join(BASE_DIR, "data", "nutrition_data.json")

def _ensure_dir_exists():
    if not os.path.exists(NUTRITION_DIR):
        try:
            os.makedirs(NUTRITION_DIR)
        except OSError as e:
            pass

def _get_pinyin_initials(text):
    if not PYPINYIN_AVAILABLE or not text:
        return ""
    try:
        initials = pinyin(text, style=Style.FIRST_LETTER)
        return "".join([p[0] for p in initials]).lower()
    except Exception:
        return ""

def _get_full_pinyin(text):
    if not PYPINYIN_AVAILABLE or not text:
        return ""
    try:
        py = pinyin(text, style=Style.NORMAL)
        return "".join([p[0] for p in py]).lower()
    except Exception:
        return ""

def _fuzzy_match(query, food_name):
    query_lower = query.lower()
    name_lower = food_name.lower()
    
    if query_lower == name_lower:
        return 100
    
    if name_lower.startswith(query_lower):
        return 90
    
    if query_lower in name_lower:
        return 80
    
    if PYPINYIN_AVAILABLE and len(query) <= 10:
        initials = _get_pinyin_initials(food_name)
        if initials.startswith(query_lower):
            return 70
        if query_lower in initials:
            return 60
    
    if PYPINYIN_AVAILABLE and len(query) <= 20:
        full_py = _get_full_pinyin(food_name)
        if full_py.startswith(query_lower):
            return 50
        if query_lower in full_py:
            return 40
    
    return 0

def _parse_food_item(item):
    name = item.get("description", "Unknown Food")
    nutrients = item.get("foodNutrients", [])
    
    parsed_nutrients = {
        "calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0,
        "sugar": 0, "sodium": 0, "calcium": 0, "vitamin_c": 0, "vitamin_d": 0
    }
    
    for n in nutrients:
        nutrient_info = n.get("nutrient", {})
        n_id = nutrient_info.get("id")
        n_name = nutrient_info.get("name", "").lower()
        amount = n.get("amount", 0)
        
        if n_id == 1008: parsed_nutrients["calories"] = amount
        elif n_id == 1003: parsed_nutrients["protein"] = amount
        elif n_id == 1004: parsed_nutrients["fat"] = amount
        elif n_id == 1005: parsed_nutrients["carbs"] = amount
        elif n_id == 1079: parsed_nutrients["fiber"] = amount
        elif n_id == 2000: parsed_nutrients["sugar"] = amount
        elif n_id == 1093: parsed_nutrients["sodium"] = amount
        elif n_id == 1087: parsed_nutrients["calcium"] = amount
        elif n_id == 1162: parsed_nutrients["vitamin_c"] = amount
        elif n_id == 1114: parsed_nutrients["vitamin_d"] = amount

    portions = []
    for portion in item.get("foodPortions", []):
        unit_name = None
        
        if "portionDescription" in portion:
            unit_name = portion["portionDescription"]
        
        if not unit_name:
            measure_unit = portion.get("measureUnit", {})
            if isinstance(measure_unit, dict):
                unit_name = measure_unit.get("name")
            elif isinstance(measure_unit, str):
                unit_name = measure_unit
        
        if not unit_name or (isinstance(unit_name, str) and unit_name.lower() == "undetermined"):
            modifier = portion.get("modifier")
            if modifier:
                unit_name = modifier
        
        gram_weight = portion.get("gramWeight")
        amount = portion.get("amount", 1.0)
        
        if unit_name and gram_weight is not None and str(unit_name).lower() != "quantity not specified":
            if amount is not None and amount != 0 and amount != 1.0:
                try:
                    gram_weight = gram_weight / float(amount)
                except (ValueError, TypeError):
                    pass
            
            portions.append({"unit_name": str(unit_name), "gram_weight": gram_weight})

    if not any(p['unit_name'] == 'g' for p in portions):
        portions.insert(0, {"unit_name": "g", "gram_weight": 1})

    portions_json = json.dumps(portions)

    return (
        name,
        parsed_nutrients["calories"],
        parsed_nutrients["protein"],
        parsed_nutrients["fat"],
        parsed_nutrients["carbs"],
        parsed_nutrients["fiber"],
        parsed_nutrients["sugar"],
        parsed_nutrients["sodium"],
        parsed_nutrients["calcium"],
        parsed_nutrients["vitamin_c"],
        parsed_nutrients["vitamin_d"],
        portions_json
    )

def _create_db_from_json(json_file):
    base_name = os.path.splitext(os.path.basename(json_file))[0]
    db_file = os.path.join(NUTRITION_DIR, f"{base_name}.db")
    
    if os.path.exists(db_file):
        return

    
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                calories REAL DEFAULT 0,
                protein REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fiber REAL DEFAULT 0,
                sugar REAL DEFAULT 0,
                sodium REAL DEFAULT 0,
                calcium REAL DEFAULT 0,
                vitamin_c REAL DEFAULT 0,
                vitamin_d REAL DEFAULT 0,
                portions_json TEXT
            )
        ''')

        with open(json_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        items_to_process = []
        for key in ["FoundationFoods", "SRLegacyFoods", "BrandedFoods", "SurveyFoods", "foods"]:
            if key in raw_data:
                items_to_process = raw_data[key]
                break
        if not items_to_process and isinstance(raw_data, list):
            items_to_process = raw_data

        food_list = [_parse_food_item(item) for item in items_to_process]

        if food_list:
            cursor.executemany('''
                INSERT INTO foods (name, calories, protein, fat, carbs, fiber, sugar, sodium, calcium, vitamin_c, vitamin_d, portions_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', food_list)
            

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_food_name ON foods(name)')
        conn.commit()

    except Exception as e:
        if conn: conn.close()
        if os.path.exists(db_file): os.remove(db_file)
    finally:
        if conn: conn.close()

def _init_dbs():
    _ensure_dir_exists()
    json_files = glob.glob(os.path.join(NUTRITION_DIR, "*.json"))
    
    for json_file in json_files:
        _create_db_from_json(json_file)

def search_food(query, db_name=None):
    if not query:
        return []
    
    all_results = []
    found_names = set()
    scored_results = []

    try:
        if os.path.exists(CUSTOM_DATA_FILE):
            with open(CUSTOM_DATA_FILE, "r", encoding="utf-8") as f:
                custom_data = json.load(f)

            for item in custom_data:
                name = item.get("name", "")
                score = _fuzzy_match(query, name)
                if score > 0:
                    scored_results.append((score, item))
                    found_names.add(name.lower())
    except Exception as e:
        pass

    _init_dbs()

    db_files = glob.glob(os.path.join(NUTRITION_DIR, "*.db"))

    for db_file in db_files:
        try:
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            sql = "SELECT * FROM foods WHERE name LIKE ? LIMIT 500"
            cursor.execute(sql, (f'%{query}%',))
            
            rows = cursor.fetchall()
            
            for row in rows:
                name = row["name"]
                if name.lower() not in found_names:
                    score = _fuzzy_match(query, name)
                    if score > 0:
                        result_item = dict(row)
                        try:
                            result_item['portions'] = json.loads(row['portions_json']) if row['portions_json'] else []
                        except (json.JSONDecodeError, TypeError):
                            result_item['portions'] = []
                        del result_item['portions_json']
                        scored_results.append((score, result_item))
                        found_names.add(name.lower())
            
            if PYPINYIN_AVAILABLE and len(query) <= 6:
                cursor.execute("SELECT * FROM foods LIMIT 1000")
                all_rows = cursor.fetchall()
                
                for row in all_rows:
                    name = row["name"]
                    if name.lower() not in found_names:
                        score = _fuzzy_match(query, name)
                        if score > 0:
                            result_item = dict(row)
                            try:
                                result_item['portions'] = json.loads(row['portions_json']) if row['portions_json'] else []
                            except (json.JSONDecodeError, TypeError):
                                result_item['portions'] = []
                            del result_item['portions_json']
                            scored_results.append((score, result_item))
                            found_names.add(name.lower())
                
            conn.close()
            
            if len(scored_results) >= 100:
                break

        except Exception as e:
            pass
    
    scored_results.sort(key=lambda x: x[0], reverse=True)
    all_results = [item for score, item in scored_results[:100]]
    
    return all_results
