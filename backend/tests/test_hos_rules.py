"""
Unit tests for Hours of Service (HOS) domain rules and compliance engine.
"""
from datetime import datetime, timedelta
import pytest
from apps.hos.domain.duty_status import DutyStatus
from apps.hos.domain.log_segment import LogSegment
from apps.hos.domain.hos_rules import HOSRuleEngine


def test_no_violations_on_compliant_shift():
    base_time = datetime(2026, 10, 1, 6, 0, 0)
    segments = [
        # 15 min pre-trip inspection
        LogSegment(base_time, base_time + timedelta(minutes=15), DutyStatus.ON_DUTY_NOT_DRIVING, "Pre-trip", "Origin", "Inspection"),
        # 5 hours driving
        LogSegment(base_time + timedelta(minutes=15), base_time + timedelta(hours=5, minutes=15), DutyStatus.DRIVING, "Driving", "En route", "Driving"),
        # 30 min rest break
        LogSegment(base_time + timedelta(hours=5, minutes=15), base_time + timedelta(hours=5, minutes=45), DutyStatus.OFF_DUTY, "Rest", "Rest Area", "Break"),
        # 5 hours driving
        LogSegment(base_time + timedelta(hours=5, minutes=45), base_time + timedelta(hours=10, minutes=45), DutyStatus.DRIVING, "Driving", "En route", "Driving"),
        # 10 hours sleeper berth
        LogSegment(base_time + timedelta(hours=10, minutes=45), base_time + timedelta(hours=20, minutes=45), DutyStatus.SLEEPER_BERTH, "Sleeper", "Truck Stop", "Rest"),
    ]

    violations = HOSRuleEngine.check_compliance(segments, initial_cycle_used=10.0)
    assert len(violations) == 0


def test_11_hour_driving_limit_exceeded():
    base_time = datetime(2026, 10, 1, 6, 0, 0)
    segments = [
        LogSegment(base_time, base_time + timedelta(hours=12), DutyStatus.DRIVING, "Driving", "En route", "Overdriving"),
    ]

    violations = HOSRuleEngine.check_compliance(segments, initial_cycle_used=0.0)
    violation_types = [v.violation_type for v in violations]
    assert "11_HOUR_DRIVING_LIMIT_EXCEEDED" in violation_types


def test_30_min_break_required_after_8h_driving():
    base_time = datetime(2026, 10, 1, 6, 0, 0)
    segments = [
        LogSegment(base_time, base_time + timedelta(hours=8, minutes=30), DutyStatus.DRIVING, "Driving", "En route", "No break"),
    ]

    violations = HOSRuleEngine.check_compliance(segments, initial_cycle_used=0.0)
    violation_types = [v.violation_type for v in violations]
    assert "30_MIN_BREAK_REQUIRED" in violation_types


def test_70_hour_cycle_limit_exceeded():
    base_time = datetime(2026, 10, 1, 6, 0, 0)
    segments = [
        LogSegment(base_time, base_time + timedelta(hours=5), DutyStatus.DRIVING, "Driving", "En route", "Driving"),
    ]

    # Initial cycle was already 68 hours -> 68 + 5 = 73 hours (violates 70h)
    violations = HOSRuleEngine.check_compliance(segments, initial_cycle_used=68.0)
    violation_types = [v.violation_type for v in violations]
    assert "70_HOUR_LIMIT_EXCEEDED" in violation_types
