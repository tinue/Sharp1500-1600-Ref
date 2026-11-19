# Sharp PC-1500 / PC-1500A / PC-1600 Reference

Hardware, firmware and programming reference for two related 1980s Sharp pocket computers:

- the **Sharp PC-1500** (1981, also sold as the Tandy/Radio Shack PC-2) and its revision, the **PC-1500A**, both with a single LH5801 CPU, and
- the **Sharp PC-1600** (1986), its dual-CPU successor: a Z-80-compatible SC7852 plus an LH5803 co-processor that runs PC-1500 software.

It is the knowledge base behind the **Calc-U-1600** emulator (a product of the [Calc-U](https://github.com/tinue/Calc-U) family) and for writing new programs and hardware for these machines. It contains:

1. **Research documents**: memory maps, bank switching, CPUs, I/O ports, ROM routines, peripherals, tape and serial formats, taken from Sharp's manuals, service manuals and the real ROM code. Every document says where its facts come from and how far they are verified.
2. **Prompt documents**: self-contained guides that let an AI assistant write working BASIC and machine-language programs for these machines. No AI model knows enough about them on its own to do this reliably.

## Find what you need

The documents are grouped by **topic**. The model is in the file name: `PC-1500-…` covers the PC-1500 and PC-1500A, `PC-1600-…` the PC-1600, no prefix means both. [`INDEX.md`](INDEX.md) lists every document in one table.

| Topic | Folder | In it |
|---|---|---|
| The models | [`Machines/`](Machines/) | chips, clocks, power, boot, ROM revisions |
| Processors | [`CPU/`](CPU/) | LH5801 and LH5803, SC-7852 (Z-80), sub-CPU; instruction sets |
| Memory | [`Memory/`](Memory/) | address decoding, chip selects, bank switching, memory maps, program areas, `NEW` |
| Display | [`Display/`](Display/) | LCD controllers, frame buffer, LCD IOCS, character generator |
| Keyboard | [`Keyboard/`](Keyboard/) | key scan, key codes, auto-repeat |
| I/O ports | [`IO-Ports/`](IO-Ports/) | port maps and bit meanings, interrupts, buzzer, timer |
| Serial, parallel | [`Serial-Parallel/`](Serial-Parallel/) | RS-232C, SIO, Centronics, serial BASIC commands |
| Storage | [`Storage/`](Storage/) | floppy, RAM disk, file system, `LOAD`/`SAVE` routing |
| Data formats | [`Data-Formats/`](Data-Formats/) | tape (FSK), WAV, serial binary transfer |
| Peripherals | [`Peripherals/`](Peripherals/) | CE-150 and CE-1600P printer/plotter |
| Expansion | [`Expansion/`](Expansion/) | connectors, system bus, memory modules |
| Firmware | [`Firmware/`](Firmware/) | IOCS, jump tables, work area, system variables, tokenizer, MODE 0/1 |
| Programming | [`Programming/`](Programming/) | prompt documents, assembly guides, porting notes |

Each folder has a `README.md` with the questions it answers and a table of its documents. What is missing is listed in [`Open-Questions.md`](Open-Questions.md). How facts are sourced and rated: [`CONVENTIONS.md`](CONVENTIONS.md), [`Sources.md`](Sources.md).

| | PC-1500 / PC-1500A | PC-1600 |
|---|---|---|
| CPU | LH5801 | SC7852 (Z-80) + LH5803 (PC-1500 mode) |
| Write BASIC | [`PC-1500-BASIC-Prompt.md`](Programming/prompts/PC-1500-BASIC-Prompt.md) | [`PC-1600-BASIC-Porting.md`](Programming/PC-1600-BASIC-Porting.md) |
| Write machine code | [`LH5801-Assembly-Prompt.md`](Programming/prompts/LH5801-Assembly-Prompt.md) | [`PC-1600-Z80-Assembly-Guide.md`](Programming/PC-1600-Z80-Assembly-Guide.md) (first pass) |
| BASIC language reference | [SharpBasicReference](https://github.com/tinue/SharpBasicReference) | [SharpBasicReference](https://github.com/tinue/SharpBasicReference) |
| Annotated ROM disassembly | [PC-1500-ROM](https://github.com/tinue/PC-1500-ROM), [Sharp_PC-1500_ROM_Disassembly](https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly) | [PC-1600-ROM](https://github.com/tinue/PC-1600-ROM) |
| Emulator | Calc-U-1600 in [Calc-U](https://github.com/tinue/Calc-U) | Calc-U-1600 in [Calc-U](https://github.com/tinue/Calc-U) |

---

## Quick start

### A. Any AI chat (no setup)

Paste or attach one prompt document, then describe the program you want:

- BASIC for the PC-1500: [`Programming/prompts/PC-1500-BASIC-Prompt.md`](Programming/prompts/PC-1500-BASIC-Prompt.md)
- LH5801 assembly for the PC-1500: [`Programming/prompts/LH5801-Assembly-Prompt.md`](Programming/prompts/LH5801-Assembly-Prompt.md)

```
Write a program that asks for a number and prints its prime factors.
```

The documents are self-contained, so the AI needs no internet access and no other files.

### B. Claude Code, inside this repository

[Claude Code](https://docs.claude.com/en/docs/claude-code/overview) is an AI assistant that runs in your terminal and can read the files in the folder you start it in.

```sh
git clone https://github.com/tinue/PC-1600-Ref.git
cd PC-1600-Ref
claude
```

Then ask questions such as:

```
How does bank switching work on the PC-1600?
Which ROM routine prints a character on the PC-1500 LCD, and how do I call it?
Write an LH5801 routine that copies 64 bytes from &4100 to &4200.
```

Claude opens `INDEX.md` or the topic `README.md` first and then only the document it needs. Large documents are read by section.

### C. Claude Code, from your own projects (recommended)

When you work on your own Sharp project (an emulator, a program, a hardware module) somewhere else, install the repo's Claude Code **skill**: a short instruction file that Claude loads when a task matches. It routes a question to the right topic folder, so Claude reads only the page it needs.

```sh
git clone https://github.com/tinue/PC-1600-Ref.git ~/PC-1600-Ref
mkdir -p ~/.claude/skills
ln -s ~/PC-1600-Ref/skills/sharp-pc1500-1600 ~/.claude/skills/sharp-pc1500-1600
```

Because the skill is a symlink, `git pull` keeps documents and skill up to date. If you copy the folder instead, or clone elsewhere, edit the `REF=` line in [`skills/sharp-pc1500-1600/SKILL.md`](skills/sharp-pc1500-1600/SKILL.md). More about skills: [Claude Code docs → Skills](https://docs.claude.com/en/docs/claude-code/skills).

The skill also uses these public repositories if they are cloned **next to** this one (BASIC references, ROM source code, the emulator). Without them it tells you which to clone:

```sh
git clone https://github.com/tinue/SharpBasicReference.git
git clone https://github.com/tinue/PC-1600-ROM.git
git clone https://github.com/tinue/PC-1500-ROM.git
git clone https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly.git
git clone https://github.com/tinue/Calc-U.git
```

You can use this repo as a model for your own skill: one repo of reference documents, a routing table from topics to folders, and a generated index.

---

## External references

**[SharpBasicReference](https://github.com/tinue/SharpBasicReference)** is a separate public repository and the home of all BASIC language documentation for both machines. Nothing is duplicated here.

| Document | Summary |
|---|---|
| `PC-1500-BASIC-Reference.md` | Full PC-1500 BASIC language reference. |
| `PC-1600-BASIC-Reference.md` | Full PC-1600 BASIC language reference, including Appendix H on PC-1500 ↔ PC-1600 compatibility. |
| `PC-1600-Command-Dictionary.md` | Entries for the PC-1600's ≈200 commands, A–Z. |
| `PC-1600-Error-Codes.md` / `Error-Codes.md` | Error-code tables for the PC-1600 and the PC-1500. |
| `CE-150-Reference.md`, `CE-158-Reference.md` | BASIC commands for the CE-150 printer/plotter and the CE-158 interface. |
| `Command-Index.md` | A–Z cross-index of every BASIC command on both machines. |
| `reference/Token-Mapping-Analysis.md` | BASIC token value map and device token allocation. |

## Related repositories

Some documents name sibling projects by repository name. None of their contents are included here.

| Repository | What | URL |
|---|---|---|
| `Calc-U` | Monorepo of the Calc-U emulators; the product `calc-u-1600` emulates the PC-1500, PC-1500A and PC-1600 and is the reference for running programs | [github.com/tinue/Calc-U](https://github.com/tinue/Calc-U) |
| `PC-1600-ROM` | PC-1600 and CE-1600P ROM dumps and annotated, reassemblable disassemblies | [github.com/tinue/PC-1600-ROM](https://github.com/tinue/PC-1600-ROM) |
| `PC-1500-ROM` | PC-1500 A01/A03/A04 and CE-150/CE-158 ROM dumps and disassemblies | [github.com/tinue/PC-1500-ROM](https://github.com/tinue/PC-1500-ROM) |
| `Sharp_PC-1500_ROM_Disassembly` | External: Jeff Birt's PC-1500 ROM disassembly (TASM dialect) | [github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly](https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly) |
| `SharpBasicReference` | BASIC references (above) | [github.com/tinue/SharpBasicReference](https://github.com/tinue/SharpBasicReference) |
| `SharpDataExchange` | Serial transfer, BASIC tokenizer and floppy-image tool | [github.com/tinue/SharpDataExchange](https://github.com/tinue/SharpDataExchange) |
| `SharpBasicPlugin` | IDE plugin for Sharp BASIC | [github.com/tinue/SharpBasicPlugin](https://github.com/tinue/SharpBasicPlugin) |
| `sdcc-pc1500` | External: LH5801 assembler/linker | [github.com/pchambre/sdcc-pc1500](https://github.com/pchambre/sdcc-pc1500) |

Material behind this repository (collected manuals, downloads, ROM work in progress) is in private repositories and is not published.

## Out of scope

- **CE-1638 / CE-163F / CE-163X** are modern hobbyist memory modules, not original Sharp hardware.
- **Generic TASM assembler manuals** are not specific to Sharp hardware.
- **Other Sharp pocket computers** (PC-1211, PC-1245, PC-1350, PC-1403, PC-G850, …) use different CPUs or BASIC dialects and are not covered here, even where a source document mentions them. The SC61860 family has its own reference.

## Limitations

- The BASIC prompt targets the PC-1500. PC-1600 BASIC is documented in SharpBasicReference, and [`PC-1600-BASIC-Porting.md`](Programming/PC-1600-BASIC-Porting.md) lists the porting gotchas, but there is no PC-1600 authoring prompt yet.
- The PC-1600 machine-language guide is a first pass. The LH5801 guide is complete and assumes a PC-1500 or PC-1500A memory layout.
- Some documents are still `draft`; see the status column in [`INDEX.md`](INDEX.md). The PC-1500 side has no documents yet for display, I/O ports and the CE-158 interface ([`Open-Questions.md`](Open-Questions.md)).

## Working on this repository

```sh
python3 tools/check.py          # headers, links, sizes, private paths, generated files
python3 tools/index.py          # regenerate INDEX.md and the file tables of the topic READMEs
python3 tools/build-prompts.py  # regenerate the LH5801 prompt from its parts
```

Conventions (document header, citations, source rank, size rule): [`CONVENTIONS.md`](CONVENTIONS.md). `sources/evidence/` keeps tests and samples that produced documented results; it is not part of the knowledge base.

## License

Copyright (C) 2026 Martin Erzberger.

- **Documents** (all Markdown files, including the prompt documents and the skill) are licensed under [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE-CC-BY-SA) (CC BY-SA 4.0).
- **Programs** (`.py`, `.asm`, `.bas` and `.pc1600` files, i.e. `tools/` and `sources/evidence/`) are free software, licensed under the [GNU General Public License, version 3](LICENSE-GPL) (GPLv3), like Calc-U.

Programs that an AI assistant writes for you with the help of the prompt documents are yours; neither license applies to them.

Sharp, PC-1500, PC-1600 and the names of their peripherals are trademarks of Sharp Corporation. Sharp's manuals, ROMs and the third-party datasheets cited here remain the property of their owners and are not covered by these licenses.
