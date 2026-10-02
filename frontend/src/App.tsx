import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  CssBaseline,
  Container,
  Box,
  Grid,
  Alert,
  Snackbar,
  Typography,
  CircularProgress,
} from '@mui/material';
import { theme } from './theme/theme';
import { Navbar } from './components/Common/Navbar';
import { TripForm } from './components/TripForm/TripForm';
import { TripSummaryCards } from './components/TripSummary/TripSummaryCards';
import { TripMap } from './components/Map/TripMap';
import { RouteTimeline } from './components/Timeline/RouteTimeline';
import { EldLogSheet } from './components/EldLog/EldLogSheet';
import { tripsApi } from './api/tripsApi';
import type { TripPlanInput, TripPlanResponse } from './types/trip';

export const App: React.FC = () => {
  const [tripData, setTripData] = useState<TripPlanResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Automatically plan default trip on first load
  useEffect(() => {
    const loadDefaultTrip = async () => {
      setIsLoading(true);
      try {
        const defaultData = await tripsApi.planTrip({
          current_location: 'Chicago, IL',
          pickup_location: 'Indianapolis, IN',
          dropoff_location: 'Dallas, TX',
          current_cycle_used: 12.5,
        });
        setTripData(defaultData);
      } catch (err: any) {
        console.error('Initial trip load failed:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadDefaultTrip();
  }, []);

  const handlePlanTrip = async (input: TripPlanInput) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await tripsApi.planTrip(input);
      setTripData(result);
      setToastMessage(`Trip calculated successfully! ${result.daily_logs.length} Daily Log Sheets generated.`);
    } catch (err: any) {
      const errorMsg =
        err.response?.data?.message ||
        err.response?.data?.error ||
        'We encountered an error calculating the trip. Please check your addresses and try again.';
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#f8fafc' }}>
        <Navbar onPrint={handlePrint} hasData={!!tripData} />

        <Container maxWidth="xl" sx={{ py: 3, flexGrow: 1 }}>
          {/* 1. Trip Input Form */}
          <Box className="trip-form-container" sx={{ mb: 3 }}>
            <TripForm onSubmit={handlePlanTrip} isLoading={isLoading} error={error} />
          </Box>

          {/* Loading Indicator */}
          {isLoading && !tripData && (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 8 }}>
              <CircularProgress size={48} sx={{ color: '#1e3a8a', mb: 2 }} />
              <Typography variant="body1" sx={{ color: '#64748b', fontWeight: 600 }}>
                Computing commercial route and FMCSA 70h/8d log sheets...
              </Typography>
            </Box>
          )}

          {/* 2. Results Section */}
          {tripData && (
            <>
              {/* Trip Summary KPIs */}
              <Box className="trip-summary-container" sx={{ mb: 3 }}>
                <TripSummaryCards summary={tripData.summary} />
              </Box>

              {/* Map & Timeline Grid */}
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid size={{ xs: 12, lg: 8 }} className="trip-map-container">
                  <TripMap stops={tripData.stops} routeGeoJson={tripData.route.geojson} />
                </Grid>

                <Grid size={{ xs: 12, lg: 4 }} className="trip-timeline-container">
                  <RouteTimeline stops={tripData.stops} />
                </Grid>
              </Grid>

              {/* 3. Driver's Daily Log Sheets (FMCSA Official Standard) */}
              <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1.5 }}>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a' }}>
                      Driver's Record of Duty Status (RODS)
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      Official FMCSA 24-hour log sheets with step line grid, remarks, and 70-hour/8-day recap table.
                    </Typography>
                  </Box>
                </Box>

                <EldLogSheet dailyLogs={tripData.daily_logs} />
              </Box>
            </>
          )}
        </Container>

        {/* Footer */}
        <Box component="footer" className="no-print" sx={{ py: 2.5, bgcolor: '#0f172a', borderTop: '1px solid #1e293b', mt: 'auto' }}>
          <Container maxWidth="xl">
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
              <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                Spotter ELD & HOS Assessment • Built with Django REST Framework & React (TypeScript, MUI)
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b' }}>
                49 CFR Part 395 Compliant • Property-Carrying CMV 70hr/8day Rules
              </Typography>
            </Box>
          </Container>
        </Box>

        {/* Toast Notification */}
        <Snackbar
          open={!!toastMessage}
          autoHideDuration={4000}
          onClose={() => setToastMessage(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={() => setToastMessage(null)} severity="success" sx={{ width: '100%', borderRadius: 2 }}>
            {toastMessage}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
};

export default App;
