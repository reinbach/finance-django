import datetime
from finance.core.utils import get_year_choices


class TestGetYearChoices():
    def test_default(self):
        choices = get_year_choices()
        current_year = datetime.date.today().year
        assert choices == [
            (current_year - 2, current_year - 2),
            (current_year - 1, current_year - 1),
            (current_year, current_year),
        ]

    def test_with_blank(self):
        choices = get_year_choices(True)
        current_year = datetime.date.today().year
        assert choices == [
            ("", "-" * 9),
            (current_year - 2, current_year - 2),
            (current_year - 1, current_year - 1),
            (current_year, current_year),
        ]
