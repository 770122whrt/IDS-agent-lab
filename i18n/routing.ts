import { defaultLocale, isLocale, type Locale } from "@/i18n/config";

export function splitLocalePath(pathname: string): {
  locale: Locale | null;
  pathWithoutLocale: string;
} {
  const normalized = pathname.startsWith("/") ? pathname : `/${pathname}`;
  const segments = normalized.split("/");
  const first = segments[1];

  if (isLocale(first)) {
    const rest = `/${segments.slice(2).join("/")}`.replace(/\/+$/, "");
    return {
      locale: first,
      pathWithoutLocale: rest === "" ? "/" : rest,
    };
  }

  return {
    locale: null,
    pathWithoutLocale: normalized === "" ? "/" : normalized,
  };
}

export function withLocale(pathname: string, locale: Locale): string {
  const { pathWithoutLocale } = splitLocalePath(pathname);
  if (pathWithoutLocale === "/") {
    return `/${locale}`;
  }
  return `/${locale}${pathWithoutLocale}`;
}

export function switchLocalePath(
  pathname: string,
  nextLocale: Locale,
  search = "",
): string {
  const path = withLocale(pathname, nextLocale);
  return search ? `${path}${search}` : path;
}

export function getLocaleFromPath(pathname: string): Locale {
  return splitLocalePath(pathname).locale ?? defaultLocale;
}
