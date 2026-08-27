import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // accessible dark theme, chat-first (Appendix B §12)
        surface: {
          DEFAULT: "#111318",
          raised: "#1a1d24",
          border: "#2a2f3a",
        },
        accent: {
          DEFAULT: "#6c9fff",
          muted: "#3b5c8f",
        },
      },
    },
  },
  plugins: [],
};
export default config;
