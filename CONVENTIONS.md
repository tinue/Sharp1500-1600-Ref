# Conventions

These rules apply to every document in this repository. They exist so that an agent can trust a fact, find out where it
came from, and tell a verified fact from a guess. They are the same as in the sibling reference repository for the
SC61860 family (`PC-1403-Ref`), with one extra header line, `Summary:`.

## Layout

One folder per topic (`CPU/`, `Memory/`, `Display/`, …), each with a `README.md` that says what questions it answers.
The model is visible in the file name: `PC-1500-…` (PC-1500 and PC-1500A), `PC-1600-…`, no prefix for both.
`INDEX.md` lists every document; it is generated.

`sources/` holds the source catalogue and `sources/evidence/`, the tests, spikes and samples that produced results
documented elsewhere. Evidence is kept for reference only: nothing links *to* it as a source of truth, and it is not part
of the knowledge base. `tools/` holds the scripts; `skills/` the router skill.

## File header

Every document starts with a title and four lines:

```
# PC-1600 Display Hardware

Summary: One sentence: what question this document answers.
Scope: PC-1600 (not PC-1500: see ../Memory/PC-1500-Address-Decoding.md)
Sources: TRM-1600 7.3, SM-1600 p.63-72, ROM:PC-1600-ROM/disasm/new/PC1600-P1-B3.asm
Status: draft | cited | ROM-verified | emulator-verified
```

`Status` is the weakest state of any section. `draft`: partly unsourced or a stub. `cited`: every fact traces to a source
document. `ROM-verified`: checked in the ROM code. `emulator-verified`: also observed in Calc-U running the ROM.
The generated prompt `Programming/prompts/LH5801-Assembly-Prompt.md` has no header, because it is pasted into chats.

## Citations

| Form | Meaning |
|---|---|
| `[S:<ID> p.<n>]` | Document `<ID>` from [`sources/sources.yaml`](sources/sources.yaml), PDF page `<n>`. |
| `[ROM:<repo>/<path>@<addr>]` | Checked in the annotated ROM disassembly, e.g. `[ROM:PC-1600-ROM/disasm/new/PC1600-P0-B0.asm@0102]`. |
| `[EMU:<scenario>]` | Observed in Calc-U running `<scenario>`. |

Older text cites in prose (`TRM §7.3`, `Service Manual p.63`). It stays as it is; new and revised text uses the forms
above. Never cite a path on the maintainer's machine; the `local` field of `sources.yaml` is the only place for one.

## Source rank

1. ROM code and emulator observation of it.
2. Sharp documents: service manuals, technical reference manuals, user manuals; chip data sheets.
3. Period books (Baum).
4. Magazines, web pages, third-party manuals.
5. Emulator source code (PockEmul and others): a hint where to look, never an authority.

When sources disagree the higher rank wins, and the disagreement is recorded, never resolved silently: give both values
with their sources and add an entry to [`Open-Questions.md`](Open-Questions.md) with a proposed test. Mark guesses as
`(unverified)`.

## Style

- English, terse, tables first. Addresses: `C000H`/`&C000` as the surrounding document does; do not mix within a table.
- Distil facts in your own words; short quotes of names (routine names, Sharp's labels) are fine.
- One topic per file. Cross-link instead of repeating; the exception is the paste-ready prompts, which are self-contained.
- Size: 5-25 KB per file is the target, 50 KB the limit. Reference tables (the LH5801 instruction set) and generated files
  are exempt. Split by question, at `##` headings, and keep section numbers so existing `§` references stay valid.
- Terms follow the Calc-U glossary: *Model* (PC-1500, PC-1500A, PC-1600), *Model family*, *Variant* (ROM A01/A03/A04,
  New/Old), *Product* (Calc-U-1600).
- A new fact goes into the topic folder that owns the hardware; if it concerns two, the other topic's README links to it.

## Tools

```sh
python3 tools/index.py          # regenerate INDEX.md and the file tables in the topic READMEs (--check: only compare)
python3 tools/build-prompts.py  # regenerate Programming/prompts/LH5801-Assembly-Prompt.md from its parts
python3 tools/check.py          # headers, links, sizes, private paths, generated files up to date
```

Run `check.py` before every commit. All three need only Python 3, no packages.
