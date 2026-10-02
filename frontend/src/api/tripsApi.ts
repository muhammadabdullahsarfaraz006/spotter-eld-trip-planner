import { apiClient } from './client';
import type { TripPlanInput, TripPlanResponse, LocationSuggestion } from '../types/trip';

export const tripsApi = {
  /**
   * Plan a trip with HOS simulation, routing, and ELD logs.
   */
  async planTrip(input: TripPlanInput): Promise<TripPlanResponse> {
    const response = await apiClient.post<TripPlanResponse>('/api/trips/plan/', input);
    return response.data;
  },

  /**
   * Fetch city autocomplete suggestions.
   */
  async getSuggestions(query: string): Promise<LocationSuggestion[]> {
    if (!query || query.trim().length < 2) return [];
    try {
      const response = await apiClient.get<LocationSuggestion[]>('/api/trips/suggest/', {
        params: { q: query },
      });
      return response.data;
    } catch {
      return [];
    }
  },

  /**
   * Fetch past planned trips.
   */
  async getRecentTrips(): Promise<TripPlanResponse[]> {
    try {
      const response = await apiClient.get('/api/trips/');
      return response.data.results || response.data || [];
    } catch {
      return [];
    }
  },

  /**
   * Fetch a saved trip by ID.
   */
  async getTripById(id: number): Promise<TripPlanResponse> {
    const response = await apiClient.get<TripPlanResponse>(`/api/trips/${id}/`);
    return response.data;
  },
};
