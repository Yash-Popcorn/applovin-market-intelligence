def format_duration(seconds):
    seconds = int(seconds)
    
    if seconds < 60:
        return f"{seconds} seconds" if seconds != 1 else "1 second"
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    if remaining_seconds == 0:
        return f"{minutes} minutes" if minutes != 1 else "1 minute"
    
    minute_text = f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
    second_text = f"{remaining_seconds} second" if remaining_seconds == 1 else f"{remaining_seconds} seconds"
    
    return f"{minute_text} {second_text}"

