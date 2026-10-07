# PC-1600 — placing a tokenised BASIC program into scattered bank memory

**Audience:** an emulator that wants to inject a tokenised BASIC program image directly
into emulated RAM (instead of driving the firmware `LOAD` path), and needs to reproduce
where the real `LOAD` would have put each byte.

**Status of the facts below:** the address‑space geometry and the `NEW` reserve
convention are from the PC‑1600 Technical Reference Manual §2.1/§2.2/§3.12–§3.13 and are
solid. The **`ADTBL+n` byte bit‑layout** (§3 here) is reverse‑engineered from the two
worked examples in TRM §3.12.2 — six sample bytes — so bits 3 and 6 are unobserved
(assume 0) and the slot‑nibble / program‑header‑bit reading, while internally consistent
across both examples, is an inference. Everything else is directly documented.

Cross‑refs: `PC-1600-Memory-Architecture.md` §4b (window geometry, `NEW` targets, worked
maps), `PC-1600-Work-Area-Map.md` §4 (the work‑area bytes), `PC-1600-Memory-Bank-Switching.md`
Part 2 (bank table) and Part 6 (`BANKSET`/`BANKREAD`, boot config).

---

## 1. Memory model recap

The SC‑7852 (Z‑80) address space is four fixed 16 KB pages; each page selects one of 8
global 16 KB banks via I/O port 31H:

| Page | Z‑80 range | Port 31H field | Relevant banks |
|---|---|---|---|
| 0 | 0000–3FFF | b0 | bank 0 = internal ROM |
| 1 | 4000–7FFF | b3:b2:b1 | internal ROM / hidden ROM |
| 2 | **8000–BFFF** | **b6:b5:b4** | **bank 0/1 = Slot 1, bank 2/3 = Slot 2** |
| 3 | C000–FFFF | b7 | bank 0 = internal 16 KB RAM |

The BASIC user area ("S0") is built from:

- **module RAM** in the page‑2 window (8000–BFFF) of banks 0/1 (Slot 1) and/or 2/3 (Slot 2),
- followed by **internal RAM** at C000–EFFF of bank 0 (F000–FFFF is the fixed work area,
  never part of S0).

Default resting mapping (always true at a quiescent point such as "just booted, before
`RUN`"): Slot 1 ↔ banks 0/1 @ 8000–BFFF, Slot 2 ↔ banks 2/3 @ 8000–BFFF, internal ↔
bank 0 @ C000–FFFF. A Slot‑2 module's live vertical bank (port 28H) is **0**.

Sub‑16 KB modules are **top‑justified** in their 16 KB window (TRM §3.12.1):

| Module | Size | Window base | Notes |
|---|---|---|---|
| CE‑151 | 4 KB | **B000** | Slot 1 only |
| CE‑155 | 8 KB | **A000** | Slot 1 only |
| CE‑159 | 8 KB | **A000** | Slot 1 only (program module) |
| CE‑161 | 16 KB | **8000** | Slot 1 or 2 |
| CE‑1600M | 32 KB | **8000** (both its banks) | Slot 1 or 2 |
| CE‑1620M | 32 KB ROM | **8000** | Slot 1 or 2 |
| any ≥16 KB bank | — | **8000** | a full bank |

The 8000..(base‑1) part of a small module's window is dead address space.

**How the ROM finds the base.** It never computes one from a module size. The module map
(P1‑B3 `67B2`–`6892`) tries fixed addresses with `MEMORYCHK` (018DH: writes and reads back
8 bytes) and takes the first one with RAM:

| Slot | Tried in order | Area |
|---|---|---|
| Slot 1 (bank 0) | 8000H → A000H → B000H | base … BFFFH |
| Slot 2 (bank 2) | 8000H → A000H (no B000H case) | base … BFFFH |
| bank 1 / 3 (2nd half of a 32 KB module) | 8000H only (`SMAPPAIR` 6898H) | 8000H … BFFFH |

So 8000H, A000H and B000H are the only bases, and the area always ends at BFFFH. A module
whose RAM is not top‑justified (e.g. 8000–9FFF only) is one the ROM cannot use either.
CE‑151 and CE‑155 reach B000H / A000H through the Slot 1 S1–S3 remap the boot probe sets in
Port 3CH (P0‑B0 `03CF`; `PC-1600-Memory-Bank-Switching.md` Part 4).

---

## 2. Two cases

| Case | How to tell | Program storage |
|---|---|---|
| **Extension memory** (the `LOAD` a big program case) | `S1MTb` and `S2MTb` are **not** in 1..5 (typ. `FEH`). Modules are folded into S0. | **One** tokenised text stream, linearised across S0's whole bank list, then into internal RAM. |
| **Program modules** | `S1MTb..S1MBb` and/or `S2MTb..S2MBb` are valid 1..5 indices. | **Independent** streams: S1's program in `ADTBL[S1MTb..S1MBb]`, S2's in `ADTBL[S2MTb..S2MBb]`, the active S0 program in `ADTBL[S0MTb..5]` + internal. Each region's leading bank carries its own 8‑byte header + 189‑byte reserve. |

The algorithm below is written for the **extension‑memory** case. For a program module,
run the same segment‑list + cursor logic on that region's `ADTBL[xMTb..xMBb]` slice, with
the leading bank's usable base at `window_base + 197` (no `NEW` ML term unless `NEW "Sx:"`
was applied to it).

---

## 3. The work‑area bytes

| Addr | Name | Meaning |
|---|---|---|
| F02AH | `S0MTb` | 1‑based `ADTBL` index where S0's bank list starts; S0 runs from there through entry 5. Not 1..5 ⇒ S0 is internal‑RAM‑only. |
| F016H / F018H | `S1MTb` / `S1MBb` | first / last `ADTBL` index of S1's list *when S1 is a program module*; `FEH` (≠1..5) ⇒ not a program module. |
| F020H / F022H | `S2MTb` / `S2MBb` | same for S2. |
| F1D6H..F1DAH | `ADTBL+1` .. `ADTBL+5` | five 1‑byte bank descriptors. |

`ADTBL+n` byte:

```
byte == 0x00   -> entry unused
else:
  bit 7        1 = LEADING bank of a program-module region (holds header + 189-byte reserve)
  bits 5..4    global bank number 0..3      bank = (byte >> 4) & 3
  bits 3..0    physical slot: 1 = Slot 1, 2 = Slot 2   (redundant with bank; use as a check)
```

Decoded TRM examples:

- **Ex.1** (CE‑159 S1 + CE‑1600M S2, extension memory): `S0MTb=03`, `S1MTb=S2MTb=FEH`,
  `ADTBL = 00 00 01 22 32` → S0 banks = `[0, 2, 3]`, then internal. Fill order = slice order.
- **Ex.2** (CE‑1600M S1 + CE‑161 S2, program modules): `ADTBL = 00 81 11 A2 00`,
  `S1MTb/S1MBb = 02/03` (`81`=bank0 leading, `11`=bank1), `S2MTb/S2MBb = 04/04` (`A2`=bank2
  leading), `S0MTb=05` (`00` → S0 internal‑only).

> If your emulator boots the real firmware, these bytes are already maintained for you —
> just read them. Only synthesise them if you inject into a state the firmware didn't
> build; the boot memory‑config routine / `NEW` / `INIT` are what normally write them.

---

## 4. Build the ordered S0 segment list

```
FUNCTION window_base(bank):
    # the ROM's own probe (P1-B3 67B2-6892): first base with RAM, area to BFFF
    candidates = { 0: [0x8000, 0xA000, 0xB000],    # Slot 1
                   2: [0x8000, 0xA000],            # Slot 2
                   1: [0x8000], 3: [0x8000] }[bank] # 2nd half of a 32 KB module (SMAPPAIR 6898)
    FOR base IN candidates:
        IF has_ram(bank, base): return base           # MEMORYCHK at base
    return NONE                                       # no module RAM in this bank

segments = []                       # {bank, base, top}  physical bank + inclusive Z-80 addr range
IF 1 <= S0MTb <= 5:
    FOR n IN S0MTb .. 5:
        b = ADTBL[n]
        IF b == 0: CONTINUE
        bank = (b >> 4) & 3
        segments.append({ bank: bank, base: window_base(bank), top: 0xBFFF })
# internal RAM is ALWAYS the final S0 segment
segments.append({ bank: 0, base: 0xC000, top: internal_ceiling() })
```

`internal_ceiling()` = `0xEFFF` minus the current variable‑area size at the top of
internal RAM (0xF000–0xFFFF work area is off‑limits). If you are injecting into a freshly
`NEW`'d machine, variables are empty and the ceiling is `0xEFFF`.

Subtract the reserved region(s) from the segment base(s):

```
# header + reserve sits at [RAM start] = bottom of the first S0 segment
segments[0].base += 197                                   # 0xC5

# NEW "S1:",e1  -> ML block at the bottom of the first S0 segment (if that segment is the S1 module)
segments[0].base += max(0, ml_expr("S1") - 197)

# NEW "S0:",e0  -> ML block at the bottom of the internal segment
internal_seg = segments[-1]
IF ml_expr("S0") > 0:
    internal_seg.base += max(0, ml_expr("S0"))           # note: NEW "S0:" already includes its own 0xC5;
                                                         # internal_seg has no separate 197 subtracted
```

(`ml_expr("Sx")` = the `<expr>` value passed to `NEW "Sx:",<expr>`, i.e. wanted size +
0xC5; 0 if no `NEW` for that region. `NEW "S2:"` similarly bites into whichever segment
is the Slot‑2 low bank.)

---

## 5. Place the tokenised image

The tokenised program is a chain of line records with no embedded absolute addresses
(`[line# hi][line# lo][len][body…][0x0D]`, `len` = body + 1), terminated by `0xFF`. Nothing
inside points at an address, so placement is a byte copy — **but lines do not straddle two
module banks.** The ROM's `LOAD` line storer (`LOADSTORE`, rom3b `7074H`) and the line editor
both follow this rule, confirmed on the ROM in Calc-U-1600 (typed vs loaded, byte for byte):

- A line goes into the current bank only if **2 bytes stay free after it**
  (`addr + record + 2 ≤ top`; `top` = BFFFH for a module bank).
- If it doesn't fit and another module bank follows, the ROM writes a two-byte
  **bank-end mark `00 00`** (a line number 0) at `addr` and continues at the next bank's
  base (8000H).
- **ADTBL entry 5's module bank runs straight on into internal RAM** (BFFFH → C000H are
  contiguous Z-80 addresses), so there a line *may* straddle, with no mark. That is also why
  internal RAM counts as ADTBL index 5 in `F02CH`.
- In the last segment (internal RAM, or the last bank of an S1/S2 program module) the same
  test decides between storing and error 16H (out of memory), against the area limit.

```
seg, addr = 0, segments[0].base
FOR each record IN program:
    WHILE addr + len(record) + 2 > run_top(seg):     # run = segments joined by contiguous seams
        IF no segment after this run: RAISE "out of memory"
        store(addr, 00 00); seg = next run's first segment; addr = segments[seg].base
    store(addr, record); addr += len(record)
store(addr, FF)                                      # end mark; prog_end = (segment of addr, addr)
```

Then update the interpreter's own pointers so it agrees with the bytes:

- **BASIC text lower bound** — the pointer `NEW` writes. Do **not** move it; ensure your
  synthesised `ADTBL`/`NEW` state already produced `segments[0].base`.
- **BASIC text end / variable‑area base** — set to `prog_end`, in whatever representation
  the interpreter uses (a logical offset, or a `(bank,addr)` pair — the same
  representation as the `CURRENT TOP` / `VARIABLE POINTER` group at F89E/F89F and
  F899/F89A, `PC-1600-Work-Area-Map.md` §3.5).
- Reset the line‑search cache (`SEARCH ADDRESS/LINE/TOP`, `CURRENT LINE/TOP` at
  F8A6–F8AB / F89C–F89F) to the defined post‑`LOAD` state (typically pointing at the
  first line / cleared).

**The ROM's own sequence.** The firmware's `LOAD` finish (`LOADEND`, rom3b `70E1H`) is the
reference for this step, and is listed in `PC-1600-Work-Area-Map.md` §3.5: `FFH` end mark;
for S0 `F867` = end and **`F02CH` = end bank** (independent of `F02BH`), `F899` reset when
it is ≤ the new end; for S1/S2 the descriptor end triple and the module header's +5/+6
(§4.5 there); then `PRGADR`, `F89E` = start, `F1C1H` = `FE3EH`. An injector that mirrors
these steps leaves the work area as a real `LOAD` would; one that skips `F02CH` is right
only while the end stays in the start bank.

---

## 6. `store_phys` — direct copy vs. simulated store

**You do not need to go through the BASIC `POKE` command, and `SLOT1MAP` / `SLOT2MAP`
need no special handling.** `SLOT1MAP` (IOCS 0196H) and `SLOT2MAP` (0199H) are
remaps that make a slot's RAM *also* visible at Bank 1 of page 0 or page 1
(`PC-1600-Memory-Bank-Switching.md` Part 2). No ROM bank calls them; they exist for user
programs, and they **alias** SRAM, never **relocate** it. At the point you inject,
the mapping is the default and the `(bank, addr)` pairs from §5 name the correct SRAM
cells regardless. The only persistent selector that matters is **port 28H = 0** (Slot‑2
vertical bank) for a vertical‑banked Slot‑2 module used as S0.

Pick the implementation that matches your memory model:

| Memory model | `store_phys(bank, addr, byte)` |
|---|---|
| **Per‑physical‑bank arrays** (`ram_s1[0x8000]`, `ram_s2[…]`, `ram_int[0x4000]`) | Direct write. `bank∈{0,1}` → `ram_s1[bank*0x4000 + (addr-0x8000)]`; `bank∈{2,3}` → `ram_s2[(bank-2)*0x4000 + (addr-0x8000)]` at vbank 0; `bank==0 && addr>=0xC000` → `ram_int[addr-0xC000]`. `SLOTxMAP` irrelevant by construction. |
| **Flat 64 K + bank registers + `decode()`** | Save ports 31H/28H/3DH. Set port 31H page‑2 field (bits 6‑4) = `bank`; set port 28H = 0; leave `SLOTxMAP` normal. Call the CPU's low‑level memory‑write (the routine behind `LD (HL),A`), **not** BASIC `POKE`. Restore the saved ports afterwards. |

Prefer the direct form where possible — it is deterministic and does not perturb emulated
I/O state.

---

## 7. Worked example (TRM §3.12.2 Example 1)

Config: CE‑159 (8 KB) in Slot 1, CE‑1600M (32 KB) in Slot 2, both extension memory, no
`NEW` ML reservation. `S0MTb=3`, `ADTBL[3..5] = 01, 22, 32`.

```
segment 0: bank 0 (Slot 1, CE-159)   base 0xA000  top 0xBFFF   -> +197 -> 0xA0C5   (7 995 B)
segment 1: bank 2 (Slot 2, CE-1600M) base 0x8000  top 0xBFFF                    (16 384 B)
segment 2: bank 3 (Slot 2, CE-1600M) base 0x8000  top 0xBFFF                    (16 384 B)
segment 3: bank 0 (internal)         base 0xC000  top 0xEFFF   (~11 800 B, less variables)
                                                               Sum ~= 52 500  ~= MEM 52 794
```

A program of 100-byte lines: 79 lines fit in segment 0 (`0xA0C5 + 100·k + 102 ≤ 0xBFFF` for
k = 0…78); the ROM then writes `00 00` at `0xBFA1` and line 80 starts at `(bank 2, 0x8000)`.
No record is split between banks.

---

## 8. Assumptions / limits

- Internal RAM (C000–EFFF, bank 0) is assumed to be **always the last** S0 segment;
  module extension banks always precede it in `ADTBL` order. Consistent with both TRM
  examples; no counter‑example known.
- The `ADTBL` slice order equals the physical fill order (TRM Example 1 states it).
- Bits 3 and 6 of an `ADTBL` byte are never set in the available samples — if you ever
  read one set, log it; the meaning is unknown.
- With simultaneous `NEW` reservations in more than one region, each affected segment has
  a hole at its base; the code in §4 handles the S1‑first and S0‑internal holes. A
  `NEW "S2:"` hole lands in whichever segment is the Slot‑2 low bank — apply the same
  `base += ml_expr` adjustment there.
- Program‑module regions (§2): repeat §4–§5 per region on its `ADTBL[xMTb..xMBb]` slice;
  the leading bank's usable base is `window_base + 197`.
