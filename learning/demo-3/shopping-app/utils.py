from datetime import datetime


def time_ago(dt):
    if not dt:
        return ""
    seconds = (datetime.utcnow() - dt).total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds/60)} mins ago"
    elif seconds < 86400:
        return f"{int(seconds/3600)} hours ago"
    else:
        return f"{int(seconds/86400)} days ago"
