import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Tabs,
  Tab,
  Grid,
  Chip,
  Button,
} from '@mui/material';
import PrintIcon from '@mui/icons-material/Print';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import type { DailyLogSheet as DailyLogType } from '../../types/trip';
import { EldGridCanvas } from './EldGridCanvas';
import { RemarksTable } from './RemarksTable';
import { RecapTable } from './RecapTable';

interface EldLogSheetProps {
  dailyLogs: DailyLogType[];
}

export const EldLogSheet: React.FC<EldLogSheetProps> = ({ dailyLogs }) => {
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);

  if (!dailyLogs || dailyLogs.length === 0) {
    return null;
  }

  const currentLog = dailyLogs[selectedDayIndex] || dailyLogs[0];
  const dateObj = new Date(currentLog.date);
  const formattedDate = dateObj.toLocaleDateString('en-US', {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
  });

  const handlePrint = () => {
    window.print();
  };

  return (
    <Card sx={{ bgcolor: '#ffffff', border: '2px solid #cbd5e1', boxShadow: '0 4px 20px rgba(0,0,0,0.06)' }}>
      {/* Day Selector Tabs */}
      <Box sx={{ borderBottom: '1px solid #e2e8f0', bgcolor: '#f8fafc', px: 2, pt: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Tabs
          value={selectedDayIndex}
          onChange={(_, newVal) => setSelectedDayIndex(newVal)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              textTransform: 'none',
              fontWeight: 700,
              fontSize: '0.9rem',
              py: 1.5,
              minHeight: 48,
            },
          }}
        >
          {dailyLogs.map((log, idx) => (
            <Tab
              key={idx}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <span>Day {log.day_number} of {log.total_days}</span>
                  <Chip
                    size="small"
                    label={`${log.total_miles_driving_today.toFixed(0)} mi`}
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      fontWeight: 600,
                      bgcolor: selectedDayIndex === idx ? '#1e3a8a' : '#e2e8f0',
                      color: selectedDayIndex === idx ? '#ffffff' : '#475569',
                    }}
                  />
                </Box>
              }
            />
          ))}
        </Tabs>

        <Button
          size="small"
          startIcon={<PrintIcon />}
          onClick={handlePrint}
          sx={{ display: { xs: 'none', sm: 'flex' }, color: '#475569', fontWeight: 600 }}
        >
          Print Log Sheet
        </Button>
      </Box>

      {/* Official FMCSA Log Book Page (Printable Container) */}
      <CardContent sx={{ p: { xs: 2, md: 3 } }} className="printable-log-sheet">
        {/* Header Block matching Attached Official Sheet */}
        <Box sx={{ borderBottom: '2px solid #0f172a', pb: 1.5, mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 1 }}>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 900, letterSpacing: '-0.02em', color: '#0f172a', textTransform: 'uppercase' }}>
                Drivers Daily Log
              </Typography>
              <Typography variant="caption" sx={{ color: '#475569', fontWeight: 700, display: 'block' }}>
                (24 hours) • Property-Carrying CMV • 70 Hours / 8 Days
              </Typography>
            </Box>

            <Box sx={{ textAlign: 'right' }}>
              <Typography variant="body2" sx={{ fontWeight: 800, color: '#0f172a', fontFamily: "'JetBrains Mono', monospace" }}>
                Date: {formattedDate}
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b', display: 'block' }}>
                Original - File at home terminal. Duplicate - Retain for 8 days.
              </Typography>
            </Box>
          </Box>

          {/* Form Fields Header Table */}
          <Grid container spacing={1.5} sx={{ mt: 1 }}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <Box sx={{ borderBottom: '1px solid #94a3b8', pb: 0.3 }}>
                <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontSize: '0.7rem' }}>
                  From (Trip Origin):
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                  {currentLog.from_location}
                </Typography>
              </Box>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <Box sx={{ borderBottom: '1px solid #94a3b8', pb: 0.3 }}>
                <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontSize: '0.7rem' }}>
                  To (Trip Destination):
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                  {currentLog.to_location}
                </Typography>
              </Box>
            </Grid>

            <Grid size={{ xs: 6, sm: 3 }}>
              <Box sx={{ border: '1px solid #94a3b8', p: 0.8, borderRadius: 1, bgcolor: '#f8fafc' }}>
                <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontSize: '0.68rem', fontWeight: 600 }}>
                  Total Miles Driving Today:
                </Typography>
                <Typography variant="body1" sx={{ fontWeight: 800, color: '#0f172a', fontFamily: "'JetBrains Mono', monospace" }}>
                  {currentLog.total_miles_driving_today.toFixed(1)} mi
                </Typography>
              </Box>
            </Grid>

            <Grid size={{ xs: 6, sm: 3 }}>
              <Box sx={{ border: '1px solid #94a3b8', p: 0.8, borderRadius: 1, bgcolor: '#f8fafc' }}>
                <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontSize: '0.68rem', fontWeight: 600 }}>
                  Vehicle Identifiers:
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a', fontFamily: "'JetBrains Mono', monospace" }}>
                  {currentLog.truck_tractor_number} / {currentLog.trailer_number}
                </Typography>
              </Box>
            </Grid>

            <Grid size={{ xs: 12, sm: 6 }}>
              <Box sx={{ borderBottom: '1px solid #94a3b8', pb: 0.3 }}>
                <Typography variant="caption" sx={{ color: '#64748b', display: 'block', fontSize: '0.7rem' }}>
                  Carrier Name & Home Terminal:
                </Typography>
                <Typography variant="body2" sx={{ fontWeight: 700, color: '#0f172a' }}>
                  {currentLog.carrier_name} • {currentLog.home_terminal_address}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* 24-HOUR GRAPH GRID (THE SVG CANVAS) */}
        <EldGridCanvas segments={currentLog.segments} totals={currentLog.totals} />

        {/* REMARKS SECTION */}
        <RemarksTable segments={currentLog.segments} />

        {/* SHIPPING DOCUMENTS & COMMODITY */}
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid size={{ xs: 12, sm: 6 }}>
            <Box sx={{ border: '1px solid #cbd5e1', p: 1.2, borderRadius: 1.5, bgcolor: '#f8fafc' }}>
              <Typography variant="caption" sx={{ fontWeight: 700, color: '#475569', display: 'block' }}>
                Shipping Documents / Manifest:
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, color: '#0f172a', mt: 0.5 }}>
                {currentLog.shipping_documents}
              </Typography>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, sm: 6 }}>
            <Box sx={{ border: '1px solid #cbd5e1', p: 1.2, borderRadius: 1.5, bgcolor: '#f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="caption" sx={{ fontWeight: 700, color: '#475569', display: 'block' }}>
                  Driver Certification:
                </Typography>
                <Typography variant="caption" sx={{ color: '#16a34a', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <CheckCircleIcon sx={{ fontSize: 14 }} /> Verified Compliant (49 CFR § 395.8)
                </Typography>
              </Box>
              <Box sx={{ borderBottom: '1px dashed #64748b', width: 140, textAlign: 'center', pb: 0.2 }}>
                <Typography variant="caption" sx={{ fontStyle: 'italic', fontFamily: 'serif', color: '#1e3a8a', fontSize: '0.85rem' }}>
                  John Doe #482
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>

        {/* 70-HOUR / 8-DAY RECAP SECTION */}
        <RecapTable recap={currentLog.recap} />
      </CardContent>
    </Card>
  );
};
