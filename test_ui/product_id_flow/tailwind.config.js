/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "nhs-blue": "#005eb8",
        "nhs-bright-blue": "#0072ce",
        "nhs-light-blue": "#41b6e6",
        "nhs-dark-blue": "#003087",
        "nhs-black": "#231f20",
        "nhs-dark-grey": "#425563",
        "nhs-mid-grey": "#768692",
        "nhs-pale-grey": "#e8edee",
        "nhs-white": "#ffffff",
        "nhs-green": "#009639",
        "nhs-aqua-green": "#00a499",
        "nhs-light-green": "#78be20",
        "nhs-red": "#da291c",
        "nhs-orange": "#ed8b00",
        "nhs-warm-yellow": "#fae100",
        "nhs-yellow": "#ffeb3b",
      },
      fontFamily: {
        sans: ["Frutiger", "Arial", "sans-serif"],
      },
      spacing: {
        72: "18rem",
        84: "21rem",
        96: "24rem",
      },
      maxWidth: {
        "4xl": "56rem",
        "7xl": "80rem",
      },
    },
  },
  plugins: [],
};
