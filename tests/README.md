# Editing posts and testing layouts

## Publishing and editing posts

Edit or add the Markdown file in `_posts/` and commit it normally. **No snapshot
refresh is required**, including when changing chapter or reading-link metadata.
CI still builds the entire site and checks internal links, assets, and navigation
metadata. A broken link or invalid metadata can still fail those checks.

## Layout regression tests

HTML snapshots cover three fixed fixture pages, rendered with the real
`_layouts/` and `_includes/` templates:

- A plain page.
- A post without optional reading links.
- A post with chapter links, multiple background links, and a follow-up.

The fixture site has its own posts and configuration in `tests/fixtures/`, and a
fixed build time. It never reads production posts, data, or configuration. The
fixtures are excluded from the published site by the production configuration.

After installing the repository's bundle, run:

```sh
bundle exec python3 tools/check_snapshots.py
```

This command compares output without changing the committed snapshots. Only
when intentionally changing templates or fixtures, review the differences and
refresh the three baselines:

```sh
bundle exec python3 tools/check_snapshots.py --update
```

Commit the updated `tests/snapshots/*.html` alongside the layout change. Do not
create snapshots of articles, feeds, pagination, or the production homepage:
those change during ordinary editorial work.
