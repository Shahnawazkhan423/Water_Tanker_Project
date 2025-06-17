import math
from datetime import datetime
from django.utils.timesince import timesince
from dateutil.relativedelta import relativedelta

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c



def human_readable_joined_date(joined_date):
    now = datetime.now(joined_date.tzinfo)
    diff = relativedelta(now, joined_date)

    if diff.years > 0 and diff.months >= 6:
        return f"{diff.years + 0.5:.1f} years ago"
    elif diff.years > 0:
        return f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
    elif diff.months > 0:
        return f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    else:
        return "Today"