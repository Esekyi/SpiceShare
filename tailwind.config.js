/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        success: '#4CAF50', // Green for success messages
        info: '#2196F3',    // Blue for info messages
        warning: '#FF9800', // Orange for warning messages
        primary: {
          DEFAULT: '#FF6B6B',
          dark: '#E05A5A',
        },
        secondary: {
          DEFAULT: '#4ECDC4',
          dark: '#3DBCB3',
        },
        background: '#F7FFF7',
        text: '#1A535C',
        accent: '#FFE66D',
        error: '#FF6B6B',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  safelist: [
    'bg-success',
    'bg-info',
    'bg-warning',
    'bg-error',
    'bg-primary',
    'bg-secondary',
    // add any other dynamic classes you might use
  ],
  plugins: [],
}
