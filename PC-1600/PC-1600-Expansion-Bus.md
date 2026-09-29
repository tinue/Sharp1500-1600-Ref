# PC-1600 Expansion Bus — Hardware Design Reference

> **STATUS: PARTIAL.** Only §1 (peripheral ROM placement) is written; the rest is the
> outline from the PC-1600 corpus restructuring (2026-08-29).

## Scope

Everything needed to **design hardware** for the PC-1600's expansion connectors: the
60-pin system bus and the two 40-pin memory-slot connectors. Raw pinouts already live in
`../Shared/Expansion-Connectors.md` §4 — this document builds on them with
the electrical, timing, and protocol detail a peripheral designer needs, plus worked
examples.

Memory modules specifically (CE-1600M etc.) get their own catalogue in
`PC-1600-Memory-Modules.md`; this document is about the bus, not the modules.

## 1. Where a 60-pin peripheral's ROM can go

**Use page 1 (4000–7FFFH), Bank 2, 6 or 7.** Nothing known occupies them, and the firmware
scans them for peripheral ROMs at reset.

**How the firmware finds it.** At reset `SCANMODS` (P0-B0 `07C5H`) maps page 1 to Banks 1–7
in turn and looks for the ID bytes `43H,16H` at **4000H** and at **6000H**. Hits go into the
bitmaps at F0AEH (4000H) and F0AFH (6000H); each module's entry at +2 is then called
(`CALLMODS`), and a module can reserve work RAM with `CALL 02DFH` (Creg 01–07 = Bank 1–7
at 4000H, 08–0E = at 6000H). A ROM can use the whole 16 KB bank, or one 8 KB half with its
header at 4000H or 6000H. Header and jump-table layout: `PC-1600-Memory-Bank-Switching.md`
Part 6. The scan never looks at page 2, so a ROM at 8000–BFFFH is not found automatically.

**What already sits in page 1:**

| Bank | Occupant | Free? |
|---|---|---|
| 0 | internal system ROM (CS001) | no |
| 1 | Slot RAM when remapped: `SLOT1MAP` A=01H (Slot 1b) or `SLOT2MAP` A=02H (Slot 2a); possibly on by default (`PC-1600-Memory-Bank-Switching.md` Part 2) | no |
| 2 | nothing (empty in TRM §7.2.1's map) | **yes** |
| 3, 3b | internal CS24 ROM; carries its own `43 16` header | no |
| 4 | CE-1600P printer ROM | no |
| 5 | CE-1600P floppy/cassette ROM (headers at 4000H and 6000H; the CE-1600F has no ROM) | no |
| 6, 7 | nothing | **yes** |

The CE-1600P decodes Banks 4 and 5 as one 32 KB ROM and has a 60-pin pass-through, so a
device behind it must keep out of 4/5 too.

**Address decode.** The SC-7852 puts the bank number of the page being accessed on PT / PU
/ PVOUT (pins 14 / 15 / 16), MSB first (TRM §7.2.1; `PC-1600-Memory-Bank-Switching.md`
Part 2). Select the ROM on:

- `MREQ` active; `RD` for output enable
- `A15` = 0, `A14` = 1 (4000–7FFFH); optionally `A13` for one 8 KB half
- PT PU PVOUT = `0 1 0` (Bank 2), `1 1 0` (Bank 6) or `1 1 1` (Bank 7)
- `ELH̄` high (Z-80 running). While the LH-5803 runs it drives the bus and PVOUT carries
  its PV; the CE-1600P gates its ROM select on ELH for the same reason (`CSNO`,
  `PC-1600-Peripherals-Hardware.md` §1.2.2).

Not yet checked on hardware: a logic-probe look at pins 14–16 while stepping Port 31H
through the page-1 banks would confirm the decode before committing a PCB.

**No "hidden" second 16 KB for a peripheral.** Port 3DH is not a general half-select. Its
bits are latched by the gate array onto address lines that go to fixed internal chips:

| Port 3DH bit | Gate-array output | Goes to | Effect |
|---|---|---|---|
| b2 | A16A | internal CS24 ROM (IC5) only | Bank 3 / 3b at page 1 |
| b1 | A15A | kanji ROM (Japan-only; wiring not traced) | kanji ROM at page 2, Bank 4 |
| b0 | A14A | not traced | — |

None of A14A–A16A is on the 60-pin bus or the memory slots
(`../Shared/Expansion-Connectors.md` §4), and CS24 only fires for page 1,
Bank 3. A device could in principle watch for `OUT (3DH)` on A0–A7/D0–D7/`IORQ`/`WR̄` and
latch D2 itself (assuming internal I/O writes are driven onto the connector, which is
unverified), but the firmware scans and runs IOCS/interrupts with 3DH = 04H and only
enters the b2 = 0 half for its own Bank-3b tokens. The peripheral would need its own
switching code and would have to keep F07DH in step. For more than 16 KB, use two banks
(e.g. 6 and 7, each with a header) or a bank latch on the peripheral's own I/O port,
which the firmware never touches — the way Port 28H extends the memory slots.

## Planned outline

- The three connectors and what each is for: 60-pin system bus (raw Z-80 bus + control:
  M1̄, INT1̄, IORQ, WAIT, IRQ, RD̄/WR̄, MREQ, ELH̄, IOE; cassette; VBAT; φOS/BFO) vs. the two
  40-pin memory slots (address/data + RAM1/RAM2 chip select + PVOUT/PU/PT bank bits +
  K0–K2 / S1–S3). Cross-ref `Expansion-Connectors.md` §4.0–4.3.
- **Electrical:** logic levels (5 V CMOS), drive strength / fan-out per line, which lines
  are inputs vs. outputs vs. bidirectional from the machine's side, pull-ups, INH usage,
  power budget available to a peripheral (VCC pins, VBAT).
- **Bus-cycle timing:** memory read/write and I/O read/write cycle diagrams, setup/hold
  vs. the SC7852 clock, WAIT-line insertion, the gate-array buffering delay on slot
  signals, LH5803-cycle differences when ELH̄ is asserted.
- **Interrupts from a peripheral:** IRQ / INT1̄ lines, IM2 vector mechanism (Port 39H),
  acknowledge cycle, sharing/priority (Port 32H/35H).
- **Address decoding for a peripheral:** how to claim an I/O range (28–2FH, 60–6FH,
  78–83H precedents), how INH lets a module override internal ROM.
- **ROM-module integration:** placement and detection are in §1; still to do: the full
  jump-table contract (entries at +2…+15H), autostart, keyword tables.
- **Worked example:** a minimal I/O peripheral on the 60-pin bus (address decode + one
  readable/writable register + optional interrupt), end to end.
- **Unresolved:** the Slot 1 / Slot 2 ↔ K0–K2 / S1–S3 connector-label discrepancy
  (`Expansion-Connectors.md` §4.2a) — needs a continuity check on real hardware.

## What partially exists elsewhere

- `../Shared/Expansion-Connectors.md` §4–5 — raw pinouts, signal-by-function
  summary, label discrepancy.
- `PC-1600-Memory-Bank-Switching.md` Part 3 (gate array), Part 5, Part 6 (module headers/
  boot), Part 10 (adapting a PC-1500 module), Part 11 (signal summary).
- An emulator with CE-1600F / CE-1600P device models is a behavioural cross-reference for this bus (see `README.md` — Sources & validation).

## Sources needed

- PC-1600 Service Manual — bus timing diagrams, gate-array (LR38041) AC characteristics.
- PC-1600 Technical Reference Manual §10 — connector chapter (already partly transcribed).
- CE-1600F / CE-1600P service manuals — as concrete peripheral-design references.
