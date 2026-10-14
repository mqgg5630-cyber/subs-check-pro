# Civil-service position-table screening skill

## Purpose

Use a public Chinese civil-service recruitment XLS/XLSX position table plus an
applicant's **self-reported** eligibility and preferences to create an
explainable shortlist. This skill is for the applicant's own decision support;
it does not make an official eligibility determination or predict selection
probability.

## Intake contract

1. The public workbook must be present under:

   ```text
   results/civil_service_exam/source/
   ```

2. Check `results/civil_service_exam/ingest_manifest.json` first. Confirm the
   file size and SHA-256 rather than assuming a partial or stale upload is the
   correct workbook.
3. Keep the personal profile local-only in:

   ```text
   config/civil_service_profile.local.json
   ```

   It is intentionally ignored by Git. Do not commit identification numbers,
   contact details, health records, or an applicant's personal profile.
4. Use only attributes volunteered by the applicant. Do not infer sex, age,
   political status, household registration, health, ethnicity, or other
   personal characteristics from names, photographs, location, or text.

## Runbook

```bash
python -m pip install -r code/civil_service_exam/requirements.txt
python code/civil_service_exam/analyze_positions.py \
  --input 'results/civil_service_exam/source/<position-table>.xls' \
  --profile config/civil_service_profile.local.json \
  --out results/civil_service_exam/local_analysis
```

The parser includes every worksheet with a recognizable position-table header;
use `--sheet '<exact worksheet name>'` only when intentionally narrowing the
scope. Use `--no-profile` to inspect the public table and detected columns
before a profile is available. Keep the full personal output local; if a
shareable deliverable is needed, publish only a redacted, source-referenced
candidate summary rather than the profile or full personalised export.

When an applicant explicitly asks to examine every position in a target region despite a major mismatch, export a **manual-review pool** rather than relabeling those jobs as eligible or major-unrestricted:

```bash
python code/civil_service_exam/export_manual_pool.py \
  --input results/civil_service_exam/local_analysis/all_positions_normalized.csv \
  --region 福建 \
  --out deliverables/civil_service_exam_2027/福建_全岗位人工复核池.csv
```

Use `--exclude-non-major-mismatch` to make a smaller inquiry queue. The pool must retain the original major requirement, source sheet/row, and non-major conflict labels; it must never be described as a final shortlist or as “不限专业” unless that is the literal public-table value.

## Required review discipline

- Keep three result layers: `初筛可报（仍须按官方公告核验）`, `需人工核验`, and
  `初筛不匹配`.
- Quote the public-cell text that produced every mismatch or review flag.
- Treat ambiguous professional catalogues, graduation status, household rules,
  political-status wording, English thresholds, service-project language, and
  remarks as manual-review items.
- A score is a stated-preference ordering only. Do not call it admission odds,
  competitiveness, salary, or an employment recommendation.
- Confirm final job code, age cut-off date, degree/major catalogue, and official
  notice wording before submitting an application.

## Local watched-file bridge

`watch.ps1` reads `watched_uploads` from `skills/git-sync/sync.config.json`.
Each entry must name one source file and one repository-relative destination.
The watcher waits for a stable file, verifies SHA-256, writes a manifest, and
uses the existing hands-free Git push. If the source is locked by Excel/WPS or
another process, it logs an unreadable state and retries on the next poll; it
must never terminate the locking application or bypass its file lock.
