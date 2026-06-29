"use client";

import { useLanguage } from "@/i18n/context/language-context";

export function LanguageToggle() {
  const { language, setLanguage } = useLanguage();

  return (
    <button
      onClick={() => setLanguage(language === 'zh' ? 'en' : 'zh')}
      className="inline-flex items-center justify-center px-3 py-1.5 text-sm font-medium rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
      title={language === 'zh' ? 'Switch to English' : '切换到中文'}
    >
      {language === 'zh' ? 'EN' : '中文'}
    </button>
  );
}
