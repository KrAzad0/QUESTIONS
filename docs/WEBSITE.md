# Physics 2027 Question Lab — GitHub Pages website

**Repository:** https://github.com/KrAzad0/QUESTIONS

## One-time publication setup (required)

The site code and GitHub Actions build are ready. The repository's GitHub Pages service must first be switched on by an administrator:

1. Open **[Repository Settings → Pages](https://github.com/KrAzad0/QUESTIONS/settings/pages)**.
2. In **Build and deployment**, choose **Source → GitHub Actions** (not “Deploy from a branch”). Save if requested.
3. Open **[Actions](https://github.com/KrAzad0/QUESTIONS/actions)**.
4. Select **Daily Physics Questions and GitHub Pages → Run workflow** on the `main` branch.
5. After the **deploy** job succeeds, visit the URL displayed in the workflow's `github-pages` deployment environment. The conventional project-site address is **https://krazad0.github.io/QUESTIONS/**, unless GitHub shows a configured custom domain.

**Important:** Do not claim the public URL is live until the GitHub Actions deployment has actually succeeded. If Pages remains disabled, the daily generator still runs and stores new question files; deployment is skipped with a setup warning.

## How daily publishing works

The [daily GitHub Actions workflow](../.github/workflows/daily-questions.yml) has a `cron` schedule of **02:30 UTC = 08:00 IST**. Each run:

1. Generates one dated **`questions/YYYY-MM-DD.md`** file of exactly **10 original worked questions**, if it doesn't exist already.
2. Verifies Python and JavaScript syntax and tests the three rotating variants of every topic family.
3. Runs [`scripts/build_site.py`](../scripts/build_site.py), converting all dated Markdown question sheets to `site/data/questions.json`.
4. Builds a static GitHub Pages artifact containing `site/index.html`, `site/styles.css`, `site/app.js`, and the daily archive JSON plus resources.
5. Deploys the website directly in the same workflow (when Pages is enabled).

**Why build and deploy together?** GitHub Actions commits made with `GITHUB_TOKEN` do not trigger a second workflow on push. A single combined workflow avoids missed daily redeployments.

### Manual publishing

If a scheduled run was delayed or missed, in GitHub visit **Actions → Daily Physics Questions and GitHub Pages → Run workflow**. Scheduling is best-effort and GitHub can delay it; daily publishing is not guaranteed at exactly 08:00.

To create a dated sheet locally:

```bash
python3 scripts/publish_daily.py --date 2026-12-01
python3 scripts/build_site.py
python3 -m http.server 8000 --directory site
```

Open **http://localhost:8000** to preview the website; `file://` won't load the JSON archive reliably because browsers restrict local `fetch`.

## Website features

- Overview dashboard with exams and personal completion counts.
- Latest ten-question set with collapsible worked solutions.
- Search questions and filter by physics subject.
- Archive organized by date; past sets remain available.
- In-site roadmap and resource library generated from repository docs.
- Light/dark display mode, responsive design and accessible controls.

**Privacy:** Your completion markers and theme preference are stored in that browser using `localStorage`. There is no user account or cross-device progress synchronization, and clearing browser data can erase the local progress record.

**Mathematics rendering:** The site loads Marked, DOMPurify and MathJax from public CDNs. Core question text can still be shown in fallback form if these providers are blocked, although rich formatting may degrade.

**Content transparency:** Auto-generated questions rotate among **30 existing concept families** (three per subject across ten subjects), with seeded parameters and worked explanations; they are **not** ten wholly new inventions each day. Exam boards' real papers are linked on the [Resources page](RESOURCES.md) rather than copied.

## Editing or expanding content

- Edit `site/styles.css` to change colors and layout.
- Edit `site/app.js` to change filters, dashboards and progress controls.
- Edit `docs/2027-ROADMAP.md` or `docs/RESOURCES.md` to update the website's study sections.
- Add new validated problem templates in `scripts/publish_daily.py` for more challenging questions.
- To hand-add a historical dated set, add exactly Q1–Q10 under headings `## Q1. Subject — Topic`, a clear `**Question.**`, and one `<details><summary>Solution</summary>... </details>` block per question. The builder refuses malformed sheets.

All published code and content remain under this repository's license.
