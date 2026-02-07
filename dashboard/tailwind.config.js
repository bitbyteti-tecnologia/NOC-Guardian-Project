/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        noc: {
          900: '#0f172a', // Background dark
          800: '#1e293b', // Card bg
          700: '#334155', // Border
          100: '#f1f5f9', // Text
          accent: '#3b82f6', // Primary brand
          success: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444',
        }
      }
    },
  },
  plugins: [],
}
