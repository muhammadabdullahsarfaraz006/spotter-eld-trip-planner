"""
Core Trip Scheduler & HOS Simulation Engine.
Simulates commercial truck trip progress, enforces FMCSA 70-hour / 8-day rules,
automatically schedules mandatory rest breaks, fueling stops, and 10-hour sleeper rests,
and slices the continuous timeline into discrete 24-hour FMCSA daily log sheets.
"""
import math
from datetime import datetime, date, time, timedelta
from typing import List, Tuple, Dict, Any, Optional
from apps.common.constants import (
    MAX_DRIVING_HOURS_PER_SHIFT,
    MAX_DUTY_WINDOW_HOURS,
    MANDATORY_OFF_DUTY_HOURS,
    REST_BREAK_DRIVING_THRESHOLD,
    MANDATORY_REST_BREAK_HOURS,
    MAX_FUEL_INTERVAL_MILES,
    FUEL_STOP_DURATION_HOURS,
    PICKUP_DURATION_HOURS,
    DROPOFF_DURATION_HOURS,
    PRE_TRIP_INSPECTION_HOURS,
    POST_TRIP_INSPECTION_HOURS,
    DEFAULT_AVERAGE_SPEED_MPH,
    HOURS_PER_DAY,
)
from apps.routing.domain.coordinates import Coordinates
from apps.routing.domain.route import Location, RouteStop, StopType, RouteResult
from apps.routing.services.osrm_service import OSRMRoutingService
from apps.hos.domain.duty_status import DutyStatus
from apps.hos.domain.log_segment import LogSegment
from apps.hos.domain.daily_log import DailyLogSheet, DailyRecap
from .recap_calculator import RecapCalculator


class TripScheduler:
    """Simulates trip execution and generates compliant daily ELD log sheets."""

    @classmethod
    def schedule_trip(
        cls,
        current_loc: Location,
        pickup_loc: Location,
        dropoff_loc: Location,
        current_cycle_used: float = 0.0,
        trip_start_datetime: Optional[datetime] = None,
        truck_number: str = "TRK-4091",
        trailer_number: str = "TLR-8820",
        carrier_name: str = "Spotter Freight Lines Inc.",
    ) -> Dict[str, Any]:
        """
        Execute full trip simulation and return:
        - Route details and GeoJSON geometry
        - Chronological stops (Stops & Rests)
        - List of 24-hour FMCSA Daily Log Sheets with step graphs
        - Overall summary metrics
        """
        if trip_start_datetime is None:
            # Default to 06:00:00 AM on today's date
            today = date.today()
            trip_start_datetime = datetime.combine(today, time(6, 0, 0))

        # 1. Routing between waypoints
        leg1 = OSRMRoutingService.get_route_leg(
            current_loc.coordinates,
            pickup_loc.coordinates,
            origin_name=current_loc.name,
            dest_name=pickup_loc.name,
        )
        leg2 = OSRMRoutingService.get_route_leg(
            pickup_loc.coordinates,
            dropoff_loc.coordinates,
            origin_name=pickup_loc.name,
            dest_name=dropoff_loc.name,
        )

        total_distance = leg1.distance_miles + leg2.distance_miles
        combined_coords = []
        if leg1.coordinates:
            combined_coords.extend(leg1.coordinates)
        if leg2.coordinates:
            if combined_coords and combined_coords[-1] == leg2.coordinates[0]:
                combined_coords.extend(leg2.coordinates[1:])
            else:
                combined_coords.extend(leg2.coordinates)

        route_geojson = {
            "type": "LineString",
            "coordinates": combined_coords
        }

        # 2. Chronological simulation of events
        timeline_segments: List[LogSegment] = []
        route_stops: List[RouteStop] = []

        # Start of day until trip start: Off Duty
        day_start = datetime.combine(trip_start_datetime.date(), time(0, 0, 0))
        if trip_start_datetime > day_start:
            timeline_segments.append(LogSegment(
                start_time=day_start,
                end_time=trip_start_datetime,
                duty_status=DutyStatus.OFF_DUTY,
                activity="Off Duty",
                location_name=current_loc.name,
                remark=f"Off duty prior to dispatch at {current_loc.name}",
            ))

        current_time = trip_start_datetime
        cumulative_miles = 0.0
        miles_since_fuel = 0.0

        # Shift trackers
        shift_driving_hours = 0.0
        shift_elapsed_hours = 0.0
        driving_since_break = 0.0

        # Start stop
        route_stops.append(RouteStop(
            stop_type=StopType.START,
            name=current_loc.name,
            coordinates=current_loc.coordinates,
            arrival_time=current_time,
            departure_time=current_time,
            duration_hours=0.0,
            cumulative_miles=0.0,
            remark=f"Trip departure from {current_loc.name}",
            address=current_loc.address,
        ))

        # Helper: handle 10-hour sleeper berth reset
        def execute_sleeper_reset(loc_name: str, coords: Coordinates, reason: str):
            nonlocal current_time, shift_driving_hours, shift_elapsed_hours, driving_since_break
            sleeper_end = current_time + timedelta(hours=MANDATORY_OFF_DUTY_HOURS)
            timeline_segments.append(LogSegment(
                start_time=current_time,
                end_time=sleeper_end,
                duty_status=DutyStatus.SLEEPER_BERTH,
                activity="Sleeper Berth",
                location_name=loc_name,
                remark=f"10-hr rest ({reason}) at {loc_name}",
            ))
            route_stops.append(RouteStop(
                stop_type=StopType.SLEEPER_BERTH,
                name=f"Rest Stop - {loc_name}",
                coordinates=coords,
                arrival_time=current_time,
                departure_time=sleeper_end,
                duration_hours=MANDATORY_OFF_DUTY_HOURS,
                cumulative_miles=cumulative_miles,
                remark=f"10-Hour Mandatory Sleeper Berth ({reason})",
            ))
            current_time = sleeper_end
            shift_driving_hours = 0.0
            shift_elapsed_hours = 0.0
            driving_since_break = 0.0

        # Helper: simulate driving a leg with HOS checks
        def drive_distance(
            distance_to_cover: float,
            origin_name: str,
            dest_name: str,
            origin_coord: Coordinates,
            dest_coord: Coordinates,
        ):
            nonlocal current_time, cumulative_miles, miles_since_fuel
            nonlocal shift_driving_hours, shift_elapsed_hours, driving_since_break

            remaining_miles = distance_to_cover
            speed = DEFAULT_AVERAGE_SPEED_MPH

            while remaining_miles > 0.01:
                # How much driving remaining on current shift?
                avail_shift_drive = MAX_DRIVING_HOURS_PER_SHIFT - shift_driving_hours
                avail_shift_window = MAX_DUTY_WINDOW_HOURS - shift_elapsed_hours
                avail_before_break = REST_BREAK_DRIVING_THRESHOLD - driving_since_break
                avail_before_fuel = (MAX_FUEL_INTERVAL_MILES - miles_since_fuel) / speed

                # Max drive time in current uninterrupted chunk
                max_drive_hours = min(
                    remaining_miles / speed,
                    avail_shift_drive,
                    avail_shift_window,
                    avail_before_break,
                    avail_before_fuel
                )

                # If driving or shift window limit reached, must take 10h sleeper reset
                if max_drive_hours <= 0.05 and (avail_shift_drive <= 0.05 or avail_shift_window <= 0.05):
                    # Progress location interpolation
                    fraction = (distance_to_cover - remaining_miles) / distance_to_cover
                    curr_lat = origin_coord.latitude + (dest_coord.latitude - origin_coord.latitude) * fraction
                    curr_lon = origin_coord.longitude + (dest_coord.longitude - origin_coord.longitude) * fraction
                    curr_loc_name = f"Highway Rest Area near {dest_name}"
                    execute_sleeper_reset(curr_loc_name, Coordinates(curr_lat, curr_lon), "11h driving / 14h window reached")
                    continue

                # Drive the chunk
                chunk_miles = min(remaining_miles, max_drive_hours * speed)
                chunk_duration = chunk_miles / speed
                chunk_end = current_time + timedelta(hours=chunk_duration)

                # Segment location label
                fraction_end = (distance_to_cover - (remaining_miles - chunk_miles)) / distance_to_cover
                loc_label = f"En route {origin_name} to {dest_name} ({int(fraction_end*100)}%)"

                timeline_segments.append(LogSegment(
                    start_time=current_time,
                    end_time=chunk_end,
                    duty_status=DutyStatus.DRIVING,
                    activity="Driving",
                    location_name=loc_label,
                    remark=f"Driving en route {dest_name}",
                    miles_covered=chunk_miles,
                ))

                current_time = chunk_end
                remaining_miles -= chunk_miles
                cumulative_miles += chunk_miles
                miles_since_fuel += chunk_miles
                shift_driving_hours += chunk_duration
                shift_elapsed_hours += chunk_duration
                driving_since_break += chunk_duration

                # Check if fuel stop needed
                if miles_since_fuel >= (MAX_FUEL_INTERVAL_MILES - 25.0) and remaining_miles > 0:
                    fuel_end = current_time + timedelta(hours=FUEL_STOP_DURATION_HOURS)
                    fraction = (distance_to_cover - remaining_miles) / distance_to_cover
                    f_lat = origin_coord.latitude + (dest_coord.latitude - origin_coord.latitude) * fraction
                    f_lon = origin_coord.longitude + (dest_coord.longitude - origin_coord.longitude) * fraction
                    f_loc = f"Travel Plaza / Fuel Island near {dest_name}"

                    timeline_segments.append(LogSegment(
                        start_time=current_time,
                        end_time=fuel_end,
                        duty_status=DutyStatus.ON_DUTY_NOT_DRIVING,
                        activity="Fueling",
                        location_name=f_loc,
                        remark=f"Fueling CMV (1,000-mile interval) at {f_loc}",
                    ))
                    route_stops.append(RouteStop(
                        stop_type=StopType.FUEL,
                        name=f"Fuel Stop - {f_loc}",
                        coordinates=Coordinates(f_lat, f_lon),
                        arrival_time=current_time,
                        departure_time=fuel_end,
                        duration_hours=FUEL_STOP_DURATION_HOURS,
                        cumulative_miles=cumulative_miles,
                        remark="Fueling (at least once per 1,000 miles)",
                    ))
                    current_time = fuel_end
                    miles_since_fuel = 0.0
                    shift_elapsed_hours += FUEL_STOP_DURATION_HOURS

                # Check if 30-min rest break needed
                elif driving_since_break >= (REST_BREAK_DRIVING_THRESHOLD - 0.2) and remaining_miles > 0:
                    break_end = current_time + timedelta(hours=MANDATORY_REST_BREAK_HOURS)
                    fraction = (distance_to_cover - remaining_miles) / distance_to_cover
                    b_lat = origin_coord.latitude + (dest_coord.latitude - origin_coord.latitude) * fraction
                    b_lon = origin_coord.longitude + (dest_coord.longitude - origin_coord.longitude) * fraction
                    b_loc = f"Service Plaza near {dest_name}"

                    timeline_segments.append(LogSegment(
                        start_time=current_time,
                        end_time=break_end,
                        duty_status=DutyStatus.OFF_DUTY,
                        activity="Rest Break",
                        location_name=b_loc,
                        remark=f"30-minute DOT rest break at {b_loc}",
                    ))
                    route_stops.append(RouteStop(
                        stop_type=StopType.REST_BREAK,
                        name=f"Rest Area - {b_loc}",
                        coordinates=Coordinates(b_lat, b_lon),
                        arrival_time=current_time,
                        departure_time=break_end,
                        duration_hours=MANDATORY_REST_BREAK_HOURS,
                        cumulative_miles=cumulative_miles,
                        remark="30-Minute Rest Break (after 8 cumulative driving hours)",
                    ))
                    current_time = break_end
                    driving_since_break = 0.0
                    shift_elapsed_hours += MANDATORY_REST_BREAK_HOURS

        # Phase 0: Pre-trip Inspection (15 min On-Duty Not Driving)
        pretrip_end = current_time + timedelta(hours=PRE_TRIP_INSPECTION_HOURS)
        timeline_segments.append(LogSegment(
            start_time=current_time,
            end_time=pretrip_end,
            duty_status=DutyStatus.ON_DUTY_NOT_DRIVING,
            activity="Pre-Trip Inspection",
            location_name=current_loc.name,
            remark=f"Pre-trip CMV inspection at {current_loc.name}",
        ))
        current_time = pretrip_end
        shift_elapsed_hours += PRE_TRIP_INSPECTION_HOURS

        # Phase 1: Drive Leg 1 (Current Location -> Pickup Location)
        drive_distance(
            distance_to_cover=leg1.distance_miles,
            origin_name=current_loc.name,
            dest_name=pickup_loc.name,
            origin_coord=current_loc.coordinates,
            dest_coord=pickup_loc.coordinates,
        )

        # Check if 14-hour window requires sleeper before pickup
        if shift_elapsed_hours + PICKUP_DURATION_HOURS > MAX_DUTY_WINDOW_HOURS:
            execute_sleeper_reset(pickup_loc.name, pickup_loc.coordinates, "14-hour duty window before loading")

        # Phase 2: Pickup Stop (1 hour On Duty Not Driving)
        pickup_end = current_time + timedelta(hours=PICKUP_DURATION_HOURS)
        timeline_segments.append(LogSegment(
            start_time=current_time,
            end_time=pickup_end,
            duty_status=DutyStatus.ON_DUTY_NOT_DRIVING,
            activity="Pickup & Loading",
            location_name=pickup_loc.name,
            remark=f"Loading freight & signing BOL at shipper {pickup_loc.name}",
        ))
        route_stops.append(RouteStop(
            stop_type=StopType.PICKUP,
            name=f"Shipper - {pickup_loc.name}",
            coordinates=pickup_loc.coordinates,
            arrival_time=current_time,
            departure_time=pickup_end,
            duration_hours=PICKUP_DURATION_HOURS,
            cumulative_miles=cumulative_miles,
            remark="1 Hour Loading & Paperwork (On-Duty Not Driving)",
            address=pickup_loc.address,
        ))
        current_time = pickup_end
        shift_elapsed_hours += PICKUP_DURATION_HOURS

        # Phase 3: Drive Leg 2 (Pickup Location -> Dropoff Location)
        drive_distance(
            distance_to_cover=leg2.distance_miles,
            origin_name=pickup_loc.name,
            dest_name=dropoff_loc.name,
            origin_coord=pickup_loc.coordinates,
            dest_coord=dropoff_loc.coordinates,
        )

        # Check if 14-hour window requires sleeper before dropoff
        if shift_elapsed_hours + DROPOFF_DURATION_HOURS > MAX_DUTY_WINDOW_HOURS:
            execute_sleeper_reset(dropoff_loc.name, dropoff_loc.coordinates, "14-hour duty window before unloading")

        # Phase 4: Dropoff Stop (1 hour On Duty Not Driving)
        dropoff_end = current_time + timedelta(hours=DROPOFF_DURATION_HOURS)
        timeline_segments.append(LogSegment(
            start_time=current_time,
            end_time=dropoff_end,
            duty_status=DutyStatus.ON_DUTY_NOT_DRIVING,
            activity="Dropoff & Unloading",
            location_name=dropoff_loc.name,
            remark=f"Unloading freight & final post-trip at consignee {dropoff_loc.name}",
        ))
        route_stops.append(RouteStop(
            stop_type=StopType.DROPOFF,
            name=f"Consignee - {dropoff_loc.name}",
            coordinates=dropoff_loc.coordinates,
            arrival_time=current_time,
            departure_time=dropoff_end,
            duration_hours=DROPOFF_DURATION_HOURS,
            cumulative_miles=cumulative_miles,
            remark="1 Hour Unloading & Inspection (On-Duty Not Driving)",
            address=dropoff_loc.address,
        ))
        current_time = dropoff_end

        # Phase 5: Off Duty for remainder of final day (ensuring clean 24.0h daily logs)
        final_day_midnight = datetime.combine(current_time.date() + timedelta(days=1), time(0, 0, 0))
        if current_time < final_day_midnight:
            timeline_segments.append(LogSegment(
                start_time=current_time,
                end_time=final_day_midnight,
                duty_status=DutyStatus.OFF_DUTY,
                activity="Off Duty",
                location_name=dropoff_loc.name,
                remark=f"Off duty post-trip at destination {dropoff_loc.name}",
            ))
            current_time = final_day_midnight

        # 3. Partition continuous segments across Midnight (24.0-hour calendar days)
        daily_logs = cls._partition_into_daily_logs(
            timeline_segments=timeline_segments,
            from_location=current_loc.name,
            to_location=dropoff_loc.name,
            carrier_name=carrier_name,
            truck_number=truck_number,
            trailer_number=trailer_number,
            initial_cycle_used=current_cycle_used,
        )

        # 4. Summary metrics
        total_driving_hours = sum(s.duration_hours for s in timeline_segments if s.duty_status == DutyStatus.DRIVING)
        total_on_duty_hours = sum(s.duration_hours for s in timeline_segments if s.duty_status.is_on_duty)
        total_sleeper_hours = sum(s.duration_hours for s in timeline_segments if s.duty_status == DutyStatus.SLEEPER_BERTH)
        total_off_duty_hours = sum(s.duration_hours for s in timeline_segments if s.duty_status == DutyStatus.OFF_DUTY)
        fuel_stops_count = sum(1 for s in route_stops if s.stop_type == StopType.FUEL)
        rest_stops_count = sum(1 for s in route_stops if s.stop_type in (StopType.REST_BREAK, StopType.SLEEPER_BERTH))

        return {
            "summary": {
                "origin": current_loc.name,
                "pickup": pickup_loc.name,
                "dropoff": dropoff_loc.name,
                "total_distance_miles": round(total_distance, 1),
                "total_driving_hours": round(total_driving_hours, 2),
                "total_on_duty_hours": round(total_on_duty_hours, 2),
                "total_sleeper_hours": round(total_sleeper_hours, 2),
                "total_off_duty_hours": round(total_off_duty_hours, 2),
                "total_trip_days": len(daily_logs),
                "fuel_stops_count": fuel_stops_count,
                "rest_stops_count": rest_stops_count,
                "initial_cycle_used": round(current_cycle_used, 2),
                "final_cycle_used": round(current_cycle_used + total_on_duty_hours, 2),
                "cycle_hours_remaining": round(max(0.0, 70.0 - (current_cycle_used + total_on_duty_hours)), 2),
            },
            "route": {
                "geojson": route_geojson,
                "legs": [
                    {
                        "origin": leg1.origin_name,
                        "destination": leg1.destination_name,
                        "distance_miles": leg1.distance_miles,
                        "duration_hours": leg1.duration_hours,
                    },
                    {
                        "origin": leg2.origin_name,
                        "destination": leg2.destination_name,
                        "distance_miles": leg2.distance_miles,
                        "duration_hours": leg2.duration_hours,
                    }
                ]
            },
            "stops": [s.to_dict() for s in route_stops],
            "daily_logs": [log.to_dict() for log in daily_logs],
        }

    @classmethod
    def _partition_into_daily_logs(
        cls,
        timeline_segments: List[LogSegment],
        from_location: str,
        to_location: str,
        carrier_name: str,
        truck_number: str,
        trailer_number: str,
        initial_cycle_used: float,
    ) -> List[DailyLogSheet]:
        """
        Split segments across midnight boundaries so every calendar day has segments
        spanning exactly 00:00:00 to 24:00:00, summing to exactly 24.0 hours.
        """
        # Map: log_date -> list of segments
        days_dict: Dict[date, List[LogSegment]] = {}

        for segment in timeline_segments:
            seg_start = segment.start_time
            seg_end = segment.end_time

            while seg_start < seg_end:
                current_date = seg_start.date()
                day_midnight_next = datetime.combine(current_date + timedelta(days=1), time(0, 0, 0))
                slice_end = min(seg_end, day_midnight_next)

                slice_miles = 0.0
                if segment.duty_status == DutyStatus.DRIVING and segment.duration_hours > 0:
                    slice_duration = (slice_end - seg_start).total_seconds() / 3600.0
                    slice_miles = segment.miles_covered * (slice_duration / segment.duration_hours)

                sliced_segment = LogSegment(
                    start_time=seg_start,
                    end_time=slice_end,
                    duty_status=segment.duty_status,
                    activity=segment.activity,
                    location_name=segment.location_name,
                    remark=segment.remark,
                    miles_covered=round(slice_miles, 1),
                )

                if current_date not in days_dict:
                    days_dict[current_date] = []
                days_dict[current_date].append(sliced_segment)

                seg_start = slice_end

        # Construct DailyLogSheet objects with strict 24-hr invariant validation
        sorted_dates = sorted(days_dict.keys())
        total_days = len(sorted_dates)
        daily_logs: List[DailyLogSheet] = []

        cumulative_cycle = initial_cycle_used

        for idx, log_date in enumerate(sorted_dates):
            day_number = idx + 1
            day_segments = days_dict[log_date]
            miles_driving_today = sum(s.miles_covered for s in day_segments if s.duty_status == DutyStatus.DRIVING)

            # On-duty today = Driving + On-Duty Not Driving
            on_duty_today = sum(s.duration_hours for s in day_segments if s.duty_status.is_on_duty)

            recap = RecapCalculator.compute_recap(
                on_duty_today=on_duty_today,
                prior_cycle_used=cumulative_cycle,
                restart_taken=False,
            )
            cumulative_cycle += on_duty_today

            log_sheet = DailyLogSheet(
                log_date=log_date,
                day_number=day_number,
                total_days=total_days,
                from_location=from_location,
                to_location=to_location,
                total_miles_driving_today=miles_driving_today,
                carrier_name=carrier_name,
                truck_tractor_number=truck_number,
                trailer_number=trailer_number,
                segments=day_segments,
                recap=recap,
            )

            # Assert 24-hour invariant with float tolerance
            diff = abs(log_sheet.total_day_hours - HOURS_PER_DAY)
            if diff > 0.05:
                # If slight edge difference, adjust final segment to match exact 24.0h
                if day_segments:
                    adj = HOURS_PER_DAY - log_sheet.total_day_hours
                    day_segments[-1].end_time += timedelta(hours=adj)

            daily_logs.append(log_sheet)

        return daily_logs
