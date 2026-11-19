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
data/reddit-accounts.yaml                # which Reddit accounts named in the archive still exist
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
  A maker who names themself only by a contact handle ("my discord is X") is credited under that handle, and
  the handle goes in their record's `contacts` (below). Emails and phone numbers are never stored. Each credit's `id` points to one person in
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
  contacts:                      # optional: where the person can be found, from their own docs
  - platform: discord            # discord, telegram, reddit, twitter, youtube, tiktok or other
    handle: thenoo_              # the username as written, without quotes or a leading "@"
  - platform: other
    label: Instagram             # required for platform other
    handle: thenoo
```

`contacts` lists only handles a person wrote in their own doc as their contact or account ("Discord: x",
"my cord is x", "x on TikTok"). Never a helper's handle, a server invite, an email, a phone number or a
numeric Discord ID. Reddit usernames stay in `reddit`. Each contact was taken from a quoted line in one of the
person's entries, and `validate.py` checks the format.

A credit belongs to a record when its Reddit handle is in `reddit`, or else its name is the record's name, an
alias or a handle (any case). A name match is not used when the credit's Reddit handle differs from the
record's handles (two people with the same display name). Co-authors stay separate records even when a byline
joins them with "/" ("A/B" is often two people). To merge two records, move one's names and handles into the
other and delete it; the next build re-links every entry.

## Reddit accounts (`data/reddit-accounts.yaml`)

```yaml
- handle: Due_Ad8334             # as spelled in the data, without u/; one row per handle (any case)
  status: active                 # active | suspended | gone | unknown
  checked: 2026-11-19            # date of the check
```

One row for every Reddit username in `data/authors.yaml` (`reddit`, reddit `contacts`) and in entries'
`authors` / `shared_by`, sorted by handle (case-insensitive). The maintainer's check script makes one request
to Reddit per handle: `active` = the account exists, `suspended` = Reddit suspended it, `gone` = Reddit says it
doesn't exist (deleted, or never existed: Reddit can't tell these apart), `unknown` = the check gave no
answer. An `unknown` result never replaces an older known one. Handles not checked yet are missing (the file
can be an empty list). The entry builder never writes this file; `validate.py` checks its format.

## Tags (`data/tags.yaml`)

The tag list is fixed (approved 2026-11-18) and lives in `data/tags.yaml`: one record per tag with `id`, `name`,
`group`, a one-line `definition`, `examples`, `aliases` (old tag names that now mean this tag) and `implies`.
`validate.py` rejects any tag that is not in the registry. Each entry has **1 to 3 tags**, most important first,
plus the meta tag `translation` when it applies.

| tag | group | when |
|---|---|---|
| `feats` | type | a character's intelligent feats, scene by scene; also a write-up of one feat ("Siesta's Scheming Feats") |
| `analysis` | type | one scene, plan, arc or trait analysed in depth ("how the Kira plan works") |
| `matchup` | type | X vs Y: who outsmarts whom ("Johan vs Moriarty") |
| `debunk` | type | argues a feat, doc or claim is wrong ("Debunking Ayanokoji's feats") |
| `rebunk` | type | answers a debunk ("Rebunk of the Light debunk") |
| `composite` | type | one character built from several versions ("Composite Sherlock Holmes") |
| `writing` | type | a character or story as writing: themes, psychology, how well written ("Femto Descent Analysis") |
| `ranking` | type | tier list, top N ("Top 10 smartest characters") |
| `guide` | type | explains SCD, its categories or a scaling system ("All categories for SCD") |
| `template` | type | a blank format to fill in ("Feats doc template") |
| `discussion` | type | opinion, essay, Q&A, debate ("What counts as intelligence?") |
| `game` | type | a community game, tournament or event ("SCD tournament") |
| `community` | type | libraries, link lists, archive or subreddit history ("The Ultimate SCD Library") |
| `story` | fiction | fiction; same as category `story` |
| `fanfiction` | fiction | fiction with existing characters; implies `story` |
| `oc` | subject | about an original character |
| `powerscaling` | subject | physical power, not intelligence: strength, speed, hax, cosmology ("Dragon Ball Scaling") |
| `translation` | meta | a translation of another doc or of source material (doesn't count toward the 3) |

Rules: the `story` tag and category `story` always go together (a story lives in `stories/<id>/`). Implied tags
are stored (`fanfiction` → `story`). The website derives the other meta labels from existing fields, so they are
not stored as tags: in progress (`completion`), text only (no PDF in `parts[].capture.files`), original gone
(`capture.status` dead/private), multi-part (several `parts`). Real people are not a tag: their characters have
`real: true` in `data/characters.yaml`, and their series is under Real life (`origin_language: real`).

Retired tags (2026-11-18, no longer stored): the skill tags `strategy`, `planning`, `scheming`, `manipulation`,
`reasoning` (now `analysis`), `fsiq`, `eq`, `cpi`, `psi`, `vsi`, `vci`, and `wis`, `humor` (`cosmology` is now `powerscaling`). Other
old names are aliases of the new tags (see `data/tags.yaml`).

## Characters (`data/characters.yaml`)

```yaml
- id: light-yagami
  name: Light Yagami
  series: death-note             # or null when unknown / an original character
  aliases: [Kira]
- id: napoleon-bonaparte
  name: Napoleon Bonaparte
  series: history
  real: true                     # optional: a real person (historical figure, internet personality, community member...)
```
