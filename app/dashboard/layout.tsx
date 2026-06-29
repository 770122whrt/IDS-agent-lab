"use client";

import { useSession } from "@/app/lib/auth-client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Toaster } from "sonner";
import { Loader2 } from "lucide-react";
import DashboardSidebar from "@/components/dashboard-sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/sign-in");
    }
  }, [isPending, session?.user, router]);

  if (isPending) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-950">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!session?.user) {
    return null;
  }

  return (
    <div className="w-full min-h-screen bg-gray-50 dark:bg-gray-950">
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
