import type { Metadata } from "next";
import "app/globals.css";
import { LanguageProvider } from "@/i18n/context/language-context";

export const metadata: Metadata = {
  title: "Sign In - My App",
  description: "Securely sign in to your account",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black flex items-center justify-center antialiased text-gray-800 dark:text-gray-100">
        <LanguageProvider>
          {children}
        </LanguageProvider>
      </body>
    </html>
  );
}
