import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Grid,
  Box,
  InputAdornment,
  CircularProgress,
  Chip,
  Alert,
  Tooltip,
} from '@mui/material';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import StorefrontIcon from '@mui/icons-material/Storefront';
import WhereToVoteIcon from '@mui/icons-material/WhereToVote';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import RouteIcon from '@mui/icons-material/Route';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import type { TripPlanInput } from '../../types/trip';

interface TripFormProps {
  onSubmit: (input: TripPlanInput) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

interface PresetOption {
  label: string;
  desc: string;
  data: TripPlanInput;
}

const PRESET_TRIPS: PresetOption[] = [
  {
    label: 'Chicago → Indy → Dallas',
    desc: '1,080 mi • Multi-Day • 1 Fuel Stop',
    data: {
      current_location: 'Chicago, IL',
      pickup_location: 'Indianapolis, IN',
      dropoff_location: 'Dallas, TX',
      current_cycle_used: 12.5,
    },
  },
  {
    label: 'New York → Chicago → LA',
    desc: '2,800 mi • Coast-to-Coast • 5 Days',
    data: {
      current_location: 'New York, NY',
      pickup_location: 'Chicago, IL',
      dropoff_location: 'Los Angeles, CA',
      current_cycle_used: 10.0,
    },
  },
  {
    label: 'Atlanta → Charlotte → Jacksonville',
    desc: '580 mi • Regional • 2 Days',
    data: {
      current_location: 'Atlanta, GA',
      pickup_location: 'Charlotte, NC',
      dropoff_location: 'Jacksonville, FL',
      current_cycle_used: 24.0,
    },
  },
];

export const TripForm: React.FC<TripFormProps> = ({ onSubmit, isLoading, error }) => {
  const [currentLocation, setCurrentLocation] = useState('Chicago, IL');
  const [pickupLocation, setPickupLocation] = useState('Indianapolis, IN');
  const [dropoffLocation, setDropoffLocation] = useState('Dallas, TX');
  const [cycleUsed, setCycleUsed] = useState('14.5');
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});

  const validate = (): boolean => {
    const errors: { [key: string]: string } = {};

    if (!currentLocation.trim()) {
      errors.currentLocation = 'Current location is required.';
    }
    if (!pickupLocation.trim()) {
      errors.pickupLocation = 'Pickup location is required.';
    }
    if (!dropoffLocation.trim()) {
      errors.dropoffLocation = 'Dropoff location is required.';
    }

    const cycleVal = parseFloat(cycleUsed);
    if (isNaN(cycleVal)) {
      errors.cycleUsed = 'Please enter a valid numeric value.';
    } else if (cycleVal < 0 || cycleVal > 70) {
      errors.cycleUsed = 'Cycle hours used must be between 0.0 and 70.0.';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate() || isLoading) return;

    await onSubmit({
      current_location: currentLocation.trim(),
      pickup_location: pickupLocation.trim(),
      dropoff_location: dropoffLocation.trim(),
      current_cycle_used: parseFloat(cycleUsed),
    });
  };

  const applyPreset = (preset: PresetOption) => {
    setCurrentLocation(preset.data.current_location);
    setPickupLocation(preset.data.pickup_location);
    setDropoffLocation(preset.data.dropoff_location);
    setCycleUsed(preset.data.current_cycle_used.toString());
    setFormErrors({});
  };

  return (
    <Card sx={{ bgcolor: '#ffffff', boxShadow: '0 4px 20px -2px rgba(0,0,0,0.06)' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
              Trip Dispatch & HOS Configuration
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              Enter waypoints to calculate commercial routing and generate official FMCSA daily log sheets.
            </Typography>
          </Box>
        </Box>

        {/* Quick Presets */}
        <Box sx={{ mb: 2.5, p: 1.5, bgcolor: '#f1f5f9', borderRadius: 2 }}>
          <Typography variant="caption" sx={{ fontWeight: 700, color: '#475569', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <FlashOnIcon sx={{ fontSize: 16, color: '#f59e0b' }} /> Quick Evaluation Presets:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {PRESET_TRIPS.map((preset, idx) => (
              <Tooltip key={idx} title={preset.desc}>
                <Chip
                  label={preset.label}
                  onClick={() => applyPreset(preset)}
                  clickable
                  disabled={isLoading}
                  sx={{
                    bgcolor: '#ffffff',
                    border: '1px solid #cbd5e1',
                    fontWeight: 600,
                    fontSize: '0.8rem',
                    '&:hover': { bgcolor: '#e2e8f0', borderColor: '#94a3b8' },
                  }}
                />
              </Tooltip>
            ))}
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2.5, borderRadius: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Grid container spacing={2}>
            {/* Current Location */}
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField
                fullWidth
                label="Current Location"
                value={currentLocation}
                onChange={(e) => setCurrentLocation(e.target.value)}
                error={!!formErrors.currentLocation}
                helperText={formErrors.currentLocation || 'City, State or Address'}
                disabled={isLoading}
                size="small"
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <MyLocationIcon sx={{ color: '#10b981', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                  },
                }}
              />
            </Grid>

            {/* Pickup Location */}
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField
                fullWidth
                label="Pickup Location (Shipper)"
                value={pickupLocation}
                onChange={(e) => setPickupLocation(e.target.value)}
                error={!!formErrors.pickupLocation}
                helperText={formErrors.pickupLocation || '1 hr On-Duty required'}
                disabled={isLoading}
                size="small"
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <StorefrontIcon sx={{ color: '#2563eb', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                  },
                }}
              />
            </Grid>

            {/* Dropoff Location */}
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField
                fullWidth
                label="Dropoff Location (Consignee)"
                value={dropoffLocation}
                onChange={(e) => setDropoffLocation(e.target.value)}
                error={!!formErrors.dropoffLocation}
                helperText={formErrors.dropoffLocation || '1 hr On-Duty required'}
                disabled={isLoading}
                size="small"
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <WhereToVoteIcon sx={{ color: '#dc2626', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                  },
                }}
              />
            </Grid>

            {/* Current Cycle Hours */}
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField
                fullWidth
                label="Current Cycle Used (Hrs)"
                type="number"
                value={cycleUsed}
                onChange={(e) => setCycleUsed(e.target.value)}
                error={!!formErrors.cycleUsed}
                helperText={formErrors.cycleUsed || 'Out of 70 hrs / 8 days'}
                disabled={isLoading}
                size="small"
                slotProps={{
                  htmlInput: { step: '0.1', min: '0', max: '70' },
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <AccessTimeIcon sx={{ color: '#d97706', fontSize: 20 }} />
                      </InputAdornment>
                    ),
                  },
                }}
              />
            </Grid>

            {/* Submit Button */}
            <Grid size={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={isLoading}
                  startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <RouteIcon />}
                  sx={{
                    px: 4,
                    py: 1.2,
                    bgcolor: '#1e3a8a',
                    fontSize: '0.95rem',
                    fontWeight: 700,
                    '&:hover': { bgcolor: '#172554' },
                  }}
                >
                  {isLoading ? 'Calculating Route & HOS Logs...' : 'Plan Trip & Generate ELD Logs'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
};
