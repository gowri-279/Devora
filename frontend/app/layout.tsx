import type { Metadata } from "next";
import "./globals.css";
import { SessionProvider } from "../components/session-provider";
import { DevoraProvider } from "../components/devora-context";

export const metadata: Metadata = { title: "DEVORA // Knowledge Engine Command Center", description: "AI-powered developer onboarding command center" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
 return <html lang="en"><body><SessionProvider><DevoraProvider>{children}</DevoraProvider></SessionProvider></body></html>;
}
