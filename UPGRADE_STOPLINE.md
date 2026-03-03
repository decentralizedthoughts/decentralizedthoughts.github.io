# Upgrade Stop Line

This document records the practical stop line reached after the upstream integration slices merged into `upgrade` through commit `8b66b0a`.

## What Was Integrated

The repo already absorbed the upstream changes that were both:

- coherent with the site's current behavior
- safe under the deterministic build and snapshot gates

That includes:

- analytics/include/layout-shell changes
- CI workflow alignment to this repo's actual build contract
- upstream asset tree adoption
- Bootstrap/CSS/JS contract migration where it did not break repo behavior
- retirement of dead legacy theme files such as `page2`, old `css/`, and old `js/`

## Why There Is A Stop Line

The remaining upstream diff is no longer mostly "theme modernization". It is a mix of:

- upstream project-maintenance files for the Beautiful Jekyll theme repo itself
- broad demo-site content rewrites
- packaging and appraisal scaffolding
- config/homepage replacements that would overwrite this blog's intentional behavior
- files that conflict with this repo's regression tooling and deterministic CI contract

At this point, merging more upstream changes mechanically would create more risk than value.

## Remaining Diff Categories

### 1. Repo-specific CI and dependency conflicts

Files:

- `.github/workflows/ci.yml`
- `Gemfile`
- `Gemfile.lock`
- `Appraisals`
- `beautiful-jekyll-theme.gemspec`

Reason to stop:

- Upstream CI assumes the theme repo's appraisal/gemspec workflow.
- This repo intentionally uses GitHub Pages-compatible locked dependencies plus custom checks.
- The current CI contract must preserve `tools/check_site.py` and the snapshot gate.

### 2. Site-specific content/config replacements

Files:

- `_config.yml`
- `index.html`
- `aboutme.md`
- `_data/SocialNetworks.yml`
- `feed.xml`
- `tags.html`

Reason to stop:

- Upstream `_config.yml` is a starter template, not a safe patch over this blog's live configuration.
- Upstream `index.html` and `aboutme.md` are demo-site content and would overwrite site identity.
- The remaining `feed.xml` and `tags.html` drift is real product behavior drift, not cleanup.

### 3. Theme-repo docs and metadata

Files:

- `README.md`
- `CHANGELOG.md`
- `LICENSE`
- `screenshot.png`

Reason to stop:

- These are valid for the Beautiful Jekyll project but not essential to running this blog.
- They should only be adopted deliberately if you want this repo to also function as a theme-distribution repo.

### 4. Local tooling / repo hygiene files

Files:

- `.gitignore`
- `.vscode/settings.json`
- `Dockerfile`
- `grep.sh`
- `print-logs.sh`
- `setup-docker.sh`
- `start-server.sh`
- `stop-server.sh`

Reason to stop:

- These are not part of the runtime site contract.
- Some are upstream-maintainer conveniences; others are local-repo choices that do not justify snapshot/build churn.

### 5. Non-theme demo assets

Files:

- `favicon.ico`
- `profile-kartik.jpg`

Reason to stop:

- These are upstream demo/repo assets, not required for this blog's current theme runtime.

## Recommended Policy Going Forward

- Treat `upgrade` at `8b66b0a` as the integration baseline.
- Only take additional upstream changes when they are repo-aware and subsystem-specific.
- Do not bulk-sync upstream `_config.yml`, homepage content, theme packaging, or CI scaffolding.
- Continue using the snapshot gate as the final correctness guard.

## Candidate Future Work

- selective `_config.yml` adoption of non-breaking knobs
- deliberate homepage migration from custom `index.html` to `layout: home`
- optional documentation refresh if you want this repo to look more like a distributable theme repo
