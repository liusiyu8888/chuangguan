/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Noto Serif SC"', 'serif'],
      },
    },
  },
  plugins: [],
}
