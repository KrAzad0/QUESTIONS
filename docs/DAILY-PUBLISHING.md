# Daily 10-question publishing — operator guide

## Intended automatic schedule

The repo includes [a GitHub Actions workflow](../.github/workflows/daily-questions.yml) with a daily schedule at **02:30 UTC / 08:00 IST**. The job:

1. Checks out the default branch.
2. Runs [`scripts/publish_daily.py`](../scripts/publish_daily.py), using today's **Asia/Kolkata** date.
3. Creates a *new* `questions/YYYY-MM-DD.md` with ten original, date-seeded numerical/conceptual practice variations and fully explained answers.
4. Commits only when that day's file does not already exist.

**Important limitations:** GitHub Actions scheduled workflows can run late or be disabled for inactive public repositories. Repository settings must allow Actions and the workflow's `contents: write` permission. A valid workflow file does not by itself prove a schedule has actually fired. Check the repository **Actions** tab for a successful first run.

## Run manually

From a clone:

```bash
python3 scripts/publish_daily.py --date 2026-12-01
python3 scripts/publish_daily.py --date 2026-12-01  # safe: will not overwrite
python3 scripts/publish_daily.py --stdout --date 2026-12-02
```

Or on GitHub: **Actions → Publish 10 daily physics questions → Run workflow**.

If workflow permissions prevent automatic commits, go to **Settings → Actions → General → Workflow permissions**, select **Read and write permissions** if available, and save. Organizational policy may supersede the repository settings.

## Content policy and quality

- Exactly **10 original solved exercises per date**, one from each of ten major physics subjects.
- **30 rotating concept families** with date-dependent numerical parameters (up to three families per subject), so the sequence **repeats topic families**. These are not ten brand-new intellectual problem designs every day.
- A concept explanation, calculation, dimensions or sanity check is provided with each answer.
- **No external API tokens, paid LLM calls, external images, scraped PDFs or copied past papers** are involved.
- Formal 2027 patterns and actual PYQs must be verified against official exam links in [Resources](RESOURCES.md).
- Editorial review is still recommended, especially when an exam board changes its syllabus or you want more advanced multi-step CSIR/TIFR questions.

**Improvement path:** Add new validated cases to the ten `make_...` functions in `scripts/publish_daily.py`; include unit tests for new generators. Maintain [the tracker](TRACKER.md) and use official paper archives for genuine PYQ training.
