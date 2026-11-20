# FreeCalcNow

**15,402 free calculators, converters and games — live at [freecalcnow.github.io](https://freecalcnow.github.io/).**

No sign-up. No account. Your numbers never leave your browser: every
calculation runs on your device, and the site's analytics log page views
only — never calculator inputs or results. See [Privacy](https://freecalcnow.github.io/privacy/)
and [How we calculate](https://freecalcnow.github.io/methodology/).

## What is here

| Area | Count (verified, 20 Nov 2026) |
| --- | --- |
| Calculator & converter pages | 15,402 |
| Categories | 14 |
| Mini games | 101 |
| Languages in the app | 36 |

Money (mortgage, loan, compound interest, SIP, tax, salary), health (BMI,
calories, BMR), unit conversions (length, mass, temperature, area, volume,
speed, data, energy — 13,811 conversion pages), maths, physics, chemistry,
biology, construction, food, sports, ecology and everyday life.

## How the site works

This repo **is** the deployed site — GitHub Pages serves it directly from
`main`. It is a fully static site: plain HTML + CSS + JavaScript, no
server, no database. The counts above come from a single generated
manifest (`assets/manifest-data.json`); every page reads its numbers from
it, so the totals shown on the site always match the real inventory.

- `assets/engine.js` — the calculation engine (formulas, unit tables).
- `assets/site.js` — page behaviour (inputs, results, validation, share).
- `assets/manifest-data.json` — generated inventory (tools, games, categories).
- `tests/` (in the build sources) — regression tests: golden formula tests
  against independently computed answers, currency-selector regression,
  privacy checks, and a full internal-link crawl (885,279 links, 0 broken
  as of v9).

## Accuracy

High-risk formulas (mortgage, loan, compound interest, SIP, income tax,
salary, BMI, unit conversions) are tested against independently computed
answers — see `tests/golden.js`. Tax tools pin their tax year on the tool
page (income tax uses 2025 US federal brackets; salary uses 2026).
Formulas are standard textbook/IRS formulas; worked examples and sources
are being added tool by tool. If a result looks wrong, please open an
issue — include the tool, the inputs, the answer you got, and the answer
you expected (with a source if you have one).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: report wrong answers and
broken links via issues, suggest new tools via the tool-request template,
and do not submit bulk-generated near-duplicate calculators.

## Privacy & ads

- Analytics: Google Analytics 4, page views only, query strings stripped
  (a shared link's numbers are never logged).
- No calculator input or result is ever sent anywhere.
- No ad network is running yet. When ads or sponsors arrive, they will be
  labelled and will never cover results. Sponsor enquiries:
  malikarslan032154@gmail.com.

## Licence

Content and code in this repo are © 2026 FreeCalcNow. All rights reserved
unless a file says otherwise.
