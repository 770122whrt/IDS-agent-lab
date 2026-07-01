# Route-Level Chinese and English Internationalization Design

Date: 2026-07-01
Branch: `codex/i18n-zh-en`

## Summary

IDS Agent will use route-level internationalization with canonical `/zh` and `/en` URL prefixes. UI text will be centralized in locale message files and read through a single translation API. The implementation will keep API routes, authentication behavior, IDS generation, IFC checking, uploaded file data, task data, and report payload schemas unchanged.

The design replaces the current client-only language toggle with URL-derived locale state. The existing `i18n/messages/zh.json`, `i18n/messages/en.json`, `i18n/context/language-context.tsx`, and `components/ui/language-toggle.tsx` remain conceptually useful, but they need to be repaired and extended.

## Goals

- Support `/zh` and `/en` as the formal entry points for every user-facing page.
- Default legacy or unprefixed page paths to Chinese, for example `/dashboard` redirects to `/zh/dashboard`.
- Keep `/api/*`, `/_next/*`, static assets, and file downloads outside locale routing.
- Keep all user-visible UI copy in centralized message files, not scattered through page components.
- Let users switch languages without losing their current page context.
- Persist the last selected locale in a cookie for root and legacy redirects.
- Localize dates, status labels, alerts, confirms, toast messages, empty states, loading text, form labels, placeholders, buttons, page titles, and report UI labels.
- Keep user data untouched, including task names, uploaded filenames, IDS/IFC content, GlobalId values, JSON field names, and raw backend error details.

## Non-Goals

- No translation of API response schemas or database fields.
- No changes to IDS generation, IFC checking, authentication providers, upload handling, or task status transitions.
- No same-screen bilingual display. A page renders in one selected language at a time.
- No third-party i18n dependency in this phase. The current app only needs two locales, and a small route-aware local implementation is lower risk.
- No SEO-heavy locale negotiation beyond route prefixes and localized metadata. Browser Accept-Language is outside this phase unless product requirements change.

## Current State

The app already has:

- `i18n/context/language-context.tsx` with `language`, `setLanguage`, and `t(key, params)`.
- `i18n/messages/zh.json` and `i18n/messages/en.json`.
- `components/ui/language-toggle.tsx`.
- `app/layout.tsx` wrapping all pages with `LanguageProvider`.
- `app/tasks/[id]/report/page.tsx` using `useLanguage()`.

The main gaps are:

- Most pages still contain direct English or corrupted Chinese UI strings.
- The current locale source is client `localStorage`, not the URL.
- Only the report page consumes the translation API.
- The current `zh.json` parses as JSON but contains mojibake text in the working copy output.
- `app/layout.tsx` hardcodes `<html lang="en">`.
- Client navigations such as `router.push("/dashboard")` do not preserve language.

## Recommended Architecture

### Routing

All user-facing routes live under `app/[locale]/...`:

```text
/zh
/en
/zh/sign-in
/en/sign-in
/zh/sign-up
/en/sign-up
/zh/reset-password
/en/reset-password
/zh/dashboard
/en/dashboard
/zh/tasks
/en/tasks
/zh/tasks/[id]
/en/tasks/[id]
/zh/tasks/[id]/report
/en/tasks/[id]/report
/zh/ids_use
/en/ids_use
```

The root `/` redirects to the saved locale cookie, falling back to `/zh`.

Legacy paths redirect to their Chinese equivalents unless a locale cookie exists:

```text
/sign-in -> /zh/sign-in
/dashboard -> /zh/dashboard
/tasks/abc -> /zh/tasks/abc
```

### Locale Source

The URL path segment is the source of truth.

```ts
type Locale = "zh" | "en";
```

`LanguageProvider` receives `locale` and `messages` from the locale layout. It may still expose `setLanguage`, but changing language becomes route navigation rather than local state mutation.

### Message Files

The message files remain JSON:

```text
i18n/messages/zh.json
i18n/messages/en.json
```

Both files must have identical key paths. Missing translations are build failures through a small checker script.

Suggested top-level namespaces:

```text
common
home
auth
nav
dashboard
tasks
taskDetail
report
idsUse
status
errors
validation
metadata
demo
```

### Navigation Helpers

Add route helpers so page code does not manually concatenate locale strings.

Responsibilities:

- Identify supported locales.
- Strip or replace the first locale segment.
- Build locale-prefixed links.
- Convert a current pathname from one locale to another.
- Preserve search params for pages like reset password.

### Middleware

`middleware.ts` handles only URL shape:

- Skip `/api`, `/_next`, static files, and favicon.
- Allow `/zh/...` and `/en/...`.
- Redirect `/` to `/${cookieLocale || "zh"}`.
- Redirect unprefixed page paths to `/${cookieLocale || "zh"}${pathname}`.
- Redirect invalid locale-like prefixes to `/zh`.

### Layouts

`app/layout.tsx` keeps the root HTML and body shell. It should not own the active locale because the locale belongs to the `[locale]` segment.

`app/[locale]/layout.tsx` validates `params.locale`, loads the matching messages, and wraps children with the i18n provider.

Because the root layout cannot reliably set a dynamic `lang` attribute from the nested route segment, a small client component updates `document.documentElement.lang` when the locale changes.

### Language Toggle

The language toggle becomes path-aware:

- On `/zh/tasks?x=1`, switching English navigates to `/en/tasks?x=1`.
- On `/en/tasks/123/report`, switching Chinese navigates to `/zh/tasks/123/report`.
- It writes a locale cookie after successful click intent.
- It shows compact labels such as `EN` on Chinese pages and `ZH` on English pages.
- It exposes accessible titles from the message catalog.

### Metadata

Localized metadata should be added at the `[locale]` layout or page level:

- Chinese default: `IDS Agent`
- English default: `IDS Agent`
- Page titles and descriptions come from `metadata.*` message keys.

### Error Handling

- Missing message key: return the English fallback if available, otherwise the key string. In development, warn once in the console.
- Missing locale file: fail build or fail the message check script before build.
- Invalid locale route: redirect to `/zh` or show `notFound()` for nested paths where redirect would hide a user mistake.
- API error details: show localized wrapper text and preserve raw backend detail after the localized prefix.

Example:

```text
Submission failed: <raw backend error>
Localized submission failure prefix: <raw backend error>
```

## Data Flow

1. User opens `/dashboard`.
2. Middleware sees no locale prefix and redirects to `/zh/dashboard`.
3. `app/[locale]/layout.tsx` receives `locale = "zh"`.
4. Layout loads `zh.json` and provides `t()`, `locale`, and routing helpers.
5. Page renders all static UI through `t("...")`.
6. User clicks language toggle.
7. Toggle computes `/en/dashboard`, stores `NEXT_LOCALE=en`, and navigates.
8. English layout loads `en.json`; page rerenders with English text.

## File Ownership

### I18n Core

- `i18n/config.ts`: supported locales, default locale, cookie name, type guards.
- `i18n/routing.ts`: path conversion and locale-prefixed route helpers.
- `i18n/context/language-context.tsx`: provider and `useLanguage()`.
- `i18n/messages/zh.json`: Chinese UI catalog.
- `i18n/messages/en.json`: English UI catalog.
- `components/ui/language-toggle.tsx`: route-aware language switcher.
- `components/i18n/lang-attribute.tsx`: client component that syncs `<html lang>`.
- `middleware.ts`: redirects and locale prefix enforcement.

### App Routes

- `app/layout.tsx`: root shell only.
- `app/page.tsx`: root redirect or minimal fallback.
- `app/[locale]/layout.tsx`: locale validation and provider wiring.
- Existing user-facing pages move under `app/[locale]/...`.

### Validation

- `scripts/check-i18n-messages.mjs`: verifies message key parity and non-empty strings.
- `package.json`: add `i18n:check` script and include it in verification instructions.

## Page Coverage

Required first-pass coverage:

- `app/[locale]/page.tsx`
- `app/[locale]/sign-in/page.tsx`
- `app/[locale]/sign-up/page.tsx`
- `app/[locale]/reset-password/page.tsx`
- `app/[locale]/dashboard/page.tsx`
- `app/[locale]/tasks/page.tsx`
- `app/[locale]/tasks/[id]/page.tsx`
- `app/[locale]/tasks/[id]/report/page.tsx`
- `app/[locale]/ids_use/page.tsx`
- `components/dashboard-sidebar.tsx`
- `components/footer.tsx`
- `components/hero-section.tsx`
- `components/side-bar.tsx`

Lower-priority but still in scope:

- `app/[locale]/demo/page.tsx`
- `app/[locale]/demo/room/[id]/page.tsx`

## Translation Boundaries

Translate:

- Labels, buttons, titles, descriptions, placeholders.
- Loading, empty, success, error, confirm, and toast text.
- Status labels derived from internal task states.
- Report UI labels and headings.
- Date formatting locale.

Do not translate:

- Task `_id`.
- User-provided text.
- File names.
- IDS XML, IFC content, JSON keys.
- GlobalId and class names.
- Raw backend error payloads.
- API route names and request or response shapes.

## Testing Strategy

### Static Checks

- `npm run i18n:check`
- `npm run lint`
- `npm run build`

### Local Browser Checks

Run the dev server and verify:

- `/` redirects to `/zh`.
- `/zh/sign-in` renders Chinese UI.
- `/en/sign-in` renders English UI.
- Language toggle preserves the current route and search params.
- `/dashboard` redirects to `/zh/dashboard`.
- `/api/resources` is not redirected by middleware.
- `/zh/tasks/[id]/report` keeps report data untouched while labels switch language.

### Manual Acceptance

- Refresh preserves locale because the route includes locale.
- Copying an `/en/...` URL opens English directly.
- All primary user paths are usable in both languages.
- No mojibake appears in user-visible UI.

## Migration Notes

The implementation should move pages into the locale segment carefully. Because the working tree already has unrelated generated IDS artifacts, implementation commits must stage only intentional i18n files and page moves.

The first implementation commit should introduce the i18n core and route skeleton. Later commits should convert pages in small groups, keeping the app buildable after each group.

## Decision

Use custom route-level i18n with `/zh` and `/en`, centralized JSON message files, middleware redirects, and route-aware language switching. Do not introduce `next-intl` in this phase.
