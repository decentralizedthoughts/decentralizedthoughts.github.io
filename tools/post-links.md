# Chapter and reading links (pilot)

Add optional lists of canonical post URLs to a post's YAML front matter:

```yaml
chapters:
  - /2026-05-25-chapter-simplex/
background:
  - /2025-11-08-benign-simplex/
continue_reading:
  - /2026-05-14-simplex-FVS/
```

Titles are taken from the referenced posts. List order controls display order.
Each list can contain several links; omit a list when it is not needed.
Links are curated in each direction, rather than automatically made reciprocal.
Chapter pages keep their existing hand-written content during the pilot.

Run `ruby tools/check_post_links.rb` to validate the metadata. Editing post
content or these metadata lists does not require updating HTML snapshots.
CI builds the site and checks links and metadata automatically.

Layout snapshots use fixed fixtures, independent of published posts. See
[the snapshot guide](../tests/README.md) when changing templates.
