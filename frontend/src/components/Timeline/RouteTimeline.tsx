import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import LocalGasStationIcon from '@mui/icons-material/LocalGasStation';
import BedtimeIcon from '@mui/icons-material/Bedtime';
import CoffeeIcon from '@mui/icons-material/Coffee';
import StorefrontIcon from '@mui/icons-material/Storefront';
import WhereToVoteIcon from '@mui/icons-material/WhereToVote';
import PlayCircleFilledWhiteIcon from '@mui/icons-material/PlayCircleFilledWhite';
import type { RouteStop } from '../../types/trip';

interface RouteTimelineProps {
  stops: RouteStop[];
}

const getStopIcon = (type: string) => {
  switch (type) {
    case 'START':
      return <PlayCircleFilledWhiteIcon sx={{ color: '#10b981' }} />;
    case 'PICKUP':
      return <StorefrontIcon sx={{ color: '#2563eb' }} />;
    case 'DROPOFF':
      return <WhereToVoteIcon sx={{ color: '#dc2626' }} />;
    case 'FUEL':
      return <LocalGasStationIcon sx={{ color: '#ea580c' }} />;
    case 'REST_BREAK':
      return <CoffeeIcon sx={{ color: '#0284c7' }} />;
    case 'SLEEPER_BERTH':
      return <BedtimeIcon sx={{ color: '#7c3aed' }} />;
    default:
      return <CheckCircleIcon sx={{ color: '#64748b' }} />;
  }
};

export const RouteTimeline: React.FC<RouteTimelineProps> = ({ stops }) => {
  return (
    <Card sx={{ bgcolor: '#ffffff', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ p: 2.5, flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a', mb: 0.5 }}>
          Route & HOS Stop Itinerary
        </Typography>
        <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mb: 2 }}>
          Chronological sequence of required fueling, breaks, loading, and sleeper berth resets.
        </Typography>

        <Box sx={{ overflowY: 'auto', pr: 1, flexGrow: 1, maxHeight: 520 }}>
          {stops.map((stop, idx) => {
            const isLast = idx === stops.length - 1;
            const arrivalFormatted = new Date(stop.arrival_time).toLocaleDateString([], {
              weekday: 'short',
              month: 'short',
              day: 'numeric',
            }) + ' ' + new Date(stop.arrival_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            const departureFormatted = new Date(stop.departure_time).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            });

            return (
              <Box key={idx} sx={{ display: 'flex', position: 'relative', pb: isLast ? 0 : 2.5 }}>
                {/* Vertical Connector Line */}
                {!isLast && (
                  <Box
                    sx={{
                      position: 'absolute',
                      left: 17,
                      top: 36,
                      bottom: 0,
                      width: 2,
                      bgcolor: '#e2e8f0',
                    }}
                  />
                )}

                {/* Stop Icon Circle */}
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    bgcolor: '#f1f5f9',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1,
                    mr: 2,
                    boxShadow: '0 2px 5px rgba(0,0,0,0.08)',
                    flexShrink: 0,
                  }}
                >
                  {getStopIcon(stop.stop_type)}
                </Box>

                {/* Stop Details */}
                <Box sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 0.5 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                      {stop.name}
                    </Typography>
                    <Chip
                      size="small"
                      label={`${stop.cumulative_miles.toFixed(1)} mi`}
                      sx={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        height: 20,
                        bgcolor: '#f1f5f9',
                      }}
                    />
                  </Box>

                  <Typography variant="caption" sx={{ color: '#475569', display: 'block', mt: 0.3 }}>
                    {arrivalFormatted} → {departureFormatted} ({stop.duration_hours}h)
                  </Typography>

                  <Typography variant="body2" sx={{ color: '#64748b', fontSize: '0.8rem', mt: 0.5 }}>
                    {stop.remark}
                  </Typography>
                </Box>
              </Box>
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );
};
