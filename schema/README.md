# Entry format (`meta.yaml`, schema version 1)

Every archived item is one folder holding a `meta.yaml` and, when there is one, a plain-text copy
(`text.txt`, or `text-1.txt`, `text-2.txt`, ... for items with several parts).

```
docs/<series-id>/<item-id>/meta.yaml     # docs: grouped by their first series
docs/_other/<item-id>/meta.yaml          # docs with no series (SCD categories, scaling systems, guides...)
stories/<item-id>/meta.yaml              # original stories and fan fiction
data/series.yaml                         # series registry
data/characters.yaml                     # character registry
data/authors.yaml                        # author registry: one record per person, with all their names
```

PDF/DOCX files are not in git. They're hosted separately, and each one is identified by its `sha256`.
The machine-readable schema is [`meta.schema.json`](meta.schema.json). Check everything with
`python scripts/validate.py` (needs `pip install -r scripts/requirements.txt`).

## Example

```yaml
schema_version: 1
id: chen-ran-wss-game-doc          # unique, lowercase-with-dashes, same as the folder name, never changes
category: doc                      # doc | story | misc
title: Chen Ran WSS Game Doc       # the title the author gave the file
alt_titles:                        # other names it's listed under (searchable)
- Chen Ran's Wolf Sheep Shepherd Game doc
authors:                           # who MADE it; empty list = "Unknown author"
- name: Jarionn                    # the name as shown on the doc
  reddit: Jarionn                  # Reddit username, without u/
  id: jarionn                      # the person in data/authors.yaml
  source: doc-text                 # where the credit came from: doc-text | library | reddit-post | submission | manual
shared_by:                         # optional: who shared it (e.g. the Reddit poster) when the doc doesn't show them as its maker
- name: SomeRedditor
  reddit: SomeRedditor
  id: someredditor
  source: reddit-post
series: [18-levels-of-hell]        # ids from data/series.yaml (first one decides the folder)
characters: [chen-ran]             # ids from data/characters.yaml
variant: Light Novel               # optional: which version (Composite, Novels, Movies, Anime...)
tags: [feats]
language: en                       # ISO 639-1 code, null if unknown
completion: unknown                # finished | in-progress | unknown (as marked by the author or library)
parts:                             # one per file; a story split into chapters has several
- title: Chapter 1                 # only when there are several parts
  source:
    type: google-doc               # google-doc | google-doc-published | google-drive-file | google-slides | reddit-post | web-page | other
    url: https://docs.google.com/document/d/.../edit
    google_id: 1JywZc7PkCB-...
  capture:
    status: complete               # complete | partial | export-blocked | dead | private | not-captured
    date: '2026-11-15'
    pages: 12
    words: 3400
    files:
    - {format: pdf, name: document.pdf, bytes: 84137, sha256: f590...}
    text: {file: text.txt, method: google-export}   # google-export | pdf-extract | html-extract | docx-extract | reddit-text | manual
    missing: {pdf: HTTP 500}       # only when something couldn't be saved
found_in:                          # where the community libraries list it
- library: old                     # old | remastered | stories
  section: '18 LEVELS OF HELL:'
  link_text: Chen Ran's Wolf Sheep Shepherd Game doc
links: []                          # optional: Reddit post, Wayback snapshot, discussion
added: '2026-11-15'
review:
  status: auto                     # auto = filled in by a script; reviewed = checked by a person
  check: [authors]                 # which fields are guesses and worth checking
notes: ''                          # optional free text
```

## Rules

- **`id` never changes** once published (links and downloads depend on it). Titles can.
- **Series and characters** must exist in the registries. Add new ones there first. A character
  with no known series has `series: null`.
- **Source language** of a series goes in `data/series.yaml`, not in entries:
  ```yaml
  - id: omniscient-reader-s-viewpoint
    name: Omniscient Reader's Viewpoint
    origin_language: ko        # ISO 639-1 code of the first published version, or `real` for real life
    origin_medium: web-novel   # optional: manga, light-novel, web-novel, novel, anime, tv, film, game, ...
  ```
  Use the language of the **first published version**, not the adaptation a doc is about (an anime made
  from a Korean webtoon is `ko`). This is different from an entry's `language`, which is the language
  the doc itself is written in. A series with no `origin_language` yet only gives a warning.
- **Docs always go under `docs/`**, even if they're also a tier list or similar.
- **Multi-part items** (a story in chapters, a doc split across files) are one entry with several `parts`.
- **Authors:** record whatever is known. Use the name shown on the doc, plus the Reddit username if known.
  Contact handles (Discord, email) are not stored. Each credit's `id` points to one person in
  `data/authors.yaml`, so one person credited under several names (a display name, a Reddit handle, an old
  username) is still one author.
- **Shared by:** when a doc was found through a Reddit post or comment and neither the doc nor the post shows
  the poster made it, the poster goes in `shared_by`, not `authors` (decided 2026-11-18). If the doc or the post
  says they made it ("Made by u/x", "my doc", "I made this"), they are an author with `source: reddit-post`
  (or `doc-text`). A person is never both an author and a sharer of the same entry.
- **Characters imply their series:** an entry lists the series of every character it lists. A character whose
  work is unknown, or an original character (OC) with no wider work, has `series: null`; OC entries get the `oc` tag.
- **Merged ids:** when two registry ids turn out to be the same character, one id is kept and the other's
  spellings become its `aliases`. The old id stops being used (the website redirects it).
- **Review:** entries created by the import script are `status: auto`. After a person checks one, set
  `status: reviewed` and clear `check`. Reviewed entries are never overwritten by scripts.

## Author registry (`data/authors.yaml`)

```yaml
- id: due-ad8334                 # stable; usually the slug of the first Reddit handle or name seen
  name: TheNoo                   # the main display name
  aliases: [Due_Ad8834]          # other names and spellings the person is credited under
  reddit: [Due_Ad8334]           # their Reddit username(s), without u/
  note: "'Made by TheNoo (u/Due_Ad8334)'"   # optional: why these names are one person
```

A credit belongs to a record when its Reddit handle is in `reddit`, or else its name is the record's name, an
alias or a handle (any case). A name match is not used when the credit's Reddit handle differs from the
record's handles (two people with the same display name). Co-authors stay separate records even when a byline
joins them with "/" ("A/B" is often two people). To merge two records, move one's names and handles into the
other and delete it; the next build re-links every entry.

## Tags

Content type: `feats`, `analysis`, `strategy`, `planning`, `scheming`, `manipulation`, `reasoning`,
`debunk`, `rebunk`, `matchup`, `composite`, `writing-analysis`, `tier-list`, `transcript`, `collection`.
Intelligence categories: `fsiq`, `eq`, `cpi`, `psi`, `vsi`, `vci`.
About SCD itself: `scd-categories`, `scaling-system`, `scd-theory`, `writing-categories`, `guide`,
`history`, `library`, `list`.
Other: `wis` (powerscaling / "who would win"), `cosmology`, `oc` (original character),
`fanfiction`, `humor`, `q-and-a`, `hall-of-shame`.
