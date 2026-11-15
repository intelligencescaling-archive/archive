# Entry format (`meta.yaml`, schema version 1)

Every archived item is one folder holding a `meta.yaml` and, when there is one, a plain-text copy
(`text.txt`, or `text-1.txt`, `text-2.txt`, ... for items with several parts).

```
docs/<series-id>/<item-id>/meta.yaml     # docs: grouped by their first series
docs/_other/<item-id>/meta.yaml          # docs with no series (SCD categories, scaling systems, guides...)
stories/<item-id>/meta.yaml              # original stories and fan fiction
data/series.yaml                         # series registry
data/characters.yaml                     # character registry
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
authors:                           # empty list = "Unknown author"
- name: Jarionn
  reddit: Jarionn                  # Reddit username, without u/
  source: doc-text                 # where the credit came from: doc-text | library | reddit-post | submission | manual
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
- **Docs always go under `docs/`**, even if they're also a tier list or similar.
- **Multi-part items** (a story in chapters, a doc split across files) are one entry with several `parts`.
- **Authors:** record whatever is known. Use the name shown on the doc, plus the Reddit username if known.
  Contact handles (Discord, email) are not stored.
- **Review:** entries created by the import script are `status: auto`. After a person checks one, set
  `status: reviewed` and clear `check`. Reviewed entries are never overwritten by scripts.

## Tags

Content type: `feats`, `analysis`, `strategy`, `planning`, `scheming`, `manipulation`, `reasoning`,
`debunk`, `rebunk`, `matchup`, `composite`, `writing-analysis`, `tier-list`, `transcript`, `collection`.
Intelligence categories: `fsiq`, `eq`, `cpi`, `psi`, `vsi`, `vci`.
About SCD itself: `scd-categories`, `scaling-system`, `scd-theory`, `writing-categories`, `guide`,
`history`, `library`, `list`.
Other: `wis` (powerscaling / "who would win"), `cosmology`, `oc` (original character),
`fanfiction`, `humor`, `q-and-a`, `hall-of-shame`.
