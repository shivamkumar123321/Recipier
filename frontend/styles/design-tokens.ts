/**
 * Design Tokens for Weight Coach
 *
 * Centralized design system tokens for consistent UI/UX across the application.
 * These tokens define the visual language of the Weight Coach brand.
 *
 * Usage:
 * import { colors, typography, spacing } from '@/styles/design-tokens';
 */

// ============================================================================
// COLOR PALETTE
// ============================================================================

export const colors = {
  // Primary Colors - Health & Nutrition Theme (Green/Teal)
  primary: {
    50: '#e6f7f5',
    100: '#b3e8e0',
    200: '#80d9cb',
    300: '#4dcab6',
    400: '#26bda7',
    500: '#00b098', // Main brand color
    600: '#00a389',
    700: '#009276',
    800: '#008163',
    900: '#006142',
  },

  // Secondary Colors - Energy & Food Theme (Orange)
  secondary: {
    50: '#fff3e6',
    100: '#ffddb3',
    200: '#ffc780',
    300: '#ffb14d',
    400: '#ffa026',
    500: '#ff8f00', // Main accent color
    600: '#f58300',
    700: '#e67300',
    800: '#d66300',
    900: '#b84700',
  },

  // Success - Positive feedback, achievements
  success: {
    50: '#e8f5e9',
    100: '#c8e6c9',
    200: '#a5d6a7',
    300: '#81c784',
    400: '#66bb6a',
    500: '#4caf50',
    600: '#43a047',
    700: '#388e3c',
    800: '#2e7d32',
    900: '#1b5e20',
  },

  // Warning - Alerts, notifications
  warning: {
    50: '#fff8e1',
    100: '#ffecb3',
    200: '#ffe082',
    300: '#ffd54f',
    400: '#ffca28',
    500: '#ffc107',
    600: '#ffb300',
    700: '#ffa000',
    800: '#ff8f00',
    900: '#ff6f00',
  },

  // Error - Validation errors, destructive actions
  error: {
    50: '#ffebee',
    100: '#ffcdd2',
    200: '#ef9a9a',
    300: '#e57373',
    400: '#ef5350',
    500: '#f44336',
    600: '#e53935',
    700: '#d32f2f',
    800: '#c62828',
    900: '#b71c1c',
  },

  // Info - Informational messages
  info: {
    50: '#e3f2fd',
    100: '#bbdefb',
    200: '#90caf9',
    300: '#64b5f6',
    400: '#42a5f5',
    500: '#2196f3',
    600: '#1e88e5',
    700: '#1976d2',
    800: '#1565c0',
    900: '#0d47a1',
  },

  // Neutral Colors - Backgrounds, text, borders
  neutral: {
    0: '#ffffff',
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
    1000: '#000000',
  },

  // Semantic Colors - Context-specific usage
  background: {
    default: '#ffffff',
    subtle: '#fafafa',
    muted: '#f5f5f5',
    overlay: 'rgba(0, 0, 0, 0.5)',
  },

  text: {
    primary: '#212121',
    secondary: '#616161',
    tertiary: '#9e9e9e',
    disabled: '#bdbdbd',
    inverse: '#ffffff',
  },

  border: {
    default: '#e0e0e0',
    subtle: '#eeeeee',
    strong: '#bdbdbd',
    focus: '#00b098',
  },

  // Nutrition-specific colors
  nutrition: {
    protein: '#ff6b6b',    // Red
    carbs: '#4ecdc4',      // Teal
    fats: '#ffe66d',       // Yellow
    fiber: '#95e1d3',      // Light green
    sugar: '#ffa07a',      // Light orange
    sodium: '#dda15e',     // Brown
    calories: '#ff8f00',   // Orange (secondary)
  },

  // Chart colors for data visualization
  chart: {
    1: '#00b098',  // Primary
    2: '#ff8f00',  // Secondary
    3: '#4caf50',  // Success
    4: '#2196f3',  // Info
    5: '#ffc107',  // Warning
    6: '#9c27b0',  // Purple
    7: '#ff5722',  // Deep orange
    8: '#009688',  // Teal
  },
} as const;

// ============================================================================
// TYPOGRAPHY
// ============================================================================

export const typography = {
  // Font Families
  fontFamily: {
    sans: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
    mono: '"Fira Code", "Roboto Mono", "Courier New", monospace',
    display: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
  },

  // Font Sizes (rem-based for accessibility)
  fontSize: {
    xs: '0.75rem',      // 12px
    sm: '0.875rem',     // 14px
    base: '1rem',       // 16px
    lg: '1.125rem',     // 18px
    xl: '1.25rem',      // 20px
    '2xl': '1.5rem',    // 24px
    '3xl': '1.875rem',  // 30px
    '4xl': '2.25rem',   // 36px
    '5xl': '3rem',      // 48px
    '6xl': '3.75rem',   // 60px
    '7xl': '4.5rem',    // 72px
  },

  // Font Weights
  fontWeight: {
    thin: 100,
    extralight: 200,
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },

  // Line Heights
  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },

  // Letter Spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },

  // Text Styles - Pre-defined combinations
  textStyles: {
    // Display text (hero sections)
    displayLarge: {
      fontSize: '3.75rem',  // 60px
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.025em',
    },
    displayMedium: {
      fontSize: '3rem',     // 48px
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.025em',
    },
    displaySmall: {
      fontSize: '2.25rem',  // 36px
      fontWeight: 600,
      lineHeight: 1.25,
      letterSpacing: '-0.025em',
    },

    // Headings
    h1: {
      fontSize: '2.25rem',  // 36px
      fontWeight: 700,
      lineHeight: 1.25,
      letterSpacing: '-0.025em',
    },
    h2: {
      fontSize: '1.875rem', // 30px
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.025em',
    },
    h3: {
      fontSize: '1.5rem',   // 24px
      fontWeight: 600,
      lineHeight: 1.35,
      letterSpacing: '0',
    },
    h4: {
      fontSize: '1.25rem',  // 20px
      fontWeight: 600,
      lineHeight: 1.4,
      letterSpacing: '0',
    },
    h5: {
      fontSize: '1.125rem', // 18px
      fontWeight: 600,
      lineHeight: 1.45,
      letterSpacing: '0',
    },
    h6: {
      fontSize: '1rem',     // 16px
      fontWeight: 600,
      lineHeight: 1.5,
      letterSpacing: '0',
    },

    // Body text
    bodyLarge: {
      fontSize: '1.125rem', // 18px
      fontWeight: 400,
      lineHeight: 1.625,
      letterSpacing: '0',
    },
    body: {
      fontSize: '1rem',     // 16px
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0',
    },
    bodySmall: {
      fontSize: '0.875rem', // 14px
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0',
    },

    // Labels and captions
    label: {
      fontSize: '0.875rem', // 14px
      fontWeight: 500,
      lineHeight: 1.25,
      letterSpacing: '0.025em',
    },
    caption: {
      fontSize: '0.75rem',  // 12px
      fontWeight: 400,
      lineHeight: 1.5,
      letterSpacing: '0.025em',
    },
    overline: {
      fontSize: '0.75rem',  // 12px
      fontWeight: 600,
      lineHeight: 1.5,
      letterSpacing: '0.1em',
      textTransform: 'uppercase' as const,
    },

    // Button text
    button: {
      fontSize: '0.875rem', // 14px
      fontWeight: 600,
      lineHeight: 1.25,
      letterSpacing: '0.025em',
    },
    buttonLarge: {
      fontSize: '1rem',     // 16px
      fontWeight: 600,
      lineHeight: 1.25,
      letterSpacing: '0.025em',
    },
  },
} as const;

// ============================================================================
// SPACING
// ============================================================================

/**
 * 8px-based spacing scale for consistent layout rhythm
 * Use these values for padding, margin, gap, etc.
 */
export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  7: '1.75rem',   // 28px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  14: '3.5rem',   // 56px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
  28: '7rem',     // 112px
  32: '8rem',     // 128px
  36: '9rem',     // 144px
  40: '10rem',    // 160px
  48: '12rem',    // 192px
  56: '14rem',    // 224px
  64: '16rem',    // 256px
} as const;

// Semantic spacing values
export const spacingSemantics = {
  containerPadding: spacing[4],        // 16px
  sectionSpacing: spacing[16],         // 64px
  componentGap: spacing[4],            // 16px
  inputPadding: spacing[3],            // 12px
  buttonPadding: `${spacing[3]} ${spacing[6]}`, // 12px 24px
  cardPadding: spacing[6],             // 24px
} as const;

// ============================================================================
// BORDER RADIUS
// ============================================================================

export const borderRadius = {
  none: '0',
  sm: '0.25rem',   // 4px
  base: '0.5rem',  // 8px
  md: '0.75rem',   // 12px
  lg: '1rem',      // 16px
  xl: '1.5rem',    // 24px
  '2xl': '2rem',   // 32px
  full: '9999px',  // Circular
} as const;

// ============================================================================
// SHADOWS
// ============================================================================

export const shadows = {
  // Elevation shadows
  none: 'none',
  xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
  base: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
  md: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
  lg: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
  xl: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  '2xl': '0 50px 100px -20px rgba(0, 0, 0, 0.25)',

  // Inner shadow
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',

  // Focus rings
  focusRing: '0 0 0 3px rgba(0, 176, 152, 0.2)',
  focusRingError: '0 0 0 3px rgba(244, 67, 54, 0.2)',
} as const;

// ============================================================================
// Z-INDEX
// ============================================================================

/**
 * Z-index scale for layering elements
 * Use these values to maintain consistent stacking order
 */
export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
  toast: 1080,
} as const;

// ============================================================================
// TRANSITIONS
// ============================================================================

export const transitions = {
  // Duration
  duration: {
    instant: '0ms',
    fast: '150ms',
    base: '200ms',
    slow: '300ms',
    slower: '500ms',
  },

  // Timing functions
  timing: {
    linear: 'linear',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },

  // Pre-defined transitions
  default: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
  fade: 'opacity 200ms cubic-bezier(0.4, 0, 0.2, 1)',
  scale: 'transform 200ms cubic-bezier(0.4, 0, 0.2, 1)',
  slide: 'transform 300ms cubic-bezier(0.4, 0, 0.2, 1)',
  color: 'color 150ms cubic-bezier(0.4, 0, 0.2, 1), background-color 150ms cubic-bezier(0.4, 0, 0.2, 1)',
} as const;

// ============================================================================
// BREAKPOINTS
// ============================================================================

/**
 * Responsive breakpoints for mobile-first design
 */
export const breakpoints = {
  xs: '0px',      // Extra small devices (phones, portrait)
  sm: '640px',    // Small devices (phones, landscape)
  md: '768px',    // Medium devices (tablets)
  lg: '1024px',   // Large devices (desktops)
  xl: '1280px',   // Extra large devices (large desktops)
  '2xl': '1536px', // 2X large devices (larger desktops)
} as const;

// ============================================================================
// CONTAINER WIDTHS
// ============================================================================

export const containerWidths = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1400px',
  full: '100%',
} as const;

// ============================================================================
// UTILITY EXPORTS
// ============================================================================

/**
 * Export all design tokens as a single object
 */
export const designTokens = {
  colors,
  typography,
  spacing,
  spacingSemantics,
  borderRadius,
  shadows,
  zIndex,
  transitions,
  breakpoints,
  containerWidths,
} as const;

/**
 * Type exports for TypeScript consumers
 */
export type ColorToken = keyof typeof colors;
export type SpacingToken = keyof typeof spacing;
export type ShadowToken = keyof typeof shadows;
export type TransitionToken = keyof typeof transitions.duration;

export default designTokens;
