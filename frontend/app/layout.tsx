import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import { AppProvider } from "@/lib/store";
import ErrorBoundary from "@/components/ErrorBoundary";
import NetworkBanner from "@/components/NetworkBanner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AccessLens v2",
  description: "Policy access simulation and scheme recommendation system",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen flex flex-col`}>
        {/* AppProvider and ErrorBoundary are client components */}
        <AppProvider>
          <ErrorBoundary>
            <Navbar />
            <NetworkBanner />
            {children}
          </ErrorBoundary>
        </AppProvider>
      </body>
    </html>
  );
}
