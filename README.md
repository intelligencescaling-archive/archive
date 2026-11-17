# Intelligence Scaling Archive

A community archive that preserves the high-effort content made by the
[r/IntelligenceScaling](https://www.reddit.com/r/IntelligenceScaling) (Smart Character Debates / SCD) community:
analysis documents, original stories, tier lists, and community projects. It saves them before
the links die.

Browse, search and download it at **[intelscaling.com](https://intelscaling.com)**.

> 🚧 **Work in progress.** The first 958 entries were filled in automatically from the community
> libraries and are still being reviewed (`review.status: auto`). Spotted a wrong author, series or tag?
> Use the "Suggest a correction" link on the item's page, or open an issue here.

## Layout

| Path | What's there |
|---|---|
| `docs/<series>/<item>/` | One folder per doc: `meta.yaml` + `text.txt` (plain text for search) |
| `docs/_other/<item>/` | Docs not about one series: SCD categories, scaling systems, guides |
| `stories/<item>/` | Original stories and fan fiction |
| `data/` | Series and character registries |
| `schema/` | The entry format: [schema/README.md](schema/README.md) |
| `scripts/validate.py` | Checks every entry (also runs on each push) |

## What's archived

| Category | Examples |
|---|---|
| **Docs** | Character analyses, feat breakdowns, strategy write-ups, debunks |
| **Original stories** | Fan fiction and fully original stories with smart characters |
| **Misc** | Tier lists, community series and boards, notable posts |

Each item keeps its title, author (when known), series, characters, tags, and its original links.
This repository holds the metadata and the plain-text versions used for search. The PDF/DOCX files are
too big for git: they're downloadable from each item's page on [intelscaling.com](https://intelscaling.com), and
each one is identified here by its `sha256`.

## Adding something

Know a doc, story, or tier list that should be here? Open an
[issue](https://github.com/intelligencescaling-archive/archive/issues) with the link and any details you know
(a proper submission form is coming). You never upload files: a maintainer script downloads
them from the original source.

## Removal requests

Are you the author of something archived here and want it removed or credited differently?
Open an issue or email **removals@intelscaling.com**. Requests are honored.

## Acknowledgments

This archive builds on the work of people who were preserving this content before us:

- **u/TheMcBaconX** and **u/BudgetPosition6080**: *The Ultimate SCD Library* (original and Remastered)
- **u/ConversationSea1684**: the library of original stories and fanfics
- Every author whose work is preserved here

## License

- **Code** (scripts, tooling, site code): [MIT](LICENSE).
- **Archived content** is © its respective authors. It is preserved here for the community and for
  reference, not relicensed. Removal on request.
