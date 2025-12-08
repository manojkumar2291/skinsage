/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0d9488', // teal-600
          dark: '#0f766e',    // teal-700
          light: '#f0fdfa',   // teal-50
        },
        secondary: {
          DEFAULT: '#3b82f6', // blue-500
          dark: '#2563eb',    // blue-600
        },
        success: '#22c55e',
        warning: '#f59e0b',
        error: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
