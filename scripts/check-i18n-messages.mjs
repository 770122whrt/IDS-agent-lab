import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = process.cwd();
const localeFiles = {
  zh: resolve(root, "i18n/messages/zh.json"),
  en: resolve(root, "i18n/messages/en.json"),
};

function flattenKeys(value, prefix = "") {
  if (typeof value === "string") {
    return [prefix];
  }

  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`Invalid message value at ${prefix || "<root>"}`);
  }

  return Object.entries(value).flatMap(([key, child]) => {
    const nextPrefix = prefix ? `${prefix}.${key}` : key;
    return flattenKeys(child, nextPrefix);
  });
}

function collectEmptyStrings(value, prefix = "") {
  if (typeof value === "string") {
    return value.trim() ? [] : [prefix];
  }

  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return [prefix || "<root>"];
  }

  return Object.entries(value).flatMap(([key, child]) => {
    const nextPrefix = prefix ? `${prefix}.${key}` : key;
    return collectEmptyStrings(child, nextPrefix);
  });
}

const catalogs = Object.fromEntries(
  Object.entries(localeFiles).map(([locale, file]) => {
    const json = JSON.parse(readFileSync(file, "utf8"));
    return [locale, json];
  }),
);

const keySets = Object.fromEntries(
  Object.entries(catalogs).map(([locale, catalog]) => [
    locale,
    new Set(flattenKeys(catalog)),
  ]),
);

const referenceLocale = "zh";
const referenceKeys = [...keySets[referenceLocale]].sort();
let failed = false;

for (const [locale, keys] of Object.entries(keySets)) {
  const missing = referenceKeys.filter((key) => !keys.has(key));
  const extra = [...keys].filter((key) => !keySets[referenceLocale].has(key)).sort();
  const empty = collectEmptyStrings(catalogs[locale]).sort();

  if (missing.length || extra.length || empty.length) {
    failed = true;
    console.error(`Message catalog mismatch for ${locale}`);
    if (missing.length) console.error(`  Missing keys: ${missing.join(", ")}`);
    if (extra.length) console.error(`  Extra keys: ${extra.join(", ")}`);
    if (empty.length) console.error(`  Empty strings: ${empty.join(", ")}`);
  }
}

if (failed) {
  process.exit(1);
}

console.log(`i18n message check passed for ${Object.keys(catalogs).join(", ")}`);
