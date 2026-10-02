import React, { useEffect, useRef } from 'react';
import { Box, Card, Typography, Paper, Chip } from '@mui/material';
import L from 'leaflet';
import type { RouteStop, GeoJsonGeometry } from '../../types/trip';

interface TripMapProps {
  stops: RouteStop[];
  routeGeoJson: GeoJsonGeometry;
}

const getMarkerIcon = (stopType: string, index: number): L.DivIcon => {
  let bgColor = '#2563eb';
  let emoji = '📍';
  let label = `${index}`;

  switch (stopType) {
    case 'START':
      bgColor = '#10b981';
      emoji = '🟢';
      label = 'Start';
      break;
    case 'PICKUP':
      bgColor = '#2563eb';
      emoji = '📦';
      label = 'Pickup';
      break;
    case 'DROPOFF':
      bgColor = '#dc2626';
      emoji = '🏁';
      label = 'Dropoff';
      break;
    case 'FUEL':
      bgColor = '#ea580c';
      emoji = '⛽';
      label = 'Fuel';
      break;
    case 'REST_BREAK':
      bgColor = '#0284c7';
      emoji = '☕';
      label = '30m Break';
      break;
    case 'SLEEPER_BERTH':
      bgColor = '#7c3aed';
      emoji = '🛏️';
      label = '10h Rest';
      break;
  }

  const html = `
    <div style="
      display: flex;
      flex-direction: column;
      align-items: center;
      transform: translate(-50%, -100%);
    ">
      <div style="
        background: ${bgColor};
        color: white;
        font-weight: 700;
        font-size: 11px;
        padding: 3px 7px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        gap: 3px;
        white-space: nowrap;
        border: 2px solid #ffffff;
      ">
        <span>${emoji}</span>
        <span>${label}</span>
      </div>
      <div style="
        width: 0;
        height: 0;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 8px solid ${bgColor};
        margin-top: -1px;
      "></div>
    </div>
  `;

  return L.divIcon({
    className: 'custom-map-pin',
    html: html,
    iconSize: [40, 40],
    iconAnchor: [0, 0],
  });
};

export const TripMap: React.FC<TripMapProps> = ({ stops, routeGeoJson }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        zoomControl: true,
        scrollWheelZoom: true,
      }).setView([39.8283, -98.5795], 4); // Center of USA

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
      }).addTo(map);

      const layerGroup = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
      layerGroupRef.current = layerGroup;
    }

    const map = mapInstanceRef.current;
    const layerGroup = layerGroupRef.current;
    if (!map || !layerGroup) return;

    layerGroup.clearLayers();

    const bounds = L.latLngBounds([]);

    // 1. Draw Route Polyline
    if (routeGeoJson && routeGeoJson.coordinates && routeGeoJson.coordinates.length > 0) {
      // GeoJSON has [lon, lat], Leaflet polyline expects [lat, lon]
      const latLngs: [number, number][] = routeGeoJson.coordinates.map((coord) => [coord[1], coord[0]]);

      const polyline = L.polyline(latLngs, {
        color: '#2563eb',
        weight: 5,
        opacity: 0.85,
        lineJoin: 'round',
        lineCap: 'round',
      }).addTo(layerGroup);

      bounds.extend(polyline.getBounds());
    }

    // 2. Draw Stop Markers
    stops.forEach((stop, index) => {
      const latLng: [number, number] = [stop.coordinates.latitude, stop.coordinates.longitude];
      bounds.extend(latLng);

      const marker = L.marker(latLng, {
        icon: getMarkerIcon(stop.stop_type, index + 1),
      }).addTo(layerGroup);

      const arrivalFormatted = new Date(stop.arrival_time).toLocaleString([], {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
      const departureFormatted = new Date(stop.departure_time).toLocaleString([], {
        hour: '2-digit',
        minute: '2-digit',
      });

      const popupContent = `
        <div style="font-family: system-ui, sans-serif; min-width: 200px;">
          <h4 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 700; color: #0f172a;">
            ${stop.name}
          </h4>
          <p style="margin: 0 0 4px 0; font-size: 12px; color: #475569;">
            <strong>Type:</strong> ${stop.stop_type.replace('_', ' ')}
          </p>
          <p style="margin: 0 0 4px 0; font-size: 12px; color: #475569;">
            <strong>Arrival:</strong> ${arrivalFormatted}
          </p>
          <p style="margin: 0 0 4px 0; font-size: 12px; color: #475569;">
            <strong>Departure:</strong> ${departureFormatted} (${stop.duration_hours}h)
          </p>
          <p style="margin: 0 0 4px 0; font-size: 12px; color: #475569;">
            <strong>Miles:</strong> ${stop.cumulative_miles} mi
          </p>
          <p style="margin: 6px 0 0 0; font-size: 11px; color: #64748b; font-style: italic;">
            ${stop.remark}
          </p>
        </div>
      `;

      marker.bindPopup(popupContent);
    });

    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
    }

    // Leaflet resize trigger
    setTimeout(() => {
      map.invalidateSize();
    }, 250);
  }, [stops, routeGeoJson]);

  return (
    <Card sx={{ height: { xs: 400, md: 540 }, position: 'relative', overflow: 'hidden' }}>
      <Box ref={mapContainerRef} sx={{ width: '100%', height: '100%' }} />

      {/* Floating Legend */}
      <Paper
        elevation={3}
        sx={{
          position: 'absolute',
          bottom: 16,
          right: 16,
          zIndex: 1000,
          p: 1.5,
          bgcolor: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(4px)',
          borderRadius: 2,
          maxWidth: { xs: 260, sm: 380 },
        }}
      >
        <Typography variant="caption" sx={{ fontWeight: 700, color: '#0f172a', display: 'block', mb: 0.8 }}>
          Map Legend & HOS Stops
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.8 }}>
          <Chip size="small" label="🟢 Origin" sx={{ bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#059669', fontWeight: 600, fontSize: '0.72rem' }} />
          <Chip size="small" label="📦 Pickup (1h)" sx={{ bgcolor: 'rgba(37, 99, 235, 0.1)', color: '#2563eb', fontWeight: 600, fontSize: '0.72rem' }} />
          <Chip size="small" label="🏁 Dropoff (1h)" sx={{ bgcolor: 'rgba(220, 38, 38, 0.1)', color: '#dc2626', fontWeight: 600, fontSize: '0.72rem' }} />
          <Chip size="small" label="⛽ Fuel (≤1,000 mi)" sx={{ bgcolor: 'rgba(234, 88, 12, 0.1)', color: '#ea580c', fontWeight: 600, fontSize: '0.72rem' }} />
          <Chip size="small" label="☕ 30m Rest (8h limit)" sx={{ bgcolor: 'rgba(2, 132, 199, 0.1)', color: '#0284c7', fontWeight: 600, fontSize: '0.72rem' }} />
          <Chip size="small" label="🛏️ 10h Sleeper Berth" sx={{ bgcolor: 'rgba(124, 58, 237, 0.1)', color: '#7c3aed', fontWeight: 600, fontSize: '0.72rem' }} />
        </Box>
      </Paper>
    </Card>
  );
};
