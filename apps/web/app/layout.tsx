import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Grant Platform",
  description:
    "Chat-first Grant Platform (G1 pilot). Submission stays disabled — " +
    "the platform prepares, you review.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
