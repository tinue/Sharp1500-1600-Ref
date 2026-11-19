# PC-1500 / PC-1500A Expansion Connectors

Summary: PC-1500 40- and 60-pin connectors pin by pin, and the PC-1500A pin reassignment.
Scope: PC-1500, PC-1500A
Sources: cited inline in the text
Status: cited

> Split from `Expansion-Connectors.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §4, §5 → [PC-1600-Connectors.md](PC-1600-Connectors.md).

## 1. Overview

This document consolidates the physical expansion-connector pinouts for the PC-1500, PC-1500A, and PC-1600 (Slot 1 and Slot 2) in one place, since understanding how any given module (period or modern) works starts with knowing exactly which physical wires it has to work with.

It covers: the PC-1500's 40-pin and 60-pin connectors (§2); the PC-1500A's pin reassignment relative to the PC-1500, and how far a fixed-wiring module can be pushed against that reassignment (§3); and the PC-1600's 60-pin system bus connector and two 40-pin slot connectors, CN-7 (Slot 1) and CN-8 (Slot 2) (§4).

For what happens *behind* these pins — the on-mainboard address decoders, chip populations, and bank-switching logic that give each pin its meaning — see `PC-1500-Address-Decoding.md` (PC-1500/1500A) and `PC-1600-Bank-Switching.md` (PC-1600). This document is the physical-pinout reference those documents assume; §3 here also hosts a worked example (a hypothetical wide module) that draws on both.

---

## 2. The PC-1500 Expansion Connectors

The PC-1500 exposes two distinct expansion connectors, both documented in TRM §4-3 ("Connector signals/LSI signals"): a 40-pin connector (§4-3-1) and a 60-pin connector (§4-3-2). The TRM's own introductory note to §4-3 states that "there may be a different kind of connector used for the 40 and 60 pin connector of the PC-1500 on account of product revision," and that "the 64-pin connector on the back of the CE-150 is compatible with the 60-pin connector of the PC-1500."

### 2.1 40-Pin Connector

The PC-1500 exposes its expansion bus on a 40-pin edge connector on the rear (confirmed by physical pin count on real hardware).

| Pin | Signal | Description |
|-----|--------|-------------|
| 1 | VCC | Power |
| 2 | **PU** | CPU flipflop output (chip select function). The TRM prints PV; measured PU (§2.2b) |
| 3 | **PV** | CPU flipflop output (chip select function). The TRM prints PU; measured PV (§2.2b) |
| 4 | YO | Address &0000–&3FFF chip select |
| 5 | S4 | Address &6000–&67FF select (may be NC depending on production month) |
| 6 | DME0 | Chip select with WAIT condition (ME0 area). The connector's only ME qualifier: issued by the I/O port controller for ME0 cycles, with precharge time for slow/dynamic memory (`PC-1500-Address-Decoding.md` §2.4) |
| 7–14 | D7–D0 | Data bus |
| 15 | INHIBIT | Prohibits ROM select when connected to GND |
| 16 | S1 | Address &4800–&4FFF select |
| 17 | S2 | Address &5000–&57FF select |
| 18 | S3 | Address &5800–&5FFF select |
| 19 | Y2 | Address &8000–&BFFF select |
| 20 | VGG | Negative supply |
| 21 | GND | Ground |
| 22–37 | AD15–AD0 | Address bus (16 bits) |
| 38 | OD | Output disable |
| 39 | R/W | Memory read/write |
| 40 | GND | Ground |

*Source: Sharp PC-1500 Technical Reference Manual, section 4-3-1, with pins 2/3 corrected by measurement (§2.2b).*

**PU and PV** (pins 2, 3; the TRM prints them the other way round, §2.2b) are CPU flipflop outputs on the LH5801 (`SPU`/`RPU`/`SPV`/`RPV` instructions), described in the TRM as "chip select" signals — modules can use them as extra chip-select gating inputs, alongside their primary role of bank-selecting the system's own &8000–&BFFF ROM area (PC-1500 system ROM vs. CE-150/CE-158 peripheral ROM). See `LH5801-PU-PV-Signals.md` for the full mechanism, including the CE-158/TRAMsoft PU conflict and why modern module recreations avoid PU/PV entirely in favor of address-range triggers.

**YO** (pin 4) is the sole chip select for the entire &0000–&3FFF module RAM/ROM region — a 16KB window with no further narrowing done by the mainboard. A module populating this window must do its own internal sub-decoding (see the CE-155 example in `PC-1500A-Rewiring.md` §3.2).

**ME0 qualification.** The connector has no ME0 or ME1 pin. S1–S4 come from the mainboard TC40H138F, which is enabled by ME0, so a chip on those strobes is ME0-only without any logic of its own. YO and Y2 come from the TC40H139F, which ME0 does not gate, so a module on YO or Y2 must gate itself with DME0 (pin 6, the ME0 enable timed for slow memory), as the CE-155's YO chip does; one that ignores DME0 answers in ME1 as well (`PC-1500-Address-Decoding.md` §2.4).

There is no dedicated bank-select address register on the connector for any region — PU/PV (write-only CPU flipflops) and the address-range strobes (Y0, Y2, S1–S3, S4) are the only mechanisms available for a module to learn "which bank" or "which sub-region" the host is addressing.

### 2.2 60-Pin Connector

| Pin | Signal | Description |
|-----|--------|-------------|
| 1 | AD7 | Address bus |
| 2 | AD6 | Address bus |
| 3 | AD5 | Address bus |
| 4 | AD4 | Address bus |
| 5 | AD3 | Address bus |
| 6 | AD2 | Address bus |
| 7 | AD1 | Address bus |
| 8 | AD0 | Address bus |
| 9 | PB0 | Not used (may be NC depending on production month) |
| 10 | PC7 | Not used |
| 11 | VCC | Power |
| 12 | VCC | Power |
| 13 | NC | Not connected |
| 14 | NC | Not connected |
| 15 | **PU** | Chip select. The TRM prints PV; measured PU (§2.2b) |
| 16 | **PV** | Chip select. The TRM prints PU; measured PV (§2.2b) |
| 17–24 | D7–D0 | Data bus |
| 25 | INHIBIT | Prohibits ROM select of the PC-1500, when connected to GND |
| 26 | WEX | External WAIT signal |
| 27 | CMTIN | Cassette data input |
| 28 | W1 | WAIT condition input |
| 29 | CMTOUT | Cassette data output |
| 30 | INT | Interrupt request to CPU |
| 31–38 | AD8–AD15 | Address bus |
| 39 | PB1 | Not used (may be NC depending on production month) |
| 40 | NC | Not connected |
| 41 | VCC | Power |
| 42 | VCC | Power |
| 43 | F-GND | Frame GND |
| 44 | F-GND | Frame GND (TRM prints VBAT; PCB artwork and a measurement give F-GND, see §2.2b) |
| 45 | VBAT | Battery voltage |
| 46 | VBAT | Battery voltage |
| 47 | VBAT | Battery voltage |
| 48 | VBAT | Battery voltage |
| 49 | NC | Not connected |
| 50 | BFO | VCC output |
| 51 | φOS | Clock in the same phase as the LSI internal clock |
| 52 | GND | Ground |
| 53 | GND | Ground |
| 54 | GND | Ground |
| 55 | GND | Ground |
| 56 | DME0 | Chip select taking consideration of WAIT condition (ME0 area designation) |
| 57 | R/W | Memory read/write signal |
| 58 | DME1 | Chip select taking consideration of WAIT condition (ME1 area designation) |
| 59 | ME1 | ME1 area designation |
| 60 | OD | Output disable |

*Source: Sharp PC-1500 Technical Reference Manual, section 4-3-2, with contacts 15, 16 and 44 corrected by measurement (§2.2b). Note in source: "PB0 of No. 9 may be NC depending on production month. PB1 of No. 39 may be NC depending on production month."*

This is the PC-1500(A)'s side expansion connector: the CE-150 plugs into it via a 60-pin male connector, and per the TRM §4-3 note above, the CE-150's own 64-pin female connector at its rear is pin-compatible with it — letting a further peripheral (typically a CE-158) chain onto the CE-150 in turn. This connector is the PC-1500's I/O expansion bus, distinct in purpose from the 40-pin memory-expansion connector in §2.1: it carries the full 16-bit address and 8-bit data bus (like the 40-pin connector), but adds cassette I/O (CMTIN/CMTOUT), an interrupt line (INT), an external WAIT mechanism (WEX/W1), and a second WAIT-qualified chip-select/area pair (DME1/ME1) alongside DME0 — none of which appear on the 40-pin connector at all.

#### 2.2a Cross-validation against the PC-1600's 60-pin connector

The PC-1600's 60-pin system bus connector (§4.0 below) is a documented match in form factor and largely in pin assignment, confirming both scans are internally consistent (this document's original transcription source for §4.0 was the PC-1600 TRM's §10.3(1), a separate document from the PC-1500 TRM scanned here). Lining the two tables up pin-for-pin:

**Strong agreement** (same pin, equivalent signal, in both machines — good corroboration for both scans):
- Pins 1–8: address bus low byte, identical bit order (AD7→AD0 / A7→A0) on both.
- Pins 17–24: data bus, identical order (D7→D0) on both.
- Pins 25: INHIBIT (PC-1500) / INH (PC-1600) — same function, same pin.
- Pins 27, 29: CMTIN, CMTOUT — identical on both, same pins.
- Pins 31–38: address bus high byte, identical order (AD8→AD15 / A8→A15) on both.
- Pins 41, 52–54: VCC and GND land on the same pins on both machines.
- Pin 50–51: BFO, φOS — identical signals, same pins, on both.
- Pin 56: DME0 — identical signal, same pin, on both.

**Divergences** (real architectural differences between the LH5801-based PC-1500 and the Z-80/LH5803-based PC-1600, not transcription errors — the PC-1600 replaces the PC-1500's direct PU/PV CPU flipflops with a PT/PU/PVOUT triple driven by the SC-7852, and its Z-80 core has separate RD/WR/IORQ/MREQ/INT/M1 lines where the LH5801 has a single R/W and a single INT):
- Pins 15–16: PC-1500 TRM has PV then PU; PC-1600 TRM has PU then PVOUT. **Not a real difference: measured on both machines, 15 = PU and 16 = PV (PVOUT on the PC-1600, which carries the LH5803's PV). The PC-1500 TRM has 15/16 swapped (§2.2b).**
- Pins 9–10, 13–14: PC-1500 has PB0/PC7 (unused)/NC/NC; PC-1600 has INT1̄/M1̄/RSTE/PT — the PC-1600 uses this range for Z-80-specific control and the sub-CPU's PT bank-select bit.
- Pins 26, 28, 30: PC-1500 WEX/W1/INT vs. PC-1600 IORQ/WAIT/IRQ — both pairs are WAIT- and interrupt-related, but the PC-1600 versions are genuine Z-80 bus signals rather than the PC-1500's simpler external-WAIT/interrupt lines.
- Pins 39, 42: PC-1500 has PB1 (unused)/VCC; PC-1600 has VGG/NC.
- Pins 43–49: PC-1500 runs F-GND (43–44) then four VBAT pins (45–48) then NC (49); PC-1600 runs FG (43–44) then two VBAT pins (45–46) then VP (47) and NC (48–49, with MREQ at 49). Both machines put frame ground on 43–44 and battery backup after it. (The PC-1500 TRM prints 44 as VBAT; the PCB artwork and a measurement give F-GND, §2.2b.)
- Pin 55: GND (PC-1500) vs. NC (PC-1600).
- Pins 57–60: PC-1500 has R/W, DME1, ME1, OD; PC-1600 has WR̄, ELH̄, IOE, RD̄ — the PC-1500's single-strobe LH5801 read/write and second-bank chip-select signals are replaced by the Z-80's split RD̄/WR̄ strobes and the PC-1600-specific ELH̄/IOE lines.

**Net assessment:** the two scans agree exactly, pin-for-pin, on every signal common to both CPU architectures (address bus, data bus, INHIBIT/INH, CMTIN/CMTOUT, VCC/GND placement, BFO/φOS, DME0) — strong evidence neither transcription has a shifted or misread pin in those ranges. The divergences are concentrated exactly where the two machines' CPUs and bus protocols genuinely differ (bank-select signal set, interrupt/WAIT signals, read/write strobes, ground/battery pin counts), which is what a real hardware difference should look like rather than an OCR error. Two places did turn out to be errors in the PC-1500 TRM table, both settled by measurement: pins 15–16 (PU and PV swapped) and pin 44 (F-GND, not VBAT). See §2.2b.

#### 2.2b Measured: 60-pin 15 = PU, 16 = PV on both machines; PC-1500 40-pin 2 = PU, 3 = PV

**Both PC-1500 TRM tables have PU and PV swapped.** Measured on real hardware, 2026-10-03:

| Source | 40-pin 2 | 40-pin 3 | 60-pin 15 | 60-pin 16 |
|---|---|---|---|---|
| PC-1500 TRM §4-3-1 / §4-3-2 (clean scans, PDF pp.107–108) | PV | PU | PV | PU |
| PC-1600 TRM §10.3(1), Service Manual CN-9 | — | — | PU | PVOUT |
| PC-1500 PCB artwork (connector, LH5801 footprint) | — | — | PU0 = PU | PU1 = PV |
| **Measured, PC-1500** | **PU** | **PV** | **PU** | **PV** |
| **Measured, PC-1600** | — | — | **PU** | **PVOUT** |

**Orientation used for all measurements.** 60-pin connector viewed straight on, key at the top: the bottom row runs contacts 60…31 from the left, the top row 30…1 (contact *n* opposite *n*+30). Top-row position *k* from the left is contact 31 − *k*, bottom-row position *k* is contact 61 − *k*. 40-pin connector seen from the rear, calculator face up: pin 1 top right, 20 top left, 21 bottom right, 40 bottom left (also printed so on a PCB silkscreen). **Trap:** the PC-1500 main-PCB artwork (CE-150 Service Manual PDF, p.57, "8. MAIN PCB") draws the 60-pin connector from the other side of the board, so AD7/AD8 appear at the left there but sit at the right when you look into the connector. The ground (52–55, 43–44) and VCC (11/12) landmarks decide the orientation, not the artwork.

**PC-1500 (unpowered, continuity):**
- **LH5801 pin 60 (PV) ↔ 60-pin contact 16; LH5801 pin 61 (PU) ↔ contact 15.** This is the deciding measurement. PV = pin 60 has three sources: an LH5801 datasheet pinout (PV 60, PU 61), the PC-1600 Service Manual (LH5803 PV = pin 60), and the PC-1500 main circuit diagram (CPU symbol: pin 60 = PV, then "PUW").
- 40-pin pin 2 ↔ 60-pin contact 15 (PU), pin 3 ↔ contact 16 (PV). PU/PV run straight through; most other bus lines don't beep, so they're probably buffered.
- 60-pin bottom row: contacts 52–55 (GND) and 43–44 (F-GND) beep to ground, nothing in the top row does. **Contact 44 is F-GND**, not the TRM's VBAT. VBAT (45–48) has no continuity to battery + (likely a diode or switch in between). Contacts 11/12 are VCC.
- 40-pin pin 1 is VCC, pin 40 GND. Pin 21 (GND per the TRM) didn't beep to the same ground.

**PCB artwork agrees.** The PC-1500 main-PCB artwork names the lines PU0/PU1, on the LH5801 footprint and on the 60-pin connector alike. Along the footprint edge the labels run R/W, P?, **PU1, PU0**, φOS, XL0…; the datasheet runs R/W, PΦ, **PV, PU**, φOS, XL0…, so PU1 = PV and PU0 = PU. The connector artwork has PU0 on contact 15 and PU1 on 16. (The artwork's labels aren't flawless: its top edge reads D0, ME1, ME0, OD, H0, H4, H2, H6…, where the datasheet has D0, ME0, ME1, OD, H0…H7. ME0/ME1 pin numbers also differ between sources: this LH5801 datasheet gives ME0 = 30, ME1 = 29, the PC-1600 Service Manual gives the LH5803 ME0 = 29, ME1 = 30.) The PC-1500 main circuit diagram uses PV/PU at the CPU and PU0/PU1 on the 40-pin connector symbol, but doesn't link the two names.

**Likely origin of the TRM error:** reading PU0 as "bit 0 = PV" (PV as the low bit) gives exactly both TRM tables.

**Why it matters:** the CE-150 gates its ROM on PV, the CE-158 gates its ROM on PV and switches its two 8 KB halves on PU (`LH5801-PU-PV-Signals.md` §5). With the same 15 = PU, 16 = PV on both machines, the cards work on the PC-1500 and the PC-1600 alike.

**PC-1600, measured (2026-10-03, unpowered, continuity, same orientation as above; the 60-pin top row assumed to run 30…1 from the left as on the PC-1500, which the VCC hit at position 20 = contact 11 supports).** Memory-slot pins against the 60-pin connector, the same on Slot 1 and Slot 2:

| Slot pin (TRM) | 60-pin top row, from left | 60-pin contact | PC-1600 TRM, 60-pin |
|---|---|---|---|
| 1 VCC | 20th | 11 | VCC ✓ |
| 2 PVIN | 20th | 11 | VCC: **pin 2 is tied to VCC**, 0 Ω to pin 1 |
| 3 PU | 16th | 15 | PU ✓ |
| 5 PVOUT | 15th | 16 | PVOUT ✓ |
| 19 PT | 17th | 14 | PT ✓ |

- **The PC-1600 tables are right: 60-pin 14 = PT, 15 = PU, 16 = PVOUT**, the same nets as slot pins 19/3/5.
- **Slot pin 2 ("PVIN") is VCC on both slots**, not the LH5803's PV. It's the programming-voltage input: the CE-1620M circuit diagram wires it to its EPROM's Vpp (A14 comes from PVOUT, pin 5). The TRM's "LH-5803 PV signal input (direct from LH-5803 pin 60)" describes the SC7852's PVIN pin (SC7852 pin 8), not this slot contact.

**How the LH5803's PU and PV reach the PC-1600 connector** (PC-1600 Service Manual schematic, read 2026-10-03; ICN2 is hard to read):

| Net | Members |
|---|---|
| PU | LH5803 PU (pin 61) · SC7852 PU (pin 6) · ICN2-60 · slot pin 3 (both slots) · 60-pin contact 15 |
| PVOUT | SC7852 PVOUT (pin 7) · ICN2-59 · slot pin 5 (both slots) · 60-pin contact 16 |
| PV | LH5803 PV (pin 60) → SC7852 PVIN (pin 8) |

- **PU is one shared line.** While the Z-80 runs, the SC7852 drives it with the Port 31H bank bit; while the LH5803 runs, the LH5803's own PU drives it (the SC7852 must release it then, as the LH5803 releases PV while the Z-80 runs). That's why the SC7852 needs no PU input.
- **PV goes through the SC7852**: PVIN in, PVOUT out — the Service Manual's "the PV signal of the LH-5803 is directly sent by PVOUT of the SC7852".
- So while the LH5803 runs, contact 15 carries its PU and contact 16 its PV, as on the PC-1500.
- The PC-1600's own LH5803 ROM uses only `SPV`/`RPV`, never `SPU`/`RPU`.
- Not verified: the drive handover on PU (needs a logic probe) and the hard-to-read ICN2 pin numbers.

---

## 3. The PC-1500A: Pin Reassignment and How Far It Reaches

### 3.1 What changed

Four pins carry a different signal depending on the model. This is a **connector pinout change, not a change to the decoder itself** — full explanation of the cause (built-in RAM growing from S0-only to S0+S1+S2) is in `PC-1500A-Rewiring.md` §3.

| Pin | PC-1500 signal | PC-1500A signal |
|---|---|---|
| 5 | S4 (&6000–&67FF) | NC |
| 16 | S1 (&4800–&4FFF) | S3 (&5800–&5FFF) |
| 17 | S2 (&5000–&57FF) | S4 (&6000–&67FF) |
| 18 | S3 (&5800–&5FFF) | S5 (&6800–&6FFF) |

Every other pin — including YO (pin 4), Y2 (pin 19), PU/PV (pins 2/3, §2.2b), DME0 (pin 6), and the full address/data bus — is unchanged between models. A module's hardware never has to know which machine it's plugged into: it just reacts to whatever strobe physically arrives on its fixed pins.

### 3.2 The ceiling: S5 never reaches the connector on the PC-1500 at all

Only **four** pins in this range carry a strobe on the PC-1500: pins 5, 16, 17, 18 (S4, S1, S2, S3). S5, S6, and S7 never appear on any connector pin on the PC-1500 — only S1–S4, YO, and Y2 reach the expansion bus. This means:

- The largest fixed-wiring module obtainable via these four pins on the PC-1500 covers **S1+S2+S3+S4** (8KB), tiling exactly against built-in S0 (2KB) to fill &4000–&67FF. S5 (&6800–&6FFF) is permanently unreachable by any module — not because Sharp chose to leave it unpopulated, but because no physical wire for it exists. This is why the PC-1500's own decode table marks S5 "Not used" (`PC-1500-Address-Decoding.md` §2.2) rather than "optional."
- The same four pins on the PC-1500A decode to: pin 5 → **NC**, pin 16 → S3, pin 17 → S4, pin 18 → S5. So the identical module gets **S3+S4+S5** (6KB) there, with the pin-5-wired bank left floating/dead.

**Worked comparison — the maximal fixed-wiring module, Y0 fully populated on both models:**

| Model | Y0 (&0000–&3FFF) | Built-in | Module (S-blocks) | Total | Gaps |
|---|---|---|---|---|---|
| PC-1500 | 16KB (module) | S0, 2KB | S1+S2+S3+S4, 8KB | **26KB** | S5 (2KB) permanently unreachable |
| PC-1500A | 16KB (module) | S0+S1+S2, 6KB | S3+S4+S5, 6KB | **28KB** | none — &0000–&6FFF fully tiled |

The PC-1500A version of this module fills its entire available window (&0000–&3FFF plus &4000–&6FFF) with no gaps. The PC-1500 version is short exactly 2KB relative to that, because S5 was never wired to the connector on that model — a ceiling Sharp's four-pin design imposes structurally, independent of chip population or built-in RAM.

A *wider* hypothetical module — one wanting S1 through S5 on the PC-1500 (10KB) and S3–S5 on the PC-1500A (6KB) — is not just short by 2KB; it's unbuildable on the PC-1500 side outright, since there is no fifth pin to wire S5 to in the first place. Sharp's connector design covers the CE-155 case (3 pins, exact 4KB shift, no gaps on either model) and stretches to a 4-pin/8KB module (1500) vs. 3-pin/6KB module (1500A) with one dead bank on the 1500A — but goes no further. See `PC-1500A-Rewiring.md` §3.3 for the independent, chip-count-based argument for why Sharp's own built-in RAM expansion stopped at the same S0–S2 boundary.

---
