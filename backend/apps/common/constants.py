"""
Domain constants for Hours of Service (HOS) and Commercial Motor Vehicle (CMV) trip planning.
Based on FMCSA 49 CFR Part 395 rules for property-carrying drivers.
"""

# HOS Rules Constants (70-Hour / 8-Day Rule for Property-Carrying Drivers)
MAX_DRIVING_HOURS_PER_SHIFT = 11.0          # Max driving hours after 10 consecutive hours off
MAX_DUTY_WINDOW_HOURS = 14.0                # 14 consecutive hour duty window once coming on duty
MANDATORY_OFF_DUTY_HOURS = 10.0             # Minimum consecutive hours off duty / sleeper berth to reset 11h/14h
REST_BREAK_DRIVING_THRESHOLD = 8.0          # Driving not permitted after 8 cumulative hours without break
MANDATORY_REST_BREAK_HOURS = 0.5            # 30-minute mandatory rest break
CYCLE_MAX_ON_DUTY_HOURS = 70.0              # 70 hours in 8 consecutive days
CYCLE_DAYS = 8
CYCLE_RESTART_OFF_DUTY_HOURS = 34.0         # 34 consecutive hours off duty for full cycle restart

# Operational Rules
MAX_FUEL_INTERVAL_MILES = 1000.0            # Fueling required at least once every 1,000 miles
FUEL_STOP_DURATION_HOURS = 0.5              # 30 minutes On-Duty (not driving) for fueling
PICKUP_DURATION_HOURS = 1.0                 # 1 hour On-Duty (not driving) for pickup
DROPOFF_DURATION_HOURS = 1.0                # 1 hour On-Duty (not driving) for drop-off
PRE_TRIP_INSPECTION_HOURS = 0.25            # 15 minutes On-Duty (not driving) pre-trip inspection
POST_TRIP_INSPECTION_HOURS = 0.25           # 15 minutes On-Duty (not driving) post-trip inspection

# Fallback Routing / Speed Estimates
DEFAULT_AVERAGE_SPEED_MPH = 55.0            # Realistic average CMV highway speed with traffic/grades
HOURS_PER_DAY = 24.0
MINUTES_PER_HOUR = 60
QUARTER_HOUR_MINUTES = 15
METERS_PER_MILE = 1609.344
MILES_PER_METER = 1.0 / METERS_PER_MILE
KM_PER_MILE = 1.609344
MILES_PER_KM = 0.621371
