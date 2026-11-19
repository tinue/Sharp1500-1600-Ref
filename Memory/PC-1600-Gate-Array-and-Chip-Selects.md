# PC-1600 Gate Array and Chip Selects

Summary: Chip complement, LR38041 gate array, chip-select signals, slot connectors, signal summary, memory PWB wiring.
Scope: PC-1600
Sources: - Service_Manual.pdf -- hardware architecture, schematics, gate array, slot pinouts - SHARP-PC1600-Systemhandbuch.pdf -- firmware, OS calls, module headers, software
Status: cited

> Split from `PC-1600-Memory-Bank-Switching.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §8 → [PC-1600-LH5803-Memory-View.md](../CPU/PC-1600-LH5803-Memory-View.md); §2 → [PC-1600-Bank-Switching.md](PC-1600-Bank-Switching.md); §9 → [PC-1600-IO-Ports.md](../IO-Ports/PC-1600-IO-Ports.md); §7, §7a, §7b, §10 → [PC-1600-Memory-Modules.md](../Expansion/PC-1600-Memory-Modules.md); §6 → [PC-1600-Transparent-Banking.md](../Firmware/PC-1600-Transparent-Banking.md).

## Part 1: System Architecture Overview

The PC-1600 is a dual-CPU pocket computer with a sophisticated bank-switched memory system that expands a 64KB directly-addressable Z-80 address space to 320KB.

### Main Chips (FPC PWB unit)

| Ref | Part | Function |
|-----|------|----------|
| IC1 | SC7852 | Main CPU 2 (Z-80 compatible, CMOS, 3.58MHz) |
| IC2 | LH5803 | Main CPU 1 (8-bit, CMOS, 2.6MHz / 1.3MHz internal) |
| IC3 | LU57813P | Sub CPU (4-bit, CMOS, 307.2KHz) -- power mgmt, RTC |
| IC4 | LR38041 | Gate Array -- glue logic: slot-select buffering, Port 3DH latch, sub-CPU data buffer, serial routing (Part 3). Memory decoding is inside the SC7852 (Part 4) |

### Memory PWB Chips

| Ref | Part | Function |
|-----|------|----------|
| IC1 | 64K SRAM | Internal RAM 1 (8KB) |
| IC2 | 64K SRAM | Internal RAM 2 (8KB) |
| IC3 | 27C256FA51 | System ROM 1 (32KB) |
| IC4 | 27C256FPA5 | System ROM 2 (32KB) |
| IC5 | 27C256FPA6 | System ROM 3 (32KB) |

- **Total internal ROM:** 96KB (80KB for Z-80 BASIC interpreter + 16KB for LH-5803)
- **Total internal RAM:** 16KB (two 8KB SRAMs), expandable to 80KB with modules

---

## Part 3: Gate Array LR38041 -- Glue Logic

The LR38041 gate array (IC4 on FPC PWB) is, in the TRM's words (§7.8), "gate circuits necessary for the connection between the LSIs". It does **not** decode memory: the chip selects (CS001/CS123/CS24, RAM1–3, LHS1–3), the PT/PU/PVOUT bank lines, the Port 31H/3CH registers and the CPU hand-off (`ELH#`) are all SC7852 functions (Part 4, `PC-1600-SC7852-Pinout-and-Control-Regs.md` §6). The gate array has no chip-select outputs and sees only A13 and A14 of the address bus (A14 "insignificant"). What it does: latch Port 3DH into A14A–A16A, derive A13A, buffer the SC7852's slot selects to the slots with safe levels at power-off / low battery, hold the sub-CPU return-data buffer (I/O 33H), route the serial lines (PRIM), pass the UART clock, and build the shared `RD` strobe while the LH-5803 runs.

### Full pin table (TRM §7.8)

Complete 64-pin list from the PC-1600 Technical Reference Manual §7.8 "Gate Array
(LR38041) Pin Beschreibung" (read from the German Systemhandbuch scan). Overbar shown as
trailing `#`.

| Pin | Signal | Dir | Active | Function |
|---|---|---|---|---|
| 1 | SLCB | In | | `PI` signal from the sub-CPU, marking system operation. Goes high when the system is off → (1) D2–D0 fixed low, (2) all outputs except A13A fixed low or high. |
| 2 | Q3 | In | | Hardware low-battery detect. Low = battery OK. High (low battery) → S1/S2/S3/K0/K1/K2 forced high, KH pulled low, RD set high-Z. |
| 3 | Z12 | In | | High when on. |
| 4 | Z13 | In | Low | Poll of BREAK/ON status while the sub-CPU is in power-save; held high during power-save to keep KH low. |
| 5 | ON | In | Low | BREAK/ON key input (low = pressed). |
| 6 | KC1 | In | | Signal input for the analog-input connector. |
| 7 | CL2 | In | | Sub-CPU **1.229 MHz** clock input. |
| 8 | RD | Out | Low | Combined read strobe: wired-OR of ME0, ME1, OD, CKOS, BRQ with the Z-80 `RD#`. High-Z while the Z-80 runs. |
| 9–16 | R20–R33 | In | | Return data from the sub-CPU; becomes Z-80 data when the Z-80 reads I/O 33H. |
| 17 | PRIM | In | | RS-232C (high) vs. SIO (low) select. Drives SDA/SDF/RXD routing (see `PC-1600-Serial-Hardware.md`). |
| 18 | TXD | In | Low | Transmit data, from the TC8576F UART. |
| 19 | RXD | Out | Low | Receive data, to the TC8576F UART (from RDF or RDA per PRIM). |
| 20 | RDA | In | Low | Receive data from the RS-232C interface. |
| 21 | SDA | Out | High | Transmit data to the RS-232C connector; held low while PRIM is low. |
| 22 | RDF | In | High | Receive data from the SIO interface. |
| 23 | SDF | Out | High | Transmit data to the SIO connector; held low while PRIM is high. |
| 24 | CKOS | In | | With ME0/ME1/OD/BRQ, builds pin-8 RD: the LH-5803's OD alone is also low outside reads and need not match Z-80 timing, so RD goes low only while the LH-5803 really reads memory or I/O. |
| 25 | VCC | — | | Power (system VGG input). |
| 26 | GND | — | | Power. |
| 27 | BRQ | In | | See pin 24. |
| 28–30 | D0–D2 | In/Out | | Z-80 data bus; the inputs of the Port 3DH latch. Fixed low while SLCB is high (system off). |
| 31–35 | D3–D7 | Out | | Z-80 data bus (return data for I/O 33H). |
| 36 | C/D | In | High | Goes high when the Z-80 writes I/O 3DH. |
| 37 | IORP# | In | Low | Places R33–R20 on the Z-80 data bus; low when the Z-80 reads I/O 33H. |
| 38 | CL# | In | Low | **System reset.** Forces A16A high, A15A low, A14A high (TRM §7.8 and Service Manual §9-4 agree). The firmware then writes 3DH = 04H (A14A low). |
| 39 | A13 | In | | CPU address A13. |
| 40 | A14 | In | | CPU address A14 (marked "insignificant"). |
| 41 | DSR | Out | | Not used. |
| 42 | CLK1 | Out | | Passes CL2 through as the TC8576F UART base clock while the system is on; low when off. |
| 43 | KH | Out | High | Inverted BREAK/ON key input, to the sub-CPU. |
| 44 | A13A | Out | | Inverted A13 — 8 KB half-select for the internal RAM chips. |
| 45–47 | A14A / A15A / A16A | Out | | C/D-latched D0/D1/D2. **A16A** is the top address bit of the 32 KB CS24 ROM: it extends the 16 KB bank-3 window (4000–7FFF) to 32 KB, Bank 3 / 3b. |
| 48–50 | LHS1–LHS3 | In | Low | Memory-select signals from the SC-7852, buffered to the slots. |
| 51–53 | KA0–KA2 | In | Low | I/O-select signals from the SC-7852, buffered to the slots. |
| 54–56 | S1–S3 | Out | Low | Buffered LHS1–3 to the expansion slots. All high when the system is off or on low battery. |
| 57–58 | — | | | Not listed in the TRM §7.8 or Service Manual §9-4 pin tables. |
| 59–61 | K0–K2 | Out | Low | Buffered KA0–2 to the expansion slots. Same. |
| 62 / 63 / 64 | ME1 / ME0 / OD | In | | LH-5803 memory-enable / output-disable strobes; feed the pin-8 RD generation. |

Buffering LHS/KA → S/K through the gate array is required because the SC-7852 is
unpowered during system-off while the gate array (on VGG) keeps the slot select lines at
a safe inactive level.

### Key Gate Array Functions

1. **Shared read strobe:** while the LH-5803 runs, builds `RD` from ME0/ME1/OD/CKOS/BRQ (pin 8, wired-OR with the Z-80 `RD#`). Bus arbitration itself is the SC7852's: its `ELH#` (pin 77; high = Z-80, low = LH-5803) drives the LH-5803's BRQ.

2. **Address Line Translation:**
   - A13A: Inverted A13, used as 8KB half-select for RAM chips
   - A14A-A16A: Latched from data bus via C/D register write
   - A16A selects which 16 KB half of the 32 KB CS24 ROM appears as Bank 3 (Bank 3 / 3b)

3. **Slot Signal Buffering:** LHS1-3 and KA0-K2 from SC7852 are buffered to S1-S3 and K0-K2 for expansion slots. Required because SC7852 power is off during system-off while gate array maintains levels.

4. **Reset Behavior:** When CL goes low, A16A forced high, A15A forced low, A14A forced high -- establishing known initial bank config.

5. **Sub-CPU and serial glue:** the R20–R33 return-data buffer (I/O 33H via `IORP#`), `CL2` → `CLK1` UART clock, BREAK/ON → `KH`, and the PRIM serial routing.

---

## Part 4: Chip Select Signals -- Address Decoding

Generated internally by the SC7852 custom CPU, based on bank selection register and current address:

| Signal | SC7852 Pin | Active | Selects |
|--------|------------|--------|---------|
| CS001 | 43 | Low | ROM 0000-7FFF Bank 0 (main system ROM) |
| CS123 | 44 | Low | ROM 8000-BFFF Bank 6, LH-5803 ROM C000-FFFF |
| CS24 | 45 | Low | ROM 4000-7FFF Bank 3/4 (sub-banked by A16A) |
| RAM3 | 49 | High | Internal 16KB RAM C000-FFFF Bank 0 |
| RAM2 | 50 | Low | Slot 1 (S1) RAM 8000-BFFF Bank 0/1 |
| RAM1 | 51 | Low | Slot 2 (S2) RAM 8000-BFFF Bank 2/3 |
| LHS3 | 46 | Low | 2 KB sub-select within 8000-BFFF, bank 0 (remappable) |
| LHS2 | 47 | Low | 2 KB sub-select within 8000-BFFF, bank 0 (remappable) |
| LHS1 | 48 | Low | 2 KB sub-select within 8000-BFFF, bank 0 (remappable) |

**INH signal** (on slot connectors): inhibits the internal ROM (CS001/CS123), letting an external slot module override internal memory.

> **Correction / cross-check against TRM §7.2.2.** The PC-1600 Technical Reference
> Manual states the ROM selected by CS001/CS123 is made non-selectable **by driving INH
> *high***, and that "on the PC-1600 the INH terminal is tied to ground and fed to the
> ROM's OE signal" — i.e. INH *is* the ROM output-enable (active-low OE), grounded by
> default so the ROM is enabled; a module drives it high to disable the ROM. This is the
> **opposite polarity** from the "pull INH low to inhibit" convention on the PC-1500 and
> from `../Expansion/PC-1600-Connectors.md` §4.3. Trust the TRM for the
> PC-1600; the connector-doc wording needs reconciling (flagged there).

**Other TRM §7.2.2 details** not previously captured:
- **RAM3** is **active-high** and drives the **CE2** (second chip-enable) input of *each*
  of the two internal 8 KB RAMs.
- **CS24** feeds the CS of a **256 Kbit** ROM; that ROM's **OE receives A15**, and the
  16 KB window is extended to **32 KB by the A16A signal** (bank 3 sub-banking). Verbatim
  TRM remark: *"CS24 is an input to the CS line of 256K bits ROM. A15 is connected to OE
  of the ROM. This 16KB space is further banked by another port signal to compose a 32KB
  area."* — "another port signal" is Port 3DH bit b2 (Auxiliary Bank Control Ports,
  below); this is the primary-source confirmation that Bank 3b is a real, distinct 16 KB
  region of the CS24 chip, independent of any dump result.
- **CS123** is likewise a **256 Kbit (32 KB)** ROM, split the same way: 16 KB is the
  Z-80-visible Bank 6 (8000–BFFFH), the other 16 KB is the LH-5803's own ROM. Verbatim TRM
  remark: *"This signal must be low to access the memory space of 8000H-BFFFH of bank 6.
  The remaining 16KB area of the second half is for the LH-5803 control ROM."* This is the
  primary-source confirmation of the empirical Stage-1 finding in
  `../../PC-1600-ROM/dumper/` on real hardware that the ordinary
  Z-80 `BANKSET`/page-2/bank-6 path **cannot** reach the LH-5803's own ROM — physically
  it's the other half of the same chip, reachable only via the LH-5803's own address bus
  (the `CALLH` bridge, Part 8), not any Z-80 port combination.
- **CS001** is the third chip of the same size: *"The ROM (64KB) selected by CS001 or
  CS123 is cleared when a high signal is given to the INH line..."* — i.e. CS001's 32 KB
  (all of Bank 0, 0000–7FFFH) plus CS123's 32 KB together make up "the ROM (64KB)" the INH
  line disables as a unit. Sharp's own service-manual parts inventory lists this trio as
  **"32KB ROM x 3"** — CS001 + CS24 + CS123, 96 KB of internal ROM silicon in total, of
  which one 16 KB half (the LH-5803's private slice of CS123) is not reachable from the
  Z-80 side at all.
- **RAM2#** (Slot 1) asserts on bank **0 or 1**, 8000H–BFFFH; **RAM1#** (Slot 2) asserts
  on bank **2 or 3**, 8000H–BFFFH.

**LHS1/LHS2/LHS3 remapping via bit b6 of I/O 3CH** (TRM SC7852 pin table, pins 46-48; the
TRM's "A800-FAFF" is a misprint for A800-AFFF):

| Signal | b6=0 | b6=1 |
|--------|------|------|
| LHS1 | A800-AFFF (Bk 0) | B000-B7FF (Bk 0) |
| LHS2 | B000-B7FF (Bk 0) | A800-AFFF (Bk 0) |
| LHS3 | B800-BFFF (Bk 0) | A000-A7FF (Bk 0) |

**On the Slot 1 connector the order is reversed** -- pin 16 (S1) carries LHS3, pin 17 (S2)
LHS2, pin 18 (S3) LHS1 (measured on a real PC-1600, 2026-10-03, below):

| Slot 1 pin | b6=0 | b6=1 |
|---|---|---|
| 16 (S1) | B800-BFFF | A000-A7FF |
| 17 (S2) | B000-B7FF | A800-AFFF |
| 18 (S3) | A800-AFFF | B000-B7FF |

**Who sets b6: the boot probe** (P0-B0 `03CF`-`03EE`). With Port 3CH = 0 it tests bank 0
B000H, then A800H, for memory (`MEMORYCHK`, CY = nothing there) and writes the result to
Port 3CH and its mirror F08DH:

| Probe result (3CH = 0) | Port 3CH | Module |
|---|---|---|
| nothing at B000H | 1BH | empty slot |
| memory at B000H, none at A800H | 1AH (b6=0) | CE-151 (S1+S2 -> B800H + B000H) |
| memory at B000H and A800H | 5BH (b6=1) | CE-155/159 (S1-S3 -> A000H-B7FFH, own Y7 decoder -> B800H), CE-161, CE-1600M |

The PC-1500 modules thus land top-justified below the internal RAM, as TRM §3.12.1 draws
them: CE-151 B000-BFFF, CE-155/159 A000-BFFF. **Measured** on a real PC-1600 with a CE-155
in Slot 1: MEM 20026 (+8192), 3CH = 5BH, four separate 2 KB blocks at A000-BFFF, BASIC
start A0C5H. With the CE-155's pins 4 and 18 taped off (S1+S2 chips only, electrically a
CE-151, Service Manual schematic 5-3): MEM 15930 (+4096), 3CH = 1AH, RAM at B000H and B800H
only, BASIC start B0C5H. Only the reversed pin order fits both.

---

## Part 5: Expansion Slot Connectors

Full CN-7 (Slot 1) and CN-8 (Slot 2) 40-pin tables, plus a by-function signal summary, have moved to `PC-1600-Connectors.md` §4, alongside the PC-1500/1500A connector for direct comparison. Key pins referenced elsewhere in this document: RAM2 (Slot 1 pin 4) / RAM1 (Slot 2 pin 4) as chip select; PVOUT (pin 5), PU (pin 3), PT (pin 19) as the three raw bank-select bits from I/O port 31H; S1-S3 (Slot 1) / K0-K2 (Slot 2) on pins 16-18; INH (pin 15) to inhibit internal ROM.

---

## Part 11: Signal Summary -- All Memory-Related Signals

### Bank Selection Signals (from SC7852, controlled by Port 31H)

| Signal | Pin | Function |
|--------|-----|----------|
| PT | 5 | Memory bank signal |
| PU | 6 | Memory bank signal |
| PVOUT | 7 | Bank 0/1 selector |

### Gate Array Generated Signals

| Signal | Pin | Function |
|--------|-----|----------|
| A13A | 44 | Inverted A13, selects 8KB RAM half |
| A14A | 45 | Latched D0 from C/D write |
| A15A | 46 | Latched D1 from C/D write |
| A16A | 47 | Latched D2 from C/D write, sub-banks CS24 |

### Bus Control Signals

| Signal | Chip | Function |
|--------|------|----------|
| ELH | SC7852 | CPU ownership (H=Z-80, L=LH-5803) |
| SLCT | SC7852 | Master memory/IO enable from sub CPU |
| LHWAIT | SC7852 | Wait signal to LH-5803 |
| MREQ | SC7852 | Memory request |
| IORQ | SC7852 | I/O request |
| INH | Slot | Inhibit internal ROM |
| DME0 | SC7852 | LH-5803 memory select |

---

## Part 12: Internal RAM/ROM Wiring (Memory PWB)

### Connector CN-12 (Memory PWB to main board, 36 pins)

| Pin | Signal | Pin | Signal | Pin | Signal |
|-----|--------|-----|--------|-----|--------|
| 1 | VGG | 13 | D6 | 25 | A1 |
| 2 | WR | 14 | D5 | 26 | A2 |
| 3 | RAM3 | 15 | D4 | 27 | A3 |
| 4 | A8 | 16 | D3 | 28 | A4 |
| 5 | A9 | 17 | INH | 29 | A5 |
| 6 | LHA90 | 18 | VCC | 30 | A6 |
| 7 | A11 | 19 | GND | 31 | A7 |
| 8 | A13A | 20 | CS001 | 32 | A12 |
| 9 | RD | 21 | D2 | 33 | CS123 |
| 10 | A10 | 22 | D1 | 34 | A14 |
| 11 | A13 | 23 | D0 | 35 | A15 |
| 12 | D7 | 24 | A0 | 36 | CS24 |

### RAM Wiring

**RAM1 (IC1):** A0-A12 to address bus, D0-D7 to data bus
- CS1 = A13A (inverted A13 from gate array)
- CS2 = LHA90, OE = RD, WR = WR

**RAM2 (IC2):** Identical except CS1 = A13 (direct, not inverted)
- RAM1 covers one 8KB half, RAM2 covers the other

Both have RAM3 on chip enable -> only active when C000-FFFF Bank 0 is selected.

### ROM Wiring

- **ROM1 (IC3):** CE = CS001 (Bank 0, 0000-7FFF), A15 = OE
- **ROM2 (IC4):** CE = CS001, same structure
- **ROM3 (IC5):** CE via resistor network, A15 = OE, A16A for extra banking
