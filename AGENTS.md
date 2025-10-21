# Repository Guidelines

This repository captures publicly available FoundationDB documentation for long-term reference. Every contribution should be sourced, reproducible, and easy to audit.

## Project Structure & Module Organization
Place raw copies under `sources/` grouped by publisher, year, and slug, e.g., `sources/apple/2017/foundationdb-overview.md`. Store video or podcast transcripts in `transcripts/`. Supporting images, diagrams, or PDFs belong in `assets/`. Maintain canonical metadata in the root `README.md` under a “Catalog” section, capturing title, author, original URL, capture date, and SHA-256 checksum (use `shasum -a 256 <file>`). If you create helper notes or scripts, keep them in `tools/` and document their usage inline.

## Build, Test, and Development Commands
Favor lightweight, repeatable steps. Use `git status` and `git diff` to verify that only intended files are staged. Run `shasum -a 256 <file>` for each new artifact and record the checksum alongside the entry you add to `README.md`. For large imports, stage files in batches so reviewers can skim meaningful diffs.

## Coding Style & Naming Conventions
Default to UTF-8 Markdown with 80-character soft wraps. Preserve original formatting when mirroring external docs; add a prefixed note if adjustments are required. Filenames should be lowercase with hyphens and end in the original extension (`.md`, `.pdf`, `.png`). Keep catalog tables in `README.md` sorted by capture date (newest first) and ensure column headers stay consistent.

## Testing Guidelines
Treat catalog accuracy as the primary “test.” Confirm every new `README.md` catalog entry includes title, author, URL, capture date, and checksum. Open a random sample of new links to confirm they resolve. When adding transcripts, proofread for obvious transcription errors and note any gaps.

## Commit & Pull Request Guidelines
Write imperative, scoped commit subjects (`archive: add 2014 layered architecture paper`). Include the original URL, capture date, and checksum in the body. Pull requests need: a one-paragraph summary, list of new sources, link to upstream material, and a short checklist of manual verification steps performed. Attach representative screenshots only when visual fidelity matters.

## Source Integrity
Prefer primary, reputable sources. Record capture context in the `README.md` catalog, and note redactions or deviations in a “Notes” column. If a document changes upstream, add a new version instead of mutating the original; cross-link predecessors in the catalog entry.
