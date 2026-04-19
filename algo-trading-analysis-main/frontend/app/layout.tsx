import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Alpha Engine - Algorithmic Trading Platform",
  description: "Sophisticated algorithmic trading backtesting platform for Indian markets",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-bg-primary">
          {/* Header */}
          <header className="border-b border-border bg-bg-secondary/50 backdrop-blur-xl sticky top-0 z-50">
            <div className="container mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-alpha rounded-lg flex items-center justify-center">
                    <span className="text-2xl font-bold">α</span>
                  </div>
                  <div>
                    <h1 className="text-xl font-bold gradient-text">Alpha Engine</h1>
                    <p className="text-xs text-text-muted">Algorithmic Trading Platform</p>
                  </div>
                </div>


                <div className="px-3 py-1 bg-accent-success/20 text-accent-success border border-accent-success/30 rounded-full text-xs font-semibold">
                  Live Demo
                </div>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="container mx-auto px-6 py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="border-t border-border mt-12">
            <div className="container mx-auto px-6 py-6">
              <p className="text-center text-text-muted text-sm">
                Built for AlgoTrading Hackathon 2026 • Powered by Next.js & FastAPI
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
