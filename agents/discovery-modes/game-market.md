# Discovery Mode: Game Market & Genre Analysis

Use this mode when the question is about **the game market** for a game project: genre landscape, top performers, retention/monetization benchmarks, virality, platform fit. This is the game-specific specialization of the generic `market` mode — games have their own metrics (retention cohorts, ARPDAU, session length, K-factor) that generic competitive analysis misses.

This mode feeds into the `game-design` mode (which uses the market window to inform mechanics) and the Product agent (which formalizes scope). Use `game-market` first, then `game-design`.

When the product is **not** a game, use the generic `market` mode instead.

---

## Additional responsibilities

- Identify the genre and sub-genre precisely (hypercasual, casual, puzzle, idle/incremental, midcore, social, hyper-competitive, etc.) — genre dictates every benchmark
- Find 4–6 top performers in the genre; for each, tear down *why* it works (core loop, hook, monetization), not just what it is
- Surface genre-specific retention and monetization benchmarks (use web search for current numbers — they shift)
- Identify the market window: is the genre saturated, growing, or declining? Where's the gap?
- Map platform fit (web / WebView / native / app store) against genre norms
- Assess virality potential (does the genre support share loops? what's a realistic K-factor?)
- Flag live-ops expectations (does the genre demand ongoing content, events, seasons?)

Use web search tools for current benchmarks — retention norms, top-grossing charts, ARPDAU figures change quarterly.

---

## What to analyze

### Genre metrics to capture (benchmark against the genre, not all games)

| Metric | What it means | Why it matters |
|---|---|---|
| **D1 / D7 / D30 retention** | % of players returning after 1 / 7 / 30 days | The single strongest signal of product-market fit for games. Hypercasual D1 ~35–45%, casual D1 ~40–50%, midcore D1 ~45–55% (verify current) |
| **Session length** | Average minutes per session | Casual: 3–8 min. Hypercasual: 1–3 min. Determines pacing and content density |
| **Sessions per day** | Frequency of return | Snackable games: 4–8/day. Session games: 1–3/day |
| **ARPDAU** | Average revenue per daily active user | Monetization viability per genre |
| **K-factor** | Viral coefficient (invites × conversion) | >1 = organic growth; most games <0.5 and rely on paid/share-prompt |
| **CPI vs LTV** | Cost-per-install vs lifetime value | Whether paid acquisition is viable |

### Monetization models by genre

- **IAP (in-app purchase):** consumables, cosmetics, progression skips, battle pass
- **Ads:** rewarded video (most player-friendly), interstitial, banner
- **Hybrid:** ads + IAP (dominant in casual/hypercasual 2024+)
- **Premium:** one-time purchase (rare on mobile, viable on Steam/console)
- **Loyalty/brand:** when the game is a brand engagement vehicle, not a revenue product (e.g., a retailer's branded game) — success metric is engagement/retention, not ARPDAU

State which model fits the project's actual goal. A brand game (like a retailer's WebView tapper) optimizes engagement + brand affinity, not revenue — different benchmark set entirely.

---

## Output format

```text
## Game Market Analysis — <game name / concept>

## Genre Classification
- Primary genre: <genre>
- Sub-genre: <sub-genre>
- Closest analogues: <2-3 named games>

## Market Window
<is the genre growing / saturated / declining? where is the gap our concept fills?>

## Top Performers Teardown

### <Game 1> — <why it works>
- Core loop: <the repeating 10-second to 1-minute action>
- Primary hook: <what makes players come back>
- Monetization: <model + rough ARPDAU if known>
- Retention signal: <D1/D7/D30 if known>
- What we can borrow: <principle, not feature>
- What to avoid: <where it falls short>

### <Game 2> — ...
(4–6 total)

## Genre Benchmarks
| Metric | Genre norm | Source / confidence |
|---|---|---|
| D1 retention | <%> | <web source / estimate> |
| D7 retention | <%> | ... |
| Session length | <min> | ... |
| Sessions/day | <n> | ... |
| Monetization | <dominant model> | ... |

## Platform Fit
<web / WebView / native / store — which fits this genre + this project's distribution>

## Virality Assessment
<realistic K-factor; what share mechanics work in this genre>

## Monetization Recommendation
<which model fits the project's actual goal — revenue vs brand engagement>

## Live-Ops Expectation
<does this genre demand ongoing content / events / seasons, or is it ship-and-done?>

## Market Risks
- <saturation / platform / monetization risks>

## Assumptions Made
- ...

## Recommended Next Step
<hand off to game-design mode with the market window + genre norms as input>
```

---

## Handoff

Append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md` with `artifact_type: "design_note"` and `status: "produced"`. Set `next_recommended_agent` to `Discovery` (for `game-design` mode) — the market window feeds directly into mechanics design.
