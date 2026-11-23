# QUESTIONS — Physics 2027 Mission

**A from-scratch, concept-first, question-driven preparation workspace for TIFR GS, Joint CSIR-UGC NET Physical Sciences, GATE Physics (PH), and IIT JAM Physics (PH).**

> Last plan verification: 23 November 2026. Official notifications control over this repository; check linked exam websites for updates. All practice questions in this repository are original, **not** claimed to be previous-year questions.

## Start here

| Your next step | Link |
|---|---|
| Full exam calendar, conceptual sequence, daily timetable and mock strategy | [2027 MASTER ROADMAP](docs/2027-ROADMAP.md) |
| Official syllabi, exam sites, real PYQ archives, open courses and textbooks | [RESOURCE LIBRARY](docs/RESOURCES.md) |
| Ten worked questions for 23 November (diagnostic launch set) | [DAY 00 — 10 solved questions](questions/2026-11-23.md) |
| Daily generated question sets | [Questions folder](questions/) |
| Track mistakes and mock-test scores | [Study tracker template](docs/TRACKER.md) |
| How scheduled question publishing works | [Daily publishing guide](docs/DAILY-PUBLISHING.md) |

## Official 2027 timeline

| Exam | Date / timing (India) |
|---|---|
| **TIFR GS Physics screening** | **13 December 2026, 2–5 PM** |
| **CSIR-UGC NET Physical Sciences (Dec 2026 cycle)** | **27 December 2026, 3–6 PM** |
| **GATE 2027** | **6–7, 13–14, or 20–21 February 2027**; check the PH paper's exact slot |
| **JAM 2027 Physics** | **14 February 2027, 2:30–5:30 PM** |

Check any potential GATE PH / JAM timetable clash after the official PH slot announcement. For NET, Physics is tested under **Joint CSIR-UGC NET Physical Sciences**, not a separate standalone UGC-NET Physics paper.

## Core method: one syllabus, four exam styles

1. **Understand** the underlying laws, approximations and physical interpretation.
2. **Derive** governing equations from first principles, with units, limits and assumptions.
3. **Solve** 10 original questions each day, then official previous-year questions (PYQs).
4. **Review** every mistake after 48 hours and one week.
5. **Test** yourself under actual exam time limits; adapt answer selection to negative marking.

**December:** TIFR first, then CSIR. **January:** complete remaining GATE/JAM topics. **February:** PYQs, full mocks and accuracy.

## Daily 10-question publishing

The intended automation is a scheduled GitHub Actions workflow at **08:00 IST** that writes a dated Markdown file with ten *parameterized original practice problems* and step-by-step answers. The same date is idempotent (no duplicate file). These are **practice variants**, not newly discovered PYQs; numeric values change from day to day and topic families rotate. GitHub Actions schedules may be delayed and require the workflow to be enabled with repository write permission.

To publish manually: `python3 scripts/publish_daily.py --date 2026-12-01`.

**Original content and teaching material only**; exam board documents and copyrighted papers remain linked to their official hosts rather than copied into this repository.

[Repository](https://github.com/KrAzad0/QUESTIONS) · [TIFR official past papers](https://www.tifr.res.in/academics/past_question_papers.php) · [GATE past papers](https://gate2026.iitg.ac.in/download.html) · [JAM 2027](https://jam.iitkgp.ac.in/) · [CSIR HRDG Physics](https://www.csirhrdg.res.in/Home/Index/1/InPage/39/26)
