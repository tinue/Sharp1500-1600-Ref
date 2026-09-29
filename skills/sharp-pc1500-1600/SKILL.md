---
name: sharp-pc1500-1600
description: Points to the Sharp PC-1500/1500A/1600 research corpus (Sharp1500-1600-Ref) and, if cloned alongside, the BASIC references, annotated ROM disassemblies and the Calc-U-1600 emulator. Use whenever a task needs background on the original hardware/firmware of these machines — memory maps, bank switching, LH5801/LH5803/Z-80 CPUs, ROM routines/addresses, BASIC and its tokenization, CE-150/CE-158/CE-1600 peripherals, tape/serial data formats — or when writing BASIC or machine-language programs for them.
---

# Sharp PC-1500 / 1500A / 1600 — research router

<!-- Install: symlink (or copy) this folder to ~/.claude/skills/sharp-pc1500-1600/.
     See the "Quick start" section of the repository README. -->

## Where the files are

`$REF` is the local clone of **Sharp1500-1600-Ref**
([github.com/tinue/Sharp1500-1600-Ref](https://github.com/tinue/Sharp1500-1600-Ref)).
To find it:

1. If this skill folder is a symlink, `$REF` is two levels above its real path
   (`$REF/skills/sharp-pc1500-1600/`): `realpath ~/.claude/skills/sharp-pc1500-1600/../..`
   — or the user edited the line below.
2. Otherwise use this line (edit it if you copied the folder instead of symlinking it):
   `REF=~/Sharp1500-1600-Ref`

Optional public repositories. They are used only if cloned **next to** `$REF`, i.e.
in `$REF/..`. If one is missing when a row needs it, tell the user which repo to clone
rather than guessing.

| Name | Folder | What |
|---|---|---|
| `$BAS` | `SharpBasicReference/` ([GitHub](https://github.com/tinue/SharpBasicReference)) | BASIC language references, PC-1500 **and** PC-1600 |
| `$P16ROM` | `PC-1600-ROM/` ([GitHub](https://github.com/tinue/PC-1600-ROM)) | PC-1600 + CE-1600P ROM dumps and annotated, reassemblable disassemblies |
| `$P15DIS` | `Sharp_PC-1500_ROM_Disassembly/` ([GitHub](https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly)) | PC-1500 system ROM disassembly (A01/A03/A04), TASM dialect |
| `$EMU` | `Calc-U-1600/` ([GitHub](https://github.com/tinue/Calc-U-1600)) | PC-1500/1500A/1600 emulator (GUI + headless CLI) |

**This skill is a router, not a reading list.** Identify the machine and the topic of
the task, then open **only** the file(s) named in the matching row. Working on the
PC-1600 should pull in PC-1600 files only, and working on the PC-1500 should not pull in
PC-1600 files. Scope is strictly PC-1500, PC-1500A and PC-1600. Other Sharp pocket
computers (PC-1211, PC-1350, PC-1403, PC-G850, …) are not covered.

---

## PC-1600 (dual CPU: Z-80-compatible SC7852 + LH5803 co-processor)

| Task / topic | Read (under `$REF/PC-1600/`) |
|---|---|
| Machine overview, chip complement, clock tree, boot, power rails | `PC-1600-Machine-Overview.md` |
| Memory map, bank layout, `NEW "S0:/S1:/S2:"`, program areas, module merge into S0, PC-1500 comparison, MODE 0/MODE 1 | `PC-1600-Memory-Architecture.md` |
| Bank-switching *mechanism*: Port 31H/28H/3DH, LR38041 gate array, chip selects, BANKSET/BANKCALL, module headers | `PC-1600-Memory-Bank-Switching.md` |
| F000H–FFFFH BASIC/IOCS work area, PTR1–PTRG, named variables, program pointers, `ADTBL` | `PC-1600-Work-Area-Map.md` |
| Emulator: injecting a tokenised BASIC program into banked memory | `PC-1600-BASIC-Program-Placement.md` |
| Which load/save commands work per MODE × peripheral, token routing | `PC-1600-Load-Save-Matrix.md` |
| SC7852 CPU: programmer's model, Z-80A instruction set, wait state, interrupts, RST map, pinout | `PC-1600-CPU-SC7852-Z80.md` |
| LH5803 side: memory map, LH5801 deltas, `CALLH`, PC-1500 compatibility | `PC-1600-CPU-LH5803-Compat.md` |
| Sub-CPU LU-57813P: power, reset cause, handshake, command set, timer/RTC | `PC-1600-SubCPU-LU57813P.md` |
| I/O ports: range map, LH5810-compat block 10–1FH, buzzer, timer/RTC/analog IOCS | `PC-1600-IO-Ports.md` |
| TC8576F CPC (UART + Centronics) at 20–23H | `PC-1600-CPC-TC8576.md` |
| RS-232C/SIO board wiring, level shifter, FTDI how-to | `PC-1600-Serial-Hardware-Notes.md` |
| BASIC serial commands (`INIT`, `SETCOM`, `OUTSTAT`, …) | `PC-1600-Serial-Commands.md` |
| Display: LCD controllers, port decode, frame buffer, LCD IOCS, 6×8 font | `PC-1600-Display-HD61202.md` |
| Keyboard: scan matrix, key IOCS, translation tables | `PC-1600-Keyboard.md` |
| IOCS calling conventions + master routine index | `PC-1600-IOCS.md` |
| Fixed ROM jump table (0000H–0312H) | `PC-1600-ROM-Jump-Table.md` |
| OLD vs NEW BASIC ROM identification | `PC-1600-ROM-Versions.md` |
| File system: header, FCB, file IOCS, RAM-disk / floppy layout | `PC-1600-Filesystem.md` |
| CE-1600P printer/plotter + CE-1600F floppy | `PC-1600-Peripherals-Hardware.md` |
| 60-pin system bus + 40-pin memory slots *(stub)* | `PC-1600-Expansion-Bus.md` |
| Memory-module catalogue *(stub)* | `PC-1600-Memory-Modules.md` |
| Writing Z-80 machine-language programs: float/int encodings, BASIC math calls, bank-aware code | `PC-1600-Assembly-Guide.md` |
| PC-1600 BASIC: where it's documented + PC-1500 → PC-1600 porting gotchas | `PC-1600-BASIC.md` |
| Sub-index with document status | `README.md` |

**PC-1600 BASIC** itself is in `$BAS`: `PC-1600-BASIC-Reference.md` (language),
`PC-1600-Command-Dictionary.md` (≈200 commands), `PC-1600-Error-Codes.md`,
`Command-Index.md` (A–Z across all machines).

**PC-1600 ROM code** — what a routine, table or address does — goes to the annotated
disassembly in `$P16ROM/disasm/{new,old}/PC1600-*.asm` (and `ce1600p/` for the printer
ROM), never to a hex dump. Default to `new/`. `$P16ROM/disasm/README.md` maps images to banks.

---

## PC-1500 / PC-1500A (single LH5801 CPU)

| Task / topic | Read (under `$REF/PC-1500/`) |
|---|---|
| Writing BASIC programs (self-contained authoring prompt) | `Basic-Programming/sharp-basic-prompt.md` |
| Writing LH5801 assembly: instruction set, `sdaslh5801` syntax, memory layout, ROM calls, BCD float | `Assembly-Programming/LH5801_Guide.md` |
| ROM pointers & system variables of the BASIC interpreter | `Memory-Architecture/PC-1500-BASIC-Pointers.md` |
| Address decoding, physical memory map, PC-1500 → 1500A rewiring, `NEW` offsets | `Memory-Architecture/PC-1500-Address-Decoding.md` |
| 16 KB module bank switching | `Memory-Architecture/PC-1500-Bank-Switching.md` |
| PU/PV flip-flops on the LH5801 and the expansion connector | `Memory-Architecture/PU-PV-Signals.md` |
| How the ROM tokenizes BASIC input | `Basic-Programming/reference/Tokenizer-Analysis.md` |
| Structure of the PC-1500 ROM disassembly | `Basic-Programming/reference/ROM-Reference.md` |
| CE-150/CE-158 peripheral token table | `Basic-Programming/reference/Peripheral-Commands.md` |
| CE-150 hardware (schematic level) | `Peripherals/CE-150-Hardware.md` |

BASIC language references in `$BAS`: `PC-1500-BASIC-Reference.md`, `CE-150-Reference.md`,
`CE-158-Reference.md`, `Command-Index.md`, `Error-Codes.md`,
`reference/Token-Mapping-Analysis.md`.

**PC-1500 ROM code**: `$P15DIS/PC-1500_ROM-A0x.lh5801.asm` (one source for A01/A03/A04,
TASM dialect — read and grep it, don't assemble it); per-revision addresses in
`$P15DIS/PC-1500_ROM-A0{1,3,4}.lst`; symbol files in `$P15DIS/lib/`.

---

## Shared (PC-1500 + PC-1500A + PC-1600)

| Task / topic | Read (under `$REF/Shared/`) |
|---|---|
| Every connector pinout (40/60-pin PC-1500, 1500A reassignment, PC-1600 bus + slots) | `Expansion-Connectors.md` |
| What a universal microcontroller memory module must do, per real module | `Software-Defined-Memory-Extension.md` |
| Serial binary transfer format (CE-158 + PC-1600 headers, payloads) | `Data-Formats/Binary-Exchange-Formats.md` |
| FSK cassette-tape format (PC-1500) | `Data-Formats/PC-1500-Tape-Format.md` |
| WAV/PCM cassette encoding (PC-1500 and PC-1600) | `Data-Formats/WAV-Cassette-Format-1500-1600.md` |

---

## Tools

- **LH5801 assembler**: `sdaslh5801` → `sdld` → `makebin` from
  [sdcc-pc1500](https://github.com/pchambre/sdcc-pc1500). The recipe is in `LH5801_Guide.md`.
- **Z-80 assembler (PC-1600)**: [zasm](https://github.com/Megatokio/zasm)
  (`zasm -uwy src.asm src.lst src.bin`), or `sdasz80` from sdcc-pc1500.
- **Running programs**: `$EMU` (Calc-U-1600). It has a Qt GUI and headless CLIs
  (`headless/pc1500_cli`, `headless/pc1600_cli`) that take `.pc1500`/`.pc1500a`/`.pc1600`
  presets; see its README.

If the machine + topic isn't covered by a row above, read `$REF/README.md` (whole-corpus
index) or `$REF/PC-1600/README.md`.
