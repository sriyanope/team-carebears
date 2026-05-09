/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        blue: {
          50: '#E8F2FB',
          100: '#B8D6F2',
          500: '#1A6FBF',
          700: '#0E4A82',
        },
        sage: {
          50: '#E6F5EC',
          500: '#1E7A4A',
        },
        amber: {
          50: '#FEF3E2',
          500: '#B85C00',
        },
        rose: {
          50: '#FDECEA',
          500: '#C0392B',
        },
        stone: {
          50: '#F5F4F2',
          100: '#ECEAE6',
          400: '#8A8680',
          700: '#4A4845',
          900: '#1E1C1A',
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', 'sans-serif'],
        serif: ['"DM Serif Display"', 'serif'],
      },
      borderRadius: {
        '2xl': '16px',
      },
      fontSize: {
        base: ['18px', '1.6'],
      },
    },
  },
  plugins: [],
}
