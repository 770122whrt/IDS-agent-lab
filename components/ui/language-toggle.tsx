"use client";

import { usePathname, useRouter } from "next/navigation";
import { localeCookieName, type Locale } from "@/i18n/config";
import { useLanguage } from "@/i18n/context/language-context";
import { switchLocalePath } from "@/i18n/routing";

export function LanguageToggle() {
  const { locale, t } = useLanguage();
  const pathname = usePathname();
  const router = useRouter();
  const nextLocale: Locale = locale === "zh" ? "en" : "zh";

  return (
    <button
      type="button"
      onClick={() => {
        document.cookie = `${localeCookieName}=${nextLocale}; path=/; SameSite=Lax`;
        const search = window.location.search;
        router.push(switchLocalePath(pathname, nextLocale, search));
      }}
      className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
      title={t("common.language.switchTo", {
        language: t(`common.language.${nextLocale}`),
      })}
    >
      {locale === "zh" ? "EN" : "中文"}
    </button>
  );
}
