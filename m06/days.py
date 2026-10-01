### m06/days.py

def days_in_month(month, leap_year=False):
    if not isinstance(month, int) or isinstance(month, bool) or month < 1 or month > 12:
        return "not valid"

    if not isinstance(leap_year, bool):
        return "not valid"

    if month == 2:
        if leap_year:
            return 29
        return 28

    if month in [4, 6, 9, 11]:
        return 30

    return 31
