import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        instagram: {
          primary: "#E1306C",
          secondary: "#833AB4",
          tertiary: "#F77737",
          blue: "#0095F6",
          border: "#DBDBDB",
          bg: "#FAFAFA",
          text: "#262626",
          textSecondary: "#8E8E8E",
        },
      },
    },
  },
  plugins: [],
};
export default config;
