import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MentorSpace",
  description: "AI-powered developer onboarding platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
