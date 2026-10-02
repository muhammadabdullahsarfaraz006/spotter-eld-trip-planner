"""
Log Segment domain entity.
Represents a continuous time slice in a specific duty status.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from .duty_status import DutyStatus


@dataclass
class LogSegment:
    start_time: datetime
    end_time: datetime
    duty_status: DutyStatus
    activity: str
    location_name: str
    remark: str
    miles_covered: float = 0.0

    @property
    def duration_hours(self) -> float:
        total_seconds = (self.end_time - self.start_time).total_seconds()
        return max(0.0, total_seconds / 3600.0)

    @property
    def start_hour_of_day(self) -> float:
        """Hour of day (0.0 to 24.0) for plotting on a 24-hour log grid."""
        return self.start_time.hour + (self.start_time.minute / 60.0) + (self.start_time.second / 3600.0)

    @property
    def end_hour_of_day(self) -> float:
        """Hour of day (0.0 to 24.0) for plotting on a 24-hour log grid."""
        if self.end_time.hour == 0 and self.end_time.minute == 0 and self.end_time.date() > self.start_time.date():
            return 24.0
        return self.end_time.hour + (self.end_time.minute / 60.0) + (self.end_time.second / 3600.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "start_hour": round(self.start_hour_of_day, 3),
            "end_hour": round(self.end_hour_of_day, 3),
            "duration_hours": round(self.duration_hours, 2),
            "duty_status": self.duty_status.value,
            "line_number": self.duty_status.line_number,
            "activity": self.activity,
            "location_name": self.location_name,
            "remark": self.remark,
            "miles_covered": round(self.miles_covered, 1),
        }
