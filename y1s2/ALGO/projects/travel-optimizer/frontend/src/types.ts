export interface AttractionLocation {
  lat: number;
  lng: number;
}

export interface Attraction {
  id: number;
  name: string;
  location: AttractionLocation;
  open_time: number;   // minutes from midnight
  close_time: number;
  duration: number;
  fee: number;
  preference: number;
  category: string;
}

export interface Visit {
  attraction_id: number;
  name: string;
  lat: number;
  lng: number;
  arrival_time: number;
  departure_time: number;
  fee: number;
  preference: number;
  category: string;
}

export interface DayPlan {
  day: number;
  visits: Visit[];
  total_satisfaction: number;
  total_cost: number;
  total_travel_time: number;
}

export interface Itinerary {
  days: DayPlan[];
  total_satisfaction: number;
  total_cost: number;
  total_attractions: number;
  algorithm: string;
  computation_ms: number;
}

export interface OptimizeRequest {
  attractions?: Attraction[];
  dataset_name?: string;
  hotel_lat: number;
  hotel_lng: number;
  num_days: number;
  daily_time_budget: number;
  total_budget: number;
  start_time: number;
  algorithm: 'greedy' | 'sa';
  sa_seed?: number;
}

export type DatasetName = 'small' | 'medium' | 'large' | 'bangkok_real' | 'hard';
