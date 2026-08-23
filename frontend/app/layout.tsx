import type { Metadata } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { SessionProvider } from "../components/session-provider";
import { DevoraProvider } from "../components/devora-context";

const body = Inter({ subsets: ["latin"], variable: "--font-body", display: "swap" });
const display = Space_Grotesk({ subsets: ["latin"], weight: ["500", "600", "700"], variable: "--font-display", display: "swap" });
const jetbrains = JetBrains_Mono({ subsets: ["latin"], weight: ["400", "500", "700", "800"], variable: "--font-jetbrains", display: "swap" });

export const metadata: Metadata = { title: "DEVORA // Knowledge Engine Command Center", description: "AI-powered developer onboarding command center" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
 return <html lang="en" className={`${body.variable} ${display.variable} ${jetbrains.variable}`}><body><SessionProvider><DevoraProvider>{children}</DevoraProvider></SessionProvider></body></html>;
}
