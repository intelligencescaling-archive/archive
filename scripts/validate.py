"""Validate every archive entry.

Checks each meta.yaml against schema/meta.schema.json, then the things a schema can't see:
  - id matches the folder name, and ids and Google ids are unique
  - docs live in docs/<first series>/<id>/ (or docs/_other/<id>/ with no series); stories in stories/<id>/
  - every series and character id exists in data/series.yaml / data/characters.yaml
  - every author/shared_by `id` exists in data/authors.yaml, and no Reddit handle belongs to two people
  - each series' origin_language is a 2-letter code or `real` (a missing one is only a warning)
  - every text file named in the entry exists, and no stray files sit in entry folders

Usage: python scripts/validate.py [repo-root]     (exit code 1 if anything is wrong)
"""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ALLOWED_FILES = {"meta.yaml"}


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent)
    validator = Draft202012Validator(json.loads((root / "schema" / "meta.schema.json").read_text(encoding="utf-8")))
    series_rows = yaml.safe_load((root / "data" / "series.yaml").read_text(encoding="utf-8")) or []
    series = {s["id"] for s in series_rows}
    chars = {c["id"]: c for c in yaml.safe_load((root / "data" / "characters.yaml").read_text(encoding="utf-8")) or []}
    ap = root / "data" / "authors.yaml"
    people = {a["id"]: a for a in (yaml.safe_load(ap.read_text(encoding="utf-8")) or [])} if ap.exists() else {}
    errors, warnings, ids, gids, n = [], [], {}, {}, 0

    for s in series_rows:
        lang = s.get("origin_language")
        if lang is None:
            warnings.append(f"data/series.yaml: {s['id']}: no origin_language yet")
        elif not (lang == "real" or (isinstance(lang, str) and len(lang) == 2 and lang.isascii() and lang.islower())):
            errors.append(f"data/series.yaml: {s['id']}: origin_language '{lang}' should be a 2-letter ISO 639-1 code or 'real'")

    for c in chars.values():
        if c.get("series") and c["series"] not in series:
            errors.append(f"data/characters.yaml: {c['id']}: unknown series {c['series']}")
    handles = {}
    for a in people.values():
        for h in a.get("reddit") or []:
            if h.lower() in handles and handles[h.lower()] != a["id"]:
                errors.append(f"data/authors.yaml: Reddit handle {h} is in both {handles[h.lower()]} and {a['id']}")
            handles[h.lower()] = a["id"]

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
