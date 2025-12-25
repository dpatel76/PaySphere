/**
 * Date Range Filter Component
 * Provides date range selection for filtering dashboard data
 */
import React, { useState, useCallback } from 'react';
import {
  Box,
  Button,
  ButtonGroup,
  Popover,
  TextField,
  Typography,
  Stack,
} from '@mui/material';
import {
  CalendarMonth as CalendarIcon,
  Today as TodayIcon,
} from '@mui/icons-material';
import { colors } from '../../styles/design-system';

export type DatePreset = 'today' | 'last7days' | 'last30days' | 'custom';

export interface DateRange {
  startDate: Date;
  endDate: Date;
  preset: DatePreset;
}

interface DateRangeFilterProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
}

// Helper to get start of day
const startOfDay = (date: Date): Date => {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
};

// Helper to get end of day
const endOfDay = (date: Date): Date => {
  const d = new Date(date);
  d.setHours(23, 59, 59, 999);
  return d;
};

// Get date range for preset
export const getDateRangeForPreset = (preset: DatePreset): DateRange => {
  const now = new Date();
  const today = startOfDay(now);
  const endOfToday = endOfDay(now);

  switch (preset) {
    case 'today':
      return { startDate: today, endDate: endOfToday, preset };
    case 'last7days':
      const last7 = new Date(today);
      last7.setDate(last7.getDate() - 6);
      return { startDate: last7, endDate: endOfToday, preset };
    case 'last30days':
      const last30 = new Date(today);
      last30.setDate(last30.getDate() - 29);
      return { startDate: last30, endDate: endOfToday, preset };
    default:
      return { startDate: today, endDate: endOfToday, preset: 'today' };
  }
};

// Convert date range to hours_back for API compatibility
export const dateRangeToHoursBack = (range: DateRange): number => {
  const now = new Date();
  const diffMs = now.getTime() - range.startDate.getTime();
  const hours = Math.ceil(diffMs / (1000 * 60 * 60));
  return Math.max(1, hours);
};

// Format date for display
const formatDateDisplay = (range: DateRange): string => {
  const formatDate = (d: Date) =>
    d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  if (range.preset === 'today') {
    return 'Today';
  }
  if (range.preset === 'last7days') {
    return 'Last 7 Days';
  }
  if (range.preset === 'last30days') {
    return 'Last 30 Days';
  }

  const start = formatDate(range.startDate);
  const end = formatDate(range.endDate);
  return start === end ? start : `${start} - ${end}`;
};

const DateRangeFilter: React.FC<DateRangeFilterProps> = ({ value, onChange }) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [customStart, setCustomStart] = useState<string>('');
  const [customEnd, setCustomEnd] = useState<string>('');

  const handlePresetClick = useCallback((preset: DatePreset) => {
    onChange(getDateRangeForPreset(preset));
    setAnchorEl(null);
  }, [onChange]);

  const handleCustomApply = useCallback(() => {
    if (customStart && customEnd) {
      onChange({
        startDate: startOfDay(new Date(customStart)),
        endDate: endOfDay(new Date(customEnd)),
        preset: 'custom',
      });
      setAnchorEl(null);
    }
  }, [customStart, customEnd, onChange]);

  const handleOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
    // Initialize custom dates with current selection
    setCustomStart(value.startDate.toISOString().split('T')[0]);
    setCustomEnd(value.endDate.toISOString().split('T')[0]);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  return (
    <Box>
      <Button
        variant="outlined"
        startIcon={<CalendarIcon />}
        onClick={handleOpen}
        sx={{
          borderColor: colors.grey[300],
          color: colors.grey[700],
          textTransform: 'none',
          '&:hover': {
            borderColor: colors.primary.main,
            backgroundColor: colors.primary.light + '10',
          },
        }}
      >
        {formatDateDisplay(value)}
      </Button>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        sx={{ mt: 1 }}
      >
        <Box sx={{ p: 2, minWidth: 280 }}>
          {/* Preset Buttons */}
          <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
            Quick Select
          </Typography>
          <ButtonGroup orientation="vertical" fullWidth sx={{ mb: 2 }}>
            <Button
              variant={value.preset === 'today' ? 'contained' : 'outlined'}
              startIcon={<TodayIcon />}
              onClick={() => handlePresetClick('today')}
              sx={{ justifyContent: 'flex-start' }}
            >
              Today
            </Button>
            <Button
              variant={value.preset === 'last7days' ? 'contained' : 'outlined'}
              onClick={() => handlePresetClick('last7days')}
              sx={{ justifyContent: 'flex-start' }}
            >
              Last 7 Days
            </Button>
            <Button
              variant={value.preset === 'last30days' ? 'contained' : 'outlined'}
              onClick={() => handlePresetClick('last30days')}
              sx={{ justifyContent: 'flex-start' }}
            >
              Last 30 Days
            </Button>
          </ButtonGroup>

          {/* Custom Date Range */}
          <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
            Custom Range
          </Typography>
          <Stack spacing={2}>
            <TextField
              label="Start Date"
              type="date"
              size="small"
              value={customStart}
              onChange={(e) => setCustomStart(e.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
            <TextField
              label="End Date"
              type="date"
              size="small"
              value={customEnd}
              onChange={(e) => setCustomEnd(e.target.value)}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
            <Button
              variant="contained"
              onClick={handleCustomApply}
              disabled={!customStart || !customEnd}
              fullWidth
            >
              Apply Custom Range
            </Button>
          </Stack>
        </Box>
      </Popover>
    </Box>
  );
};

export default DateRangeFilter;
