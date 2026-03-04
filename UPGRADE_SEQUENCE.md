# Upgrade Sequence

This document summarizes the upstream integration performed on `upgrade` from the deterministic baseline through commit `8b66b0a`.

## Invariants Used Throughout

Each accepted slice preserved these checks:

- clean git status after merge
- reproducible production build in CI
- `tools/check_site.py`
- snapshot regeneration with no unexpected drift
- custom tooling under `tests/` and `tools/`

## Baseline

Before upstream slicing, `upgrade` already carried repo-specific correctness infrastructure:

- deterministic Jekyll/GitHub Pages build setup
- internal link and asset checker
- normalized HTML snapshot harness

Key pre-slice commits:

- `c0fc5a7` reproducible local build settings
- `187727f` GitHub Pages gem-set CI build
- `f37d8db` custom site integrity checker in CI
- `f96eab5` normalized snapshot harness

## Slice Summary

### Slices 1-4

- `97e2f32` slice 1: imported Cloudflare analytics include changes
- `ae2a927` slice 2: integrated upstream include updates and hardened snapshot normalization
- `cf027ba` slice 3: aligned upstream CI with this repo's build gates instead of appraisal/theme-repo assumptions
- `7fb2f01` slice 4b: imported the upstream `assets/` tree without switching layout references yet

### Slices 5-8

Merged commits:

- `6895100`
- `cc73a6a`
- `18c1bdb`
- `e4ea6e0`

These were the early narrow theme-alignment slices between the asset-tree import and the larger layout migrations. They kept the regression gates intact while moving theme references closer to the upstream structure.

### Slice 9

- `3603562`: migrated `base` layout Bootstrap CSS to the CDN contract

### Slice 10

- `3b364af`: migrated `minimal` layout Bootstrap CSS to the CDN contract

### Slice 11

- `990dfef`: migrated `minimal` stylesheet reference to the upstream `assets/` path

### Slice 12

- `2dee03a`: migrated the shared JS stack for `base` and `minimal`

Important retained divergence:

- kept full jQuery rather than upstream slim jQuery because repo compatibility mattered more than theme purity

### Slice 13

- `7204f7a`: modernized the content layout family (`default`, `page`, `post`, plus dormant `home` scaffold)

### Slice 14

- `ae6d73a`: added dormant support assets and removed dead includes

### Slice 15

- `6aeed2f`: modernized `base` and `minimal` shells while preserving repo-specific behavior

### Slice 16

- `cc2c031`: retired the last live legacy theme branch

Changes:

- migrated `contents.md` from `page2` to `page`
- removed `_layouts/page2.html`
- removed `_includes/just_comments.html`
- deleted obsolete legacy `css/` and `js/` trees

### Slice 17

- `c5b60f4`: updated auxiliary/theme-support files with a narrowed, repo-safe scope

Accepted changes:

- `404.html`
- `_data/ui-text.yml`
- `staticman.yml`
- minimal `feed.xml` normalization

Rejected during narrowing:

- broader `feed.xml` and `tags.html` behavior drift that would have required intentional baseline changes without a strong payoff

### Slice 18

- `8b66b0a`: normalized layout asset front matter in `base` and `minimal`

This was a formatting-only alignment slice and cleared CI without snapshot churn.

## Result

The repo now carries the upstream theme/runtime changes that fit a content-heavy research blog with deterministic CI, while intentionally preserving:

- custom regression tooling
- snapshot-based correctness gating
- repo-specific CI workflow
- blog-specific content and navigation structure
- compatibility-driven divergences where upstream theme defaults were not safe

## Current Baseline

- branch: `upgrade`
- merge head after accepted slices: `8b66b0a`
- recommended stop line: see `UPGRADE_STOPLINE.md`
