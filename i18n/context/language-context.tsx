"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';

// Import translations
import zhMessages from '../messages/zh.json';
import enMessages from '../messages/en.json';

type Language = 'zh' | 'en';

const messages: Record<Language, Record<string, unknown>> = {
  zh: zhMessages,
  en: enMessages,
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
}

export function LanguageProvider({ children }: LanguageProviderProps) {
  const [language, setLanguage] = useState<Language>('zh');

  // Initialize from localStorage on mount
  useEffect(() => {
    const savedLang = localStorage.getItem('language');
    if (savedLang === 'zh' || savedLang === 'en') {
      setLanguage(savedLang);
    }
  }, []);

  const handleSetLanguage = useCallback((lang: Language) => {
    setLanguage(lang);
    localStorage.setItem('language', lang);
  }, []);

  const t = useCallback((key: string, params?: Record<string, string | number>): string => {
    const keys = key.split('.');
    let value: unknown = messages[language];

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = (value as Record<string, unknown>)[k];
      } else {
        // Fallback to key if translation not found
        return key;
      }
    }

    if (typeof value !== 'string') {
      return key;
    }

    // Replace parameters like {count} with actual values
    if (params) {
      return value.replace(/\{(?<paramKey>\w+)\}/g, (match, ...args) => {
        const groups = args[args.length - 1] as { paramKey: string };
        const key = groups.paramKey;
        return key in params ? String(params[key]) : match;
      });
    }

    return value;
  }, [language]);

  return (
    <LanguageContext.Provider value={{ language, setLanguage: handleSetLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
