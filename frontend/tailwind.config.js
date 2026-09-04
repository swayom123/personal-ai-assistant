/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0B0F17',
        surface: {
          DEFAULT: '#111827',
          elevated: '#1F2937',
          subtle: '#161F30',
        },
        border: {
          DEFAULT: '#1F2937',
          subtle: '#374151',
          accent: '#4B5563',
        },
        primary: {
          DEFAULT: '#6366F1',
          hover: '#4F46E5',
          muted: 'rgba(99, 102, 241, 0.15)',
        },
        accent: {
          emerald: '#10B981',
          cyan: '#06B6D4',
          violet: '#8B5CF6',
          amber: '#F59E0B',
        },
        text: {
          primary: '#F9FAFB',
          secondary: '#9CA3AF',
          muted: '#6B7280',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
