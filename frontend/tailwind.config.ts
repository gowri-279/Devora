import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#101828",
        navy: "#14213D",
        violet: "#635BFF",
        mint: "#10B981",
        soft: "#F7F8FC"
      },
      boxShadow: {
        card: "0 10px 30px rgba(16,24,40,.07)"
      }
    }
  },
  plugins: []
};

export default config;
