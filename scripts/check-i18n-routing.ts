import assert from "node:assert/strict";
import { defaultLocale } from "../i18n/config";
import {
  getLocaleFromPath,
  splitLocalePath,
  switchLocalePath,
  withLocale,
} from "../i18n/routing";

assert.equal(defaultLocale, "zh");

assert.deepEqual(splitLocalePath("/zh/tasks/123"), {
  locale: "zh",
  pathWithoutLocale: "/tasks/123",
});

assert.deepEqual(splitLocalePath("/en"), {
  locale: "en",
  pathWithoutLocale: "/",
});

assert.deepEqual(splitLocalePath("/dashboard"), {
  locale: null,
  pathWithoutLocale: "/dashboard",
});

assert.equal(withLocale("/dashboard", "zh"), "/zh/dashboard");
assert.equal(withLocale("/en/tasks", "zh"), "/zh/tasks");
assert.equal(withLocale("/", "en"), "/en");
assert.equal(switchLocalePath("/zh/tasks", "en", "?tab=report"), "/en/tasks?tab=report");
assert.equal(getLocaleFromPath("/en/sign-in"), "en");
assert.equal(getLocaleFromPath("/sign-in"), "zh");

console.log("i18n routing check passed");
