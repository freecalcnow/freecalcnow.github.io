# Contributing to FreeCalcNow

Thank you for helping make the calculators right. This is a static site
served by GitHub Pages — there is no server, no database and no build
step on the server. Please read the notes below before opening a pull
request.

## What helps most

1. **Wrong answers.** Open an issue with the tool URL, the inputs you
   typed, the answer the site gave, and the answer you expected — with a
   source (textbook, IRS publication, NHS/WHO page, unit standard) if you
   have one. High-risk tools (money, tax, health) are checked first.
2. **Broken links / missing pages.** Open an issue with the page you were
   on and the link that failed.
3. **New tool ideas.** Use the tool-request issue template. One tool per
   issue, with the formula and a worked example. Bulk lists of
   near-duplicate calculators are not accepted — the catalogue already
   has 15,402 pages and quality matters more than count.

## Pull requests

- Keep the site working offline-first: no new third-party scripts that
  send user data anywhere. Analytics must never receive calculator
  inputs or results.
- No green chrome anywhere; the site's colours are navy and gold.
- No emoji in the UI — use the custom SVG icons in `assets/icons/`.
- No channel or social-media promotion inside tool pages.
- Shared assets (`assets/*.js`, `assets/*.css`) are the right place for
  fixes that affect many pages. Do not edit thousands of generated pages
  by hand — if a fix needs to reach every page, say so in the PR and the
  maintainer will apply it with the generator.
- Add or update a test under `tests/` when you change a formula or a
  shared behaviour. All tests must pass (`node tests/run-all.js`)
  before a PR is merged.
- The tool-data source and generator live outside this repo, so new
  tools are added by the maintainer from approved issue requests.

## Code of conduct

Be kind and factual. Corrections are welcome — with sources, even more so.
