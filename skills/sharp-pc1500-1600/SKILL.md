---
name: sharp-pc1500-1600
description: Points to the Sharp PC-1500/1500A/1600 research corpus (PC-1600-Ref) and, if cloned alongside, the BASIC references, annotated ROM disassemblies and the Calc-U-1600 emulator. Use whenever a task needs background on the original hardware/firmware of these machines — memory maps, bank switching, LH5801/LH5803/Z-80 CPUs, ROM routines/addresses, BASIC and its tokenization, display, keyboard, I/O ports, serial, floppy/RAM disk, CE-150/CE-158/CE-1600 peripherals, tape/serial data formats — or when writing BASIC or machine-language programs for them.
---

# Sharp PC-1500 / 1500A / 1600 — research router

<!-- Install: symlink (or copy) this folder to ~/.claude/skills/sharp-pc1500-1600/.
     See "Quick start C" in the repository README. -->

## Where the files are

`$REF` is the local clone of **PC-1600-Ref** ([github.com/tinue/PC-1600-Ref](https://github.com/tinue/PC-1600-Ref)).

1. If this skill folder is a symlink, `$REF` is two levels above its real path:
   `realpath ~/.claude/skills/sharp-pc1500-1600/../..`
2. Otherwise use this line (edit it if you copied the folder): `REF=~/PC-1600-Ref`

Other public repositories are used only if present. Look next to `$REF` first (`$REF/..`, the family folder of the
maintainer's layout `sharp/PC-1600/`), then one and two levels up (`sharp/`, the development root). If one is missing
when a task needs it, tell the user which repo to clone instead of guessing.

| Name | Repository | What |
|---|---|---|
| `$BAS` | `SharpBasicReference` ([GitHub](https://github.com/tinue/SharpBasicReference)) | BASIC language references, PC-1500 **and** PC-1600 |
| `$P16ROM` | `PC-1600-ROM` ([GitHub](https://github.com/tinue/PC-1600-ROM)) | PC-1600 + CE-1600P ROM dumps, annotated reassemblable disassemblies |
| `$P15ROM` | `PC-1500-ROM` ([GitHub](https://github.com/tinue/PC-1500-ROM)) | PC-1500 A01/A03/A04, CE-150, CE-158 dumps and disassemblies |
| `$P15DIS` | `Sharp_PC-1500_ROM_Disassembly` ([GitHub](https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly)) | PC-1500 system ROM, TASM dialect |
| `$EMU` | `Calc-U`, folder `products/calc-u-1600/` ([GitHub](https://github.com/tinue/Calc-U)) | Calc-U-1600, the emulator (GUI + harness) |

## How to use the corpus

**This skill is a router, not a reading list.** Identify the *topic* and the *model*, open the topic's `README.md`, then
the one document it names.

1. Topic → folder under `$REF/` (table below). Model → file name prefix: `PC-1500-…` is PC-1500 and PC-1500A,
   `PC-1600-…` is PC-1600, no prefix is both. A PC-1500 task pulls no PC-1600 files and vice versa, except where a
   document says otherwise.
2. Not sure? Read `$REF/INDEX.md` (one line per document: model, status, size, what it answers).
3. **Files over 25 KB: never read whole.** `grep -n '^## ' <file>`, then read the line range you need. The biggest are
   `CPU/LH5801-Instruction-Set.md`, `Firmware/PC-1600-Work-Area-Map.md` and the paste-ready prompts.
4. Trust the header: `Status` is `draft` < `cited` < `ROM-verified` < `emulator-verified`. Say so when you rely on a
   `draft` document. Conflicts and unknowns are in `$REF/Open-Questions.md`.
5. What a ROM routine, table or address *does* comes from the annotated disassembly, never from a hex dump:
   PC-1600 → `$P16ROM/disasm/new/PC1600-*.asm` (default `new/`; `old/` and `ce1600p/` exist; `disasm/README.md` maps images
   to banks); PC-1500 → `$P15ROM/disasm/a0{1,3,4}/` or `$P15DIS/PC-1500_ROM-A0x.lh5801.asm` (TASM dialect: read and grep it).

Scope is PC-1500, PC-1500A and PC-1600. Other Sharp pocket computers (PC-1211, PC-1350, PC-1403, PC-G850, …) are not
covered (the SC61860 family has its own reference).

## Topic → folder

| Topic | Folder (`$REF/…`) | Typical question |
|---|---|---|
| Models, chips, clocks, boot, ROM revisions | `Machines/` | Which ROM is this? What is the clock tree? |
| CPUs, instruction sets, sub-CPU | `CPU/` | LH5801 opcode, Z-80 timing/wait states, LH5803 deltas |
| Memory map, decoding, bank switching, `NEW`, program areas | `Memory/` | Where does `NEW "S1:"` put a program? Port 31H? |
| LCD | `Display/` | Frame buffer, LCD IOCS, font |
| Keyboard | `Keyboard/` | Key scan, auto-repeat, key readiness |
| I/O port bits, interrupts, buzzer, timer/RTC | `IO-Ports/` | What does port 1BH bit 1 do? |
| RS-232C / SIO / Centronics, serial BASIC commands | `Serial-Parallel/` | TC8576 setup, `SETCOM` |
| Floppy, RAM disk, file system, `LOAD`/`SAVE` routing | `Storage/` | FCB layout, FAT, what `BSAVE` does in MODE 1 |
| Tape, WAV, serial binary formats | `Data-Formats/` | Header of a transferred file |
| Printer / plotter, CE-150, CE-1600P | `Peripherals/` | Plotter ports, Centronics mode |
| Connectors, system bus, modules | `Expansion/` | Slot pinout, CE-1601M, module emulation |
| IOCS, jump tables, work area, system variables, tokenizer, MODE 0/1 | `Firmware/` | `F1BCH`? ROM entry for BASIC math? `$F957`? |
| Writing programs | `Programming/` | see below |

## Writing programs

| Task | Read |
|---|---|
| PC-1500 BASIC (self-contained authoring prompt) | `Programming/prompts/PC-1500-BASIC-Prompt.md` |
| LH5801 assembly: syntax, memory layout, ROM calls, BCD floats (self-contained) | `Programming/prompts/LH5801-Assembly-Prompt.md` (generated; its parts are in `Programming/`, `CPU/`, `Firmware/`; grep it, do not read it whole) |
| PC-1600 Z-80 machine code | `Programming/PC-1600-Z80-Assembly-Guide.md` (first pass) |
| PC-1500 → PC-1600 BASIC porting | `Programming/PC-1600-BASIC-Porting.md` |

BASIC language references are in `$BAS`: `PC-1500-BASIC-Reference.md`, `PC-1600-BASIC-Reference.md`,
`PC-1600-Command-Dictionary.md`, `CE-150-Reference.md`, `CE-158-Reference.md`, `Command-Index.md`,
`Error-Codes.md`, `PC-1600-Error-Codes.md`, `reference/Token-Mapping-Analysis.md`.

## Tools

- **LH5801 assembler**: `sdaslh5801` → `sdld` → `makebin` from [sdcc-pc1500](https://github.com/pchambre/sdcc-pc1500); the recipe is in the LH5801 assembly guide.
- **Z-80 assembler (PC-1600)**: [zasm](https://github.com/Megatokio/zasm) (`zasm -uwy src.asm src.lst src.bin`), or `sdasz80` from sdcc-pc1500.
- **Running programs**: `$EMU` (Calc-U-1600) with a Qt GUI and a headless harness that takes `.pc1500`/`.pc1500a`/`.pc1600`
  presets; see `$EMU/CLAUDE.md` and its help.

## Changing the corpus

Follow `$REF/CONVENTIONS.md` (document header, citations, source rank, 25 KB target). After an edit run
`python3 tools/index.py && python3 tools/check.py` in `$REF`. Questions with their expected documents are in `evals.md`
next to this file; re-run them after larger changes.
