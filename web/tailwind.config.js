/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#F26522',
          dark: '#D94F1A',
          light: '#FF8A5B',
        },
        success: {
          DEFAULT: '#10B981',
          light: '#34D399',
        },
        warning: {
          DEFAULT: '#F59E0B',
          light: '#FBBF24',
        },
        danger: {
          DEFAULT: '#EF4444',
          light: '#F87171',
        },
        secondary: {
          DEFAULT: '#3D3D3D',
          light: '#6B7280',
        },
      },
    },
  },
  plugins: [],
}
