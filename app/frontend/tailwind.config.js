/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          teal: "#68ccd1",
          green: "#669900",
        },
      },
    },
  },
  plugins: [],
};

