# state_manager.py
active_states = {}

def init_player_state(user_id):
    active_states[user_id] = {
        "message_id": None,
        "attempts": [],
        "hints": []
    }

def get_state(user_id):
    return active_states.get(user_id)

def set_message_id(user_id, msg_id):
    if user_id in active_states:
        active_states[user_id]["message_id"] = msg_id

def add_attempt(user_id, answer):
    if user_id in active_states:
        active_states[user_id]["attempts"].append(answer)

def add_hint(user_id, hint_index):
    if user_id in active_states:
        active_states[user_id]["hints"].append(hint_index)
