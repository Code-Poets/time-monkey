import datetime


def format_timedelta_to_hours_and_minutes_only(timedelta: datetime.timedelta) -> str:
    minutes = (timedelta.seconds + timedelta.days * 86400) // 60
    hours, minutes = divmod(minutes, 60)
    return "{:d}:{:02d}".format(hours, minutes)
