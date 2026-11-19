# PC-1600 Expansion Connectors

Summary: PC-1600 60-pin system bus and the two 40-pin memory-slot connectors; module hardware status.
Scope: PC-1600
Sources: cited inline in the text
Status: cited

> Split from `Expansion-Connectors.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §1, §2, §3 → [PC-1500-Connectors.md](PC-1500-Connectors.md).

## 4. PC-1600 Expansion Slot Connectors

The PC-1600 has three expansion connectors in total: a 60-pin system bus connector (for peripherals that need the raw Z-80 bus, e.g. the CE-1600F floppy or CE-1600P plotter/printer units) and two 40-pin memory slot connectors, one per memory slot. Unlike the PC-1500/1500A's single connector, these carry Z-80 (not LH5801) bus signals, plus the SC-7852's bank-select lines and the gate-array-buffered slot selects described in `PC-1600-Gate-Array-and-Chip-Selects.md` Part 3–4.

### 4.0 The 60-pin system bus connector

*Source: PC-1600 Technical Reference Manual §10.3(1).*

| Pin | Signal | Pin | Signal | Pin | Signal | Pin | Signal |
|---|---|---|---|---|---|---|---|
| 1 | A7 | 16 | PVOUT | 31 | A8 | 46 | VBAT |
| 2 | A6 | 17 | D7 | 32 | A9 | 47 | VP |
| 3 | A5 | 18 | D6 | 33 | A10 | 48 | NC |
| 4 | A4 | 19 | D5 | 34 | A11 | 49 | MREQ |
| 5 | A3 | 20 | D4 | 35 | A12 | 50 | BFO |
| 6 | A2 | 21 | D3 | 36 | A13 | 51 | φOS |
| 7 | A1 | 22 | D2 | 37 | A14 | 52 | GND |
| 8 | A0 | 23 | D1 | 38 | A15 | 53 | GND |
| 9 | INT1̄ | 24 | D0 | 39 | VGG | 54 | GND |
| 10 | M1̄ | 25 | INH | 40 | NC | 55 | NC |
| 11 | VCC | 26 | IORQ | 41 | VCC | 56 | DME0 |
| 12 | NC | 27 | CMTIN | 42 | NC | 57 | WR̄ |
| 13 | RSTE | 28 | WAIT | 43 | FG | 58 | ELH̄ |
| 14 | PT | 29 | CMTOUT | 44 | FG | 59 | IOE |
| 15 | PU | 30 | IRQ | 45 | VBAT | 60 | RD̄ |

This is a different, larger connector than the two memory slots — it exposes Z-80 control signals (M1̄, INT1̄, IORQ, WAIT, IRQ) that the memory slots don't, plus cassette I/O (CMTIN/CMTOUT), battery-backup (VBAT), and the sub-CPU timing signals (BFO, φOS) that never appear on a memory-only connector. PT, PU and PVOUT (pins 14, 15, 16) carry the bank number of the page being accessed, MSB first (`../Memory/PC-1600-Bank-Switching.md` Part 2): on a 4000–7FFF access, Port 31H b3/b2/b1. A 60-pin peripheral ROM decodes its bank from them, as the CE-1600P does for Banks 4/5. Measured: 14/15/16 are the same nets as memory-slot pins 19/3/5 (PT/PU/PVOUT). While the LH5803 runs, 15 carries its PU (a shared line) and 16 its PV (via PVIN → PVOUT), the same as the PC-1500's 15 = PU, 16 = PV (§2.2b).

### 4.1 Memory Slot 1 (S1) Connector — CN7

*Source: PC-1600 TRM §9.1(4) "Connector Circuit Diagram" (printed p.267, PDF p.275),
`SLOT1` / CN7. The pin layout is the one in TRM §10.3, whose two slot tables have their
headings swapped (§4.2a).*

| Pin | Signal | Pin | Signal | Pin | Signal | Pin | Signal |
|-----|--------|-----|--------|-----|--------|-----|--------|
| 1 | VCC | 11 | D3 | 21 | NC | 31 | A6 |
| 2 | PVIN | 12 | D2 | 22 | A15 | 32 | A5 |
| 3 | PU | 13 | D1 | 23 | A14 | 33 | A4 |
| 4 | **RAM2** | 14 | D0 | 24 | A13 | 34 | A3 |
| 5 | PVOUT | 15 | INH | 25 | A12 | 35 | A2 |
| 6 | MREQ | 16 | **S1** | 26 | A11 | 36 | A1 |
| 7 | D7 | 17 | **S2** | 27 | A10 | 37 | A0 |
| 8 | D6 | 18 | **S3** | 28 | A9 | 38 | RD |
| 9 | D5 | 19 | PT | 29 | A8 | 39 | WR |
| 10 | D4 | 20 | VGG | 30 | A7 | 40 | GND |

### 4.2 Memory Slot 2 (S2) Connector — CN8

*Source: same diagram, `SLOT2` / CN8.*

Identical layout to §4.1 except:
- Pin 4 = **RAM1** (instead of RAM2)
- Pin 16 = **K0**, Pin 17 = **K1**, Pin 18 = **K2** (instead of S1/S2/S3)

**Pin 21 (NC) has a factory option on both slots.** On Slot 2 it runs to an open jumper
**J1**. The far side of J1 is the net that also feeds R1, the pull-up on KC2 (CN2-58),
which reads as VCC. On Slot 1 the pin-21 trace is marked **CUT**. Neither is fitted on a
production board as drawn, so pin 21 is unconnected, which agrees with the tables.

### 4.2a Resolved: TRM §10.3 swaps the two slot tables

TRM §10.3(2) "Memory slot 1 (S1) connector" lists **RAM1 + K0/K1/K2**, and §10.3(3)
"Memory slot 2 (S2) connector" lists **RAM2 + S1/S2/S3** (checked again in the English
PDF, pp.286–287). Every other source puts them the other way round, and so does the TRM
itself in two other places:

- **TRM §9.1(4) Connector Circuit Diagram** (printed p.267): `SLOT1`/CN7 pin 4 = RAM2 and
  pins 16–18 = S1/S2/S3; `SLOT2`/CN8 pin 4 = RAM1 and pins 16–18 = K0/K1/K2. This is
  legible in a sharp photo of the printed page; the PDF scan is too coarse to read.
- **TRM §7 RAM-select text**: "The RAM2 signal is a memory select signal for the memory
  slot 1 (S1)… The RAM1 signal is a memory select signal for the memory slot 2 (S2)."
  This matches SC-7852 pins 50/51 (`../CPU/PC-1600-SC7852-Pinout-and-Control-Regs.md` §6).
- The **CE-1601M** (`PC-1600-Memory-Modules.md` Part 7a) must go in slot S2, and
  its decoder is driven by its edge-connector pins K0 and K2. ***superRAM*** (Part 7b) also
  goes in Slot 2 and uses the same Port 28H / K0–K2 mechanism.
- Measured: the Slot 1 pins 16–18 carry the 2 KB strobes of a CE-151/155/159
  (`PC-1600-Gate-Array-and-Chip-Selects.md` Part 4).

So the error is in the two §10.3 headings only; the pin layout itself is right. §4.1–4.2
above give the corrected assignment, and "Slot 1" and "Slot 2" mean the same physical bay
in every document in this corpus.

### 4.3 Key signals, by function

RAM2/S1–S3 on Slot 1, RAM1/K0–K2 on Slot 2 (§4.1–4.2a).

| Pin | Signal | Function |
|---|---|---|
| 2 | PVIN | **Programming-voltage input, tied to VCC** (measured on both slots, §2.2b). The CE-1620M wires it to its EPROM's Vpp; the CE-1601E programmer supplies 21 V there. The TRM's "LH-5803 PV signal input (direct from LH-5803 pin 60)" describes the SC7852's own PVIN pin (SC7852 pin 8), a different net. |
| 3 | PU | Bank select bit, from I/O port 31H |
| 4 | RAM2 (Slot 1) / RAM1 (Slot 2) | Chip select for the respective slot's RAM banks. Called **RAMSN** on the CE-1600M/CE-1620M schematics. Asserted (low) **only** for 8000–BFFF accesses when the Port 31H page-2 field selects this slot (banks 0/1 → Slot 1; banks 2/3 → Slot 2). Never asserts for 4000–7FFF or any other window — a memory-bay module cannot answer outside 8000–BFFF. |
| 5 | PVOUT | The selected module's **A14-equivalent** — which 16 KB half / which of the slot's two banks. **= Port 31H bit b4** (LSB of the 8000–BFFF bank field), i.e. the bit distinguishing bank 0 from 1 (Slot 1) or bank 2 from 3 (Slot 2). *Not* Port 31H bit b0: b0 is also nicknamed "PVOUT" but is the 0000–3FFF page / LH5803-PV bit and does not reach this pin. (Corrected here from an earlier "from I/O port 31H b0" — confirmed against the CE-1600M schematic, which uses pin 5 as one of the two `{A13, PVOUT}` select inputs to its 4-way SRAM decoder, and Part 7a's CE-1601M description of the same pin distinguishing "Z-80 Bank 2 vs. Bank 3".) |
| 6 | MREQ | Z-80 memory request |
| 15 | INH | Inhibit internal ROM (CS001/CS123), letting the module override internal memory. **Polarity note:** PC-1600 TRM §7.2.2 says the ROM is inhibited by driving INH **high** — on the PC-1600 INH *is* the ROM's active-low OE, tied to ground by default. This is opposite to the PC-1500's "connect to GND to inhibit". See `../Memory/PC-1600-Gate-Array-and-Chip-Selects.md` Part 4; not yet reconciled against a second source. |
| 16–18 | S1/S2/S3 (Slot 1) or K0/K1/K2 (Slot 2) | Slot 1: 2 KB sub-selects in bank 0, the gate array's buffered LHS3/LHS2/LHS1 (reverse order, measured). Port 3CH b6 = 0: B800/B000/A800; b6 = 1: A000/A800/B000. The boot probe sets 1AH (b6 = 0) for a CE-151, 5BH (b6 = 1) for a CE-155 — see `../Memory/PC-1600-Gate-Array-and-Chip-Selects.md` Part 4. Slot 2: I/O selects for 28–2FH |
| 19 | PT | Bank select bit, from I/O port 31H |
| 22–37 | A15–A0 | Full 16-bit Z-80 address bus |
| 7–14 | D7–D0 | Data bus |
| 38/39 | RD/WR | Z-80 read/write strobes |

PVOUT, PU, and PT are on the connector, but the **CE-1600M schematic shows Sharp's own 32KB RAM module wiring only PVOUT** (pin 5) as its bank input — plus RAMSN (pin 4) as enable and A0–A13 for the window. PU (pin 3) and PT (pin 19) go unconnected on that module; they are the Port 31H 4000–7FFF field bits (b1/b2), broadcast machine-wide but not needed by a memory module (which only ever lives in the 8000–BFFF window). So the practical selection a 32KB module gets from its pins is **one bit** (PVOUT = b4, the 16KB-half select), giving 2 banks × 16KB = 32KB. A module wanting more must instead be driven through **Port 28H** — a write-only "vertical bank" selector (values 0–7, one 32KB bank each, decoded on the module side from K0–K2) that reaches 256KB for Slot 2 with Sharp's own decoder hardware. See Part 2, Part 7 and Part 7a of `PC-1600-Bank-Switching.md`, and §5 below.

Compared to the PC-1500/1500A single connector, the PC-1600 slots expose: a full 16-bit address bus directly (vs. no address bus reaching a PC-1500 module beyond what's needed for its own local decode — actually the PC-1500 does expose the full AD15–AD0 bus, pins 22–37, so this is symmetric); three dedicated bank-select bits (PVOUT/PU/PT) instead of two flipflops (PU/PV) plus four narrow address-range strobes; and, on Slot 1 only, three 2 KB strobes S1–S3 in bank 0 that stand in for the PC-1500's S1–S3, so that the PC-1500 modules CE-151/155/159 work there (RAM2 on pin 4 plays the part of Y0). PC-1600 modules proper are bank-selected, not address-range-selected.

---

## 5. PC-1600 Module Hardware: Status

`PC-1600-Bank-Switching.md` covers the bank-switching architecture (Port 31H truth tables, gate array pin assignments, firmware bank-call mechanism, and the CN-7/CN-8 pinout now consolidated above) in solid detail, confirmed against the Service Manual and Systemhandbuch.

**Resolved, now from two independent sources** (CE-1601M Service Manual, Part 7a; *superRAM* modern-module manual, Part 7b): Port 28H is a write-only "vertical bank" selector for Slot 2, values 0–7 natively, decoded entirely on the module side (via the K0–K2 I/O-select lines) rather than on the mainboard. Each vertical bank is 32KB — confirmed both from the CE-1601M's chip layout (a 64KB module occupies exactly two vertical banks) and from *superRAM*'s own stated memory map. That makes **256KB the officially-supported ceiling for Slot 2** (8 banks × 32KB), and only vertical bank 0 is reachable as ordinary program/expansion memory — banks 1–7 are file-system-only. **512KB is directly confirmed** by *superRAM*, which extends the vertical-bank field to 4 bits (0–15) in hardware (a jumper-selected extra address line on its single large SRAM chip, replacing Sharp's one-chip-per-bank decoder approach) and patches the PC-1600's file-system header/capacity fields at runtime, since the stock `INIT` command has no notion of a disk that large. Sharp's own largest factory module was the 64KB CE-1601M — confirmed directly by the *superRAM* manual's own text.

**Still open:**
- **CE-1650M** (256KB, 8 vertical banks × 32KB, Slot 2, Japan-only). Shown in the CE-1601M Service Manual §5 map. No standalone schematic, but the CE-1601M schematic now largely explains it: that PWB carries a **`0M`/`1M` solder-jumper strap** on the `TC74HC131F`'s high select input — `0M` = 2 vertical banks (CE-1601M), `1M` = all 8 (CE-1650M) — so the CE-1650M is almost certainly the same board with all SRAM sites populated and the strap set. See `PC-1600-Memory-Modules.md` Part 7a.
- **Slot 1's ceiling.** Slot 1 has no equivalent of Port 28H in the documentation so far (RAM2 chip select is unconditional on PVOUT/PU/PT alone, and *superRAM* itself states Slot 1 operation "would there behave like a 32KB RAM module") — worth confirming whether that's a hard architectural cap or just unimplemented.
