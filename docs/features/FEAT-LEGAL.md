# Feature: FEAT-LEGAL — Legal Pages and Cookie Consent

---

## Metadata

```
feature_id:    FEAT-LEGAL
status:        spec
created_by:    product
created_at:    2026-03-25
```

---

## Summary

Add GDPR-compliant legal infrastructure to the Unfolda web app:
- **Terms of Service** and **Privacy Policy** static pages at localised URLs (`/en/terms`, `/ru/terms`, `/sr/terms`, `/en/privacy`, etc.)
- **Cookie consent banner** shown once per browser on first visit
- **Footer** on all app pages with links to Terms and Privacy
- **Login page** note referencing Terms of Service before the sign-in action

This is a compliance deliverable, not a product engagement feature. It is a pre-requisite for public launch.

---

## Problem

Unfolda processes user files, stores them for up to 30 days, authenticates via Google OAuth, and charges credits. There is currently no Terms of Service, Privacy Policy, or cookie consent mechanism. This exposes the product to GDPR and consumer-protection risk before public launch.

---

## Goals

1. **Compliance** — Have a ToS and Privacy Policy covering the key legal obligations of an AI translation SaaS.
2. **Discoverability** — Users can navigate to legal pages from the footer on every page and from the login screen.
3. **Cookie consent** — A GDPR-compliant first-visit banner so users can acknowledge cookies/session storage use.
4. **Localisation** — All UI chrome (banner, footer links, login note) is translated into EN / RU / SR. Legal page content may be in English with a note that the binding version is English.

---

## Non-Goals

- Multi-language legal content (full translation of the dense legal text). The legal pages are English-only body text with a disclaimer that the English version is binding. The i18n keys cover UI chrome only (labels, headings, CTA buttons).
- Cookie management panel (granular opt-in/out). The app does not run third-party analytics; only the session cookie and `localStorage` for consent state are used.
- Backend changes — no new API endpoints, no DB columns, no migration.
- Versioning or legal update notifications.

---

## User Flow

### First visit (unauthenticated)
1. User arrives at `/en/login`.
2. Cookie banner slides up at the bottom.
3. User clicks "Accept" — banner disappears, `localStorage["cookie-consent"] = "accepted"` is set.
4. Beneath the Google sign-in button: "By signing in you agree to our [Terms of Service] and [Privacy Policy]."
5. Footer of login page shows "Terms · Privacy" links.

### Returning visit
1. Banner is hidden (consent already stored in localStorage).

### Legal page visit
1. User clicks "Terms" in footer → navigates to `/en/terms`.
2. Clean page with full Terms of Service text, header and footer.
3. User clicks browser back to return.

---

## Functional Requirements

### FR-1: Terms of Service page
- Route: `/{locale}/terms` for locale ∈ {en, ru, sr}
- Content: English-only Terms of Service body. Header and footer rendered via `AppShell`.
- Content covers: service description (AI translation SaaS), user responsibilities, copyright (user owns source files), data retention (30 days, controlled by `RETENTION_WINDOW_DAYS`), credits system terms, limitation of liability, governing law, contact.

### FR-2: Privacy Policy page
- Route: `/{locale}/privacy` for locale ∈ {en, ru, sr}
- Same structure as Terms. English-only body.
- Content covers: what data is collected (account email, uploaded EPUB, output EPUB), how it is used, retention window, third-party processors (Google OAuth, Anthropic API), no data selling, user rights (deletion on request).

### FR-3: Cookie consent banner
- Shown once per browser (check `localStorage["cookie-consent"]`).
- Displayed at the bottom of the viewport, fixed position.
- Text: explains cookies/localStorage use for session and preferences.
- Single "Accept" CTA. No "Reject" (app requires session cookie to function).
- On accept: sets `localStorage["cookie-consent"] = "accepted"`, hides banner.
- The banner is a client component added to the root locale layout so it appears on all pages.

### FR-4: Footer links
- The existing `AppShell` footer is updated to include "Terms · Privacy" links in addition to the current copyright notice.
- Links use `/{locale}/terms` and `/{locale}/privacy` (locale-prefixed).

### FR-5: Login page ToS note
- Beneath the Google sign-in button, add a small paragraph:
  > "By signing in you agree to our Terms of Service and Privacy Policy."
- "Terms of Service" and "Privacy Policy" are anchor links to the respective legal pages.

---

## Content Requirements

### Terms of Service — key clauses
- **Service**: Unfolda provides AI-assisted EPUB translation using large language models.
- **Account**: Google OAuth; user is responsible for account security.
- **User content**: User retains all rights to uploaded files. By uploading, user grants a limited processing licence for translation.
- **Copyright**: User warrants they have rights to upload the source file.
- **Data retention**: Uploaded files and translated outputs are deleted after `RETENTION_WINDOW_DAYS` days (currently 30).
- **Credits**: Credits are a consumable virtual currency; no refunds except as required by law.
- **Liability**: Service provided "as is"; no warranty on translation quality.
- **Governing law**: To be determined (placeholder).

### Privacy Policy — key clauses
- **Data collected**: Google account email and name (authentication); EPUB file content (processing only); job configuration and metadata.
- **Purpose**: To provide the translation service.
- **Retention**: Files deleted after 30 days. Account data retained until account deletion request.
- **Third parties**: Google (OAuth), Anthropic (LLM processing). No advertising or analytics SDKs.
- **No data selling**: User data is never sold or shared for marketing.
- **User rights**: Right to deletion — contact support.

---

## MVP Slice

All five deliverables (FR-1 through FR-5) are required for MVP. There is no smaller slice; legal compliance requires all of them to be deployed together.

---

## Constraints

- **No backend changes** — pure frontend feature.
- **No new npm dependencies** — cookie consent implemented with plain React + localStorage.
- **Content quality** — Legal text must be substantive and specific to Unfolda's service model. Generic filler text is not acceptable.
- **Accessibility** — Cookie banner must be keyboard-navigable.

---

## Risks

| Risk | Mitigation |
|---|---|
| Legal text is inaccurate or insufficient | Text drafted by Product; flagged as "not legal advice — review with counsel before launch". |
| Cookie banner causes CLS (layout shift) | Use `useEffect` to check consent state after hydration; render null until checked. |
| Broken links in footer or login page | Covered by Reviewer acceptance criteria. |

---

## Success Criteria

- [ ] `/en/terms`, `/ru/terms`, `/sr/terms` return 200 and render substantive ToS content.
- [ ] `/en/privacy`, `/ru/privacy`, `/sr/privacy` return 200 and render substantive Privacy Policy content.
- [ ] Cookie banner appears on first load (localStorage cleared), disappears after Accept, does not reappear on reload.
- [ ] Footer on all app pages shows "Terms" and "Privacy" links that navigate correctly.
- [ ] Login page shows ToS/Privacy note beneath sign-in button.
- [ ] `npm run build` succeeds with no TypeScript errors.

---

## Task Breakdown (initial)

| ID | Title | Type |
|---|---|---|
| TASK-73 | i18n strings for legal chrome (footer, cookie banner, login note) | small |
| TASK-74 | AppShell footer links + login ToS note | small |
| TASK-75 | Terms of Service page (`/[locale]/terms`) | small |
| TASK-76 | Privacy Policy page (`/[locale]/privacy`) | small |
| TASK-77 | Cookie consent banner component + integration | small |
