"use client";

import { useSession, signOut } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Dashboard() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (!isPending) {
      if (!session?.user) {
        router.push("/sign-in");
      }
      setChecked(true);
    }
  }, [isPending, session, router]);

  if (!checked) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
      <h1 className="text-3xl md:text-5xl font-bold mb-4 text-gray-800 dark:text-gray-100">
        Welcome, <span className="text-blue-600 dark:text-blue-400">{session?.user?.name || "User"}</span> 👋
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        You are logged in as <strong>{session?.user?.email}</strong>
      </p>
      <Button
        onClick={async () => {
          await signOut();
          router.push("/sign-in");
        }}
        className="w-40"
      >
        Sign Out
      </Button>
    </div>
  );
}
