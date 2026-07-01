"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type ReactNode,
} from "react";
import type { Locale } from "@/i18n/config";

type Messages = Record<string, unknown>;

interface LanguageContextType {
  locale: Locale;
  language: Locale;
  messages: Messages;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
  locale: Locale;
  messages: Messages;
}

function getMessage(messages: Messages, key: string): unknown {
  return key.split(".").reduce<unknown>((value, part) => {
    if (value && typeof value === "object" && part in value) {
      return (value as Record<string, unknown>)[part];
    }
    return undefined;
  }, messages);
}

export function LanguageProvider({
  children,
  locale,
  messages,
}: LanguageProviderProps) {
  const t = useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      const value = getMessage(messages, key);

      if (typeof value !== "string") {
        if (process.env.NODE_ENV !== "production") {
          console.warn(`Missing translation key: ${key}`);
        }
        return key;
      }

      if (!params) {
        return value;
      }

      return value.replace(/\{(\w+)\}/g, (match, paramKey: string) => {
        return paramKey in params ? String(params[paramKey]) : match;
      });
    },
    [messages],
  );

  const contextValue = useMemo(
    () => ({ locale, language: locale, messages, t }),
    [locale, messages, t],
  );

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
