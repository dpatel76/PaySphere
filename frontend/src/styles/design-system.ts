/**
 * GPS CDM Design System
 * Based on SynapseDTE2 patterns with Deloitte brand colors
 */

export const colors = {
  // Primary - Deloitte Teal
  primary: {
    main: '#0E7C7B',
    light: '#17A398',
    dark: '#0A5A59',
    contrastText: '#FFFFFF',
  },
  // Secondary - Deloitte Blue
  secondary: {
    main: '#62B5E5',
    light: '#8AC5ED',
    dark: '#3A9BD8',
    contrastText: '#FFFFFF',
  },
  // Semantic Colors
  success: {
    main: '#4CAF50',
    light: '#81C784',
    dark: '#388E3C',
    contrastText: '#FFFFFF',
  },
  warning: {
    main: '#FF9800',
    light: '#FFB74D',
    dark: '#F57C00',
    contrastText: '#000000',
  },
  error: {
    main: '#F44336',
    light: '#E57373',
    dark: '#D32F2F',
    contrastText: '#FFFFFF',
  },
  info: {
    main: '#2196F3',
    light: '#64B5F6',
    dark: '#1976D2',
    contrastText: '#FFFFFF',
  },
  // Pipeline Zone Colors
  zones: {
    bronze: {
      main: '#CD7F32',
      light: '#DAA06D',
      dark: '#8B4513',
    },
    silver: {
      main: '#C0C0C0',
      light: '#D3D3D3',
      dark: '#A9A9A9',
    },
    gold: {
      main: '#FFD700',
      light: '#FFEC8B',
      dark: '#DAA520',
    },
    analytical: {
      main: '#9370DB',
      light: '#B19CD9',
      dark: '#663399',
    },
  },
  // Status Colors
  status: {
    pending: '#FFA726',
    processing: '#42A5F5',
    completed: '#66BB6A',
    failed: '#EF5350',
    warning: '#FFCA28',
  },
  // Neutrals
  grey: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
  // Background
  background: {
    default: '#FAFAFA',
    paper: '#FFFFFF',
    dark: '#121212',
  },
  // Text
  text: {
    primary: 'rgba(0, 0, 0, 0.87)',
    secondary: 'rgba(0, 0, 0, 0.6)',
    disabled: 'rgba(0, 0, 0, 0.38)',
    hint: 'rgba(0, 0, 0, 0.38)',
  },
};

export const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: { fontSize: '2.5rem', fontWeight: 700, lineHeight: 1.2 },
  h2: { fontSize: '2rem', fontWeight: 600, lineHeight: 1.3 },
  h3: { fontSize: '1.75rem', fontWeight: 600, lineHeight: 1.3 },
  h4: { fontSize: '1.5rem', fontWeight: 600, lineHeight: 1.4 },
  h5: { fontSize: '1.25rem', fontWeight: 600, lineHeight: 1.4 },
  h6: { fontSize: '1rem', fontWeight: 600, lineHeight: 1.5 },
  body1: { fontSize: '1rem', fontWeight: 400, lineHeight: 1.5 },
  body2: { fontSize: '0.875rem', fontWeight: 400, lineHeight: 1.5 },
  caption: { fontSize: '0.75rem', fontWeight: 400, lineHeight: 1.5 },
  button: { fontSize: '0.875rem', fontWeight: 500, textTransform: 'none' as const },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const borderRadius = {
  xs: 2,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  round: '50%',
};

export const shadows = {
  none: 'none',
  xs: '0 1px 2px rgba(0,0,0,0.05)',
  sm: '0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)',
  md: '0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)',
  lg: '0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)',
  xl: '0 20px 25px rgba(0,0,0,0.1), 0 10px 10px rgba(0,0,0,0.04)',
};

export const transitions = {
  fast: '150ms ease-in-out',
  normal: '250ms ease-in-out',
  slow: '350ms ease-in-out',
};

// Pipeline flow constants
export const pipelineConfig = {
  layers: ['bronze', 'silver', 'gold', 'analytical'] as const,
  layerNames: {
    bronze: 'Bronze (Raw)',
    silver: 'Silver (Cleansed)',
    gold: 'Gold (CDM)',
    analytical: 'Analytical',
  },
  layerDescriptions: {
    bronze: 'Raw ingested messages with minimal transformation',
    silver: 'Validated and cleansed payment instructions',
    gold: 'Unified CDM entities ready for downstream',
    analytical: 'Aggregated views for reporting',
  },
};
