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
  const { data: session, isPending } = useSession(); // Use Hook

  useEffect(() => {
    if (!isPending && session?.user) {
      // Already logged-in user will be redirected
      router.push("/dashboard");
    }
  }, [session, isPending, router]);

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

        {!session?.user && (
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
        )}
      </motion.div>

      <footer className="absolute bottom-6 text-xs text-neutral-500">
        built with{" "}
        <Link
          href="https://better-auth.com"
          target="_blank"
          className="underline ml-1 text-neutral-600 dark:text-neutral-300"
        >
          better-auth
        </Link>
      </footer>
    </div>
  );
}
