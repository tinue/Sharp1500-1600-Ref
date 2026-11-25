# PC-1500 RAM Sizing and NEW Offsets

Summary: RAM size and NEW offset calculations for the empty machine, CE-155, 16K module, program modules; screen reverse.
Scope: PC-1500, PC-1500A
Sources: cited inline in the text
Status: cited

> Split from `PC-1500-Address-Decoding.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §1, §2, §4, Appendix: Superseded → [PC-1500-Address-Decoding.md](PC-1500-Address-Decoding.md); Appendix: Reading, Appendix: PC-1500A Chip, Appendix: PC-1500 Chip → [PC-1500-Chip-Select-Tables.md](PC-1500-Chip-Select-Tables.md); §3 → [PC-1500A-Rewiring.md](../Expansion/PC-1500A-Rewiring.md).

## 5. RAM Sizing and NEW Offset Calculations

These figures follow directly from the chip population in §2–§3: the size of the reserve area used by `NEW` depends on which model and which expansion modules are attached, and the total addressable RAM depends on how far the resulting module + built-in tiling extends.

### 5.1 Empty machine (no memory module)

|Model|Start|End|Size|MEM|
|-----|-----|---|----|---|
|PC-1500|4000|4800|2k|1850|
|PC-1500A|4000|5800|6k|5946|
|PC-1600 LH5803|4000|8000|16k|11834|
|PC-1600 Z80|C000|10000|16k|11834|

### 5.2 Machine plus CE-155 (8k)

|Model|Start|End|Size|MEM|
|-----|-----|---|----|---|
|PC-1500|3800|6000|10k|10042|
|PC-1500A|3800|7000|14k|14138|
|PC-1600 LH5803|2000|8000|24k |20026|

### 5.3 Machine plus a 16k memory module (modern recreation)

|Model|Start|End|Size|
|-----|-----|---|----|
|PC-1500|0000|4800|18k|
|PC-1500A|0000|5800|22k|
|PC-1600 LH5803|0000|8000|32k|

(Exact `NEW`/MEM figures depend on the specific module's own firmware reserve — see its own documentation.)

Sharp's own 16 KB module, the **CE-161** (battery-backed RAM, Y0), has this layout with no firmware reserve: `NEW 0` gives MEM 18234 on the PC-1500. Its Instruction Manual prescribes `NEW 256` (BASIC from &0100, MEM 18175) so that the program can later be write-protected as a program module (§5.6).

### 5.4 Calculations

Find the `[RAM start]` with `256 * PEEK(&7863)`

`NEW 0` will set the start of Basic memory to `[RAM start] + C5`. This is because the first 197 bytes are used by various Basic data structures. Therefore, if one needs to reserve e.g. 100 bytes for a machine language program, the Basic start must be `[RAM start] + 197 + 100`. This
results in e.g. `NEW &129` on a machine with the 16k RAM module.

A memory module's own onboard firmware needs its own reserve of bytes on top of the 197-byte BASIC reserve (see `PC-1500-Bank-Switching.md` for the mechanism); the exact figure is module-specific — see that module's own documentation for the minimum `NEW` offset it requires.

On the PC-1600, the start is not set using an absolute address. This is because the LH5803 processor and the Z80 processor see the same memory in different address ranges.
Instead, the memory is reserved using an amount, i.e. 197 plus whatever is needed for the assembly program.

### 5.5 Screen Reverse start addresses

The screen reverse program is 18 bytes long. The start addresses are therefore at least:
* PC-1500 / CE-158: `NEW &38D7`; Add 197
* PC-1500A / a memory module: `NEW` offset depends on the module's own firmware reserve (see the module's own documentation)
* PC-1600: `NEW "S0:",&D7`: Add 197

### 5.5a RAM contents after power loss

Measured on a real PC-1500 (maintainer, 2026): after the batteries were out, every byte of
&7600–&7BFF (display RAM and the first 1 KB of system RAM, 1.5 KB) reads &FF, the lock byte
&79FF included; the rest of RAM, the reserve area among it, reads mostly &00. The A04 ROM's
RESET, COLD_START and CL paths never write &79FF (only `NEW0`'s UNLOCK does)
[ROM:PC-1500-ROM/disasm/a04/PC-1500-A04.asm], so this is the RAM chips' power-up state, not
code. A cold start therefore needs `NEW0`: a plain `NEW` leaves the BASIC pointers at
&7865–&786A as &FF. The PC-1500A's upper 1 KB of system RAM (&7C00–&7FFF) has not been
measured.

### 5.6 Machine plus a program module (ROM module, or a write-protected CE-161)

A **program module** holds a BASIC program and its reserve-key contents in memory the CPU can't write: a mask-ROM module such as the CE-502B, or a CE-161 whose write-protect switch (in the RAMs' R/W line, CE-161 Service Manual) is set. The system ROM recognizes it at power-on and then lays out memory differently from §5.1–§5.4.

**Layout of a program module.** Sharp's program modules share one layout: the mask-ROM CE-502B as well as a CE-161 prepared by its manual (both end in the same bytes at &3FF9–&3FFF):

| Address (module at page &00) | Contents |
|---|---|
| &0000–&0007 | Header: &55, module page, program start (page offset, low byte), 3 bytes not read by the scan, list flag |
| &0008–&00C4 | Reserve area: the DEF-key labels and key strings |
| &00C5 or &0100 → | The tokenized BASIC program, ending in the usual &FF end marker |
| … – &3FF8 | &FF fill |
| &3FF9–&3FFE | `FE FF 03 F1 8E 0D` = line `65279 END` |
| &3FFF | &FF, its end marker |

- **Program start:** the CE-502B starts at &00C5, the CE-161 manual at &0100 (&052A with the CE-153's machine code at &0100). The ROM accepts any start from &00C5 up; why Sharp chose &0100 for the CE-161 is unknown.
- **&FF fill:** needed. It lets the block search skip the gap to a RAM program at &4000 (measured, see below).
- **`65279 END`:** present in the CE-502B mask ROM and written by the CE-161 procedure, but its purpose is unknown. On A01, A03 and A04, &FF up to &3FFF without this line worked the same.

**Recognition (A04 `RESET_9`…`RESET_18`, E098–E0FD).** The reset routine walks the pages &00–&6F. It writes &5A and &A5 to `xx00`, reads them back and restores the byte. The first writable page becomes `RAM_ST` (&7863), the first non-writable page after the RAM block `RAM_END` (&7864). A page that is *not* writable and holds &55 at `xx00` is a module header; only the first one counts:

| Offset | Meaning | Result |
|---|---|---|
| +0 | &55 | – |
| +1 | page override (&FF = this page) | &7860 = module page |
| +2 | program start, page offset; bit 7 set = no program | &7861 = module page + offset |
| +3 | program start, low byte | &7862 |
| +4…+6 | not read by the scan | – |
| +7 | bit 7 set: the module's lines may be listed / edited; clear: ERROR 31 | read by `LAST_LINE_2_INBUF` (D277) |

The five results are compared with &7860–&7864; a difference sets bit 2 of &7A20 and the computer asks `NEW0? :CHECK`. A writable page is never taken as a module, whatever it holds — a CE-161 with its switch off is plain RAM (§5.3). The CE-502B's header is `55 00 00 C5 40 00 00 FF` (program at &00C5); the CE-161 manual's `POKE 0,85,0,1,0,0,0,0,255` writes `55 00 01 00 00 00 00 FF` (program at &0100).

**Layout with a program module (PC-1500; PC-1500A: RAM to &57FF).**

| | No module | RAM module in Y0 (e.g. CE-161, switch off) | Program module in Y0 |
|---|---|---|---|
| &7860 / &7863 / &7864 | FF / 40 / 48 | FF / 00 / 48 | 00 / 40 / 48 |
| Reserve area | &4008–&40C4 | &0008–&00C4 | in the module, &0008–&00C4 |
| BASIC after `NEW 0` | &40C5 | &00C5 | &4000 |
| Variables | down from &47FF | down from &47FF | down from &47FF |
| MEM, empty (PC-1500 / PC-1500A) | 1850 / 5946 | 18234 / 22330 | 2047 / 6143 |

- **Reserve area:** `RSRV_MEM_START` (CE9F) returns `ST_ROM_MOD`:08 when &7860 ≠ FF, else `RAM_ST`:08. The reserve keys are the module's and can't be reprogrammed (the routine hands back error code 24 for that case).
- **RAM BASIC:** `BCMD_NEW` (C80A) sets `NEW 0` to `RAM_ST`:00 instead of `RAM_ST`:C5 — the &C5 bytes only exist for the reserve area, which now lives in the module.
- **Program start:** `PRG_SA_2_XREG` (VMJ 12, DF93) returns the module's program start (&7861/&7862) when &7861 bit 7 is clear, else `BASPRG_ST`. `RUN` starts the module's program.
- **Module and RAM program:** a label (DEF key, `RUN "label"`, `GOTO "label"`) is found in either program; a line number is not — `GOTO`/`LIST` of a RAM line number from the module side, or of a module line from a RAM line, gives ERROR 11. A RAM program next to a program module is therefore started by label, as the CE-161 manual (p. 37) requires.
- **Plugging in or out:** the scan result changes, so `NEW 0` is needed and moves RAM BASIC between `RAM_ST`:00 and `RAM_ST`:C5. The built-in RAM's program and variables are lost; the module keeps its program and reserve contents.

**The CE-161 procedure (Instruction Manual pp. 17–25).** With the switch off: `NEW 256`, enter the program, run the manual's fill program (fills from the end marker to &3FF8 with &FF and writes `FE FF 03 F1 8E 0D FF` = line `65279 END` + end marker at &3FF9–&3FFF), `POKE 0,85,0,1,0,0,0,0,255`; OFF, switch on, ON, `NEW 0`. The ROM does not require &0100: with `NEW 0` and a header pointing at &00C5 (`POKE 0,85,0,0,197,0,0,0,255`) the module behaves the same and holds 59 bytes more, like the CE-502B. The manual's CE-153 variant loads that board's machine code at &0100 (`CALL &100`/`&104`/`&108`) and starts BASIC at &052A (`POKE 0,85,0,5,42,0,0,0,255`).

**Why the &FF fill.** A search that reaches a block's end marker doesn't stop: `LINE_SEARCH` (D2E0) skips &FF bytes, bounded by `BASPRG_END`, and reads the first other byte as the start of the next block (the MERGE mechanism). Between the module program's end and &4000 only &FF is certain to be skipped; anything else is read as a block of lines and the search loses its way before the RAM program. Measured with the module protected and a RAM program with a label at &4000:

| Contents after the module program | Module labels, `RUN`, `LIST` | Label in the RAM program |
|---|---|---|
| &FF to &3FF8 + `65279 END` (manual) | OK | OK |
| &FF to &3FFF, no `END` line | OK | OK |
| old contents of the card | OK | ERROR 11 |
| zeros, gap a multiple of 3 | OK | OK |
| zeros, gap not a multiple of 3 | OK | ERROR 11 |

Zeros only work by luck: `00 00 00` reads as an empty line 3 bytes long, which lands exactly on &4000 only if the gap divides by 3. The module's own program needs no fill. The `65279 END` line made no difference in these tests; its purpose is open.

The CE-502B and protected-CE-161 layouts above were checked on the Calc-U-1600 emulator with the A04 ROM; the PC-1500A MEM figures follow from the RAM boundaries.

---
