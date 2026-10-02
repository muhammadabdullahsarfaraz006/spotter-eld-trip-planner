"""
FMCSA Hours of Service (HOS) rules and compliance checks.
Accurately tracks consecutive off-duty / sleeper periods even across midnight boundaries.
"""
from dataclasses import dataclass
from typing import List
from apps.common.constants import (
    MAX_DRIVING_HOURS_PER_SHIFT,
    MAX_DUTY_WINDOW_HOURS,
    MANDATORY_OFF_DUTY_HOURS,
    REST_BREAK_DRIVING_THRESHOLD,
    MANDATORY_REST_BREAK_HOURS,
    CYCLE_MAX_ON_DUTY_HOURS,
)
from .duty_status import DutyStatus
from .log_segment import LogSegment


@dataclass
class HOSViolation:
    violation_type: str
    description: str
    occurred_at: str
    severity: str = "ERROR"


class HOSRuleEngine:
    """Validates log segments against FMCSA 70-hour / 8-day property-carrying rules."""

    @classmethod
    def check_compliance(
        cls,
        segments: List[LogSegment],
        initial_cycle_used: float = 0.0
    ) -> List[HOSViolation]:
        violations: List[HOSViolation] = []

        cumulative_cycle = initial_cycle_used
        driving_since_rest = 0.0
        shift_driving_hours = 0.0
        shift_duty_window = 0.0
        consecutive_off_duty = 0.0
        in_shift = False

        for segment in segments:
            duration = segment.duration_hours

            if segment.duty_status in (DutyStatus.OFF_DUTY, DutyStatus.SLEEPER_BERTH):
                consecutive_off_duty += duration

                # 30-minute qualifying rest break resets the 8-hour driving clock
                if consecutive_off_duty >= (MANDATORY_REST_BREAK_HOURS - 0.01):
                    driving_since_rest = 0.0

                # 10 consecutive hours off duty or sleeper resets the shift (11h / 14h clocks)
                if consecutive_off_duty >= (MANDATORY_OFF_DUTY_HOURS - 0.01):
                    shift_driving_hours = 0.0
                    shift_duty_window = 0.0
                    driving_since_rest = 0.0
                    in_shift = False
                continue

            # Driver is On Duty (Driving or On Duty Not Driving)
            consecutive_off_duty = 0.0
            in_shift = True
            cumulative_cycle += duration

            if cumulative_cycle > CYCLE_MAX_ON_DUTY_HOURS + 0.01:
                violations.append(HOSViolation(
                    violation_type="70_HOUR_LIMIT_EXCEEDED",
                    description=f"Driver exceeded 70-hour on-duty limit ({cumulative_cycle:.1f} hrs cumulative).",
                    occurred_at=segment.start_time.isoformat(),
                ))

            shift_duty_window += duration
            if shift_duty_window > MAX_DUTY_WINDOW_HOURS + 0.01 and segment.duty_status == DutyStatus.DRIVING:
                violations.append(HOSViolation(
                    violation_type="14_HOUR_WINDOW_EXCEEDED",
                    description=f"Driving occurred after the 14th consecutive hour ({shift_duty_window:.1f}h) of coming on duty.",
                    occurred_at=segment.start_time.isoformat(),
                ))

            if segment.duty_status == DutyStatus.DRIVING:
                shift_driving_hours += duration
                driving_since_rest += duration

                if shift_driving_hours > MAX_DRIVING_HOURS_PER_SHIFT + 0.01:
                    violations.append(HOSViolation(
                        violation_type="11_HOUR_DRIVING_LIMIT_EXCEEDED",
                        description=f"Driver exceeded 11-hour driving limit in a shift ({shift_driving_hours:.1f} hrs).",
                        occurred_at=segment.start_time.isoformat(),
                    ))

                if driving_since_rest > REST_BREAK_DRIVING_THRESHOLD + 0.01:
                    violations.append(HOSViolation(
                        violation_type="30_MIN_BREAK_REQUIRED",
                        description=f"Driver drove {driving_since_rest:.1f} hours without a qualifying 30-minute rest break.",
                        occurred_at=segment.start_time.isoformat(),
                    ))

        return violations
