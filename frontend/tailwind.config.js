/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        night:  "#1B1931",
        velvet: "#44174E",
        wine:   "#662249",
        rose:   "#A34054",
        amber:  "#ED9E59",
        blush:  "#E9BCB9",
      },
      fontFamily: {
        display: ["'Playfair Display'", "serif"],
        body:    ["'DM Sans'", "sans-serif"],
      },
    },
  },
  plugins: [],
};