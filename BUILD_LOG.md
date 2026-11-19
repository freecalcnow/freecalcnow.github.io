# FreeCalcNow live-site build log

- Built: 2026-11-19T13:49:57.484Z
- Brand: FreeCalcNow · Free address: https://freecalcnow.github.io · .com upgrade later: freecalcnow.com (RDAP-verified free 19 Nov 2026, not registered yet)
- Tool pages built: 15390 / 15390 (one page per tool at /<tool-slug>/)
- Categories: 14 hubs at /category/<id>/ (note: the plan's /money/, /work/ hub slugs were written before the real 14-category list was known; hubs use the real category ids)
- Homepage, A–Z index (/tools/), info pages (/about/, /privacy/, /contact/, /methodology/, /sponsors/), assistant page (/ask/), games hub (/games/), Daily Number redirect (/daily-number/ → /games/daily-number/)
- Sitemap: sitemap.xml index + 16 chunk files (15519 URLs) · robots.txt included
- Slug collisions with reserved paths: none
- Games: 78 games in the registry, 1177 playable variations (Batch 1)
- Sponsor email on every page footer: malikarslan032154@gmail.com

## Pacing — build everything now, launch in batches

All 15390 tool pages are built now, but Search Console submission goes in batches to avoid Google's scaled-content-abuse risk: Batch 1 = the 20–25 richest pages first (Mortgage Calculator first, then the top money + freelance tools), then 100–200 pages only if Batch 1 indexes cleanly. The build is complete; the launch is paced.

## Games roadmap — patches, no shortage

- **Batch 1 (now):** 78 unique games + 1177 playable variations (engines + endless generated questions/levels). Every game is fully playable (levels, score, win/lose, restart) — no demos, no placeholders.
- **Patches (Phase 2+):** more real full games keep arriving in patches; the variation system (difficulty/theme/board-size) carries the playable total past 1,000. 15,390 unique games are NOT possible — each patch adds genuine full games, no demos. Games are a modular registry (games.json): adding a game = one new page folder + one registry entry — no rebuild of other pages. The games hub reads the registry at runtime, so new games appear automatically.
- Rotation: each tool page's teaser shows a different game (hash of the tool id over the registry), collapsed by default, click to play on the game's own page.

## Deploy

Deployed to GitHub Pages (free, 24/7) at https://freecalcnow.github.io — repo freecalcnow/freecalcnow.github.io. Search Console + GA4 set up (free); AdSense next (needs the owner's CNIC — confirmed his own, 19 Nov 2026 — plus a Pakistani bank account; Payoneer is NOT an AdSense payout method in Pakistan).

## Honest limits

- No rankings, user counts or income are promised. First Google movement is typically 2–4 months; real traffic 3–12 months.
- AdSense approval is harder on a free github.io subdomain; if rejected there, reapply after the .com upgrade.
- GitHub Pages: 1 GB site limit; this build is ~250 MB and fits.
