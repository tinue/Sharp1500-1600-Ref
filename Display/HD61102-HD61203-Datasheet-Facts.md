# HD61102 / HD61203 Datasheet Facts

Summary: Hitachi HD61102/HD61203 datasheet facts: registers, instruction set, read pipeline, duty and scan, reset, timing.
Scope: PC-1600
Sources: PC-1600 Technical Reference Manual §7.3 (LCD hardware), read from the German Systemhandbuch scan. §3.1 (IOCS routines for LCD, work area, character font) and §10.1 (character-code table) pending. §3's port/command decode …
Status: cited

> Split from `PC-1600-Display-HD61202.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: Scope, §1, §2, §3, §4, §5, TODO → [PC-1600-Display-Hardware.md](PC-1600-Display-Hardware.md); §6, §7, §8 → [PC-1600-Display-IOCS.md](PC-1600-Display-IOCS.md).

## 9. Controller datasheet facts (Hitachi HD61102 / HD61203, 1989)

**Sources:** Hitachi *HD61102 Dot Matrix LCD Graphic Display Column Driver* (data book
pp. 261–290) and *HD61203 Dot Matrix LCD Graphic Display Common Driver* (pp. 361–387),
scans (sources HITACHI-HD61102 and HITACHI-HD61203 in sources/sources.yaml). The HD61102 sheet names the **HD61103A** as its common
driver. The HD61203 sheet names the **HD61202** as its column driver. Both use the same
FRM/CL/M/φ1/φ2 interface, and the PC-1600 uses the HD61102 + HD61203 pair (§2). Anything
marked *inferred* combines a datasheet fact with the PC-1600 wiring. The datasheets do not
state it directly.

### 9.1 HD61102 register selection

The chip is selected only when **CS1 = L, CS2 = L, CS3 = H** (active levels as §3 already
lists them). D/I and R/W then pick one of four operations (datasheet Table 1):

| D/I | R/W | Operation | PC-1600 port offset (§3) |
|---|---|---|---|
| 0 | 0 | write instruction | +0 (ROM-trace confirmed) |
| 0 | 1 | read status | +1 (ROM-trace confirmed) |
| 1 | 0 | write display data | +2 (ROM-trace confirmed) |
| 1 | 1 | read display data | +3 (*inferred*: it is the only operation left) |

This matches D/I following port-address bit 1 and R/W following bit 0 or the Z-80's
read/write direction. The datasheet makes +3 = data read the only consistent choice,
and ROM code confirms it (bank 6 `81E8H`/`8AA2H` read 57H/5BH, §9.3).

On a write, data is latched at the **falling edge of E**. On a read, data is driven while
E = H. RST and ADC act whether or not the chip is selected.

**Inferred:** a *read* from the "both controllers" block (50H–53H) would make IC2 and IC3
drive DB0–7 at the same time. Only writes (broadcast instructions such as the ROM's first
`3EH` display-off) make sense there.

### 9.2 Instruction set (datasheet Table 2)

| Instruction | Code (D/I=0, R/W=0) | Effect |
|---|---|---|
| Display ON/OFF | `0011111D` = **3EH / 3FH** | D=1 on, D=0 off. RAM and registers are unchanged. |
| Display start line | `11AAAAAA` = **C0H–FFH** | Sets the RAM line (0–63) shown on the top common line (COM1). Used for scrolling. |
| Set page (X address) | `10111AAA` = **B8H–BFH** | Page 0–7. The X counter does **not** auto-increment. |
| Set Y address | `01AAAAAA` = **40H–7FH** | Column 0–63. Auto-increments after each data read or write and wraps 63 → 0. |

Hitachi's naming is the reverse of the screen's: **"X" = page (vertical, 8-dot bands)**
and **"Y" = column**. The address counter is 9 bits: 3 page bits and 6 column bits.
512 bytes = 64 columns × 8 pages.

**Status byte** (D/I=0, R/W=1):

| Bit | Meaning |
|---|---|
| DB7 | **BUSY**: 1 = executing, and only Status Read is accepted |
| DB6 | 0 |
| DB5 | **ON/OFF**: 1 = display **off**, 0 = on (reverse of the instruction's D bit) |
| DB4 | **RESET**: 1 = still initialising after RST |
| DB3–DB0 | 0 |

The ROM's busy-wait at `IN A,(55H)` / `IN A,(59H)` is this read. The datasheet says to
wait for DB7 = 0 before every instruction, and for DB4 = 0 as well after a reset. The
ROM tests **DB7 only**, on both chips in one loop (bank 0 `0807H`, bank 6 `817FH`):
`IN A,(59H) / RLA / IN A,(55H) / RRA / AND C0H / JP NZ,loop`. DB5 and DB4 are never
looked at.

**Busy time:** 1/f_CLK ≤ T_BUSY ≤ 3/f_CLK, where f_CLK is the φ1/φ2 frequency.

### 9.3 Read pipeline: one dummy read after setting an address

A data read returns the **output register**. The RAM cell at the current address is
latched into that register at the falling edge of E, and then Y increments. After a
Set-page or Set-Y instruction, the **first data read returns stale data**. The byte at
the new address arrives on the *second* read (datasheet Fig. 5: set address → dummy read
→ data N → data N+1 …). An emulator of offset +3 must model this. Writes need no dummy
access.

**ROM confirmation:** bank 6 `81E8H` is `PUSH AF / CALL 817FH (busy-wait) / IN A,(C) /
POP AF / RET`, a busy-wait plus a discarded read. The block reader at `8AA2H` calls it
and then reads four bytes (`IN E/D/L/H,(C)`) with a busy-wait before each one. The
scroll/copy routines at `8A2CH` (IC2, C = 5BH) and `8A66H` (IC3, C = 57H) read four bytes
that way and write them back one page further on (`8ABAH`).

### 9.4 Display scan, duty and why the right block works (HD61203)

- The HD61203 has **64 common outputs X1–X64** and an internal timing generator. In
  **master mode** (M/S = Vcc) it supplies **φ1, φ2, FRM, CL (via CL2) and M** to the
  column drivers. The HD61102 has no timing source of its own. **Confirmed** as the
  PC-1600's mode: the Service Manual key circuit diagram (printed p. 43) ties M/S to VCC.
- Duty is set by pins DS1/DS2: 1/48 (L,L), **1/64 (L,H)**, 1/96 (H,L), 1/128 (H,H). The
  TRM's 1/64 duty (§1) is **DS1 = GND, DS2 = Vcc**, which the key circuit diagram
  shows. So there is one HD61203 and all 64 commons are in use.
- At 1/64 duty each HD61102's 6-bit **Z counter** steps through RAM lines 0–63, one per
  common. FRM reloads it from the display-start-line register. Common X*n* therefore shows
  RAM line (start + *n* − 1) mod 64 on every segment output.
- **Consequence for §2** (*inferred* from the scan rule plus the TRM block diagram): with
  start line 0, commons X1–X32 show lines 0–31 (pages 0–3) and X33–X64 show lines 32–63
  (pages 4–7). The right 28-dot block is wired to X33–X64 and to 28 of IC2's segment
  outputs. So it displays **pages 4–7 of 28 IC2 columns**. These are separate RAM bits
  from the left block's pages 0–3, on shared physical Y pins. That removes the need for
  92 outputs on one chip, which the `Y1–Y66` label seemed to imply. Which 28 of IC2's 64
  column addresses are used depends on its ADC pin (§9.5), which the TRM does not give.
- The same rule places the status symbols. Commons X49–X64 are RAM lines 48–63, which is
  **pages 6 and 7 = 16 bits of one column** on the segment line that feeds the status row
  (IC3, the TRM's `Y6f`, probably Y64). That is exactly the "16 symbols" of §1.
  **Resolved from ROM code (§6.3):** the ROM does not pack. B=02H is a third byte, at
  **page 4** of the same column 63. Page 4 is RAM lines 32–39, i.e. commons X33–X40, not
  X49–X64, so the TRM diagram's "X49–X64 into the status row" is incomplete. §9.4.1 has
  the full wiring from the Service Manual.

#### 9.4.1 Status-row wiring (Service Manual key circuit diagram)

**Source:** PC-1600 Service Manual, key circuit diagram, printed pp. 43–44 (PDF pp. 46–47).
It shows the LF7204E glass pinout with the status legend printed under the pins. The
legend strip starts with a **Y64** segment pin, followed by the commons listed below. Pins
between them that belong to the dot matrix (Y16–Y20, Y36–Y45, Y56–Y64, IC3's Y′11–Y′60)
only pass through the connector. The ROM writes the symbols to **IC3** (C = 54H, §6.3), so
that Y64 is IC3's column 63. The sheet uses Y′ for IC3 elsewhere, and the prime is
missing on this pin.

Common X*n* scans RAM line *n* − 1 (start line 0), so each common is one bit of column 63:

| Common | Page | Bit | Legend | SMBLSET |
|---|---|---|---|---|
| X57 | 7 | 0 | BUSY | B=00H b0 |
| X58 | 7 | 1 | SHIFT | B=00H b1 |
| X59 | 7 | 2 | ローマ字→カナ (part) | B=00H b2, "—" in the TRM |
| X60 | 7 | 3 | SMALL | B=00H b3 |
| X61 | 7 | 4 | III | B=00H b4 |
| X62 | 7 | 5 | II | B=00H b5 |
| X63 | 7 | 6 | I | B=00H b6 |
| X64 | 7 | 7 | DEF | B=00H b7 |
| X49 | 6 | 0 | DE(G) | B=01H b0 |
| X50 | 6 | 1 | G(RAD) | B=01H b1 |
| X51 | 6 | 2 | RAD | B=01H b2 |
| X53 | 6 | 4 | RESERVE | B=01H b4 |
| X54 | 6 | 5 | PRO | B=01H b5 |
| X55 | 6 | 6 | RUN | B=01H b6 |
| X33 | 4 | 0 | BATT | B=02H b0 |
| X34 | 4 | 1 | CTRL | B=02H b1 |
| X35 | 4 | 2 | ローマ字→カナ (part) | B=02H b2, "—" in the TRM |
| X36 | 4 | 3 | S | B=02H b3 |

So there are 18 electrodes. Every TRM symbol sits on the common its bit predicts. The
diagram shows no status pin for X52, X56 (page 6 b3, b7) or X37–X40 (page 4 b4–b7).
**KBII (B=02H b7, X40) therefore has no electrode of its own**, which fits the ROM
folding it into S. The "ローマ字→カナ" caption is instead two electrodes on **X35 and
X59**, placed after S in pin order. The diagram doesn't say which part of the caption
each one lights.

With the western "new" ROM, a probe through boot, KBII, SHIFT, CTRL and MODE never set
bit 2 of the page-4 shadow (F3C6H) or the page-7 shadow (F64EH). The romaji→kana
electrodes stay dark on that machine unless a program writes those bits (SMBLSET B=02H
keeps bit 2: `AND 77H`).
- **Start line moves everything together.** A non-zero start line rotates the whole
  64-line scan, including the status symbols and the right block. The ROM sets start
  line 0 (`C0H`, §3).

### 9.5 ADC pin (column direction)

The ADC pin is tied to Vcc or GND and must never change while running (changing it
corrupts registers and RAM).

- **ADC = H:** Y address 0 → pin Y1, 63 → Y64.
- **ADC = L:** Y address 0 → pin Y64, 63 → Y1.

The TRM does not show IC2's or IC3's ADC level. §4's "column = x within its block"
assumes ADC = H on both.

### 9.6 Reset

RST = L sets **display OFF** and **start line 0**. While RST is low only Status Read is
accepted. According to the datasheet, a reset *during operation* may destroy all RAM and
registers except the ON/OFF register. That fits the TRM's VGG note (§1): the HD61102s
stay powered and keep their RAM across auto-power-off, so they must not be reset on
wake-up.

### 9.7 Clocking and timing

- **HD61203 oscillator:** fosc = 2 × f(φ1/φ2). For a **70 Hz frame** the sheet gives
  fosc = **430 kHz** or **215 kHz**, selected by the FS pin. (The printed text says
  "FCS" in the FS row, apparently a typo.) An external clock goes into **CR** with R and C
  left open (range 50–600 kHz, duty 45–55 %).
- **PC-1600** (**confirmed**, Service Manual key circuit diagram, printed p. 43 / PDF
  p. 46): CK0 (CN1-40) drives the HD61203's **CR** pin with **R and C open**, which is
  the external-clock setup. The other pins are M/S, FCS, STB, SHL and DS2 = VCC, and FS,
  DS1, CL1 and TH = GND. So CK0 = **217 kHz** (§1) is the 215 kHz case, which gives
  **φ1/φ2 ≈ 108.5 kHz** and a frame rate of about **70 Hz**. It is inside the HD61102's φ limits (cycle 2.5–20 µs; 108.5 kHz ≈ 9.2 µs).
  It follows that the HD61102s get **no clock while port 37H bit 4 = 0**, so busy never
  clears and the display does not refresh. The boot ROM must enable CK0 before it
  polls busy.
- **HD61102 busy time** at 108.5 kHz is about **9.2–27.6 µs** per instruction or data
  access (§9.2's formula at the confirmed φ).
- **MPU bus (HD61102):** E cycle ≥ 1000 ns, E high ≥ 450 ns, E low ≥ 450 ns, address
  setup ≥ 140 ns, write data setup ≥ 200 ns, read data delay ≤ 320 ns. These are the
  limits the SC-7852's delayed `E` strobe (§3) has to meet.

### 9.8 Power (for context)

| | HD61102 | HD61203 |
|---|---|---|
| Logic VCC | 5 V ± 10 % | 5 V ± 10 % |
| VEE | 0 to −10 V; LCD drive span ≤ 15.5 V | VCC − VEE = 8–17 V |
| Drive levels | V1/V2 select, V3/V4 non-select | V1/V2 select, V5/V6 non-select |
| Power | ≤ 2 mW, ≤ 100 µA at 1/64 duty with φ = 250 kHz | ≈ 5 mW |

The PC-1600's VEE of about −8.5 V gives VCC − VEE ≈ 13.5 V, inside both ranges. The
contrast control sets the V1…V6 bias resistor chain; for 1/9 bias the sheet uses
4R1 + R2 : R1 = 9 : 1 (e.g. R1 = 3 kΩ, R2 = 15 kΩ). The PC-1600's actual values are not
known.
