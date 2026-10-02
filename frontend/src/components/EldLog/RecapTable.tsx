import React from 'react';
import { Box, Typography, Paper, Grid } from '@mui/material';
import type { DailyRecap } from '../../types/trip';

interface RecapTableProps {
  recap: DailyRecap;
}

export const RecapTable: React.FC<RecapTableProps> = ({ recap }) => {
  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a', mb: 1 }}>
        70-Hour / 8-Day Driver Recap (Complete at end of day)
      </Typography>

      <Paper
        elevation={0}
        sx={{
          border: '1px solid #cbd5e1',
          borderRadius: 2,
          p: 1.5,
          bgcolor: '#ffffff',
        }}
      >
        <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 3 }}>
            <Box sx={{ p: 1, border: '1px solid #e2e8f0', borderRadius: 1.5, bgcolor: '#f8fafc', height: '100%' }}>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600, display: 'block' }}>
                On Duty Hours Today
              </Typography>
              <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block', mb: 0.5 }}>
                Total Lines 3 & 4
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#1e3a8a', fontFamily: "'JetBrains Mono', monospace" }}>
                {recap.on_duty_today.toFixed(2)} hrs
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 3 }}>
            <Box sx={{ p: 1, border: '1px solid #e2e8f0', borderRadius: 1.5, bgcolor: '#f8fafc', height: '100%' }}>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600, display: 'block' }}>
                A. On Duty Last 7 Days
              </Typography>
              <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block', mb: 0.5 }}>
                Including Today
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a', fontFamily: "'JetBrains Mono', monospace" }}>
                {recap.hours_last_7_days_including_today.toFixed(2)} hrs
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 3 }}>
            <Box sx={{ p: 1, border: '1px solid #e2e8f0', borderRadius: 1.5, bgcolor: 'rgba(22, 163, 74, 0.05)', borderColor: '#bbf7d0', height: '100%' }}>
              <Typography variant="caption" sx={{ color: '#15803d', fontWeight: 700, display: 'block' }}>
                B. Available Tomorrow
              </Typography>
              <Typography variant="caption" sx={{ color: '#16a34a', display: 'block', mb: 0.5 }}>
                70 hrs minus Line A*
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#15803d', fontFamily: "'JetBrains Mono', monospace" }}>
                {recap.hours_available_tomorrow.toFixed(2)} hrs
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 3 }}>
            <Box sx={{ p: 1, border: '1px solid #e2e8f0', borderRadius: 1.5, bgcolor: '#f8fafc', height: '100%' }}>
              <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 600, display: 'block' }}>
                C. On Duty Last 8 Days
              </Typography>
              <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block', mb: 0.5 }}>
                Including Today
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#0f172a', fontFamily: "'JetBrains Mono', monospace" }}>
                {recap.hours_last_8_days_including_today.toFixed(2)} hrs
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Typography variant="caption" sx={{ color: '#64748b', fontStyle: 'italic', display: 'block', mt: 1 }}>
          * If you took 34 consecutive hours off duty you have 70 hours available.
        </Typography>
      </Paper>
    </Box>
  );
};
