"""
Date and time utilities.

This module provides utilities for date and time operations,
including formatting, parsing, and manipulation.
"""

from datetime import datetime, timedelta, date
from typing import Optional, Tuple
import calendar


def get_current_utc_datetime() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        Current datetime in UTC timezone
    """
    return datetime.utcnow()


def get_current_date() -> date:
    """
    Get current date.

    Returns:
        Current date
    """
    return date.today()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string.

    Args:
        dt: Datetime to format
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse datetime string.

    Args:
        dt_str: Datetime string to parse
        format_str: Format string

    Returns:
        Parsed datetime

    Raises:
        ValueError: If string cannot be parsed
    """
    return datetime.strptime(dt_str, format_str)


def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> date:
    """
    Parse date string.

    Args:
        date_str: Date string to parse
        format_str: Format string

    Returns:
        Parsed date

    Raises:
        ValueError: If string cannot be parsed
    """
    dt = datetime.strptime(date_str, format_str)
    return dt.date()


def add_days(dt: datetime, days: int) -> datetime:
    """
    Add days to datetime.

    Args:
        dt: Starting datetime
        days: Number of days to add

    Returns:
        New datetime with days added
    """
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """
    Add hours to datetime.

    Args:
        dt: Starting datetime
        hours: Number of hours to add

    Returns:
        New datetime with hours added
    """
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """
    Add minutes to datetime.

    Args:
        dt: Starting datetime
        minutes: Number of minutes to add

    Returns:
        New datetime with minutes added
    """
    return dt + timedelta(minutes=minutes)


def get_days_between(start_date: date, end_date: date) -> int:
    """
    Get number of days between two dates.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Number of days between dates
    """
    return (end_date - start_date).days


def get_age(birth_date: date, reference_date: Optional[date] = None) -> int:
    """
    Calculate age in years.

    Args:
        birth_date: Date of birth
        reference_date: Reference date; defaults to today

    Returns:
        Age in years
    """
    if reference_date is None:
        reference_date = get_current_date()

    age = reference_date.year - birth_date.year
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def get_month_name(month: int, short: bool = False) -> str:
    """
    Get month name from number.

    Args:
        month: Month number (1-12)
        short: If True, return short name (Jan), else full name (January)

    Returns:
        Month name
    """
    if short:
        return calendar.month_abbr[month]
    else:
        return calendar.month_name[month]


def is_leap_year(year: int) -> bool:
    """
    Check if year is a leap year.

    Args:
        year: Year to check

    Returns:
        True if leap year, False otherwise
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def get_days_in_month(year: int, month: int) -> int:
    """
    Get number of days in a month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        Number of days in month
    """
    return calendar.monthrange(year, month)[1]


def get_fiscal_year(dt: datetime, start_month: int = 1) -> Tuple[int, int]:
    """
    Get fiscal year for a datetime.

    Args:
        dt: Datetime
        start_month: Month when fiscal year starts (1-12)

    Returns:
        Tuple of (fiscal_year_start, fiscal_year_end)
    """
    if dt.month >= start_month:
        return dt.year, dt.year + 1
    else:
        return dt.year - 1, dt.year


def is_business_day(dt: date) -> bool:
    """
    Check if date is a business day (Mon-Fri).

    Args:
        dt: Date to check

    Returns:
        True if business day, False otherwise
    """
    return dt.weekday() < 5  # 0-4 are Mon-Fri, 5-6 are Sat-Sun


def get_next_business_day(dt: date) -> date:
    """
    Get next business day.

    Args:
        dt: Starting date

    Returns:
        Next business day
    """
    next_day = dt + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    return next_day


def is_holiday(dt: date, holidays: list = None) -> bool:
    """
    Check if date is a holiday.

    Args:
        dt: Date to check
        holidays: List of holiday dates; defaults to India holidays

    Returns:
        True if holiday, False otherwise
    """
    # TODO: Implement with actual holiday list
    # For now, just return False
    return False


# TODO: Add more date utilities
# - Timezone conversions
# - Business day calculations
# - Working hours calculations
# - Date range utilities
