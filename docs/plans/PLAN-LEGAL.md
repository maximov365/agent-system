# Implementation Plan: FEAT-LEGAL — Legal Pages and Cookie Consent

---

## Metadata

```
plan_id:      PLAN-LEGAL
feature_id:   FEAT-LEGAL
status:       plan
created_by:   architect
created_at:   2026-03-25
```

---

## Overview

Pure-frontend feature. No backend changes, no new npm dependencies, no DB migration.
All work is in the `web/` directory.

---

## Files to Create

| File | Purpose |
|---|---|
| `web/app/[locale]/terms/page.tsx` | Terms of Service static page |
| `web/app/[locale]/privacy/page.tsx` | Privacy Policy static page |
| `web/components/CookieConsent.tsx` | Cookie banner (client component) |

## Files to Modify

| File | Change |
|---|---|
| `web/components/AppShell.tsx` | Footer: add Terms/Privacy links; update opacity on links |
| `web/app/[locale]/login/page.tsx` | Add ToS note beneath sign-in button |
| `web/app/[locale]/layout.tsx` | Add `<CookieConsent />` after children |
| `web/messages/en.json` | Add `legal` and `cookieConsent` namespaces |
| `web/messages/ru.json` | Same |
| `web/messages/sr.json` | Same |

---

## Step-by-step Plan

### Step 1 — i18n strings [small]

Add two new namespaces to all three message files.

**`legal` namespace** (used in Terms/Privacy page headings and footer):
```json
"legal": {
  "termsTitle": "Terms of Service",
  "privacyTitle": "Privacy Policy",
  "termsLink": "Terms",
  "privacyLink": "Privacy",
  "lastUpdated": "Last updated: March 2026",
  "bindingNote": "This document is provided in English. The English version is binding."
}
```

**`cookieConsent` namespace**:
```json
"cookieConsent": {
  "message": "This site uses strictly necessary cookies for authentication and localStorage to remember your preferences. No tracking or advertising cookies are used.",
  "accept": "Got it"
}
```

**`login` namespace — new key** `tosNote`:
```
"tosNote": "By signing in you agree to our"
"tosLink": "Terms of Service"
"privacyLink": "Privacy Policy"
```

**`nav` namespace — new keys** for footer:
```
"terms": "Terms",
"privacy": "Privacy"
```

RU and SR translations:
- `legal.termsTitle`: "Условия использования" / "Uslovi korišćenja"
- `legal.privacyTitle`: "Политика конфиденциальности" / "Politika privatnosti"
- `legal.termsLink`: "Условия" / "Uslovi"
- `legal.privacyLink`: "Конфиденциальность" / "Privatnost"
- `cookieConsent.message`: translated (see below)
- `cookieConsent.accept`: "Понятно" / "Razumem"
- `login.tosNote`: "Войдя, вы принимаете" / "Prijavom prihvatate"
- `login.tosLink`: "Условия использования" / "Uslove korišćenja"
- `login.privacyLink`: "Политику конфиденциальности" / "Politiku privatnosti"
- `nav.terms`: "Условия" / "Uslovi"
- `nav.privacy`: "Конфиденциальность" / "Privatnost"

### Step 2 — AppShell footer update [small]

Replace current footer:
```tsx
<p>Unfolda &mdash; {t("footer")}</p>
```
With:
```tsx
<div className="flex items-center justify-between flex-wrap gap-3">
  <p>Unfolda &mdash; {t("footer")}</p>
  <nav className="flex items-center gap-4" aria-label="Legal">
    <a href={`/${locale}/terms`}>{t("terms")}</a>
    <a href={`/${locale}/privacy`}>{t("privacy")}</a>
  </nav>
</div>
```
Footer opacity already applied to the outer element — links inherit it. Remove the `opacity: 0.5` from the outer `<footer>` and apply it to the text elements individually so that hover states can work on links (links should lighten on hover via `opacity: 0.7` → `1`).

### Step 3 — Login page ToS note [small]

After the sign-in button `</button>`, add:
```tsx
<p className="mt-4 text-center text-xs" style={{ color: "var(--color-navy)", opacity: 0.55 }}>
  {t("tosNote")}{" "}
  <a href={`/${locale}/terms`} className="underline">{t("tosLink")}</a>
  {" "}&amp;{" "}
  <a href={`/${locale}/privacy`} className="underline">{t("privacyLink")}</a>
</p>
```

### Step 4 — Terms of Service page [small]

`web/app/[locale]/terms/page.tsx`:
- Server component (no "use client")
- Uses `AppShell` for layout (header + footer)
- Uses `useTranslations("legal")` via a child client component OR just `getTranslations` server-side for the `<title>` — but since the page body is static text, it uses a simple layout with i18n for the heading/meta and inline English content for the body
- Structure: `<AppShell><article>…content…</article></AppShell>`

Implementation note: Legal pages use `AppShell` for shell, then an `<article>` with `prose`-style Tailwind. Since Tailwind's `@tailwindcss/typography` plugin may not be installed, use inline styles / Tailwind spacing classes directly.

Page layout:
```tsx
export default async function TermsPage({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "legal" });
  return (
    <AppShell>
      <article className="mx-auto max-w-2xl py-12 space-y-8" style={{ color: "var(--color-navy)" }}>
        <header>
          <h1 className="font-heading text-3xl mb-2">{t("termsTitle")}</h1>
          <p className="text-sm" style={{ opacity: 0.5 }}>{t("lastUpdated")}</p>
          <p className="text-sm mt-1" style={{ opacity: 0.5 }}>{t("bindingNote")}</p>
        </header>
        {/* Sections rendered as JSX */}
      </article>
    </AppShell>
  );
}
```

Content sections (English body only, no i18n for body text):
1. Service Description
2. User Accounts
3. User Content and Copyright
4. Data Retention
5. Credits and Payments
6. Prohibited Uses
7. Disclaimer of Warranties
8. Limitation of Liability
9. Changes to Terms
10. Contact

### Step 5 — Privacy Policy page [small]

Same structure as Step 4, `web/app/[locale]/privacy/page.tsx`.

Sections:
1. Introduction
2. Information We Collect
3. How We Use Your Information
4. Data Retention
5. Third-Party Services
6. Data Security
7. Your Rights
8. No Data Selling
9. Cookies and Local Storage
10. Changes to This Policy
11. Contact

### Step 6 — Cookie consent banner [small]

`web/components/CookieConsent.tsx`:
```tsx
"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";

const CONSENT_KEY = "cookie-consent";

export function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const t = useTranslations("cookieConsent");

  useEffect(() => {
    if (!localStorage.getItem(CONSENT_KEY)) {
      setVisible(true);
    }
  }, []);

  if (!visible) return null;

  function accept() {
    localStorage.setItem(CONSENT_KEY, "accepted");
    setVisible(false);
  }

  return (
    <div
      role="dialog"
      aria-label="Cookie consent"
      aria-live="polite"
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        backgroundColor: "var(--color-navy)",
        color: "#fff",
        padding: "1rem 1.5rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        gap: "1rem",
        flexWrap: "wrap",
        borderTop: "2px solid rgba(255,255,255,0.1)",
      }}
    >
      <p style={{ fontSize: "0.875rem", lineHeight: "1.5", flex: 1, margin: 0 }}>
        {t("message")}
      </p>
      <button
        type="button"
        onClick={accept}
        style={{
          backgroundColor: "#fff",
          color: "var(--color-navy)",
          border: "none",
          borderRadius: "0.375rem",
          padding: "0.5rem 1.25rem",
          fontSize: "0.875rem",
          fontWeight: 500,
          cursor: "pointer",
          whiteSpace: "nowrap",
          flexShrink: 0,
        }}
      >
        {t("accept")}
      </button>
    </div>
  );
}
```

Integrated into `web/app/[locale]/layout.tsx`:
```tsx
import { CookieConsent } from "@/components/CookieConsent";
// ...
return (
  <NextIntlClientProvider messages={messages}>
    {children}
    <CookieConsent />
  </NextIntlClientProvider>
);
```

---

## Acceptance Criteria

- [ ] `GET /en/terms` → 200, renders ToS with ≥8 substantive sections
- [ ] `GET /en/privacy` → 200, renders Privacy Policy with ≥8 substantive sections
- [ ] `GET /ru/terms` and `GET /sr/terms` → 200, same English body, localised heading
- [ ] Footer on upload/jobs pages shows "Terms" and "Privacy" links
- [ ] Login page shows ToS/Privacy note
- [ ] Cookie banner appears when `localStorage["cookie-consent"]` is absent
- [ ] Cookie banner hidden when `localStorage["cookie-consent"] === "accepted"`
- [ ] `npm run build` succeeds, zero TypeScript errors

---

## Non-Goals

- No backend changes
- No new npm packages
- No analytics events
- No granular cookie management panel

---

## Risks

| Risk | Mitigation |
|---|---|
| CLS from cookie banner | `useEffect` guard — banner renders only after hydration |
| `AppShell` used in server components | `AppShell` is already a client component — legal pages import it normally |

---

## Assumptions

- `AppShell` is importable in the `app/[locale]/terms` and `app/[locale]/privacy` page files.
- `getTranslations` from `next-intl/server` is available (already used in the project).
- No `@tailwindcss/typography` plugin — use manual prose styles.
