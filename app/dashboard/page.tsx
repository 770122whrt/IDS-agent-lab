"use client";

import { useSession, signOut } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Dashboard() {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/sign-in");
    }
  }, [isPending, session?.user, router]);

  if (isPending) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
        <svg className="animate-spin h-8 w-8 text-blue-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
        </svg>
        <p className="text-lg text-gray-700 dark:text-gray-200 font-medium">Loading...</p>
      </div>
    );
  }

  if (!session?.user) {
    //avoid flashing, useEffect has already redirected, this is a fallback
    return null;
  }

  const handleSignOut = async () => {
    await signOut();
    router.push("/sign-in");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
      <h1 className="text-3xl md:text-5xl font-bold mb-4 text-gray-800 dark:text-gray-100">
        Welcome, <span className="text-blue-600 dark:text-blue-400">{session.user.name || "User"}</span> 👋
      </h1>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        You are logged in as <strong>{session.user.email}</strong>
      </p>
      <Button className="w-40 mb-4" onClick={() => router.push("/ids_use")}>try 🚀IDS_agent🤖</Button>
      <Button onClick={handleSignOut} className="w-40">
        Sign Out
      </Button>
    </div>
  );
}