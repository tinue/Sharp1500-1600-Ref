# Sharp PC-1500 / PC-1500A / PC-1600 Reference

Hardware, firmware and programming reference for two related 1980s Sharp pocket computers:

- the **Sharp PC-1500** (1981, also sold as the Tandy/Radio Shack PC-2) and its revision, the **PC-1500A**, both with a single LH5801 CPU, and
- the **Sharp PC-1600** (1986), its dual-CPU successor: a Z-80-compatible SC7852 plus an LH5803 co-processor that runs PC-1500 software.

Both machines get the same depth of coverage. The repo contains:

1. **Research documents**: memory maps, bank switching, CPUs, I/O ports, ROM routines, peripherals, and tape and serial formats. All of it is taken from Sharp's manuals, service manuals and the real ROM code.
2. **Prompt documents**: self-contained guides that let an AI assistant write working BASIC and machine-language programs for these machines. No AI model knows enough about them on its own to do this reliably.

## At a glance

| | PC-1500 / PC-1500A | PC-1600 |
|---|---|---|
| CPU | LH5801 | SC7852 (Z-80) + LH5803 (PC-1500 mode) |
| Start here | [`PC-1500/`](PC-1500/) | [`PC-1600/README.md`](PC-1600/README.md) |
| Write BASIC | [`sharp-basic-prompt.md`](PC-1500/Basic-Programming/sharp-basic-prompt.md) (prompt) | [`PC-1600-BASIC.md`](PC-1600/PC-1600-BASIC.md) (porting notes) |
| Write machine code | [`LH5801_Guide.md`](PC-1500/Assembly-Programming/LH5801_Guide.md) (prompt) | [`PC-1600-Assembly-Guide.md`](PC-1600/PC-1600-Assembly-Guide.md) (first pass) |
| BASIC language reference | [SharpBasicReference](https://github.com/tinue/SharpBasicReference) | [SharpBasicReference](https://github.com/tinue/SharpBasicReference) |
| Annotated ROM disassembly | [Sharp_PC-1500_ROM_Disassembly](https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly) | [PC-1600-ROM](https://github.com/tinue/PC-1600-ROM) |
| Emulator | [Calc-U-1600](https://github.com/tinue/Calc-U-1600) | [Calc-U-1600](https://github.com/tinue/Calc-U-1600) |

Documents that cover both machines (connectors, data formats) are in [`Shared/`](Shared/).

---

## Quick start

Pick the path that fits how you work.

### A. Any AI chat (no setup)

Paste or attach one prompt document, then describe the program you want:

- BASIC for the PC-1500: [`PC-1500/Basic-Programming/sharp-basic-prompt.md`](PC-1500/Basic-Programming/sharp-basic-prompt.md)
- LH5801 assembly for the PC-1500: [`PC-1500/Assembly-Programming/LH5801_Guide.md`](PC-1500/Assembly-Programming/LH5801_Guide.md)

```
Write a program that asks for a number and prints its prime factors.
```

The documents are self-contained, so the AI needs no internet access and no other files.

### B. Claude Code, inside this repository

[Claude Code](https://docs.claude.com/en/docs/claude-code/overview) is an AI assistant that runs in your terminal and can read the files in the folder you start it in.

```sh
git clone https://github.com/tinue/Sharp1500-1600-Ref.git
cd Sharp1500-1600-Ref
claude
```

Then ask questions such as:

```
How does bank switching work on the PC-1600?
Which ROM routine prints a character on the PC-1500 LCD, and how do I call it?
Write an LH5801 routine that copies 64 bytes from &4100 to &4200.
```

### C. Claude Code, from your own projects (recommended)

This option is for when you work on your own Sharp project (an emulator, a program, a hardware module) somewhere else. The repo ships a Claude Code **skill**: a short instruction file that Claude loads on its own when a task matches. The skill tells Claude which document in this repo answers which question, so Claude reads only the page it needs.

```sh
git clone https://github.com/tinue/Sharp1500-1600-Ref.git ~/Sharp1500-1600-Ref
mkdir -p ~/.claude/skills
ln -s ~/Sharp1500-1600-Ref/skills/sharp-pc1500-1600 ~/.claude/skills/sharp-pc1500-1600
```

Because the skill is a symlink, `git pull` keeps both the documents and the skill up to date. If you copy the folder instead of linking it, or clone somewhere other than `~/Sharp1500-1600-Ref`, edit the `REF=` line in [`skills/sharp-pc1500-1600/SKILL.md`](skills/sharp-pc1500-1600/SKILL.md). More about skills: [Claude Code docs → Skills](https://docs.claude.com/en/docs/claude-code/skills).

The skill also knows about these public repositories. Clone any of them **next to** this one to get BASIC references, ROM source code and an emulator:

```sh
cd ~   # the folder that contains Sharp1500-1600-Ref
git clone https://github.com/tinue/SharpBasicReference.git
git clone https://github.com/tinue/PC-1600-ROM.git
git clone https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly.git
git clone https://github.com/tinue/Calc-U-1600.git
```

You can use this repo as a model for your own skill: one repo of reference documents plus a routing table from topics to files.

---

## Repository layout

```
PC-1500/                PC-1500 and PC-1500A
  Basic-Programming/      BASIC prompt, tokenizer and ROM notes, sample programs
  Assembly-Programming/   LH5801 guide (prompt + reference), samples
  Memory-Architecture/    address decoding, bank switching, BASIC pointers, PU/PV
  Peripherals/            CE-150 printer/plotter/cassette hardware
PC-1600/                PC-1600: CPUs, memory, IOCS, display, keyboard, serial, files, ROM
Shared/                 both machines: connectors, module emulation, data formats
skills/                 the Claude Code skill described in Quick start C
```

---

## Documents

### PC-1600/

This folder covers the **Sharp PC-1600** in enough detail to build an emulator, write Z-80 machine-language programs, and design expansion hardware. [`PC-1600/README.md`](PC-1600/README.md) is its sub-index and tracks the status of each document (complete, first pass or stub). PC-1600 BASIC itself lives in [SharpBasicReference](https://github.com/tinue/SharpBasicReference) (see *External references*).

| Area | Documents |
|---|---|
| Machine, CPUs | `PC-1600-Machine-Overview.md`, `PC-1600-CPU-SC7852-Z80.md`, `PC-1600-CPU-LH5803-Compat.md`, `PC-1600-SubCPU-LU57813P.md` |
| Memory | `PC-1600-Memory-Architecture.md`, `PC-1600-Memory-Bank-Switching.md`, `PC-1600-Work-Area-Map.md`, `PC-1600-BASIC-Program-Placement.md`, `PC-1600-Memory-Modules.md` *(stub)* |
| Firmware / ROM | `PC-1600-IOCS.md`, `PC-1600-ROM-Jump-Table.md`, `PC-1600-ROM-Versions.md`, `PC-1600-ROM-Disassembly.md` |
| Display, keyboard, I/O | `PC-1600-Display-HD61202.md`, `PC-1600-Keyboard.md`, `PC-1600-IO-Ports.md` |
| Serial | `PC-1600-CPC-TC8576.md`, `PC-1600-Serial-Hardware-Notes.md`, `PC-1600-Serial-Commands.md` |
| Files, peripherals | `PC-1600-Filesystem.md`, `PC-1600-Load-Save-Matrix.md`, `PC-1600-Peripherals-Hardware.md`, `PC-1600-Expansion-Bus.md` *(stub)* |
| Programming | `PC-1600-Assembly-Guide.md`, `PC-1600-BASIC.md`, `program-area-tests/` (Calc-U-1600 presets) |

### PC-1500/

| Document | Summary |
|---|---|
| `Basic-Programming/sharp-basic-prompt.md` | **Prompt document.** Defines the AI's role, device limits, output format (`.bas` source + `.md` guide), coding conventions and the full BASIC keyword reference. The output can be sent straight to a real PC-1500. |
| `Assembly-Programming/LH5801_Guide.md` | **Prompt document** and LH5801 reference. It covers the instruction set, the `sdaslh5801` assembler and toolchain, running programs in Calc-U-1600, memory layout, system variables, ROM calling conventions, the BCD float format and common idioms. |
| `Basic-Programming/reference/Tokenizer-Analysis.md` | How the ROM tokenizes BASIC input at `$F957`. |
| `Basic-Programming/reference/ROM-Reference.md` | A guide to the structure of the PC-1500 ROM disassembly. |
| `Basic-Programming/reference/Peripheral-Commands.md` | The CE-150/CE-158 peripheral token table. It overlaps with SharpBasicReference's `Token-Mapping-Analysis.md`. |
| `Memory-Architecture/PC-1500-BASIC-Pointers.md` | ROM pointers and system variables of the BASIC interpreter. |
| `Memory-Architecture/PC-1500-Address-Decoding.md` | Address decoder, physical memory map, the PC-1500 → PC-1500A rewiring, and RAM sizing and `NEW` offsets. |
| `Memory-Architecture/PC-1500-Bank-Switching.md` | How 16 KB modules bank-switch into the low 16 KB window. It also covers CE-163 modules in PC-1600 slots. |
| `Memory-Architecture/PU-PV-Signals.md` | The LH5801's PU/PV flip-flop pins and their role on the expansion connector. |
| `Peripherals/CE-150-Hardware.md` | The CE-150 at schematic level, taken from the Service Manual: LH5810, address decode, plotter and cassette wiring, EX-BOX bus. |
| `Peripherals/CE-150-Plotter-Links.md` | Third-party replacement parts for the CE-150 pen mechanism. |

### Shared/

| Document | Summary |
|---|---|
| `Expansion-Connectors.md` | Every connector: the PC-1500's 40- and 60-pin connectors, the PC-1500A reassignment, and the PC-1600's 60-pin system bus and two memory slots. |
| `Software-Defined-Memory-Extension.md` | What a microcontroller-based universal module would have to do on the wire to emulate every real PC-1500/1500A/1600 memory module. |
| `Data-Formats/Binary-Exchange-Formats.md` | The serial binary format: CE-158 header (PC-1500), PC-1600 header, and the BASIC, machine-code, reserve-area and variables payloads. |
| `Data-Formats/PC-1500-Tape-Format.md` | The FSK cassette-tape format of the PC-1500 series. |
| `Data-Formats/WAV-Cassette-Format-1500-1600.md` | WAV/PCM cassette encoding for the PC-1500 and PC-1600. |

---

## External references

**[SharpBasicReference](https://github.com/tinue/SharpBasicReference)** is a separate public repository and the home of all BASIC language documentation for both machines. Nothing is duplicated here.

| Document | Summary |
|---|---|
| `PC-1500-BASIC-Reference.md` | Full PC-1500 BASIC language reference. |
| `PC-1600-BASIC-Reference.md` | Full PC-1600 BASIC language reference (Operation Manual Part IV + internal data representation), including Appendix H on PC-1500 ↔ PC-1600 compatibility. |
| `PC-1600-Command-Dictionary.md` | Entries for the PC-1600's ≈200 commands, A–Z. |
| `PC-1600-Error-Codes.md` / `Error-Codes.md` | Error-code tables for the PC-1600 and the PC-1500. |
| `CE-150-Reference.md`, `CE-158-Reference.md` | BASIC commands for the CE-150 printer/plotter and the CE-158 interface (PC-1500, and the PC-1600 in MODE 1). |
| `Command-Index.md` | A–Z cross-index of every BASIC command on both machines. |
| `reference/Token-Mapping-Analysis.md` | BASIC token value map and device token allocation. |

## Related repositories

Some documents name sibling projects by their folder name, e.g. `Calc-U-1600/` or `PC-1600-ROM/`, because they are used side by side. None of their contents are included here. This table shows which ones you can reach:

| Folder name used in the docs | Status | URL |
|---|---|---|
| `Calc-U-1600/` | Public — PC-1500/1500A/1600 emulator; the reference for running programs | [github.com/tinue/Calc-U-1600](https://github.com/tinue/Calc-U-1600) |
| `PC-1600-ROM/` | Public — PC-1600 + CE-1600P ROM dumps and annotated, reassemblable disassemblies | [github.com/tinue/PC-1600-ROM](https://github.com/tinue/PC-1600-ROM) |
| `PC-1500-ROM/` | Public — CE-150 ROM dump | [github.com/tinue/PC-1500-ROM](https://github.com/tinue/PC-1500-ROM) |
| `Sharp_PC-1500_ROM_Disassembly/` | Public (external) — PC-1500 A01/A03/A04 ROM disassembly | [github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly](https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly) |
| `SharpBasicReference/` | Public | [github.com/tinue/SharpBasicReference](https://github.com/tinue/SharpBasicReference) |
| `SharpDataExchange` | Public | [github.com/tinue/SharpDataExchange](https://github.com/tinue/SharpDataExchange) |
| `SharpBasicPlugin/` | Public | [github.com/tinue/SharpBasicPlugin](https://github.com/tinue/SharpBasicPlugin) |
| `sharp-pocket-computer/` | Public | [github.com/tinue/sharp-pocket-computer](https://github.com/tinue/sharp-pocket-computer) |
| `sdcc-pc1500/` | Public (external) — LH5801 assembler/linker | [github.com/pchambre/sdcc-pc1500](https://github.com/pchambre/sdcc-pc1500) |
| `pc1500emu/` | Public (external fork), being retired; not an authority for this corpus | [github.com/tinue/pc1500emu](https://github.com/tinue/pc1500emu) |
| `pc1600/` | **Private** — annotation workspace behind `PC-1600-ROM/disasm/` | — |
| `pc1500/` (CE-1638, CE-163F, CE-163X) | **Private** | — |
| `pc1500preset/`, `tasm/`, `tasm-35/`, `lh5801_asm/reference/` | Not published | — |

## Out of scope

- **CE-1638 / CE-163F / CE-163X** are modern hobbyist memory modules, not original Sharp hardware. Their material lives in a private repository.
- **Generic TASM assembler manuals** are not specific to Sharp hardware.
- **Other Sharp pocket computers** (PC-1211, PC-1245, PC-1350, PC-1403, PC-G850, …) use different CPUs or BASIC dialects and are not covered, even where a source document mentions them.

## Limitations

- The BASIC prompt targets the PC-1500. PC-1600 BASIC is documented in SharpBasicReference, and `PC-1600/PC-1600-BASIC.md` lists the porting gotchas, but there is no PC-1600 authoring prompt yet.
- The PC-1600 machine-language guide is a first pass. The PC-1500 LH5801 guide is complete and assumes a PC-1500 or PC-1500A memory layout.
- Some PC-1600 documents are still stubs or first passes. `PC-1600/README.md` shows the status of each one.

## License

Copyright (C) 2026 Martin Erzberger.

- **Documents** (all Markdown files, including the prompt documents and the skill) are licensed under [Creative Commons Attribution-ShareAlike 4.0 International](LICENSE-CC-BY-SA-4.0.txt) (CC BY-SA 4.0).
- **Programs** (`.py`, `.asm`, `.bas` and `.pc1600` files) are free software, licensed under the [GNU General Public License, version 3](LICENSE-GPL-3.0.txt) (GPLv3), like [Calc-U-1600](https://github.com/tinue/Calc-U-1600).

Programs that an AI assistant writes for you with the help of the prompt documents are yours; neither license applies to them.

Sharp, PC-1500, PC-1600 and the names of their peripherals are trademarks of Sharp Corporation. Sharp's manuals, ROMs and the third-party datasheets cited here remain the property of their owners and are not covered by these licenses.
