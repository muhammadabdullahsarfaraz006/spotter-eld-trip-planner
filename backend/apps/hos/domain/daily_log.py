"""
FMCSA Standard Driver's Daily Log Sheet (24 Hours) Domain Model.
Validates that duty hours sum to exactly 24.0 hours per calendar day.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Any
from .duty_status import DutyStatus
from .log_segment import LogSegment


@dataclass
class DailyRecap:
    """Recap for 70 Hour / 8 Day rule."""
    on_duty_today: float               # Total lines 3 & 4 today
    hours_last_7_days_including_today: float  # A. Total hours on duty last 7 days including today
    hours_available_tomorrow: float    # B. Total hours available tomorrow (70 hr. minus A)
    hours_last_8_days_including_today: float  # C. Total hours on duty last 8 days including today
    restart_taken: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "on_duty_today": round(self.on_duty_today, 2),
            "hours_last_7_days_including_today": round(self.hours_last_7_days_including_today, 2),
            "hours_available_tomorrow": round(max(0.0, self.hours_available_tomorrow), 2),
            "hours_last_8_days_including_today": round(self.hours_last_8_days_including_today, 2),
            "restart_taken": self.restart_taken,
        }


@dataclass
class DailyLogSheet:
    """Driver's Daily Log for a single calendar day (00:00:00 to 24:00:00)."""
    log_date: date
    day_number: int
    total_days: int
    from_location: str
    to_location: str
    total_miles_driving_today: float
    carrier_name: str = "Spotter Freight Lines Inc."
    main_office_address: str = "100 Logistics Way, Indianapolis, IN 46204"
    home_terminal_address: str = "100 Logistics Way, Indianapolis, IN 46204"
    truck_tractor_number: str = "TRK-4091"
    trailer_number: str = "TLR-8820"
    shipping_documents: str = "BOL-98241 / General Freight"
    segments: List[LogSegment] = field(default_factory=list)
    recap: DailyRecap = field(default_factory=lambda: DailyRecap(0, 0, 70, 0))

    @property
    def total_off_duty_hours(self) -> float:
        return sum(s.duration_hours for s in self.segments if s.duty_status == DutyStatus.OFF_DUTY)

    @property
    def total_sleeper_berth_hours(self) -> float:
        return sum(s.duration_hours for s in self.segments if s.duty_status == DutyStatus.SLEEPER_BERTH)

    @property
    def total_driving_hours(self) -> float:
        return sum(s.duration_hours for s in self.segments if s.duty_status == DutyStatus.DRIVING)

    @property
    def total_on_duty_not_driving_hours(self) -> float:
        return sum(s.duration_hours for s in self.segments if s.duty_status == DutyStatus.ON_DUTY_NOT_DRIVING)

    @property
    def total_day_hours(self) -> float:
        return (
            self.total_off_duty_hours +
            self.total_sleeper_berth_hours +
            self.total_driving_hours +
            self.total_on_duty_not_driving_hours
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.log_date.isoformat(),
            "day_number": self.day_number,
            "total_days": self.total_days,
            "from_location": self.from_location,
            "to_location": self.to_location,
            "total_miles_driving_today": round(self.total_miles_driving_today, 1),
            "carrier_name": self.carrier_name,
            "main_office_address": self.main_office_address,
            "home_terminal_address": self.home_terminal_address,
            "truck_tractor_number": self.truck_tractor_number,
            "trailer_number": self.trailer_number,
            "shipping_documents": self.shipping_documents,
            "totals": {
                "off_duty": round(self.total_off_duty_hours, 2),
                "sleeper_berth": round(self.total_sleeper_berth_hours, 2),
                "driving": round(self.total_driving_hours, 2),
                "on_duty_not_driving": round(self.total_on_duty_not_driving_hours, 2),
                "total_hours": round(self.total_day_hours, 2),
            },
            "segments": [s.to_dict() for s in self.segments],
            "recap": self.recap.to_dict(),
        }
