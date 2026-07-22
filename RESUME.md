# Houghton Planner — project state & how to resume

_Parked 2026-07-23. Everything below is durable; pick up from "Next steps"._

## What this is
A mobile-first festival timetable planner. The full Houghton 2026 lineup (344 sets, 14
stages, Thu–Sun) as a tappable grid. People mark who's going to what; picks show as
colour bars; the group plans live. Built as a possible product (see "Product" below).

**Live:** https://labmasd.github.io/houghton-planner/
**Repo:** LabMasd/houghton-planner (GitHub Pages off `master`, `/`)
**Stack:** single `index.html` (data inlined) + `sw.js` + `manifest.webmanifest` + `icon.svg`.
No build step. Edit → commit → push → live in ~1 min.

## Firebase (party mode)
- Project **partyplanner** (id `partyplanner-e87c3`), free Spark plan, under user's Google org.
- Realtime Database in **europe-west1**. Anonymous auth on. Rules: `rooms/$room` needs `auth != null`.
- Web config is embedded in `index.html` (`const FIREBASE_CONFIG = {...}`). API key is public
  by design — security is in the rules, not the key.
- Console: https://console.firebase.google.com/project/partyplanner-e87c3
- Set `FIREBASE_CONFIG = null` in index.html to disable party mode (app still works, offline/local).
- Test party `DX59TE` (member MARCOS) exists in the DB from end-to-end testing — harmless, delete anytime.

## How party mode works (the model)
- **Party** = room with name, 6-char code, colour set (chosen by host), members, picks. URL always
  carries `#r=CODE` when in a party.
- **Person** = name + colour from the party's set, protected by a 4-digit passcode (SHA-256, client-side)
  once claimed. Colour is the person's identity everywhere.
- **Host** = room creator; gets an unfakeable HOST badge; can edit/remove anyone and reset passcodes;
  chose the colour set. Stored as `orgP` (which person) + `org` (which anon uid).
- **One seat per guest** — a guest holds one claimed name; only the host adds extra people.
- **Sync:** picks/people debounced-pushed to Firebase; `onValue` merges back. Passcodes write
  **directly/immediately** (never via the debounced queue — that was a bug, now fixed).
- **Offline:** service worker caches the app; installable to home screen; picks queue and push on reconnect.
- Fallback with no backend: base64 `#i=` share links + import banner.

## UX architecture (one-page writeup)
Artifact: https://claude.ai/code/artifact/4929e218-6356-48e6-a8ff-95b2edc79feb
Two overlay families were merged → **all sheets are now centred floating cards** (max-width capped
so desktop doesn't balloon). Colour grammar: grey block = unpicked (alternating 2 greys),
white card + colour bar(s) = someone's going, colour fill = the person, red = clash, green = everyone.
Text on any person-colour auto-flips black/white by luminance (`textOn()`), so all palettes stay legible.

## Colour libraries
5 palettes in `PALETTES` (index.html): Flat UI (default), Material, Tailwind, Retro, Neon.
Host picks one per party; guests choose within it; taken colours lock.

## Known-good state / what was verified
End-to-end tested in-browser: create party → pick palette → name → claim + passcode → code in URL →
server state correct (people, pins, host badge). 4 sync/race bugs found and fixed during a full audit.
**Untested:** a genuinely second physical device (phone) joining — the real-world mile. Do this at/before Houghton.

## Data pipeline
See `pipeline/` — extract3 → build3 → finalize turns the timetable PDF into `acts_final.json`,
which is inlined into `index.html`. README there has the gotchas (O-for-zero, hidden old-lineup layer, etc).

---

## Product context (why this exists beyond Houghton)
- **Wedge:** small/mid festivals (~1k–20k cap) that publish a PDF/Instagram timetable and never make an app.
  Big players (Woov, Aloompa, Greencopper) serve big festivals; the long tail has nobody.
- **Model:** festival pays ~£300–800 (≈£500 sweet spot) for a branded planner at their own URL, free to
  attendees. Optional B2C fallback: host-pays party unlock (~£5–8). Upsell: anonymised demand analytics.
- **Closest competitors:** timetable.lol (friend rooms), Frontstage Festivals (3rd-party UK schedule pages),
  Clashfinder (+ Pal). None combine: no-account PWA + party codes + PDF→planner delivery service.
- **Moat isn't the code (copyable in a week):** relationships in a small industry, accumulated per-festival
  coverage, groups returning to your rooms, speed + taste, demand data over seasons.
- **Timeline:** this summer = field proof (Houghton, then user's other no-app festival). Sept–Oct = build the
  delivery machine. Oct–Feb = selling season (organisers plan next year). Spring = deliver. Next summer = revenue.
- Target festival list (UK, tiered) is in the chat history; Tier 1 = Houghton's electronic scene
  (Gottwood, Field Maneuvers, We Out Here, Lost Village, GALA, Body Movements, Waterworks, Freerotation...).

## Next steps to go from "works" to "sellable" (~2 focused weekends)
1. **Multi-festival** — load festival data instead of the one inlined blob (config/param, not baked in). ~1 day.
2. **Import tool** — make `pipeline/` a repeatable PDF/CSV/paste-in → planner-JSON tool. A few days. Add CSV path
   (festivals have the schedule as a spreadsheet before it's a PDF — skips parsing entirely for B2B).
3. **Schedule-edit flow** — admin grid to fix/patch set times live (also the fallback for messy PDFs). A few days.
4. **Per-festival home** — `<fest>.party` style subdomain + their name/colour. Mostly config once #1 exists.
5. **Landing page** — one page, Houghton demo embedded, price on it, email-to-buy. ~1 day.
6. **Master admin** (optional, later) — Google sign-in for user's email + `/admin` page reading all rooms for
   usage stats. Right now the Firebase console already shows every party/member/pick, visible only to the user.

## First action when resuming
None of the above is urgent. The one thing that matters near-term costs no code:
**use it at Houghton, make the group party go well, screenshot the coloured grid.** Everything downstream
(pitches, demos, the product) is built on that proof. Then start at Next-step #1.
