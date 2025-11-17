"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/app/lib/auth-client";

export default function Home() {
  const router = useRouter();
  const { data: session, isPending } = useSession();

  useEffect(() => {
    if (!isPending && session?.user) {
      router.push("/dashboard");
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

  if (session?.user) {
    //already logged in, useEffect has already redirected
    return null;
  }

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center min-h-screen w-full px-6",
        "bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black text-center"
      )}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-md mx-auto space-y-6"
      >
        <h1 className="text-3xl md:text-5xl font-bold text-gray-800 dark:text-gray-100">
          Welcome to{" "}
          <span className="text-blue-600 dark:text-blue-400">My App</span>
        </h1>

        <p className="text-gray-600 dark:text-gray-400 text-sm md:text-base leading-relaxed">
          A simple authentication demo built with Next.js and better-auth.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center pt-2">
          <Link href="/sign-in">
            <Button
              size="lg"
              className="w-full sm:w-auto px-6 py-2 text-base font-medium"
            >
              Sign In
            </Button>
          </Link>
          <Link href="/sign-up">
            <Button
              variant="outline"
              size="lg"
              className="w-full sm:w-auto px-6 py-2 text-base font-medium"
            >
              Sign Up
            </Button>
          </Link>
        </div>
      </motion.div>

      <footer className="absolute bottom-6 text-xs text-neutral-500">
        built with{" "}
        <Link
          href="https://better-auth.com"
          target="_blank"
          className="underline ml-1 text-neutral-600 dark:text-neutral-300"
        >
          ids_agent
        </Link>
      </footer>
    </div>
  );
}