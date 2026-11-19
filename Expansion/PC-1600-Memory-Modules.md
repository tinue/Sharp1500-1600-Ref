# PC-1600 Memory Modules

Summary: Module catalogue: CE-1600M, CE-1601M, superRAM, PC-1500 8x16K module in the PC-1600.
Scope: PC-1600
Sources: - Service_Manual.pdf -- hardware architecture, schematics, gate array, slot pinouts - SHARP-PC1600-Systemhandbuch.pdf -- firmware, OS calls, module headers, software
Status: cited

> Split from `PC-1600-Memory-Bank-Switching.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §8 → [PC-1600-LH5803-Memory-View.md](../CPU/PC-1600-LH5803-Memory-View.md); §2 → [PC-1600-Bank-Switching.md](../Memory/PC-1600-Bank-Switching.md); §1, §3, §4, §5, §11, §12 → [PC-1600-Gate-Array-and-Chip-Selects.md](../Memory/PC-1600-Gate-Array-and-Chip-Selects.md); §9 → [PC-1600-IO-Ports.md](../IO-Ports/PC-1600-IO-Ports.md); §6 → [PC-1600-Transparent-Banking.md](../Firmware/PC-1600-Transparent-Banking.md).

## Overview: the modules at a glance

Written from the former stub of this document; the details are in the Parts below (original numbering kept).

| Module | Size / slot | Notes | Details |
|---|---|---|---|
| CE-1600M | 32 KB, either slot | Fits the native two-bank capacity; no Port 28H. | Part 7 |
| CE-1601M | 64 KB, Slot 2 only | First module that needs Port 28H vertical banking (2 vertical banks); `INIT` modes A-D. | Part 7a |
| CE-1620M | 32 KB EPROM, either slot | CE-1601E programmer, VPP 21 V (on slot pin 2, "PV IN"; VCC in the PC-1600). | [Software-Defined-Memory-Extension.md](Software-Defined-Memory-Extension.md) §3 |
| CE-1650M | larger, Japan-only | Shown with the same vertical-bank scheme in the CE-1601M manual's memory map; no schematic-level source yet. | Part 7b footnote |
| superRAM | 256 KB / 2x256 KB / 512 KB, Slot 2 (modern) | 4-bit vertical-bank field; runtime file-system patch for >256 KB. | Part 7b |
| PC-1500 8x16 KB module | adapted | Adapter board, bank-signal mapping, driver approaches. | Part 10 |

Cross-cutting rules: only vertical bank 0 is live program/expansion memory; Slot 1 caps at 32 KB toward `MEM`,
Slot 2 at one vertical bank; the theoretical `MEM` ceiling is about 77 KB (see
[PC-1600-Bank-Switching.md](../Memory/PC-1600-Bank-Switching.md), "Why Slot 1 and Slot 2 contribute so differently" and "The theoretical maximum").
CE-163 behaviour in PC-1600 slots: [PC-1500-Bank-Switching.md](../Memory/PC-1500-Bank-Switching.md) §9-10.

## Part 7: CE-1600M Memory Extension Module

### Specifications

| Property | Value |
|----------|-------|
| Model | CE-1600M |
| Capacity | 32KB (4 x 8KB SRAM) |
| Battery | 3V DC lithium (CR2032 x 1), ~5 years in use, ~24 months removed |
| Write protect | Slide switch (dot side = protected) |
| Size | 40.9 x 42.8 x 8.5 mm, 15 grams |

### Internal Hardware

- 4 x 8KB SRAM chips (RAM1-RAM4, wire-bonded, not replaceable)
- 1 x TC74HC139F dual 2-to-4 decoder/demultiplexer
- 2 x 560K ohm pull-up resistors
- DAN202 diode array + 1SS98 diode (battery protection)
- CR2032 lithium battery
- DIP switch (configuration)

### Connector Wiring (from the CE-1600M *Schaltplan*)

The 40-pin slot connector, as actually wired on the module ("Battery side" pins 1–20, "Memory side" pins 21–40):

| Pin | Signal | | Pin | Signal |
|---|---|---|---|---|
| 1 | VCC | | 24 | A13 |
| 4 | **RAMSN** (RAM1#/RAM2#) | | 25–36 | A12 … A1 |
| 5 | **PVOUT** | | 37 | A0 |
| 6 | MREQ | | 38 | RD# |
| 7–14 | D7 … D0 | | 39 | WR# |
| 20 | VGG | | 40 | GND |

**Not connected on this module:** pin 2 (PVIN), pin 3 (PU), pin 15 (INH), pins 16–18 (K0–K2), pin 19 (PT), pins 22–23 (A14/A15). A 32KB memory module needs none of them.

### Circuit Description

The `TC74HC139F` (one half of the dual 2-to-4 decoder) takes select inputs **{A13, PVOUT}** and enable **`1G` = RAMSN**; its four active-low outputs each drive one 8KB SRAM's chip-enable. So:

- **RAMSN** (pin 4) — the whole-module enable. The SC7852 asserts it (RAM1#/RAM2#) only when the Z-80 addresses **8000–BFFF** and the Port 31H page-2 bank field points at this slot (banks 0/1 → Slot 1's RAM2#; banks 2/3 → Slot 2's RAM1#). There is no 4000–7FFF path.
- **PVOUT** (pin 5) — the module's **A14-equivalent**: which 16KB half (= which of the slot's two banks). PVOUT is the LSB of the accessed page's bank number (Part 2); on an 8000–BFFF access that is Port 31H **b4**. `{PVOUT, A13}` together pick 1 of 4 chips.
- **A0–A13** (pins 24–37) — address within the 16KB window. A14/A15 from the connector are unused; the module's 15th address bit is PVOUT.

The `CE-1620M` (32KB ROM cartridge, `VHi-27C256-20S` EPROM in an LCC-32 package) uses the same scheme (its Service Manual circuit diagram): CE ← RAMSN (pin 4), OE ← RD (pin 38), A0–A13 ← connector, **A14 ← PVOUT (pin 5)**, VCC ← pin 1. **Slot pin 2, labelled "PV IN", goes to the EPROM's Vpp**: it's the programming-voltage input, not a PV signal. In a PC-1600 slot it is tied to VCC (measured, `PC-1500-Connectors.md` §2.2b), which is the EPROM's read level; the CE-1601E programmer supplies the 21 V there.

### Memory Maps

**When in Slot 2:**
- 8000-BFFF: Bank 2 and Bank 3 accessible
- User area: up to 44,612 bytes

**When in Slot 1:**
- 8000-BFFF: Bank 0 and Bank 1 accessible
- User area: up to 44,612 bytes

**With CE-159 in S1 and CE-1600M in S2:**
- User area: up to 52,794 bytes (across Banks 0, 2, and 3)

---

## Part 7a: CE-1601M Memory Extension Module (64KB)

**Source:** Sharp Service Manual, CE-1601M (code 00ZCE1601MSME, 1987-02).

Where the CE-1600M (Part 7) is small enough (32KB) to be addressed with Port 31H's PVOUT/PU/PT bits alone and can go in either slot, the CE-1601M is the first module that actually needs Port 28H's vertical-bank mechanism, and Sharp restricts it to Slot 2 accordingly.

### Specifications

| Property | Value |
|---|---|
| Model | CE-1601M |
| Capacity | 64KB (2 x 32Kx8 SRAM) |
| Slot | **Slot 2 (S2) only** -- "If mounted in memory slot S1, the computer may not perform properly or data may not be written properly in the RAM module." |
| Battery | 3V DC lithium (CR2032 x1); ~5 years in-module, ~20 months removed |
| Write protect | Slide DIP switch, hardware-gated (see Circuit below) |
| Size / weight | 40.9 x 42.8 x 8.5mm, 15g -- identical footprint to the CE-1600M |

### Connector Wiring (from the CE-1601M *Schaltplan*)

Same 40-pin connector as the CE-1600M (Part 7), with two additions:

| Pin | Signal | Notes |
|---|---|---|
| 1 | VCC | |
| 4 | **RAM1** (slot select / RAMSN) | 8000–BFFF only, as Part 7 |
| 5 | **PVOUT** | the SRAM's A14 (= Port 31H b4, the 16KB-half select) |
| 6 | MREQ | |
| 7–14 | D7 … D0 | also the vertical-bank value latched by the '131F on a port-28H write |
| **16** | **K0** | Slot 2 I/O-select — feeds the '131F (enable / latch-clock) |
| **18** | **K2** | Slot 2 I/O-select — feeds the '131F |
| 20 | VGG | |
| 24–37 | A13 … A0 | **A0–A13 only**; no A14/A15 on the connector |
| 38 / 39 | RD# / WR# | WR# also gated through the write-protect network |
| 40 | GND | |

Not wired: pin 2 (PVIN), pin 3 (PU), pin 15 (INH), pin 17 (K1), pin 19 (PT), pins 22–23 (A14/A15).

### Internal Hardware

- 2 x D43256G / μPB43256G SRAM (32Kx8 = 32KB each), part suffix -12L or -15L (speed grade; -15L→-12L from '87 Feb. production) -- labeled RAM0 and RAM1 on the PWB
- 1 x TC74HC131F -- a **3-to-8 decoder/demultiplexer with address latch** (74HC137-class: A/B/C select inputs, CK latch-enable, G1/G2A/G2B enables, Y0-Y7 outputs). The latch holds the last-selected vertical bank across the interval when the Z-80 bus is doing something unrelated to port 28H.
- **`0M` / `1M` solder-jumper pads** (with R4, 560K pull-up) feeding the '131F's high select input -- a **bank-count mode strap**: `0M` leaves only Y0/Y1 usable (2 vertical banks = the CE-1601M's 64KB); `1M` enables all 8 Y-outputs (8 vertical banks = 256KB). The same PWB with all SRAM sites populated and this strap set is almost certainly the **CE-1650M**. Structurally the same idea as *superRAM*'s Options 1/2/3 jumper (Part 7b), on Sharp's own board.
- DAN202K diode array + 1SS98 diode -- battery-vs-VCC switchover
- DTA143XK transistor pair x2 + 4.7K/10K resistor network -- write-protect gating, driven by the "Protect SW" slide switch (positions 0/1, 560K pull-up R1) and the RD/WR lines
- 1uF capacitor -- supply smoothing near the battery node

### Circuit Description

The TC74HC131F latches the **data byte** written to I/O port 28H (the vertical-bank number 0–n, per the §5 map: "selected when data of 0 to 9 are written in 28H") on a strobe decoded from the slot's **K0/K2** I/O-select lines (connector pins 16/18) -- i.e. from the Z-80 I/O-port decode for the 28-2FH range, not the memory-mapped MREQ path. Its A/B/C select inputs are the low data bits; its Y-outputs each active-low-enable one physical SRAM chip's CS. With only 2 SRAM chips (RAM0, RAM1) and the `0M` strap, only Y0/Y1 are populated -- the CE-1601M occupies **vertical banks 0 and 1** of the 8 Port 28H can select, leaving 2-7 electrically absent. Populated with 8 chips and the `1M` strap, the same board reaches the full 256KB Slot-2 ceiling (Part 2) -- this is the CE-1650M.

(The §5 map's own wording is "data of **0 to 9**" -- present in the clean manual text, not just an OCR artefact as an earlier revision guessed -- but the hardware is 8 vertical banks: the map's own bank numbering runs 0–7, and *superRAM* (Part 7b) independently confirms 0–7. Treat "0 to 9" as a longstanding quirk of Sharp's wording, 8 banks as the truth.)

The connector carries only A0–A13 (14 bits); each 32Kx8 SRAM's 15th address bit (A14) comes from **PVOUT**, distinguishing the two 16KB halves (Z-80 Bank 2 vs. Bank 3) of whichever 32KB vertical bank the '131F has selected -- confirming "one vertical bank = 32KB = Bank2+Bank3 together" from Part 2, and matching the CE-1600M's identical use of PVOUT (Part 7).

### Usage Modes (via `INIT`)

The 64KB is split at the file-system level, not the hardware level -- hardware always presents all 64KB (2 vertical banks); `INIT` just partitions how the OS's driver treats each vertical bank:

| Mode | Layout | Command |
|---|---|---|
| A | Entire 64KB as RAM file | `TITLE ENTER`, `NEW 0 ENTER`, `INIT "S2:","F" ENTER` -> 61KB user (62,464B), 48 directory entries |
| B | 32KB program memory + 32KB RAM file | `INIT "S2:","P" ENTER` |
| C | 32KB expansion memory + 32KB RAM file | `INIT "S2:","M" ENTER` -> 29.5KB (30,208B) RAM file; expansion memory area grows by exactly 32,768 bytes |
| D | Program memory (n KB) + expansion memory ((32-n) KB) + 32KB RAM file | `INIT "S2:","P",n ENTER` -- n is an odd number of KB, 2 to 32 |

Since only vertical bank 0 can hold program/expansion memory (Part 2), Modes B-D always consume vertical bank 0 for that purpose and leave vertical bank 1 (or whatever's left of the split within it) as the RAM-file area -- the OS never needs to drive Port 28H to reach program/expansion memory, only to walk the file system across both banks.

**"Program memory" vs. "expansion memory" -- distinct terms, distinct `MEM` behaviour** (confirmed against the CE-1601M manual's §5 map, see `PC-1600-Program-Areas-and-NEW.md` §4a):

- **Expansion memory** (`"M"`, and the (32-n) KB remainder of `"P",n`) is the *only* thing `MEM` counts -- it extends the active BASIC work area. Mode C therefore raises `MEM` by exactly 32,768; Mode D raises it by (32-n) KB.
- **Program memory** (`"P"`, and the *n* KB named in `"P",n`) is a *separate resident program store* -- `TITLE`-named, cleared with `NEW 0`. It is CPU-addressable when active but never shows in `MEM`: plain `INIT "S2:","P"` leaves `MEM` unchanged. The manual notes this area is internally structured exactly like §3's internal RAM -- an 8-byte header + a 189-byte "Reserve Program Area" + the "BASIC text area" (the tokenised program lines) -- but only "program memory" matters at the `INIT` level; the sub-region names don't affect the partitioning.
- Persistence differs too: program-memory and RAM-file contents live in the module SRAM and survive a CR2032 swap; expansion-memory bookkeeping lives in main-unit RAM and does not.

Changing an already-initialized module's mode requires clearing it first (`KILL` every file, or `TITLE "S2:" ENTER NEW 0 ENTER` to clear program memory / `TITLE ENTER NEW ENTER` to clear expansion memory) -- the manual is explicit that the mode can't be changed with live data present. (A bare `TITLE`, as used here, is identical to `TITLE "S0:"` (ROM handler and real hardware) even though the Operation Manual lists only `TITLE "S0:"/"S1:"/"S2:"/?`; see `PC-1600-Program-Areas-and-NEW.md` §4.1. `INIT` also refuses a program module currently selected with `TITLE`.)

### Write Protect and Battery Notes

- The slide switch, marked with a dot for the protected position, gates WR through the DTA143XK transistor network -- this is a hardware block on writes, not a software flag, matching the CE-1600M's mechanism.
- Resetting the PC-1600 while accessing a CE-1601M file can show `NEW0?`; CL clears it and both main memory and module contents survive.
- Swapping the CR2032 requires removing the module from the computer first if it's in active use as a RAM file or program file; expansion-memory contents do **not** survive a battery swap and must be saved elsewhere first (RAM-file/program-memory contents, held in the SRAM itself, do survive -- it's the expansion-memory *bookkeeping*, held in main-unit RAM, that's lost).

---

## Part 7b: superRAM (Modern 256KB / 2x256KB / 512KB Module)

**Source:** "SHARP PC-1600 'superRAM' Memory Expansion" user manual, Revision 2 (third-party/hobbyist kit).

This is a modern, from-scratch Slot-2 module, useful here because its manual documents the vertical-bank mechanism explicitly and in the module-designer's own words, rather than requiring inference from Sharp's chip layout as with the CE-1601M (Part 7a). It independently confirms the Part 2 model exactly, and directly demonstrates the 512KB path.

### Design

Where Sharp's own modules (CE-1600M, CE-1601M) use one small SRAM chip per vertical bank behind a 3-to-8 decoder, *superRAM* inverts the approach: a **single 4096Kbit (512Kx8) SRAM** (AS6C4008-55ZIN, 19 address lines) is used, and the vertical-bank number written to Port 28H is latched (via a 74HC173, a 4-bit D-type register) directly onto the chip's *high-order* address lines rather than used to pick among several small chips' chip-selects. A 74HC00 (quad NAND) provides glue logic. Functionally identical to Sharp's scheme from the Z-80/OS side -- same Port 28H semantics, same 32KB-per-vertical-bank granularity -- but a materially different circuit: one chip whose address space is sliced by the vertical-bank register, instead of N chips each fully decoded by it.

### Three modes, one board, a solder jumper

A 3-pad jumper field (Options 1/2/3 -- structurally the same idea as a solder-selectable connector pin, just on the module rather than the mainboard) selects which of the SRAM's address line A15 (and, implicitly, whether vertical-bank values 8-15 are reachable at all) is tied to:

| Mode | Option | Mechanism | Result |
|---|---|---|---|
| 256KB (default) | 1 (A15 -> GND) | A15 fixed low; only the SRAM's lower 256KB is ever reachable | Native -- `INIT`/`DSKF` work unmodified, exactly like a CE-1601M |
| 2x256KB | Switch between 1 and 2 (A15 -> GND or VGG) | A15 hardware-toggled between the SRAM's lower and upper 256KB halves | Two independent 256KB banks, native `INIT` in each, but not concurrently addressable -- an operator/hardware switch, not software |
| 512KB | 1 temporarily, then 3 (A15 -> decoder output Q4) | A15 driven by on-board logic from the vertical-bank register itself (i.e. becomes vertical-bank bit 3, extending the field from 3 to 4 bits) | Full flat 512KB, vertical banks 0-15 -- but only reachable once a patch (below) retargets the OS's capacity bookkeeping |

This confirms directly, from a working implementation, that the 3-bit vs. 4-bit vertical-bank field is purely a hardware choice at the module -- Sharp's own chips just never wired a 4th select bit anywhere.

### The 512KB software patch

Because the PC-1600's `INIT` command has no notion of a >256KB S2: disk, initializing 512KB mode natively fails outright. The manual's documented procedure:

1. Set the jumper to Option 1 (256KB) and `INIT "S2:"` normally (`"F"`, `"M"`, or `"P"` -- same as Part 7a's CE-1601M modes) -- `DSKF"S2:"` reads 251904 (pure RAM disk) or 220160 (with a 32KB S0: expansion carved out), identical figures to a real CE-1601M/256KB-mode module.
2. Load and `CALL &C0C5` a small patch binary (`SUPERRAM.BIN`) that detects the 256KB/224KB disk just initialized and rewrites its file-system header and capacity fields in place to 512KB/480KB -- described as "not a full replacement of the `INIT` command, but a patch routine only."
3. Switch the jumper to Option 3 (512KB) and power-cycle -- `DSKF"S2:"` now reads 514048 or 481280.

The manual is explicit that the patch **cannot verify the module actually has 512KB of physical SRAM behind it** -- it only recognizes and rewrites a 256KB/224KB disk's header. Skipping the jumper change (step 3) after patching corrupts the disk, since the OS would then address only the low 256KB of a disk whose header claims 512KB.

Three upload paths for the patch binary are documented (CE-133T/CE-140T RS-232 in native PC-1600 mode; CE-158 in PC-1500-compatibility mode via `MODE1`; CE-150 via cassette-audio `.WAV` playback through Audacity) -- useful context for how any custom machine-code utility gets onto a PC-1600 with no other transfer path, not specific to this module.

### Confirms, precisely

- Port 28H: `OUT (28H),A`, values 0-7 native (256KB), 0-15 with the patch (512KB) -- the exact figures this document's Part 2 derives independently from the CE-1601M.
- 32KB per vertical bank, exactly matching the CE-1601M's two-chip/two-bank layout.
- Only vertical bank 0 usable as S0: (main memory expansion); the rest is file-system-only.
- Sharp's *own* documented ceiling for a factory module is 64KB (CE-1601M) -- the manual states this directly: *"The largest original RAM module from SHARP is the CE-1601M with 64KB."* 256KB and 512KB are exclusively third-party/modern territory as far as this source is aware, though the CE-1601M's own memory-map diagram (Part 7a) does depict a second, larger, Japan-only module -- **CE-1650M** -- using the same vertical-bank scheme; no schematic-level source for it has turned up yet.

---

## Part 10: Using a PC-1500 8x16K Module in the PC-1600

This section describes how to adapt a PC-1500 memory extension module (8 banks of 16KB = 128KB) for use in the PC-1600 with transparent bank switching.

### Challenge 1: Physical Connector

The PC-1500 uses a different expansion connector than the PC-1600's 40-pin slot connectors. An adapter board is needed.

**PC-1600 Slot 2 is preferred** because:
- Port 28H provides vertical-bank sub-selection for modules >32KB (up to 256KB, confirmed in Part 2/7a)
- RAM1 chip select is on pin 4
- K0/K1/K2 I/O select signals available on pins 16-18
- Full address bus (A0-A15), data bus (D0-D7), RD, WR available

### Challenge 2: Bank Select Signal Mapping

The PC-1600 natively supports 2 banks per slot (e.g., Bank 2 + Bank 3 for Slot 2). Your module has 8 banks of 16KB each = 128KB.

Standard bank signals on the slot connector:
- **PVOUT** (pin 5): 1 bit
- **PU** (pin 3): 1 bit
- **PT** (pin 19): 1 bit
- **RAM1** (pin 4): chip select for Slot 2

**Correction (confirmed against real CE-1601M hardware, Part 7a):** Port 28H's vertical-bank field selects among 32KB units, not 16KB ones -- PVOUT still does the within-vertical-bank 16KB half-select, exactly as it does for the un-sub-banked case. So this 128KB module doesn't need all 8 vertical banks; it needs exactly **4** (0-3), with PVOUT distinguishing each bank's two 16KB halves. The wiring below is adjusted accordingly -- 2 bank-select bits from Port 28H (not 3), plus PVOUT.

### Approach A: Direct Port 28H Sub-Banking (Recommended)

Port 28H is specifically designed for Slot 2 modules larger than 32KB. The module's bank select lines should be wired to the sub-bank signals provided through Port 28H.

**Implementation:**

1. Build an adapter board that maps the PC-1500 module's edge connector to the PC-1600 Slot 2 (CN-8) 40-pin connector.

2. Wire 2 of your module's 3 bank-select lines to a vertical-bank value (0-3) written to Port 28H; wire the third to PVOUT (pin 5) directly, since it's already the within-vertical-bank 16KB half-select. Port 28H itself is decoded on the module side from the K0/K1/K2 I/O-select lines (pins 16-18), per Part 7a.

3. Use RAM1 (pin 4) as the master chip enable, gated with the decoded bank select.

4. Wire address lines A0-A13 to select within each 16KB bank.

5. Connect RD (pin 38), WR (pin 39), and data bus D0-D7 (pins 7-14).

### Approach B: Firmware Driver with BANKCALL

If direct Port 28H wiring is insufficient, write a machine-language driver that:

1. Resides in Bank 0 (0000-3FFF) or is called via `BANKCALL` (019FH).

2. Manages the 8 banks -- 4 vertical banks x 2 PVOUT halves each -- by writing the vertical-bank number to Port 28H and setting PVOUT for the half:

```asm
LD A,<vertical_bank>  ; 0-3
OUT (28H),A            ; Select vertical bank in Slot 2
; then RPV/SPV or the module's own PVOUT-equivalent logic selects the 16KB half
```

3. Performs the actual data transfer while the correct bank is selected.

4. Provides a RAM-Disk interface by placing proper module headers at the start of each bank:
   - Offset +0: 43H (ID code)
   - Offset +1: 16H (ID code)
   - Offset +7: FFH ("M" = RAM-Disk module)

5. Hooks into the boot sequence so the OS detects the module.

### Software Integration for Transparent Access

To make the 128KB module work transparently with BASIC commands:

1. Format the module as RAM-Disk using the `INIT` command or by manually writing the correct headers.

2. The OS will detect the module at boot via `SLOTST` (00E8H) and the module header scan.

3. Once detected as type "M" (RAM-Disk), the OS handles all bank switching transparently when you use:

```basic
SAVE "S2:filename"
LOAD "S2:filename"
FILES "S2:"
KILL "S2:filename"
```

4. For the 8 sub-banks (4 Port-28H vertical banks x 2 PVOUT halves), you may need a custom driver that extends the standard 2-bank (32KB) Slot 2 handling to cover all 128KB. This driver would:
   - Hook the file system calls for S2:
   - Calculate which vertical bank and PVOUT half contains the target data
   - Write the vertical bank to Port 28H and set PVOUT for the half
   - Perform the access in the 8000-BFFF window
   - Restore the previous Port 28H/PVOUT state

### Key Considerations

- Bank 0 (0000-3FFF) must never be disturbed -- all gateway routines live here
- The module must respond correctly to `MEMORYCHK` (018DH) probes during boot -- each 16KB bank should return A=01 (RAM)
- Battery backup must be maintained for SRAM contents
- The write-protect signal should be wired through if the PC-1500 module supports it

**Total accessible RAM with this setup:**

| Component | Size |
|-----------|------|
| Internal (C000-FFFF) | 16KB |
| Slot 1 (if CE-1600M or CE-159) | up to 32KB |
| Slot 2 (your 8x16K module) | 128KB |
| **Total** | **up to 176KB** |

---
