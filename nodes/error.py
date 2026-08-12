def error(state):
    state["error_history"].append(state["error"])
    state["retry_count"] += 1
    return state