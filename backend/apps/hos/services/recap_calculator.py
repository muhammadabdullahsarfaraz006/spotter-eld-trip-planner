"""
FMCSA 70-Hour / 8-Day Recap Calculator.
Calculates hours on duty today, cumulative hours over 7/8 days, and hours available tomorrow.
"""
from apps.common.constants import CYCLE_MAX_ON_DUTY_HOURS
from apps.hos.domain.daily_log import DailyRecap


class RecapCalculator:
    """Computes daily HOS recap entries following FMCSA instructions."""

    @classmethod
    def compute_recap(
        cls,
        on_duty_today: float,
        prior_cycle_used: float,
        restart_taken: bool = False
    ) -> DailyRecap:
        if restart_taken:
            # 34-hour restart resets the cycle
            total_last_7 = on_duty_today
            available_tomorrow = max(0.0, CYCLE_MAX_ON_DUTY_HOURS - total_last_7)
            total_last_8 = on_duty_today
        else:
            total_last_7 = prior_cycle_used + on_duty_today
            available_tomorrow = max(0.0, CYCLE_MAX_ON_DUTY_HOURS - total_last_7)
            total_last_8 = total_last_7  # In this trip span

        return DailyRecap(
            on_duty_today=round(on_duty_today, 2),
            hours_last_7_days_including_today=round(total_last_7, 2),
            hours_available_tomorrow=round(available_tomorrow, 2),
            hours_last_8_days_including_today=round(total_last_8, 2),
            restart_taken=restart_taken
        )
