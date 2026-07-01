"use client";

import { useEffect } from "react";
import { Loader2 } from "lucide-react";
import { Toaster } from "sonner";
import { useRouter } from "next/navigation";
import { useSession } from "@/app/lib/auth-client";
import DashboardSidebar from "@/components/dashboard-sidebar";
import { useLanguage } from "@/i18n/context/language-context";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { data: session, isPending } = useSession();
  const { locale } = useLanguage();
  const router = useRouter();

  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push(`/${locale}/sign-in`);
    }
  }, [isPending, session?.user, router, locale]);

  if (isPending) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-950">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!session?.user) {
    return null;
  }

  return (
    <div className="min-h-screen w-full bg-gray-50 dark:bg-gray-950">
      <DashboardSidebar
        user={{
          name: session.user.name,
          email: session.user.email,
        }}
      />
      <main className="ml-64 min-h-screen">
        <div className="px-4 py-8">{children}</div>
      </main>
      <Toaster position="top-right" richColors />
    </div>
  );
}
