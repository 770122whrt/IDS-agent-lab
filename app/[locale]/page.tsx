"use client";

import Link from "next/link";
import { useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useSession } from "@/app/lib/auth-client";
import { Button } from "@/components/ui/button";
import { LanguageToggle } from "@/components/ui/language-toggle";
import { useLanguage } from "@/i18n/context/language-context";
import { cn } from "@/lib/utils";

export default function Home() {
  const router = useRouter();
  const { data: session, isPending } = useSession();
  const { t, locale } = useLanguage();

  useEffect(() => {
    if (!isPending && session?.user) {
      router.push(`/${locale}/dashboard`);
    }
  }, [isPending, session?.user, router, locale]);

  if (isPending) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black">
        <svg className="mb-4 h-8 w-8 animate-spin text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
        </svg>
        <p className="text-lg font-medium text-gray-700 dark:text-gray-200">{t("home.loading")}</p>
      </div>
    );
  }

  if (session?.user) {
    return null;
  }

  return (
    <div
      className={cn(
        "flex min-h-screen w-full flex-col items-center justify-center px-6",
        "bg-gradient-to-br from-gray-50 to-gray-100 text-center dark:from-gray-900 dark:to-black",
      )}
    >
      <div className="absolute right-6 top-6">
        <LanguageToggle />
      </div>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mx-auto max-w-md space-y-6"
      >
        <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100 md:text-5xl">
          {t("home.titlePrefix")}{" "}
          <span className="text-blue-600 dark:text-blue-400">{t("common.appName")}</span>
        </h1>

        <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-400 md:text-base">
          {t("home.description")}
        </p>

        <div className="flex flex-col justify-center gap-3 pt-2 sm:flex-row">
          <Link href={`/${locale}/sign-in`}>
            <Button size="lg" className="w-full px-6 py-2 text-base font-medium sm:w-auto">
              {t("home.signIn")}
            </Button>
          </Link>
          <Link href={`/${locale}/sign-up`}>
            <Button variant="outline" size="lg" className="w-full px-6 py-2 text-base font-medium sm:w-auto">
              {t("home.signUp")}
            </Button>
          </Link>
        </div>
      </motion.div>

      <footer className="absolute bottom-6 text-xs text-neutral-500">
        {t("home.learnMore")}{" "}
        <Link
          href="https://buildingSMART.org"
          target="_blank"
          className="ml-1 underline text-neutral-600 dark:text-neutral-300"
        >
          IDS
        </Link>
      </footer>
    </div>
  );
}
