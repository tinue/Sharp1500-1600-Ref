# PC-1600 Display Hardware

Summary: Panel, HD61203 + 2xHD61102 topology, I/O ports 50-5BH, frame-buffer model, PC-1500 compatibility, open items.
Scope: PC-1600
Sources: PC-1600 Technical Reference Manual §7.3 (LCD hardware), read from the German Systemhandbuch scan. §3.1 (IOCS routines for LCD, work area, character font) and §10.1 (character-code table) pending. §3's port/command decode …
Status: cited

> Split from `PC-1600-Display-HD61202.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §6, §7, §8 → [PC-1600-Display-IOCS.md](PC-1600-Display-IOCS.md); §9 → [HD61102-HD61203-Datasheet-Facts.md](HD61102-HD61203-Datasheet-Facts.md).

## Scope

The PC-1600 LCD hardware: panel, controller topology, the I/O interface, and the
frame-buffer addressing model. The BASIC/IOCS drawing path (character font, `GPRINT`,
cursor, graphics primitives) comes from TRM §3.1 and §10.1 and is **not yet
transcribed** — see "TODO" below.

**Sources:** PC-1600 Technical Reference Manual §7.3 (LCD hardware), read from the German
Systemhandbuch scan. §3.1 (IOCS routines for LCD, work area, character font) and §10.1
(character-code table) pending. §3's port/command decode additionally sourced from a
headless trace of the genuine PC-1600 boot ROM (`romI-0.bin`/`romIV-6.bin`) executing
against a from-scratch SC-7852 emulation, 2026-08-30 — the real firmware's own I/O
behavior, not a description of it, so treated as primary alongside the TRM.
Chip-level behavior (instruction set, status bits, read pipeline, duty/clock options) from
the **Hitachi HD61102 and HD61203 datasheets (1989 data book)**, §9 below.

---

## 1. Panel

- Module: **LF7204E**.
- **Graphics area: 156 × 32 dots.** Plus a **status-symbol line of 16 symbols** above it.
- Drive: **1/64 duty**.
- LCD base clock: **217 kHz**, supplied from the SC-7852 `CK0` pin (pin 56). `CK0` is
  emitted only while **bit 4 of Z-80 I/O port 37H = 1** — 0 at power-on, set by the boot
  routine when it enables the LCD (`PC-1600-SC7852-Pinout-and-Control-Regs.md` §6, pin 56).
- Negative bias from the **VEE** rail (≈ −8.5 V, `PC-1600-Machine-Overview.md` §5).
- `VGG` keeps the HD61102s' display data alive across auto-power-off while the machine
  stays on.

### 1.1 The status-symbol line is fixed-legend segments, not dot-matrix text

**Confirmed 2026-08-30 from a photo of a genuine PC-1600 unit** (the physical hardware
itself — as primary a source as the TRM). The 16 status positions are **printed legend
text permanently etched on the LCD glass**, each with its own small individually-drivable
segment, the same style as a scientific calculator's fixed "DEG/RAD/GRAD" mode strip —
**not** glyphs the firmware draws into the 156×32 dot-matrix graphics area the way
character/graphics mode does. Left to right, the printed legend reads:

```
BUSY  SHIFT  S[ローマ字→カナ]  SMALL  DEGRAD  RUNPRO  RESERVE  DEF  I II III  CTRL  BATT
```

("ローマ字→カナ" = "romaji→kana", a Japanese input-mode toggle, printed as part of the
combined **S** legend.) Several printed labels appear to be single fixed captions with
**two selectable positions each** rather than sixteen independent icons (matching
"DEGRAD" being one legend that shows either DEG or RAD is active, "RUNPRO" showing
either RUN or PRO, and "I II III" being three positions sharing one concept — likely a
memory-area indicator): this is consistent with a "16 symbols" count without there being
sixteen visually-separate icons. **This resolves why the DEG/PRO/I indicators an actual
boot shows never appear in an emulation that only ever draws into the 156×32 dot-matrix
area**: they are architecturally a completely separate display region from that area,
driven by whatever discrete segment lines exist for this strip (the LR38041 pin table has none) —
not more page/column-addressed HD61102 writes. **Still needed**: the actual per-segment
port/bit mapping (which `SMBLSET` bit lights which named position) — TRM §3.1 p28's own
bit map, not yet transcribed (see this doc's TODO).

## 2. Controller topology (TRM §7.3)

- **1 × HD61203** — common (row) driver. Provides the X (common) outputs across the
  panel: the 32 graphics rows on each side plus the status line.
- **2 × HD61102** — segment (column) drivers, labelled **IC2** and **IC3** on the board.

The 156-dot width is split into three column blocks: **64 + 64 + 28 = 156**, confirmed
2026-08-30 from the TRM's own LCD block diagram (Systemhandbuch, LCD: LF7204E), which
gives the exact internal Y/X wiring, not just the block sizes:

- **Left 64-dot block** (screen columns 0–63): driven by **IC2**'s `Y1–Y64` outputs.
- **Centre 64-dot block** (columns 64–127): driven by **IC3**'s own `Y1–Y64` outputs,
  labelled independently in the diagram.
- **Right 28-dot block** (columns 128–155): driven by `Y1–Y28`. IC2's label in the
  diagram reads `Y1–Y66`. The right block shares physical segment pins with the left
  block's first 28 columns, but it is **not** a duplicate of them. At 1/64 duty every
  HD61102 scans all 64 of its RAM lines, one per HD61203 common (datasheets, §9.4). The
  right block sits on commons `X33–X64`, so its 28 columns show RAM lines 32–63
  (pages 4–7) of IC2. The left block shows lines 0–31 (pages 0–3) of the same outputs on
  `X1–X32`. The right block's pixels are therefore separate and individually
  addressable, and no chip needs extra output pins.

Row (common) driving: **1 × HD61203** supplies the panel's X (common) outputs — `X1–X32`
into the left block, `X1–X32` into the centre block (IC3's own, a second/independent
32-line group despite the same numbering), and `X33–X64` into the right block. Two
further connections feed the **status-symbol line specifically**, distinct from the main
32-row screen's own addressing: IC3's `Y6f` pin, and HD61203's `X49–X64` common-line
group — both drawn in the diagram entering the panel at the status-line row, not the
32-dot screen body. This is consistent with (though doesn't fully resolve) `PC1600StatusLine`
being a separate mechanism from the graphics-area HD61102 ports — see §1.1 above; the
status line's own *software-side* port/bit protocol (which `SMBLSET` value lights which
segment) is still not given by this diagram and remains open (§6.3/TODO).

## 3. I/O interface

The HD61102s sit in the Z-80 I/O space at **50H–5BH** (6800-family bus via the SC-7852
`E` strobe, pin 60, which fires on any I/O access to 40H–5FH — issued a half-cycle after
`IORQ`). Each HD61102 has three chip-select inputs **CS1#, CS2#, CS3**, and is selected
only when **all three** are asserted. The board wires each CS to a different low
address bit so the two controllers (and the register-select within each) decode from the
port number:

| HD61102 CS pin | driven from, IC2 | driven from, IC3 |
|---|---|---|
| CS1# | A2 | A3 |
| CS2# | A5 | A5 |
| CS3 | A4 | A4 |
| I/O port range that selects it | 50H–53H and 58H–5BH | 50H–53H and 54H–57H |

(The 50H–53H overlap in the source table is as printed; the SC-7852 I/O-map page renders
the split as "50H = HD61102 (IC2)+(IC3), 58H = IC3, 5BH = IC2" — i.e. within 50–5FH the
A2/A3/A4/A5 combination picks controller + instruction/data + which half.)

**Command/data/status port assignment within each 4-port block, confirmed 2026-08-30 by
a headless trace of the genuine PC-1600 boot ROM (`romI-0.bin`/`romIV-6.bin`) executing
against a from-scratch SC-7852 emulation** (a primary source: the actual Sharp firmware
running, not a secondary description of it): within a controller's 4-port block (IC3 =
54H–57H, IC2 = 58H–5BH, "both" = 50H–53H), the **command register and the data register
are two different ports, not one port with a D/I-selecting bit as this doc previously
guessed**. The boot ROM was observed writing exclusively to the block's first and third
port (offset 0 and offset 2 from the block's base — e.g. 54H and 56H for IC3) and reading
exclusively from the block's second port (offset 1 — e.g. 55H for IC3, matching the
already-documented busy-wait at `IN A,(55H)`/`IN A,(59H)`, §7 below and
`PC-1600-SC7852-Z80.md` §5.2's cause list is unrelated to this): never a write to
offset 1/3, never a read of offset 0/2. So:

| Offset from block base | Direction | Register |
|---|---|---|
| +0 | write | command |
| +1 | read | status |
| +2 | write | data |
| +3 | read | data (not in the boot trace, but confirmed from ROM code: bank 6 `81E8H`/`8AA2H` read with `IN r,(C)` at C = 57H/5BH, §9.3) |

Within the command register, three command-byte ranges were directly observed being
written by the real ROM and, once decoded this way, produced a genuinely-lit real pixel
in a from-scratch emulation running that same ROM (also a primary-source result — the
effect of running the actual firmware, not a guess): **0x3E = display off / 0x3F =
display on** (bit 0 selects — the ROM's very first-ever display write in a cold-boot
trace is `0x3E` to the "both controllers" port, an ordinary display-off init step),
**0xB8–0xBF = set page address** (low 3 bits = page 0–7, e.g. `0xBC`/`0xBE`/`0xBF`
observed = pages 4/6/7), and **0x40–0x7F = set column address** (low 6 bits = column
0–63, e.g. `0x7F`/`0x40` observed = columns 63/0). A fourth range, **0xC0–0xFF = set
display start line**, was also written by the ROM (`0xC0` observed) but its effect was
not independently exercised/confirmed by this trace.

## 4. Frame-buffer / addressing model

Standard HD61102: 64 columns × 8 pages of 8 bits per controller; a byte written to a
(page, column) cell is a vertical run of 8 pixels, LSB at the top. The PC-1600's
156×32 graphics area is 4 pages tall (32 rows) spread across the three column blocks /
two controllers as in §2. A pixel at (x, y) maps to: controller = block(x); page =
y >> 3; column = x within its block; bit = y & 7.

## 5. PC-1500-compatibility (MODE 1)

In MODE 1 the display is restricted to **26 × 1** (only the bottom text line used) and
character codes `&27` / `&5B` / `&5D` are remapped to their PC-1500 meanings. The
mechanism and the open question of how an LH-5803 PC-1500 program's writes to the
literal `&7600–&774F` display-buffer addresses reach these I/O-port-mapped controllers
are in `PC-1600-LH5803-Memory-View.md` §5 (unresolved: hardware shim vs. software shim).
Note the SC-7852 `LHA90` exception (pin 38): an LH-5803 access to 7400H–744FH / 7500H–754FH
physically lands on 7600H–764FH / 7700H–774FH.

## TODO

- ~~SMBLSET's per-symbol-set bit map~~ — resolved 2026-08-30 from the TRM's own SMBLSET
  page (§3.1 p28), see §6.3 above.
- The character-*code* table (glyph assignments) — TRM §10.1. **Not needed by an emulator** (the ROM's own font tables, §8, do the rendering); useful for the program-writing agent.
- Reconcile the `LINE`/`BOX` entry-address vs. the §3.1 example's `CALL &0124`.
- ~~§3's offset 3 (data read)~~ — confirmed 2026-09-26 from ROM code: bank 6
  `81E8H` (busy-wait + discarded dummy read) and `8AA2H` (four reads) at C = 57H/5BH
  (§9.3).
- ~~Status-line RAM mapping~~ — resolved 2026-09-26 from the ROM's symbol writer
  (bank 6 `8220H`): IC3 column 63, pages 7/6/4 + DSPLPTR (§6.3, §9.4). ~~How commons
  X33–X40 reach the status row~~ — Service Manual glass pinout, §9.4.1.
- Which part of "ローマ字→カナ" X35 and X59 each light, and whether a Japanese ROM
  drives them (§9.4.1).
- IC2/IC3 ADC pin levels, and which 28 IC2 column addresses feed the right block (§9.5).
- ~~§2's three-column-block (64+64+28) sizes and the right block's wiring~~ — sizes
  from the TRM block diagram (2026-08-30). The right block is IC2 pages 4–7 on commons
  X33–X64, from the datasheets' 1/64-duty scan (2026-09-26, §9.4).
- The status-symbol line's Y6f/X49-X64 wiring (§2 above) is now confirmed as physically
  separate from the main screen, but its *software* side — which port/value actually
  drives Y6f or selects X49-X64 — is not given by the block diagram and remains open;
  still needs TRM §3.1 p28's own bit map (see the first TODO item above).
