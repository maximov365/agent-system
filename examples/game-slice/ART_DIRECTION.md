# Lantern Market — reference slice

Purpose: demonstrate the framework's asset provenance, real interactions, coherent art direction, audio feedback, reproducible checks, and measured performance in one portable browser game. This is an original framework example, not a redesign of an existing downstream game.

The player runs a small harbor market at dusk and packs three-item orders before the evening ends. The core loop is read order → choose goods → immediate readable feedback → complete order → reward → next customer. Keyboard 1–4 and pointer/touch are equivalent. A short session, pause/resume, retry, best-score persistence, sound toggle, reduced motion, and responsive layouts are required.

Direction: a warm illustrated seaside market, deep teal sea and ink, soft ivory paper, amber lanterns, coral accents, confident serif titles and clear sans-serif labels. Handcrafted illustrated background sets the world; clean interactive product cards and a receipt-style order keep gameplay legible. No neon dashboard, generic glass cards, emoji as production art, or baked-in UI text. Native image generation produces the environment; code-native vectors are appropriate for the small recurring item silhouettes.

Target: desktop and mobile browser, portrait controls and a wide composed layout; four large item buttons, clear order progress, understated motion and a sound control. Prototype target: 60 Hz, p95 observed frame time ≤ 25 ms on the current desktop test host, export budget < 8 MiB. Physical mobile performance and uncoached player enjoyment remain separate validation.

Automation uses an explicit seeded short fixture (`?evidence=1`) while the regular play session lasts 60 seconds. Fixture results must be labeled separately; test hooks expose state and measured frame data, not a hidden auto-win mode.
