
from datetime import datetime, date

def get_half_hour_period_id(dt: datetime) -> int:
    
    return dt.hour * 2 + (1 if dt.minute >= 30 else 0)

def get_day_period_key(dt: datetime) -> tuple:
    
    return (dt.date().isoformat(), get_half_hour_period_id(dt))

def should_trigger_reminder(last_drink_time: datetime = None) -> bool:
    
    now = datetime.now()
    

    if last_drink_time is None:
        return True
    

    current_key = get_day_period_key(now)
    last_drink_key = get_day_period_key(last_drink_time)
    

    return current_key != last_drink_key

def is_reminder_time(dt: datetime) -> bool:
    
    return dt.minute in [0, 30]
