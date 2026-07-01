"use client";

import { useEffect } from "react";
import type { Locale } from "@/i18n/config";

type LangAttributeProps = {
  locale: Locale;
};

export function LangAttribute({ locale }: LangAttributeProps) {
  useEffect(() => {
    document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
  }, [locale]);

  return null;
}
