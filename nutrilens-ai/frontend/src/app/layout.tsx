import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import "./dashboard-dark.css";
import { ToastProvider } from "@/hooks/useToast";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "NutriLens AI - Food Intelligence Platform",
  description: "AI-powered food freshness detection and health-aware recommendations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className} suppressHydrationWarning>
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  );
}
