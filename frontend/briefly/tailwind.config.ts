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
        navy: '#000080',
        dark_navy: "#00003b",
        grey_navy: "#141441",
        white: "#ffffff",
      },
    },
  },
  plugins: [],
};
export default config;
