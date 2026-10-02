import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import PrintIcon from '@mui/icons-material/Print';
import VerifiedIcon from '@mui/icons-material/Verified';

interface NavbarProps {
  onPrint?: () => void;
  hasData?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onPrint, hasData }) => {
  return (
    <AppBar position="static" elevation={0} sx={{ bgcolor: '#0f172a', borderBottom: '1px solid #1e293b' }}>
      <Toolbar sx={{ justifyContent: 'space-between', py: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 44,
              height: 44,
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              color: '#fff',
              boxShadow: '0 4px 12px rgba(37, 99, 235, 0.4)',
            }}
          >
            <LocalShippingIcon sx={{ fontSize: 26 }} />
          </Box>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
                SPOTTER <span style={{ color: '#60a5fa' }}>ELD</span>
              </Typography>
              <Chip
                icon={<VerifiedIcon sx={{ fontSize: '14px !important', color: '#10b981 !important' }} />}
                label="FMCSA 70h/8d Compliant"
                size="small"
                sx={{
                  bgcolor: 'rgba(16, 185, 129, 0.12)',
                  color: '#34d399',
                  border: '1px solid rgba(16, 185, 129, 0.25)',
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  height: 24,
                }}
              />
            </Box>
            <Typography variant="caption" sx={{ color: '#94a3b8', display: 'block', mt: -0.2 }}>
              Commercial Trip Planner & 24-Hour Driver's Daily Log Generator
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {hasData && onPrint && (
            <Tooltip title="Print / Export Daily Log Sheets">
              <IconButton
                onClick={onPrint}
                sx={{
                  color: '#f8fafc',
                  bgcolor: 'rgba(255, 255, 255, 0.08)',
                  '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.16)' },
                  borderRadius: 2,
                  px: 1.5,
                  gap: 0.8,
                  fontSize: '0.85rem',
                }}
              >
                <PrintIcon fontSize="small" />
                <Typography variant="body2" sx={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  Print Log Sheets
                </Typography>
              </IconButton>
            </Tooltip>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};
