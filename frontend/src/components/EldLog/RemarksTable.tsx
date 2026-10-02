import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import type { LogSegment } from '../../types/trip';

interface RemarksTableProps {
  segments: LogSegment[];
}

const getDutyBadge = (status: string) => {
  switch (status) {
    case 'OFF_DUTY':
      return <Chip size="small" label="1. Off Duty" sx={{ bgcolor: '#f1f5f9', color: '#475569', fontWeight: 600, fontSize: '0.72rem' }} />;
    case 'SLEEPER_BERTH':
      return <Chip size="small" label="2. Sleeper Berth" sx={{ bgcolor: 'rgba(124, 58, 237, 0.1)', color: '#7c3aed', fontWeight: 600, fontSize: '0.72rem' }} />;
    case 'DRIVING':
      return <Chip size="small" label="3. Driving" sx={{ bgcolor: 'rgba(37, 99, 235, 0.1)', color: '#2563eb', fontWeight: 600, fontSize: '0.72rem' }} />;
    case 'ON_DUTY_NOT_DRIVING':
      return <Chip size="small" label="4. On Duty" sx={{ bgcolor: 'rgba(217, 119, 6, 0.1)', color: '#d97706', fontWeight: 600, fontSize: '0.72rem' }} />;
    default:
      return null;
  }
};

export const RemarksTable: React.FC<RemarksTableProps> = ({ segments }) => {
  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#0f172a', mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
        Remarks & Duty Status Changes
        <Typography variant="caption" sx={{ color: '#64748b', fontWeight: 400 }}>
          (Locations of reporting, release, and duty status changes)
        </Typography>
      </Typography>

      <TableContainer component={Paper} elevation={0} sx={{ border: '1px solid #e2e8f0', borderRadius: 2 }}>
        <Table size="small">
          <TableHead sx={{ bgcolor: '#f8fafc' }}>
            <TableRow>
              <TableCell sx={{ fontWeight: 700, color: '#475569', fontSize: '0.78rem' }}>Time Range</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#475569', fontSize: '0.78rem' }}>Duration</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#475569', fontSize: '0.78rem' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#475569', fontSize: '0.78rem' }}>Location</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#475569', fontSize: '0.78rem' }}>Miles</TableCell>
              <TableCell sx={{ fontWeight: 700, color: '#475569', fontSize: '0.78rem' }}>Remark / Activity Description</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {segments.map((seg, idx) => {
              const startFormatted = new Date(seg.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
              const endFormatted = new Date(seg.end_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

              return (
                <TableRow key={idx} hover sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                  <TableCell sx={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.78rem', color: '#0f172a' }}>
                    {startFormatted} - {endFormatted}
                  </TableCell>
                  <TableCell sx={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.78rem', fontWeight: 600 }}>
                    {seg.duration_hours.toFixed(2)}h
                  </TableCell>
                  <TableCell>
                    {getDutyBadge(seg.duty_status)}
                  </TableCell>
                  <TableCell sx={{ fontSize: '0.82rem', fontWeight: 600, color: '#1e293b' }}>
                    {seg.location_name}
                  </TableCell>
                  <TableCell sx={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '0.78rem', color: '#64748b' }}>
                    {seg.miles_covered > 0 ? `${seg.miles_covered.toFixed(1)} mi` : '—'}
                  </TableCell>
                  <TableCell sx={{ fontSize: '0.82rem', color: '#475569' }}>
                    {seg.remark}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
