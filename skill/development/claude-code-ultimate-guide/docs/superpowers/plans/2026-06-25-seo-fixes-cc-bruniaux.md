# SEO Fixes: cc.bruniaux.com: Updated Plan (25 June 2026)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture the remaining 400+ clicks/month left on the table after the first wave of fixes. Fix glossary meta, add internal links to weak-but-close pages, and speed up Google re-indexing of already-deployed changes.

**Architecture:** All fixes live in the landing repo at `/Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/`. Content pages use Astro + Starlight with frontmatter controlling `<title>` and `<meta name="description">`. Starlight pages at `/guide/` are generated from `src/content/docs/guide/`. Non-guide pages are in `src/pages/`. Internal links are in Astro component files under `src/components/` and `src/pages/`.

**Tech Stack:** Astro 5, GitHub Pages, Starlight, TypeScript, `astro.config.mjs` redirects.

## Global Constraints

- Landing repo: `/Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/`
- Guide repo: `/Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide/`
- Guide Starlight files (generated, do NOT edit directly (re-run prepare-guide-content.mjs if needed)): `src/content/docs/guide/`
- Build command: `cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing && pnpm build`
- Deploy: push to `main` → GitHub Actions CI → GitHub Pages
- All titles: 50-60 chars. All descriptions: 140-160 chars.
- Language: English only
- Do not introduce `http://` URLs anywhere

---

## Already Done: Do Not Redo

These were deployed in commit `b4f045b` and earlier. Skip:

| Issue | Status |
|-------|--------|
| `data-privacy` title + description rewritten | ✅ Deployed |
| `01-quick-start` title fixed | ✅ Deployed |
| `github-actions` description fixed | ✅ Deployed |
| 20+ 404 URLs redirected via `astro.config.mjs` | ✅ Deployed |
| `/guide/claude-code-releases/` → `/releases/` redirect | ✅ Deployed |
| Releases page `dateModified` updated | ✅ Deployed |

Awaiting Google re-crawl (7-14 days). No action needed on these.

---

## Fresh GSC Data (90-day snapshot from MCP, 25 June 2026)

| Page | Clics | Impressions | CTR | Position | Gap |
|------|-------|-------------|-----|----------|-----|
| `/quiz/` | 326 | 5 415 | 6.0% | 6.3 | None, #1 performer |
| `/cheatsheet/` | 120 | 2 913 | 4.1% | 14.2 | Position too low |
| `/` homepage | 97 | 8 913 | 1.1% | 16.8 | Low CTR + rank |
| `/whitepapers/` | 33 | 416 | 7.9% | 11.2 | OK |
| `/glossary/` | 18 | 6 757 | 0.3% | 26.6 | Bad meta + low rank |
| `/releases/` | 13 | 51 690 | 0.03% | 15.7 | Low rank, no internal links |
| `/guide/ai-ecosystem/` | 4 | 14 825 | 0.03% | 18.5 | No internal links |
| `/guide/data-privacy/` | 0 | 12 748 | 0% | 9.8 | Fix deployed, awaiting re-crawl |
| `guide/third-party-tools/` | 2 | 1 874 | 0.1% | 9.3 | Striking distance, no internal links |
| `guide/workflows/iterative-refinement/` | 15 | 2 258 | 0.7% | 10.2 | HTTP indexed, good candidate |

---

## Task 1: Fix glossary meta (P0)

**Impact:** 6,757 impressions at position 26.6, barely visible, zero actionable CTR. Title is literally "Glossary" and description is "Definitions for Claude Code terminology". Both are useless in SERPs. Fixing these alone won't push position 26 to page 1 alone; adding internal links (Task 3) together with better meta gives Google a reason to promote it.

**Files:**
- Modify: `src/pages/glossary/index.astro` (lines 1-15, frontmatter `title` + `description` constants)

- [ ] **Step 1: Read the current frontmatter**

```bash
head -15 /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/src/pages/glossary/index.astro
```

Expected:
```
---
import Layout from '../../layouts/Layout.astro'
...
const title = 'Glossary'
const description = 'Definitions for Claude Code terminology'
```

- [ ] **Step 2: Update title and description constants**

In `src/pages/glossary/index.astro`, replace the `title` and `description` variable assignments:

```js
const title = 'Claude Code Glossary: 80+ Terms Defined (Hooks, MCP, Agents, Slash Commands)'
const description = 'Definitions for every Claude Code concept: hooks (PreToolUse, PostToolUse), MCP servers, slash commands, sub-agents, CLAUDE.md, permission modes, context window, and 70+ more terms.'
```

- [ ] **Step 3: Verify build passes**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing && pnpm build 2>&1 | tail -5
```

Expected: no errors.

- [ ] **Step 4: Verify new title appears in built HTML**

```bash
grep -o '<title>[^<]*</title>' /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/dist/glossary/index.html
```

Expected: `<title>Claude Code Glossary: 80+ Terms Defined (Hooks, MCP, Agents, Slash Commands) | Claude Code Ultimate Guide</title>`

- [ ] **Step 5: Commit**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing
git add src/pages/glossary/index.astro
git commit -m "seo: fix glossary title/desc (was 'Glossary' / 'Definitions for...' (6.7k impressions, 0 useful CTR)"
```

---

## Task 2: Fix FAQ meta (P1)

**Impact:** `/faq/` has 1,999 impressions at position 29.9 with 0 clicks. Same problem as glossary: generic meta.

**Files:**
- Modify: `src/pages/faq/index.astro` (title + description constants)

- [ ] **Step 1: Read current meta**

```bash
grep -n "const title\|const description" /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/src/pages/faq/index.astro | head -5
```

- [ ] **Step 2: Update title and description**

Replace the `title` and `description` assignments with:

```js
const title = 'Claude Code FAQ: 30+ Questions Answered (Cost, Privacy, Limits, Setup)'
const description = 'Answers to the most common Claude Code questions: subscription vs API cost, what data gets sent to Anthropic, context window limits, how to run offline, and setup troubleshooting.'
```

- [ ] **Step 3: Build and verify**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing && pnpm build 2>&1 | tail -3
grep -o '<title>[^<]*</title>' /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/dist/faq/index.html
```

- [ ] **Step 4: Commit**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing
git add src/pages/faq/index.astro
git commit -m "seo: fix FAQ title/desc (was generic (2k impressions, pos 30, 0 clicks)"
```

---

## Task 3: Add internal links from quiz and cheatsheet to weak pages (P0)

**Why this matters:** Quiz has 326 clicks and is on page 1 (pos 6.3). Cheatsheet has 120 clicks and is on page 2 (pos 14.2). Adding anchor links from these pages to `/releases/`, `/glossary/`, and `/guide/data-privacy/` passes authority to those pages and increases their ranking over the next 2-4 weeks. This is free PageRank redistribution.

**Files:**
- Modify: `src/pages/quiz/index.astro` (add footer/sidebar link block)
- Modify: `src/pages/cheatsheet/index.astro` (add related resources section)

- [ ] **Step 1: Read quiz page bottom section**

```bash
tail -40 /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/src/pages/quiz/index.astro
```

Note the closing `</Layout>` tag position.

- [ ] **Step 2: Add related resources block in quiz page**

In `src/pages/quiz/index.astro`, just before the closing `</Layout>` tag, add:

```astro
  <section class="content-section" style="background: var(--bg-secondary);">
    <div class="container">
      <h2>Keep Learning</h2>
      <ul class="feature-list">
        <li><a href="/cheatsheet/">Cheatsheet</a>: all commands on one page</li>
        <li><a href="/glossary/">Glossary</a>: definitions for every Claude Code term</li>
        <li><a href="/releases/">Releases</a>: full version history and env vars reference</li>
        <li><a href="/guide/data-privacy/">Data Privacy</a>: what gets sent to Anthropic and how to control it</li>
      </ul>
    </div>
  </section>
```

- [ ] **Step 3: Read cheatsheet page bottom section**

```bash
tail -40 /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/src/pages/cheatsheet/index.astro
```

- [ ] **Step 4: Add related resources block in cheatsheet page**

In `src/pages/cheatsheet/index.astro`, just before the closing `</Layout>` tag, add:

```astro
  <section class="content-section" style="background: var(--bg-secondary);">
    <div class="container">
      <h2>Related Resources</h2>
      <ul class="feature-list">
        <li><a href="/quiz/">Test your Claude Code knowledge</a></li>
        <li><a href="/glossary/">Full glossary of Claude Code terms</a></li>
        <li><a href="/releases/">Version history and changelog</a></li>
        <li><a href="/guide/data-privacy/">Privacy: what data Claude Code sends to Anthropic</a></li>
      </ul>
    </div>
  </section>
```

- [ ] **Step 5: Build and verify links appear in HTML**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing && pnpm build 2>&1 | tail -3
grep 'href="/glossary/"\|href="/releases/"' /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/dist/quiz/index.html | head -3
grep 'href="/glossary/"\|href="/releases/"' /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/dist/cheatsheet/index.html | head -3
```

Expected: at least one match per page.

- [ ] **Step 6: Commit**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing
git add src/pages/quiz/index.astro src/pages/cheatsheet/index.astro
git commit -m "seo: add internal links from quiz+cheatsheet to releases, glossary, data-privacy"
```

---

## Task 4: Add internal links from homepage to releases and ecosystem (P1)

**Why:** Homepage has 8,913 impressions at position 16.8 and 97 clicks, a strong authority page. Adding links to `/releases/` and `/guide/ai-ecosystem/` from the homepage boosts those pages' authority signal significantly.

**Files:**
- Modify: `src/components/landing/Releases.astro` OR `src/pages/index.astro` (find whichever contains the releases section) the releases section appears on homepage

- [ ] **Step 1: Find where the releases section is in the homepage**

```bash
grep -n "releases\|ai-ecosystem\|Releases\|Ecosystem" /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/src/pages/index.astro | head -20
grep -n "href.*releases\|href.*ecosystem" /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/src/components/landing/Releases.astro 2>/dev/null | head -10
```

- [ ] **Step 2: Verify there is a link to /releases/ on the homepage**

```bash
grep 'href="/releases/"' /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/dist/index.html | head -3
```

If no match: the homepage doesn't link to `/releases/`. Find the closest section (the Releases component) and add an explicit text link: `<a href="/releases/">View full release history →</a>`.

- [ ] **Step 3: Verify there is a link to /guide/ai-ecosystem/ on the homepage**

```bash
grep 'href="/guide/ai-ecosystem/"' /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/dist/index.html | head -3
```

If no match: find the ClaudeEcosystem component and add a "View full AI ecosystem guide →" link pointing to `/guide/ai-ecosystem/`.

- [ ] **Step 4: Make the changes if needed**

Based on Step 2 and 3 findings, add the missing links. Each link should be a natural text anchor inside the relevant section, not a hidden link. Pattern:

```astro
<a href="/releases/" class="btn btn-secondary">View full release history →</a>
```

or inline in prose:

```astro
<p>See the <a href="/releases/">complete release history</a> for all versions.</p>
```

- [ ] **Step 5: Build and verify**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing && pnpm build 2>&1 | tail -3
grep 'href="/releases/"' /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/dist/index.html | wc -l
grep 'href="/guide/ai-ecosystem/"' /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing/dist/index.html | wc -l
```

Expected: at least 1 match each.

- [ ] **Step 6: Commit**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing
git add src/components/landing/ src/pages/index.astro
git commit -m "seo: add explicit /releases/ and /guide/ai-ecosystem/ links from homepage"
```

---

## Task 5: Request indexing via GSC for priority pages (P0)

These pages have fixes deployed but Google hasn't re-crawled them. Requesting indexing accelerates the process from 2-4 weeks to 3-7 days.

**No code changes: manual steps in Google Search Console.**

- [ ] **Step 1: Open GSC URL Inspection**

Go to: Search Console → cc.bruniaux.com → URL Inspection

- [ ] **Step 2: Request indexing for data-privacy**

Enter `https://cc.bruniaux.com/guide/data-privacy/` → click "Request indexing".
This is the highest priority: 12,748 impressions, 0 clicks, fix already deployed.

- [ ] **Step 3: Request indexing for remaining priority pages**

In sequence (one at a time, GSC rate-limits):
- `https://cc.bruniaux.com/glossary/` (after Task 1 is deployed)
- `https://cc.bruniaux.com/guide/ultimate-guide/01-quick-start/`
- `https://cc.bruniaux.com/guide/workflows/github-actions/`
- `https://cc.bruniaux.com/releases/`

Wait 30 seconds between each request.

- [ ] **Step 4: Submit sitemap for full re-index**

GSC → Sitemaps → select `sitemap-index.xml` → click "Resubmit".

---

## Task 6: Deploy and monitor (P1)

- [ ] **Step 1: Push all commits to main**

```bash
cd /Users/florianbruniaux/Sites/perso/claude-code-ultimate-guide-landing
git push origin main
```

- [ ] **Step 2: Verify GitHub Pages deployment**

Check the Actions tab at `https://github.com/FlorianBruniaux/claude-code-ultimate-guide-landing/actions` and wait for the green checkmark.

- [ ] **Step 3: Smoke-test live URLs**

```bash
curl -s https://cc.bruniaux.com/glossary/ | grep -o '<title>[^<]*</title>'
# Expected: "Claude Code Glossary: 80+ Terms Defined..."

curl -s https://cc.bruniaux.com/quiz/ | grep -c 'href="/glossary/"'
# Expected: >= 1

curl -I https://cc.bruniaux.com/guide/claude-code-releases/
# Expected: HTTP/2 301 to /releases/ (GitHub Pages handles the meta-refresh redirect)
```

- [ ] **Step 4: Set a 14-day monitoring reminder**

Check GSC on 2026-07-09 for:
- `/guide/data-privacy/` CTR: should be > 0 now
- `/glossary/` position: should improve from 26.6
- `/releases/` position: should improve from 15.7
- 404 count: should be near 0

---

## Opportunity Map: Out of Scope for Now

These require content work, not just meta/link fixes. Monitor for 30 days then decide:

| Opportunity | Why Deferred |
|-------------|--------------|
| Releases individual version pages (`/releases/v2.1.186/`) | High content volume, uncertain ROI vs existing page authority |
| Quiz modules for "claude 101 certification" queries | New content, 2-3 days work, prioritize after link building results come in |
| `/guide/ai-ecosystem/` content expansion (pos 18.5) | 14,825 impressions but ranking problem, not meta problem, needs links first |
| `/cheatsheet/` ranking improvement from pos 14 → 8 | Needs external link building, out of code scope |

---

## Self-Review

**Spec coverage:**
- Glossary zero-CTR → Task 1 ✓
- FAQ zero-CTR → Task 2 ✓
- Internal links to weak pages → Task 3 + Task 4 ✓
- GSC URL Inspection for deployed fixes → Task 5 ✓
- Deploy + smoke-test → Task 6 ✓

**Placeholder scan:** No TBDs. All code blocks are concrete. All paths are absolute.

**Type consistency:** No type interfaces used, pure Astro/HTML changes.
