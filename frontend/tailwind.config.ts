import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: "#0f1419",
        panel: "#1a2332",
        accent: "#3b82f6",
        muted: "#94a3b8",
      },
    },
  },
  plugins: [],
};

export default config;
