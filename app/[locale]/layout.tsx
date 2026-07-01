import { notFound } from "next/navigation";
import { LangAttribute } from "@/components/i18n/lang-attribute";
import { isLocale, type Locale } from "@/i18n/config";
import { LanguageProvider } from "@/i18n/context/language-context";

import enMessages from "@/i18n/messages/en.json";
import zhMessages from "@/i18n/messages/zh.json";

const messagesByLocale = {
  zh: zhMessages,
  en: enMessages,
} satisfies Record<Locale, Record<string, unknown>>;

export function generateStaticParams() {
  return [{ locale: "zh" }, { locale: "en" }];
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!isLocale(locale)) {
    notFound();
  }

  return (
    <LanguageProvider locale={locale} messages={messagesByLocale[locale]}>
      <LangAttribute locale={locale} />
      {children}
    </LanguageProvider>
  );
}
