import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
} from '@mui/material';
import MapIcon from '@mui/icons-material/Map';
import SpeedIcon from '@mui/icons-material/Speed';
import LocalGasStationIcon from '@mui/icons-material/LocalGasStation';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import EventNoteIcon from '@mui/icons-material/EventNote';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import type { TripSummary } from '../../types/trip';

interface TripSummaryCardsProps {
  summary: TripSummary;
}

export const TripSummaryCards: React.FC<TripSummaryCardsProps> = ({ summary }) => {
  const cyclePercent = Math.min(100, Math.round((summary.final_cycle_used / 70.0) * 100));

  const stats = [
    {
      title: 'Total Distance',
      value: `${summary.total_distance_miles.toLocaleString()} mi`,
      subtitle: `${summary.origin} → ${summary.dropoff}`,
      icon: <MapIcon sx={{ fontSize: 24, color: '#2563eb' }} />,
      bg: 'rgba(37, 99, 235, 0.08)',
    },
    {
      title: 'Driving Time',
      value: `${summary.total_driving_hours} hrs`,
      subtitle: `At commercial truck highway speeds`,
      icon: <SpeedIcon sx={{ fontSize: 24, color: '#059669' }} />,
      bg: 'rgba(5, 150, 105, 0.08)',
    },
    {
      title: 'Daily Log Sheets',
      value: `${summary.total_trip_days} ${summary.total_trip_days === 1 ? 'Day' : 'Days'}`,
      subtitle: `24-Hour FMCSA logs generated`,
      icon: <EventNoteIcon sx={{ fontSize: 24, color: '#7c3aed' }} />,
      bg: 'rgba(124, 58, 237, 0.08)',
    },
    {
      title: 'Fuel Stops',
      value: `${summary.fuel_stops_count}`,
      subtitle: `Every ≤ 1,000 miles (30m each)`,
      icon: <LocalGasStationIcon sx={{ fontSize: 24, color: '#ea580c' }} />,
      bg: 'rgba(234, 88, 12, 0.08)',
    },
    {
      title: 'Rest & Sleeper Stops',
      value: `${summary.rest_stops_count}`,
      subtitle: `30m Breaks & 10h Resets`,
      icon: <BedtimeIcon sx={{ fontSize: 24, color: '#0284c7' }} />,
      bg: 'rgba(2, 132, 199, 0.08)',
    },
    {
      title: '70-Hr Cycle Remaining',
      value: `${summary.cycle_hours_remaining} hrs`,
      subtitle: `Used: ${summary.final_cycle_used}h / 70.0h`,
      icon: <HourglassEmptyIcon sx={{ fontSize: 24, color: '#d97706' }} />,
      bg: 'rgba(217, 119, 6, 0.08)',
      isCycle: true,
    },
  ];

  return (
    <Grid container spacing={2}>
      {stats.map((stat, idx) => (
        <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }} key={idx}>
          <Card
            sx={{
              height: '100%',
              bgcolor: '#ffffff',
              transition: 'transform 0.2s, box-shadow 0.2s',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 6px 18px rgba(0,0,0,0.08)',
              },
            }}
          >
            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="caption" sx={{ fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>
                  {stat.title}
                </Typography>
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: stat.bg,
                  }}
                >
                  {stat.icon}
                </Box>
              </Box>

              <Typography variant="h5" sx={{ fontWeight: 700, color: '#0f172a', mb: 0.3 }}>
                {stat.value}
              </Typography>

              <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontSize: '0.75rem' }}>
                {stat.subtitle}
              </Typography>

              {stat.isCycle && (
                <Box sx={{ mt: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={cyclePercent}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      bgcolor: '#e2e8f0',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: cyclePercent > 85 ? '#dc2626' : '#d97706',
                      },
                    }}
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};
