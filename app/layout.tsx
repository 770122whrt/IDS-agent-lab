import type { Metadata } from "next";
import "app/globals.css";

export const metadata: Metadata = {
  title: "IDS Agent",
  description: "Generate and review IDS files",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 text-gray-800 antialiased dark:from-gray-900 dark:to-black dark:text-gray-100">
        {children}
      </body>
    </html>
  );
}
