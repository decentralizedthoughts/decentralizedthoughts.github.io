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

Run `ruby tools/check_post_links.rb` to validate the metadata. After building,
refresh HTML snapshots with
`python3 tools/list_urls.py | python3 tools/snapshot_html.py`.
