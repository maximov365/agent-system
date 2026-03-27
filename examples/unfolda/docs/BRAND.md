# Unfolda — Brand Identity

This file is the canonical brand reference for all UI and frontend tasks.
Any agent working on UI, frontend, or design work **must read this file** before producing artifacts.

---

## Color Palette

| Role        | Name        | Hex       | Usage                                              |
|-------------|-------------|-----------|-----------------------------------------------------|
| Primary     | Deep Navy   | `#1a1f36` | Original text, headings, borders, primary actions  |
| Accent      | Warm Amber  | `#e8a849` | Translation layer, highlights, interactive states  |
| Background  | Cream       | `#faf6ef` | Page background, card surfaces                     |

**Two-color story:** Navy represents the original source text. Amber represents the translation. The palette is the product metaphor made visible.

---

## Typography

| Role     | Family  | Weight      | Usage                          |
|----------|---------|-------------|--------------------------------|
| Headings | Satoshi | Medium 500  | Page titles, section headings  |
| Body     | Inter   | Regular 400 | Prose, labels, UI copy         |

Font loading: Satoshi is a variable font available via Fontshare. Inter is available via Google Fonts or Fontsource. Both must be self-hosted or loaded via a privacy-respecting CDN — no tracking pixels.

---

## Tone of Voice

| Attribute | Meaning                                                                 |
|-----------|-------------------------------------------------------------------------|
| Calm      | Never urgent. Never pushy. The reader is in control.                   |
| Clear     | Say what it does. No marketing fluff or filler.                        |
| Literate  | Respect the reader. They came here because they love books.            |
| Honest    | Show estimates as estimates. Show limitations without hiding them.     |

**What to avoid:** exclamation points in body copy, loading spinners without status, jargon that the reader's language teacher wouldn't use.

---

## Core Metaphor

> **Unfold** = develop the folded meaning.

A book in a foreign language is folded — the meaning is there but compressed and inaccessible. Unfolda unfolds it: not just word-for-word, but sense-for-sense.

This metaphor should inform:
- Empty states ("Your books will appear here as you unfold them.")
- Error messages ("We couldn't unfold this file.")
- Onboarding copy ("Upload a book. We'll unfold the rest.")

---

## Design Principles

1. **Calm, not loud.** Whitespace is content. Resist adding visual elements.
2. **Clear, not clever.** Labels describe what a thing does. Avoid wit that confuses.
3. **Book-first.** The book cover and title are always the hero. UI chrome recedes.
4. **Two colors tell the story.** Navy for source, amber for translation. Use sparingly and consistently.
5. **Generous line length.** Reading UI should feel like reading a book. 60–75ch for body text.
6. **No dark patterns.** No fake urgency, no hidden limits, no confusing default selections.

---

## Component Conventions

- **Buttons:** primary actions use navy fill + cream text; secondary actions use amber fill + navy text; destructive actions use red outline only (no fill)
- **Progress states:** use amber for active/in-progress; navy for completed; grey for pending
- **Error states:** red `#c0392b` for blocking errors; amber for warnings; navy for informational
- **Spacing:** base unit 4px; standard component padding 16px; page margin 24px (mobile) / 48px (desktop)

---

## What This File Is Not

- This is not a full design system. Component-level decisions are made per-feature.
- This is not a style guide for code. See `.cursor/rules.md` for that.
- Colors and fonts may be refined as the product matures. Changes must be reflected here first.

---

*Last updated: 2026-03-15*
