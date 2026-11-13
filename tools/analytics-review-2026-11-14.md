# DT readership audit — November 14, 2026

## Scope and baseline

Read the connected GA4 property 517183869 in Chrome. Selected an explicit
90-day report period: August 16–November 13, 2026. Reviewed Pages and screens,
404 titles with a secondary Page path dimension, Traffic acquisition, Landing
page, Demographic details, Tech overview, and the engagement/retention overview.
These are observations from the report UI, not a raw event export. No GA
administration settings or historical data were changed. This file is in the
excluded `tools/` directory and is not published with the website.

| Metric | 90-day baseline |
| --- | ---: |
| Views | 18,445 |
| Active users | 9,759 |
| Sessions | 13,466 |
| Engaged sessions | 3,074 |
| Engagement rate | 22.83% |
| Average engagement per active user | 39 seconds |
| Average engagement per session | 28 seconds |
| Reported key events | 0 |

## Findings and actions

### 1. Recover requests to known old URLs

The 404 title received 470 views (2.55% of all views), across 269 title/path
combinations. `/about-ittai/` alone received 79, approximately 17% of 404 views.
Other observed paths included `/about-ling/` (8), `/about-kartik/` (6),
`/2019-06-27-what-is-consensus/` (13),
`/2020-02-26-blockchain-selfish-mining/` (11), and
`/2019-11-10-authenticated-synchronous-bft` with and without a trailing slash
(7 and 4). Some error URLs appear to be guessed article names; a 404 is not
automatically evidence of a broken internal link.

Added Jekyll redirects for confirmed author and article destinations, including
two dated article URLs previously exempted by the internal-link validator.
Kept canonical article URLs. Made `/tags/` the tag index permalink and preserved
`/tags.html` as an alias. Used root-relative author image paths to avoid path
resolution differences. The subcubic-broadcast article already exists at its
canonical URL; only the observed `.md/` variant needs an alias.
The stronger validator also found self-redirect metadata on the optimistic
responsiveness post. Its canonical June 12 URL is preserved; the alias now
maps the filename's June 11 date to that canonical URL.

Removed clickable `TBD`, `...`, and unpublished-security-post placeholders,
preserving their prose. The clock post's unpublished sequel is now plain text.
Several historical placeholder errors already had no corresponding live broken
link; no destinations were invented for them.

Replaced the dismissive 404 message and image with archive search, Start Here,
latest posts, and topic browsing. Added a `page_not_found` event to the existing
GA destination, containing the requested pathname without its query string.

### 2. Grow the channels that produce engaged readers

| Channel | Sessions | Engaged sessions | Engagement rate | Average engagement/session |
| --- | ---: | ---: | ---: | ---: |
| Direct | 7,976 | 986 | 12.36% | 11s |
| Organic Search | 2,545 | 1,194 | 46.92% | 59s |
| Referral | 2,071 | 609 | 29.41% | 52s |
| Organic Social | 560 | 234 | 41.79% | 13s |
| AI Assistant | 156 | 65 | 41.67% | 1m 45s |

Organic search contributes 38.84% of engaged sessions from 18.9% of sessions.
This is the strongest demonstrated channel to develop. AI referrals look
promising but have a much smaller sample. Do not prioritize publishing volume
or a visual redesign solely from the sitewide average.

Next: use Search Console query/impression/position data to choose explainers
with search growth potential. Those data were not available in this review;
GA page views alone do not establish search ranking or click-through problems.

### 3. Help readers enter the archive

The homepage has 2,322 views and 12 seconds average engagement per active user.
Popular evergreen pages include Merkle trees (891 views, 1m 08s), synchrony
(436, 54s), What is Consensus? (313, 1m), and Dolev–Strong (303, 1m 58s).
Start Here has 584 views and 31 seconds engagement per active user.

Added a compact homepage introduction with paths to foundations, Merkle trees,
and the Simplex chapter, plus archive search. Recent posts remain below it;
pagination pages retain the feed without repeating the introduction.

Popular posts already contain curated background and follow-up metadata.
Preserved those selections. Added `reading_link_click` for those links and
homepage/404 discovery links, with source path, destination path, and link type.
Search queries are not collected by this new instrumentation. Link clicks
measure navigation, not successful reading or comprehension.

### 4. Separate traffic quality from reader experience

Singapore accounts for 3,365 active users (34.48%) but only 140 engaged sessions,
a 4.04% engagement rate, and 6 seconds engagement per active user. The US has
3,599 active users, 19.86% engagement, and 32 seconds. India has 48.3%
engagement and 2m 37s; Israel has 49.11% and 1m 24s.

Desktop represents 88.5% of users, mobile 11.1%, and tablet 0.3% in the Tech
overview. The leading resolutions include 1280×1200 (2,620 users), 1280×1280
(1,251), and 800×600 (1,085). City concentrations include Singapore and The
Dalles. These patterns are consistent with automation but do not prove it.
Do not block countries or discard direct traffic based on these observations.
Compare source, location, device, and engagement together before filtering.

The retention overview provides cohort charts, but this review did not extract
a numerical return rate. New and active user counts must not be subtracted to
infer returning users.

## Verification and follow-up

Built the site, checked all internal links/assets and redirect destinations,
validated chapter/reading metadata, and confirmed three unchanged layout
snapshots. Added regression tests for placeholder links and self-redirects,
and enabled them in CI. JavaScript checks covered navigation events, query
stripping, external links, and unavailable analytics. Visually checked the
homepage and verified a 404-page search for “merkle” returned the expected post.
The local preview disables GA so testing does not add production events.

After deployment, verify both new event types in GA, then compare equal 28-day
periods for valid-content engagement, 404 paths, homepage discovery clicks,
reading-link clicks, and organic-search engaged sessions. Report geography and
source alongside averages. A fall in total 404s is useful, but recovering the
specific mapped URLs is the direct test of the redirects. Historical totals
will not change. GA key events remain unconfigured; confirm the desired reader
outcome before treating clicks as conversions.
