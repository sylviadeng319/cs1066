import pytest

from days import days_in_month


@pytest.mark.parametrize(
    ("month", "expected"),
    [
        (1, 31),
        (2, 28),
        (3, 31),
        (4, 30),
        (5, 31),
        (6, 30),
        (7, 31),
        (8, 31),
        (9, 30),
        (10, 31),
        (11, 30),
        (12, 31),
    ],
)
def test_days_in_month_regular_year(month, expected):
    assert days_in_month(month) == expected


def test_days_in_month_february_in_leap_year():
    assert days_in_month(2, leap_year=True) == 29


@pytest.mark.parametrize("month", [-1, 0, 13, "2", None, True])
def test_days_in_month_invalid_month(month):
    assert days_in_month(month) == "not valid"


@pytest.mark.parametrize("leap_year", [0, 1, "False", None])
def test_days_in_month_invalid_leap_year(leap_year):
    assert days_in_month(2, leap_year=leap_year) == "not valid"