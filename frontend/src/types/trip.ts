export type DutyStatus = 'OFF_DUTY' | 'SLEEPER_BERTH' | 'DRIVING' | 'ON_DUTY_NOT_DRIVING';

export type StopType = 'START' | 'PICKUP' | 'DROPOFF' | 'FUEL' | 'REST_BREAK' | 'SLEEPER_BERTH';

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface RouteStop {
  stop_type: StopType;
  name: string;
  coordinates: Coordinates;
  arrival_time: string;
  departure_time: string;
  duration_hours: number;
  cumulative_miles: number;
  remark: string;
  address?: string;
}

export interface LogSegment {
  start_time: string;
  end_time: string;
  start_hour: number;
  end_hour: number;
  duration_hours: number;
  duty_status: DutyStatus;
  line_number: number;
  activity: string;
  location_name: string;
  remark: string;
  miles_covered: number;
}

export interface DailyRecap {
  on_duty_today: number;
  hours_last_7_days_including_today: number;
  hours_available_tomorrow: number;
  hours_last_8_days_including_today: number;
  restart_taken: boolean;
}

export interface DailyLogSheet {
  date: string;
  day_number: number;
  total_days: number;
  from_location: string;
  to_location: string;
  total_miles_driving_today: number;
  carrier_name: string;
  main_office_address: string;
  home_terminal_address: string;
  truck_tractor_number: string;
  trailer_number: string;
  shipping_documents: string;
  totals: {
    off_duty: number;
    sleeper_berth: number;
    driving: number;
    on_duty_not_driving: number;
    total_hours: number;
  };
  segments: LogSegment[];
  recap: DailyRecap;
}

export interface TripSummary {
  origin: string;
  pickup: string;
  dropoff: string;
  total_distance_miles: number;
  total_driving_hours: number;
  total_on_duty_hours: number;
  total_sleeper_hours: number;
  total_off_duty_hours: number;
  total_trip_days: number;
  fuel_stops_count: number;
  rest_stops_count: number;
  initial_cycle_used: number;
  final_cycle_used: number;
  cycle_hours_remaining: number;
}

export interface RouteLegInfo {
  origin: string;
  destination: string;
  distance_miles: number;
  duration_hours: number;
}

export interface GeoJsonGeometry {
  type: string;
  coordinates: [number, number][]; // [lon, lat]
}

export interface TripPlanResponse {
  id: number;
  summary: TripSummary;
  route: {
    geojson: GeoJsonGeometry;
    legs: RouteLegInfo[];
  };
  stops: RouteStop[];
  daily_logs: DailyLogSheet[];
  created_at: string;
}

export interface TripPlanInput {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  current_cycle_used: number;
  start_datetime?: string;
  truck_number?: string;
  trailer_number?: string;
  carrier_name?: string;
}

export interface LocationSuggestion {
  name: string;
  latitude: number;
  longitude: number;
  state: string;
}
