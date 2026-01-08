_subscribers = {}

USER_DATA_SAVED = "user_data_saved"
WATER_ADDED = "water_added"
LANGUAGE_CHANGED = "language_changed"
SLEEP_ADDED = "sleep_added"
EXERCISE_ADDED = "exercise_added"

def subscribe(event_type: str, callback):
    if event_type not in _subscribers:
        _subscribers[event_type] = []
    _subscribers[event_type].append(callback)

def unsubscribe(event_type: str, callback):
    if event_type in _subscribers:
        try:
            _subscribers[event_type].remove(callback)
        except ValueError:
            pass

def publish(event_type: str, *args, **kwargs):
    if event_type not in _subscribers:
        return

    for callback in list(_subscribers[event_type]):
        try:
            callback(*args, **kwargs)
        except Exception:
            pass
