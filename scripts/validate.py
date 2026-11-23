"""Validate every archive entry.

Checks each meta.yaml against schema/meta.schema.json, then the things a schema can't see:
  - id matches the folder name, and ids and Google ids are unique
  - docs live in docs/<first series>/<id>/ (or docs/_other/<id>/ with no series); stories in stories/<id>/
  - every series and character id exists in data/series.yaml / data/characters.yaml
  - every author/shared_by `id` exists in data/authors.yaml, and no Reddit handle belongs to two people
  - people's `contacts` use a known platform and a plain username (no '@', emails, phone numbers or IDs)
  - data/reddit-accounts.yaml (if present): {handle, status, checked} rows, sorted, no duplicates
  - each series' origin_language is a 2-letter code or `real` (a missing one is only a warning)
  - every tag exists in data/tags.yaml; 1 to 3 tags besides meta tags; implied tags are present;
    the `story` tag and category `story` go together; characters' `real` is true/false
  - every text file named in the entry exists, and no stray files sit in entry folders
  - reader files (capture.blocks, blocks.json): valid v1 JSON whose image/palette references resolve, safe links only
  - image placement (files[].media_id, px): only on image files of reddit-post parts, media ids unique within a part

Usage: python scripts/validate.py [repo-root]     (exit code 1 if anything is wrong)
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ALLOWED_FILES = {"meta.yaml"}
CONTACT_PLATFORMS = ("discord", "telegram", "reddit", "twitter", "youtube", "tiktok", "other")
REDDIT_STATUSES = ("active", "suspended", "gone", "unknown")
EMAIL = re.compile(r"\S+@\S+\.\w+")


BLOCK_KINDS = {"p", "h", "li", "img", "table", "box", "hr", "sep", "gap", "break", "notes", "anchor"}
SAFE_HREF = re.compile(r"^(https?://|mailto:|#)", re.I)


def check_blocks(path, err):
    """A reader file (blocks.json): JSON, version 1, known block kinds, image and palette references resolve,
    links are http(s)/mailto/#anchor only, image file names are plain hash names."""
    name = path.name
    if not path.is_file():
        err(f"missing reader file {name}")
        return
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError) as e:
        err(f"{name}: not valid JSON ({e})")
        return
    if not isinstance(doc, dict) or doc.get("v") != 1 or not isinstance(doc.get("b"), list):
        err(f"{name}: needs v: 1 and a block list b")
        return
    imgs, pal = doc.get("img") or {}, doc.get("pal") or {}
    for k, im in imgs.items():
        src = im.get("src") or {}
        for f in (src.get("p"), src.get("f")):
            if f is not None and not re.fullmatch(r"[0-9a-f]{16}-(720|1360)\.webp", str(f)):
                err(f"{name}: image {k}: bad file name {f}")
    problems = set()

    def runs(rs):
        for r in rs or []:
            if "img" in r and r["img"] not in imgs:
                problems.add(f"unknown image {r['img']}")
            if r.get("c") and r["c"] not in pal:
                problems.add(f"unknown palette key {r['c']}")
            if r.get("a") and not SAFE_HREF.match(str(r["a"])):
                problems.add(f"unsafe link {str(r['a'])[:40]}")

    def walk(bs):
        for b in bs:
            k = b.get("k")
            if k not in BLOCK_KINDS:
                problems.add(f"unknown block kind {k}")
                continue
            if k == "img" and b.get("i") not in imgs:
                problems.add(f"unknown image {b.get('i')}")
            if b.get("bg") and b["bg"] not in pal:
                problems.add(f"unknown palette key {b['bg']}")
            runs(b.get("r"))
            for row in b.get("rows") or []:
                for c in row.get("c") or []:
                    if c.get("bg") and c["bg"] not in pal:
                        problems.add(f"unknown palette key {c['bg']}")
                    walk(c.get("b") or [])
            if k == "box":
                walk(b.get("b") or [])
            for n in b.get("notes") or []:
                walk(n.get("b") or [])

    walk(doc["b"])
    ws = [b.get("w") for b in doc["b"]]
    if any(not isinstance(w, int) for w in ws) or any(a > b for a, b in zip(ws, ws[1:])):
        problems.add("block word offsets (w) must be integers that never go down")
    for p in sorted(problems)[:5]:
        err(f"{name}: {p}")


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
    validator = Draft202012Validator(json.loads((root / "schema" / "meta.schema.json").read_text(encoding="utf-8")))
    series_rows = yaml.safe_load((root / "data" / "series.yaml").read_text(encoding="utf-8")) or []
    series = {s["id"] for s in series_rows}
    chars = {c["id"]: c for c in yaml.safe_load((root / "data" / "characters.yaml").read_text(encoding="utf-8")) or []}
    ap = root / "data" / "authors.yaml"
    people = {a["id"]: a for a in (yaml.safe_load(ap.read_text(encoding="utf-8")) or [])} if ap.exists() else {}
    tp = root / "data" / "tags.yaml"
    tag_rows = (yaml.safe_load(tp.read_text(encoding="utf-8")) or []) if tp.exists() else []
    tags = {t["id"]: t for t in tag_rows}
    errors, warnings, ids, gids, n = [], [], {}, {}, 0

    if not tp.exists():
        errors.append("data/tags.yaml is missing")
    seen_names = {}
    for t in tag_rows:
        for k in ("id", "name", "group", "definition"):
            if not t.get(k):
                errors.append(f"data/tags.yaml: {t.get('id')}: missing {k}")
        if re.search(r"[`*]", str(t.get("definition") or "")):
            errors.append(f"data/tags.yaml: {t.get('id')}: definition is shown on the website, use plain text (no ` or *)")
        if t.get("group") not in ("type", "fiction", "subject", "meta"):
            errors.append(f"data/tags.yaml: {t.get('id')}: group should be type, fiction, subject or meta")
        for a in [t.get("id"), *(t.get("aliases") or [])]:
            if a in seen_names:
                errors.append(f"data/tags.yaml: '{a}' is used by both {seen_names[a]} and {t.get('id')}")
            seen_names[a] = t.get("id")
        for i in t.get("implies") or []:
            if i not in {r.get("id") for r in tag_rows}:
                errors.append(f"data/tags.yaml: {t.get('id')}: implies unknown tag {i}")
    old_names = {a: t["id"] for t in tag_rows for a in t.get("aliases") or []}

    for s in series_rows:
        lang = s.get("origin_language")
        if lang is None:
            warnings.append(f"data/series.yaml: {s['id']}: no origin_language yet")
        elif not (lang == "real" or (isinstance(lang, str) and len(lang) == 2 and lang.isascii() and lang.islower())):
            errors.append(f"data/series.yaml: {s['id']}: origin_language '{lang}' should be a 2-letter ISO 639-1 code or 'real'")

    for c in chars.values():
        if "real" in c and not isinstance(c["real"], bool):
            errors.append(f"data/characters.yaml: {c['id']}: real should be true or false")
        if c.get("series") and c["series"] not in series:
            errors.append(f"data/characters.yaml: {c['id']}: unknown series {c['series']}")
    for a in people.values():
        cs = a.get("contacts")
        if cs is None:
            continue
        if not isinstance(cs, list) or not cs:
            errors.append(f"data/authors.yaml: {a['id']}: contacts should be a non-empty list")
            continue
        for c in cs:
            where = f"data/authors.yaml: {a['id']}: contact {c}"
            if not isinstance(c, dict) or set(c) - {"platform", "handle", "label"}:
                errors.append(f"{where}: only platform, handle and label are allowed")
                continue
            if c.get("platform") not in CONTACT_PLATFORMS:
                errors.append(f"{where}: platform should be one of {', '.join(CONTACT_PLATFORMS)}")
            if c.get("platform") == "other" and not c.get("label"):
                errors.append(f"{where}: platform other needs a label (e.g. Instagram)")
            h = c.get("handle")
            if not isinstance(h, str) or not h.strip():
                errors.append(f"{where}: handle should be a non-empty string")
            elif h.startswith("@") or EMAIL.search(h) or re.fullmatch(r"[\d\s+()-]{7,}", h):
                errors.append(f"{where}: handle should be a username without '@' (no emails, phone numbers or numeric IDs)")
    handles = {}
    for a in people.values():
        for h in a.get("reddit") or []:
            if h.lower() in handles and handles[h.lower()] != a["id"]:
                errors.append(f"data/authors.yaml: Reddit handle {h} is in both {handles[h.lower()]} and {a['id']}")
            handles[h.lower()] = a["id"]

    rp = root / "data" / "reddit-accounts.yaml"
    if rp.exists():
        rows = yaml.safe_load(rp.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            errors.append("data/reddit-accounts.yaml: should be a list (can be empty)")
            rows = []
        seen_h, prev = set(), ""
        for r in rows:
            if not isinstance(r, dict) or set(r) != {"handle", "status", "checked"}:
                errors.append(f"data/reddit-accounts.yaml: {r}: needs exactly handle, status and checked")
                continue
            h = r["handle"]
            if not isinstance(h, str) or not re.fullmatch(r"[A-Za-z0-9_-]{3,20}", h):
                errors.append(f"data/reddit-accounts.yaml: {h}: not a Reddit username (3-20 letters, digits, _ or -, no u/)")
                continue
            if h.lower() in seen_h:
                errors.append(f"data/reddit-accounts.yaml: {h}: listed twice (any case)")
            if h.lower() < prev:
                errors.append(f"data/reddit-accounts.yaml: {h}: not sorted by handle (case-insensitive)")
            seen_h.add(h.lower())
            prev = h.lower()
            if r["status"] not in REDDIT_STATUSES:
                errors.append(f"data/reddit-accounts.yaml: {h}: status should be one of {', '.join(REDDIT_STATUSES)}")
            if not isinstance(r["checked"], dt.date):
                errors.append(f"data/reddit-accounts.yaml: {h}: checked should be a date (YYYY-MM-DD)")

    for mp in sorted(list(root.glob("docs/*/*/meta.yaml")) + list(root.glob("stories/*/meta.yaml"))):
        n += 1
        rel = mp.parent.relative_to(root).as_posix()
        err = lambda msg: errors.append(f"{rel}: {msg}")
        try:
            m = yaml.safe_load(mp.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            err(f"YAML error: {e}")
            continue
        for e in validator.iter_errors(m):
            err(f"schema: {'/'.join(map(str, e.path)) or '(root)'}: {e.message}")
        if not isinstance(m, dict) or "id" not in m:
            continue
        if m["id"] != mp.parent.name:
            err(f"id '{m['id']}' does not match folder name")
        if m["id"] in ids:
            err(f"duplicate id (also {ids[m['id']]})")
        ids[m["id"]] = rel
        top = mp.parent.relative_to(root).parts[0]
        if m.get("category") == "story" and top != "stories":
            err("stories go in stories/<id>/")
        if top == "docs":
            want = (m.get("series") or ["_other"])[0]
            if mp.parent.parent.name != want:
                err(f"should be in docs/{want}/ (first series)")
        for s in m.get("series", []):
            if s not in series:
                err(f"unknown series '{s}' (add it to data/series.yaml)")
        for c in m.get("characters", []):
            if c not in chars:
                err(f"unknown character '{c}' (add it to data/characters.yaml)")
        mt = m.get("tags") or []
        for tg in mt:
            if tg not in tags:
                hint = f" (old name: use '{old_names[tg]}')" if tg in old_names else ""
                err(f"unknown tag '{tg}'{hint} (tags must be in data/tags.yaml)")
        main_tags = [tg for tg in mt if tags.get(tg, {}).get("group") != "meta"]
        if not 1 <= len(main_tags) <= 3:
            err(f"has {len(main_tags)} tags besides meta tags (should be 1 to 3)")
        for tg in mt:
            for i in tags.get(tg, {}).get("implies") or []:
                if i not in mt:
                    err(f"tag '{tg}' implies '{i}', which is missing")
        if ("story" in mt) != (m.get("category") == "story"):
            err("the 'story' tag and category 'story' should go together")
        for a in [*(m.get("authors") or []), *(m.get("shared_by") or [])]:
            if isinstance(a, dict) and a.get("id") and a["id"] not in people:
                err(f"unknown author id '{a['id']}' (add it to data/authors.yaml)")
        named = set(ALLOWED_FILES)
        for p in m.get("parts", []):
            g = p.get("source", {}).get("google_id")
            if g:
                if g in gids:
                    err(f"Google id {g} also used by {gids[g]}")
                gids[g] = rel
            t = p.get("capture", {}).get("text", {}).get("file")
            if t:
                named.add(t)
                if not (mp.parent / t).is_file():
                    err(f"missing text file {t}")
            seen_media = set()
            for f in p.get("capture", {}).get("files") or []:
                if "media_id" in f or "px" in f:
                    if p.get("source", {}).get("type") != "reddit-post" or f.get("format") not in ("png", "jpg"):
                        err(f"{f.get('name')}: media_id/px only belong on image files of a reddit-post part")
                    if f.get("media_id") in seen_media:
                        err(f"{f.get('name')}: media id {f.get('media_id')} used twice in one part")
                    seen_media.add(f.get("media_id"))
            bf = (p.get("capture", {}).get("blocks") or {}).get("file")
            if bf:
                named.add(bf)
                if not t:
                    err(f"reader file {bf} needs a text file in the same part (its word offsets count that text)")
                check_blocks(mp.parent / bf, err)
        for f in mp.parent.iterdir():
            if f.name not in named:
                err(f"unexpected file {f.name}")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(e)
    print(f"{n} entries checked, {len(errors)} problem(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


main()
