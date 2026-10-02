import React, { useMemo } from 'react';
import { Box, Typography } from '@mui/material';
import type { LogSegment } from '../../types/trip';

interface EldGridCanvasProps {
  segments: LogSegment[];
  totals: {
    off_duty: number;
    sleeper_berth: number;
    driving: number;
    on_duty_not_driving: number;
    total_hours: number;
  };
}

const ROW_LABELS = [
  { line: 1, label: '1. Off Duty', key: 'off_duty' },
  { line: 2, label: '2. Sleeper Berth', key: 'sleeper_berth' },
  { line: 3, label: '3. Driving', key: 'driving' },
  { line: 4, label: '4. On Duty (not driving)', key: 'on_duty_not_driving' },
];

export const EldGridCanvas: React.FC<EldGridCanvasProps> = ({ segments, totals }) => {
  // SVG Dimensions & Layout Constants
  const width = 1000;
  const height = 230;

  const leftMargin = 160;  // Space for row label text
  const rightMargin = 90;  // Space for totals column
  const topMargin = 38;    // Space for header hour numbers
  const bottomMargin = 12;

  const gridWidth = width - leftMargin - rightMargin;
  const gridHeight = height - topMargin - bottomMargin;

  const rowHeight = gridHeight / 4.0;
  const hourWidth = gridWidth / 24.0;
  const quarterWidth = hourWidth / 4.0;

  // Row Y center coordinates
  const getRowY = (lineNumber: number): number => {
    return topMargin + (lineNumber - 0.5) * rowHeight;
  };

  // Convert hour of day (0.0 to 24.0) to SVG X coordinate
  const getX = (hour: number): number => {
    const clamped = Math.max(0.0, Math.min(24.0, hour));
    return leftMargin + clamped * hourWidth;
  };

  // Build the unbroken step path across the 24 hours
  const { pathD, transitionPoints } = useMemo(() => {
    if (!segments || segments.length === 0) return { pathD: '', transitionPoints: [] };

    // Sort segments by start hour
    const sorted = [...segments].sort((a, b) => a.start_hour - b.start_hour);

    let d = '';
    const points: { x: number; y: number; label: string; time: string; status: string }[] = [];

    sorted.forEach((seg, idx) => {
      const xStart = getX(seg.start_hour);
      const xEnd = getX(seg.end_hour);
      const y = getRowY(seg.line_number);

      const startTimeStr = new Date(seg.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      if (idx === 0) {
        d += `M ${xStart} ${y}`;
        points.push({ x: xStart, y, label: seg.activity, time: startTimeStr, status: seg.duty_status });
      } else {
        // Vertical step transition to this row
        d += ` L ${xStart} ${y}`;
        points.push({ x: xStart, y, label: seg.activity, time: startTimeStr, status: seg.duty_status });
      }

      // Horizontal line across the segment duration
      d += ` L ${xEnd} ${y}`;
    });

    return { pathD: d, transitionPoints: points };
  }, [segments]);

  // Hourly header labels
  const hourHeaders = [
    'Mid-night', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
    'Noon', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', 'Mid-night'
  ];

  return (
    <Box sx={{ width: '100%', overflowX: 'auto', bgcolor: '#ffffff', p: 1.5, borderRadius: 2 }}>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', minWidth: 880, height: 'auto', display: 'block' }}
      >
        <defs>
          <linearGradient id="headerGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#1e293b" />
            <stop offset="100%" stopColor="#0f172a" />
          </linearGradient>
          <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
            <feDropShadow dx="0" dy="1" stdDeviation="1" floodOpacity="0.25" />
          </filter>
        </defs>

        {/* 1. Header Bar (Black Banner matching official FMCSA log) */}
        <rect
          x={leftMargin}
          y={4}
          width={gridWidth}
          height={topMargin - 6}
          fill="url(#headerGrad)"
          rx={4}
        />
        <rect
          x={width - rightMargin + 4}
          y={4}
          width={rightMargin - 8}
          height={topMargin - 6}
          fill="url(#headerGrad)"
          rx={4}
        />
        <text
          x={width - rightMargin / 2}
          y={23}
          fill="#ffffff"
          fontSize="11"
          fontWeight="700"
          textAnchor="middle"
          fontFamily="system-ui, sans-serif"
        >
          Total Hours
        </text>

        {/* Header Hour Numbers */}
        {hourHeaders.map((hdr, i) => {
          const x = leftMargin + i * hourWidth;
          const isMid = i === 0 || i === 24;
          const isNoon = i === 12;

          return (
            <text
              key={i}
              x={x}
              y={isMid ? 18 : 23}
              fill="#ffffff"
              fontSize={isMid ? '8.5' : isNoon ? '10' : '9.5'}
              fontWeight={isMid || isNoon ? '700' : '500'}
              textAnchor="middle"
              fontFamily="system-ui, sans-serif"
            >
              {isMid ? (
                <>
                  <tspan x={x} dy="0">Mid-</tspan>
                  <tspan x={x} dy="9">night</tspan>
                </>
              ) : (
                hdr
              )}
            </text>
          );
        })}

        {/* 2. Grid Background & Row Bands */}
        {ROW_LABELS.map((row, idx) => {
          const y = topMargin + idx * rowHeight;
          const isEven = idx % 2 === 0;

          return (
            <g key={row.line}>
              {/* Row Label on Left */}
              <text
                x={leftMargin - 12}
                y={y + rowHeight / 2 + 4}
                fill="#1e293b"
                fontSize="11.5"
                fontWeight="700"
                textAnchor="end"
                fontFamily="system-ui, sans-serif"
              >
                {row.label}
              </text>

              {/* Row Cell Background */}
              <rect
                x={leftMargin}
                y={y}
                width={gridWidth}
                height={rowHeight}
                fill={isEven ? '#ffffff' : '#f8fafc'}
                stroke="#cbd5e1"
                strokeWidth="0.8"
              />

              {/* Totals Box on Right */}
              <rect
                x={width - rightMargin + 4}
                y={y}
                width={rightMargin - 8}
                height={rowHeight}
                fill={isEven ? '#f1f5f9' : '#e2e8f0'}
                stroke="#cbd5e1"
                strokeWidth="0.8"
                rx={2}
              />
              <text
                x={width - rightMargin / 2}
                y={y + rowHeight / 2 + 5}
                fill="#0f172a"
                fontSize="13"
                fontWeight="700"
                textAnchor="middle"
                fontFamily="'JetBrains Mono', monospace"
              >
                {(totals[row.key as keyof typeof totals] as number).toFixed(2)}
              </text>
            </g>
          );
        })}

        {/* 3. Grid Vertical Lines & 15-Minute Sub-ticks */}
        {Array.from({ length: 24 }).map((_, hour) => {
          const hourX = leftMargin + hour * hourWidth;

          return (
            <g key={hour}>
              {/* Major Hour Line (Full Height) */}
              <line
                x1={hourX}
                y1={topMargin}
                x2={hourX}
                y2={topMargin + gridHeight}
                stroke="#94a3b8"
                strokeWidth="1.2"
              />

              {/* 15, 30, 45 Minute Ticks inside each row */}
              {ROW_LABELS.map((_, rIdx) => {
                const rowTop = topMargin + rIdx * rowHeight;
                const rowBottom = rowTop + rowHeight;

                return (
                  <g key={rIdx}>
                    {/* 15 min tick (top & bottom) */}
                    <line
                      x1={hourX + quarterWidth}
                      y1={rowTop}
                      x2={hourX + quarterWidth}
                      y2={rowTop + 5}
                      stroke="#cbd5e1"
                      strokeWidth="0.8"
                    />
                    <line
                      x1={hourX + quarterWidth}
                      y1={rowBottom - 5}
                      x2={hourX + quarterWidth}
                      y2={rowBottom}
                      stroke="#cbd5e1"
                      strokeWidth="0.8"
                    />

                    {/* 30 min tick (medium height) */}
                    <line
                      x1={hourX + 2 * quarterWidth}
                      y1={rowTop}
                      x2={hourX + 2 * quarterWidth}
                      y2={rowTop + 9}
                      stroke="#94a3b8"
                      strokeWidth="1"
                    />
                    <line
                      x1={hourX + 2 * quarterWidth}
                      y1={rowBottom - 9}
                      x2={hourX + 2 * quarterWidth}
                      y2={rowBottom}
                      stroke="#94a3b8"
                      strokeWidth="1"
                    />

                    {/* 45 min tick (top & bottom) */}
                    <line
                      x1={hourX + 3 * quarterWidth}
                      y1={rowTop}
                      x2={hourX + 3 * quarterWidth}
                      y2={rowTop + 5}
                      stroke="#cbd5e1"
                      strokeWidth="0.8"
                    />
                    <line
                      x1={hourX + 3 * quarterWidth}
                      y1={rowBottom - 5}
                      x2={hourX + 3 * quarterWidth}
                      y2={rowBottom}
                      stroke="#cbd5e1"
                      strokeWidth="0.8"
                    />
                  </g>
                );
              })}
            </g>
          );
        })}

        {/* Final 24th Hour Line (Midnight) */}
        <line
          x1={leftMargin + gridWidth}
          y1={topMargin}
          x2={leftMargin + gridWidth}
          y2={topMargin + gridHeight}
          stroke="#94a3b8"
          strokeWidth="1.2"
        />

        {/* 4. Plotted Duty Status Path (Bold Blue Continuous Stepping Line) */}
        {pathD && (
          <>
            {/* Soft Shadow under path */}
            <path
              d={pathD}
              fill="none"
              stroke="#2563eb"
              strokeWidth="4"
              strokeOpacity="0.2"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {/* Crisp Ink Path */}
            <path
              d={pathD}
              fill="none"
              stroke="#1d4ed8"
              strokeWidth="2.8"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          </>
        )}

        {/* Transition Point Markers */}
        {transitionPoints.map((pt, idx) => (
          <g key={idx}>
            <circle
              cx={pt.x}
              cy={pt.y}
              r="3.5"
              fill="#1d4ed8"
              stroke="#ffffff"
              strokeWidth="1.5"
            />
          </g>
        ))}
      </svg>

      {/* Grid Footer Notes */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1, px: 1 }}>
        <Typography variant="caption" sx={{ color: '#64748b' }}>
          * Each sub-division tick marks 15 minutes. Stepped blue line represents continuous Record of Duty Status (RODS).
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 700, color: '#0f172a' }}>
            Daily Hours Sum:
          </Typography>
          <Typography
            variant="caption"
            sx={{
              fontWeight: 800,
              fontFamily: "'JetBrains Mono', monospace",
              color: Math.abs(totals.total_hours - 24.0) < 0.1 ? '#16a34a' : '#dc2626',
              bgcolor: Math.abs(totals.total_hours - 24.0) < 0.1 ? 'rgba(22, 163, 74, 0.1)' : 'rgba(220, 38, 38, 0.1)',
              px: 1,
              py: 0.2,
              borderRadius: 1,
            }}
          >
            {totals.total_hours.toFixed(2)} / 24.00 Hours
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};
