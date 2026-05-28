# Discovery Mode: Game Design — Mechanics Analysis & Concept Synthesis

Use this mode when the question is about **how a game should play**: core loop, reward schedules, progression, difficulty, retention hooks, game feel. This is where approaches are analyzed and **the recommended game concept is generated** (the solution-synthesis step).

This mode is distinct from:
- `game-market` (the market window — runs first, feeds this mode)
- `technical` (how to build it — game engine, rendering)
- `references` (visual/UX benchmarks)
- Product agent (formalizes the concept into a feature spec)

Use `game-design` after `game-market`. Its output (Recommended Game Concept) hands off to Product.

When the product is **not** a game, this mode does not apply.

---

## Additional responsibilities

- Analyze the **core loop** at three timescales: the 10-second loop (moment-to-moment), the 1-minute loop (session beat), the full-session / meta loop
- Design (or evaluate) the **reward schedule** — and do it ethically: anticipation and mastery, not exploitation
- Recommend a **progression system** matched to the genre and goal
- Map the **difficulty curve** to keep players in the flow channel (not bored, not frustrated)
- Identify **retention hooks** that are fair (avoid dark patterns; a brand game especially must not feel manipulative)
- Reference **game feel / juice** patterns that make the core action satisfying
- Run a **frustration analysis** — where would players rage-quit, and how to prevent it
- Design the **FTUE** (first-time user experience) — ideally teach by doing, no tutorial wall
- **Synthesize** all of the above into a single Recommended Game Concept

Use web search for genre-specific design patterns and feel references when useful.

---

## Analysis framework

### 1. Core loop (the heart of the game)

Describe the loop at three timescales:

| Timescale | Question | Example (conveyor-belt tapper) |
|---|---|---|
| **10-second loop** | What does the player do moment-to-moment? | Tap items as they pass; avoid bombs |
| **1-minute loop** | What's the session beat — tension build/release? | Speed ramps, combos build, occasional event (rush/power-up) |
| **Session / meta loop** | Why come back tomorrow? | Beat high score, reach new "shift", share result |

A game without a tight 10-second loop has no foundation. A game without a meta loop has no retention.

### 2. Reward schedule (ethical design)

| Schedule | Effect | Use |
|---|---|---|
| **Fixed ratio** | Predictable (every N actions → reward) | Progression milestones, predictable goals |
| **Variable ratio** | Engaging but risky (random reward) | Use sparingly; powerful, can be exploitative |
| **Anticipation / near-miss** | "So close!" drives retry | Score-chase games; keep it honest (real near-miss, not rigged) |
| **Mastery** | Skill improvement is its own reward | The healthiest hook — player gets genuinely better |

**Ethical line:** favor mastery and anticipation. Avoid manufactured FOMO, pay-to-skip-frustration loops, or rigged near-misses. For brand games, manipulation damages the brand — fairness is a hard requirement, not a nicety.

### 3. Progression & meta-game

Options ranked by complexity:
- **Score-chase only** (simplest — high score + leaderboard)
- **Unlock progression** (new content/skins/modes earned)
- **Level/world progression** (discrete stages)
- **Meta-currency + upgrades** (between-run progression, roguelite-style)
- **Live-ops seasons** (highest effort — recurring content)

Match to the genre norm from `game-market` and the project's effort budget.

### 4. Difficulty curve (flow channel)

Keep the player between boredom (too easy) and anxiety (too hard):
- Start below the player's skill (build confidence in FTUE)
- Ramp difficulty as skill grows (speed, complexity, new mechanics)
- Use tension-release rhythm — peaks of challenge, valleys of recovery
- Provide comeback mechanics so a bad moment isn't a death spiral
- Define the failure state clearly and make it feel fair ("I see why I lost")

### 5. Retention hooks (fair)

- **Mastery progression** — "I'm getting better" (healthiest)
- **Score/social** — beat your own / friends' scores
- **Daily variation** — new challenge/seed each day
- **Streaks** — reward consistency (without punishing absence harshly)
- **Comeback events** — positive reasons to return, not guilt

### 6. Game feel / juice

The tactile satisfaction layer (hand off to Animator for specs):
- Immediate visual + audio feedback on every input (<50ms)
- Squash & stretch, anticipation, follow-through on key actions
- Screen shake / hit-stop on impactful moments (sparingly)
- Particle bursts, number pop-ups, combo escalation effects
- Sound design that rewards (rising pitch on combo, satisfying "thunk")

### 7. Frustration analysis

For each potential rage-quit point, name the cause and the mitigation:
- Unfair difficulty spike → smooth the curve
- Unclear failure cause → make the failure legible
- Input lag / unresponsive controls → performance budget (hand off to perf review)
- Repetitive grind → vary content / shorten loop
- Pay wall at frustration peak → never (especially brand games)

### 8. FTUE (first-time user experience)

- Teach by doing, not by reading (no tutorial wall when avoidable)
- First 5 seconds: player is already playing
- Introduce one mechanic at a time
- First session should deliver a "win" or a clear "I almost had it"

---

## Output format — Recommended Game Concept (the solution synthesis)

After the analysis, synthesize into a concrete, buildable concept:

```text
## Game Design Analysis — <game name / concept>

**Market input:** <reference the game-market findings: genre, window, benchmarks>

## Core Loop
- 10-second loop: <description>
- 1-minute loop: <description>
- Session/meta loop: <description>

## Reward Schedule
<which schedules, where, and the ethical rationale>

## Progression System
<chosen system + why it fits genre + effort budget>

## Difficulty Curve
<how difficulty ramps; tension-release rhythm; comeback mechanics; failure state>

## Retention Hooks
<the fair hooks chosen; explicitly note any rejected dark patterns and why>

## Game Feel Direction
<key juice moments to hand off to Animator>

## Frustration Mitigations
| Rage-quit risk | Mitigation |
|---|---|
| ... | ... |

## FTUE Plan
<how the first session teaches and delivers a first win>

---

## RECOMMENDED GAME CONCEPT (synthesis)

<2–4 paragraph synthesis: what the game IS, the single core fantasy, the loop,
the progression, the monetization/engagement model — and crucially WHY this
combination will work for the market window identified in game-market. This is
the "right solution" — a concrete, opinionated recommendation, not a menu.>

**One-sentence pitch:** <the game in one sentence>

**Why it works:** <tie back to market window + genre benchmarks + a defensible hook>

**Biggest design risk:** <the one thing most likely to make it not-fun, and the plan to de-risk it>

## Assumptions Made
- ...

## Recommended Next Step
<hand off to Product to formalize the concept into a feature spec with MVP scope>
```

---

## Handoff

Append a handoff block per `docs/AGENT_HANDOFF_CONTRACT.md` with `artifact_type: "design_note"` and `status: "produced"`. Set `next_recommended_agent` to `Product` — the Recommended Game Concept becomes the input for the feature specification. Product applies cascading inference: it reads the concept and asks only about gaps that affect MVP scope.
