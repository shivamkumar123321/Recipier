export const designTokens = {
    colors: {
        primary: {
            DEFAULT: '#6366F1', // Indigo 500
            foreground: '#FFFFFF',
            50: '#EEF2FF',
            100: '#E0E7FF',
            200: '#C7D2FE',
            300: '#A5B4FC',
            400: '#818CF8',
            500: '#6366F1',
            600: '#4F46E5',
            700: '#4338CA',
            800: '#3730A3',
            900: '#312E81',
        },
        secondary: {
            DEFAULT: '#10B981', // Emerald 500
            foreground: '#FFFFFF',
            50: '#ECFDF5',
            100: '#D1FAE5',
            200: '#A7F3D0',
            300: '#6EE7B7',
            400: '#34D399',
            500: '#10B981',
            600: '#059669',
            700: '#047857',
            800: '#065F46',
            900: '#064E3B',
        },
        neutral: {
            50: '#F9FAFB',
            100: '#F3F4F6',
            200: '#E5E7EB',
            300: '#D1D5DB',
            400: '#9CA3AF',
            500: '#6B7280',
            600: '#4B5563',
            700: '#374151',
            800: '#1F2937',
            900: '#111827',
        },
        success: {
            DEFAULT: '#10B981', // Emerald 500
            foreground: '#FFFFFF',
        },
        warning: {
            DEFAULT: '#F59E0B', // Amber 500
            foreground: '#FFFFFF',
        },
        error: {
            DEFAULT: '#EF4444', // Red 500
            foreground: '#FFFFFF',
        },
        background: '#F9FAFB', // Light gray
        foreground: '#1F2937', // Dark gray
        card: '#FFFFFF',
        cardForeground: '#1F2937',
    },
    typography: {
        fontFamily: {
            sans: ['Inter', 'system-ui', 'sans-serif'],
        },
        fontSize: {
            xs: '0.75rem',
            sm: '0.875rem',
            base: '1rem',
            lg: '1.125rem',
            xl: '1.25rem',
            '2xl': '1.5rem',
            '3xl': '1.875rem',
            '4xl': '2.25rem',
        },
    },
    spacing: {
        container: {
            padding: '2rem',
            maxWidth: '1280px',
        },
    },
    borderRadius: {
        sm: '0.375rem', // 6px
        md: '0.5rem',   // 8px
        lg: '0.75rem',  // 12px
        full: '9999px',
    },
    shadows: {
        sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    },
};
