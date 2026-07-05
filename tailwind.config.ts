import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0057B8",
          foreground: "#FFFFFF",
        },
        accent: {
          DEFAULT: "#0078D4",
          foreground: "#FFFFFF",
        },
        background: "#F7F9FC",
        surface: "#FFFFFF",
        border: "#E5E7EB",
        ink: {
          DEFAULT: "#1F2937",
          muted: "#6B7280",
        },
        success: "#22C55E",
        warning: "#F59E0B",
        danger: "#DC2626",
      },
      borderRadius: {
        DEFAULT: "12px",
        lg: "12px",
        md: "10px",
        sm: "8px",
      },
      fontFamily: {
        sans: [
          "Inter",
          "Segoe UI",
          "-apple-system",
          "BlinkMacSystemFont",
          "sans-serif",
        ],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(16, 24, 40, 0.04), 0 1px 3px rgba(16, 24, 40, 0.06)",
        elevated:
          "0 4px 12px rgba(16, 24, 40, 0.06), 0 2px 4px rgba(16, 24, 40, 0.04)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(4px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "typing-dot": {
          "0%, 60%, 100%": { opacity: "0.3" },
          "30%": { opacity: "1" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.25s ease-out",
        "typing-dot": "typing-dot 1.2s infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
