"""
Hours of Service (HOS) Duty Status classifications according to FMCSA regulations.
Matches the 4 lines on the official Driver's Daily Log:
Line 1: Off Duty
Line 2: Sleeper Berth
Line 3: Driving
Line 4: On Duty (not driving)
"""
from enum import Enum


class DutyStatus(str, Enum):
    OFF_DUTY = "OFF_DUTY"
    SLEEPER_BERTH = "SLEEPER_BERTH"
    DRIVING = "DRIVING"
    ON_DUTY_NOT_DRIVING = "ON_DUTY_NOT_DRIVING"

    @property
    def line_number(self) -> int:
        """Line number on standard FMCSA paper log sheet (1-4)."""
        mapping = {
            DutyStatus.OFF_DUTY: 1,
            DutyStatus.SLEEPER_BERTH: 2,
            DutyStatus.DRIVING: 3,
            DutyStatus.ON_DUTY_NOT_DRIVING: 4,
        }
        return mapping[self]

    @property
    def display_name(self) -> str:
        mapping = {
            DutyStatus.OFF_DUTY: "1. Off Duty",
            DutyStatus.SLEEPER_BERTH: "2. Sleeper Berth",
            DutyStatus.DRIVING: "3. Driving",
            DutyStatus.ON_DUTY_NOT_DRIVING: "4. On Duty (not driving)",
        }
        return mapping[self]

    @property
    def is_on_duty(self) -> bool:
        """Whether this status counts towards the 70-hour / 8-day cumulative duty limit."""
        return self in (DutyStatus.DRIVING, DutyStatus.ON_DUTY_NOT_DRIVING)
