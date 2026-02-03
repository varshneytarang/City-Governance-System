/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: '#1e3a5f',
          darkBlue: '#2c5282',
          blue: '#3b82f6',
          lightBlue: '#60a5fa',
          slate: '#334155',
          darkGray: '#1f2937',
          gray: '#6b7280',
          lightGray: '#9ca3af',
        },
        accent: {
          gold: '#d4af37',
          lightGold: '#f0d98f',
          bronze: '#cd7f32',
          silver: '#c0c0c0',
        },
        professional: {
          green: '#10b981',
          teal: '#14b8a6',
          indigo: '#6366f1',
          purple: '#8b5cf6',
        },
        neutral: {
          white: '#ffffff',
          offWhite: '#f8fafc',
          cream: '#fefcf9',
          lightBg: '#f1f5f9',
        }
      },
      fontFamily: {
        display: ['Inter', 'system-ui', 'sans-serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Playfair Display', 'serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 20s linear infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'slide-up': 'slideUp 0.6s ease-out',
        'slide-in': 'slideIn 0.8s ease-out',
        'fade-in': 'fadeIn 0.5s ease-out',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 20px rgba(0, 212, 255, 0.5)' },
          '50%': { opacity: '0.8', boxShadow: '0 0 40px rgba(0, 212, 255, 0.8)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(100px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-100px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'subtle': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'soft': '0 4px 16px rgba(0, 0, 0, 0.12)',
        'professional': '0 8px 24px rgba(0, 0, 0, 0.15)',
        'elevated': '0 12px 32px rgba(0, 0, 0, 0.18)',
        'gold-glow': '0 0 24px rgba(212, 175, 55, 0.3)',
        'blue-glow': '0 0 20px rgba(59, 130, 246, 0.25)',
      }
    },
  },
  plugins: [],
}
