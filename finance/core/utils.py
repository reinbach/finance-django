import datetime


def get_year_choices(blank=False):
    current_year = datetime.date.today().year
    choices = [(x, x) for x in range(current_year - 2,
                                     current_year + 1)]
    if blank:
        choices = [("", "-" * 9)] + choices
    return choices
