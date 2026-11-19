# PC-1600 Module Window Layout

Summary: Where a module sits in the 8000-BFFF window and how the BASIC/ML area slides; worked max-RAM example.
Scope: PC-1600
Sources: cited inline in the text
Status: cited

> Split from `PC-1600-Memory-Architecture.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §5 → [PC-1600-LH5803-Memory-View.md](../CPU/PC-1600-LH5803-Memory-View.md); §1, §2, §2a, §3, §6, §7 → [PC-1600-Memory-Map.md](PC-1600-Memory-Map.md); §4, §4a → [PC-1600-Program-Areas-and-NEW.md](PC-1600-Program-Areas-and-NEW.md); §8 → [PC-1600-MODE0-MODE1.md](../Firmware/PC-1600-MODE0-MODE1.md).

## 4b. Where a Module Sits in the 8000–BFFF Window, and How the BASIC/ML Area Slides (TRM §3.12–§3.13)

§4 covered the `NEW "Sx:"` *command*; this section adds the two TRM figures that show the *geometry* — **§3.12.1** ("Slots and Memory Modules", TRM p.127) and **§3.13.1** ("Location of Memory Module", TRM p.135) — plus the "no `NEW` yet" starting state, worked as memory maps. These are the third and fourth previously-untranscribed Chapter-2/Chapter-3 figures (the first two are §2.1's dual bank map and §2.1's internal-RAM map, §2–§3 above).

### 4b.1 The four module "locations" A / B / C / D

TRM §3.13.1 names the four 16 KB module apertures — identical to `PC-1600-Gate-Array-and-Chip-Selects.md` Part 1's Slot 1a/1b/2a/2b and §2a's convention-1 table, but with the TRM's own single-letter labels:

| Loc | Z-80 window | Global bank | Slot | Port 31H page-2 field (b6:b5:b4) |
|---|---|---|---|---|
| **A** | 8000–BFFF | Bank 0 | Slot 1, lower 16 KB | `000` |
| **B** | 8000–BFFF | Bank 1 | Slot 1, upper 16 KB | `001` |
| **C** | 8000–BFFF | Bank 2 | Slot 2, lower 16 KB | `010` |
| **D** | 8000–BFFF | Bank 3 | Slot 2, upper 16 KB | `011` |

"Main memory" is always Bank 0's C000–FFFF (internal 16 KB). TRM §3.13.1's capacity→location rule:

| Module size | Slot 1 | Slot 2 |
|---|---|---|
| ≤ 16 KB | → A | → C |
| 32 KB | → A + B | → C + D |
| ≥ 48 KB | **cannot be used** | → C + D (one 32 KB slice), rest via Port 28H vertical-bank switching |

### 4b.2 Small modules are top-justified inside their 16 KB location

The single most important detail in the §3.12.1 figure, and the answer to "a CE-155 only covers 8 KB of the window": a sub-16 KB module **occupies the *high* end of location A**, ending at BFFF, with the low part of the window left unmapped (the figure hatches it "not used"). From the figure:

| Module | Size | Slot(s) | Covers (in location A / bank 0) |
|---|---|---|---|
| CE-151 | 4 KB | S1 only | **B000–BFFF** (top 4 KB; its S1/S2 chips at B800/B000 with Port 3CH = 1AH, measured — `PC-1600-Gate-Array-and-Chip-Selects.md` Part 4) |
| CE-155 | 8 KB | S1 only | **A000–BFFF** (top 8 KB) |
| CE-159 | 8 KB (program) | S1 only | **A000–BFFF** (top 8 KB) |
| CE-161 | 16 KB | S1 **or** S2 | **8000–BFFF** (fills the whole location) |
| CE-1600M | 32 KB | S1 **or** S2 | 8000–BFFF **× 2 banks** (A + B, or C + D) |
| CE-1620M | 32 KB EPROM | S1 or S2 | A + B, or C + D |
| CE-1601M | 64 KB | **S2 only** | C + D, one vertical bank live, Port 28H for the rest |

Top-justification is what makes the merge with internal RAM seamless: the module's last byte is BFFF, internal RAM's first byte is C000, so module-then-internal is one gap-free ascending run and BASIC only needs a single `RAM_START` pointer. The unmapped low part of the window (8000–9FFF for a CE-155, 8000–AFFF for a CE-151) is simply dead address space — not counted by `MEM`, not usable.

TRM §3.12.1's own footnote: *"Even when a memory module is installed in S1 or S2, if it is used as an extension memory, it is referred to as S0."* — i.e. the moment a module's RAM is glued onto the work area, `NEW`/`MEM`/`STATUS` treat it as part of **S0**, not as a separate S1/S2 object. S1/S2 as `NEW`/`INIT`/`TITLE` targets mean "the module *as a program module or RAM file*", a different role (§4a).

### 4b.3 No `NEW` executed yet — the default BASIC-area structure

With no machine-language reservation (after `NEW 0` or the power-on default — plain `NEW` keeps any earlier reservation, §4.1) the **Machine Program Area is empty**: BASIC's program-text pointer sits directly on top of the 197-byte reserve, at `[RAM start] + C5H`. What `[RAM start]` *is* depends on the modules:

**(a) Bare machine, no modules** — `[RAM start]` = C000H (internal RAM base).

```
Z-80 view, Bank 0                       MEM = 11 834
  8000 ┌───────────────────┐ ─┐
       │  open bus          │  │  no Slot 1 module → dead space
  C000 ├───────────────────┤ ─┘
       │ Header      8 B    │  C000–C007
  C008 │ Reserve   189 B    │  C008–C0C4     ┐ 197 B fixed (C5H)
  C0C5 ├───────────────────┤ ◄─ BASIC text start   ┐
       │ BASIC program  ▲  │                       │
       │       ⋮           │  grows up             │ User Area
       │ Variables      ▼  │  grows down from EFFF │ = 11 834 B   (§3.1: with module RAM merged it continues down into the module banks)
  EFFF ├───────────────────┤                       ┘
  F000 │ Work Area (fixed) │  4 KB, F000–FFFF (never moves, §2/§3)
  FFFF └───────────────────┘
```

**(b) CE-155 (8 KB) in Slot 1, used as extension memory** — `[RAM start]` slides down to A000H. The header + 197-byte reserve **move to the module base**; internal RAM's own C000 area becomes plain user space (only one reserve exists — TRM §3.13.2: *"only one header is placed in location A or C"*).

```
Z-80 view                              MEM = 20 026   (= 11 834 + 8 192, PC-1500-RAM-Sizing-and-NEW.md §5.2)
  8000 ┌───────────────────┐  open bus (CE-155 does not reach here)
  A000 ├───────────────────┤ ◄─ [RAM start]
       │ Header + Reserve  │  A000–A0C4  (197 B)
  A0C5 ├───────────────────┤ ◄─ BASIC text start
       │ BASIC program  ▲  │   CE-155 body  A0C5–BFFF  ┐
  C000 ├─ ─ ─ ─ ─ ─ ─ ─ ─ ─┤   (module → internal,     │ one contiguous
       │       ⋮   ▲/▼      │    no gap at BFFF→C000)   │ User Area
  EFFF ├───────────────────┤                           ┘
  F000 │ Work Area (fixed) │
  FFFF └───────────────────┘
```

Same shape for CE-151 (`[RAM start]` = B000H, `MEM` = 11 834 + 4 096) and CE-161 (`[RAM start]` = 8000H, `MEM` = 11 834 + 16 384).

**(c) CE-1600M (32 KB) in Slot 1** — fills locations A **and** B. `[RAM start]` = 8000H (bank 0). The OS leaves the page-2 register on bank 0, so the CPU sees `8000–BFFF(A) → C000–FFFF(internal)` as a flat 32 KB run; the B half (bank 1) is reached by the OS flipping page-2 to bank 1 transparently while walking the program text.

```
                                        MEM = 44 602   (≈ CE-1600M manual's "up to 44,612")
  Bank 0  8000–BFFF  CE-1600M low  (loc A)   header+reserve at 8000H, BASIC text from 80C5H
  Bank 1  8000–BFFF  CE-1600M high (loc B)   ← page-2 flips here transparently
  Bank 0  C000–EFFF  internal RAM (BASIC/vars)
  Bank 0  F000–FFFF  Work Area
```

**(d) Slot 2.** Slot 2's RAM is in **Bank 2/3**, not the default bank, so *something* has to repoint page-2 at Bank 2 and leave it there — and boot-time module detection does exactly that, **for every RAM module**:

- **Flat module (CE-1600M; a CE-161).** Folded into the work area **automatically at reset**, exactly as in Slot 1. `MEM` = 77 370 straight after reset with a CE-1600M in each slot (emulator).
- **Vertical-banked module (CE-1601M, CE-1650M, *superRAM*, 128 KB+).** Also merged **automatically at reset** — its **vertical bank 0** (32 KB) becomes expansion memory; the other vertical banks are RAM-disk space only. `MEM` = 77 370 straight after reset with a CE-1600M in Slot 1 and a CE-1601M in Slot 2 (emulator), and the real-hardware 128 KB Slot 2 + CE-155 test gave 52 794, i.e. a full 32 KB from Slot 2 (`PC-1600-Bank-Switching.md` Part 2).

In both cases `INIT "S2:","M"` is a no-op on a freshly merged module; it only matters to *re-type* a module that is currently a program module (`"P"`) or a RAM disk (`"F"`) back to expansion memory. After the merge the Z-80 map `8000–BFFF(C) → C000–FFFF(internal)` is flat — same picture as (c).

The structural Slot-1/Slot-2 asymmetry (`PC-1600-Bank-Switching.md` Part 2) is only about the *ceiling* — Slot 2 can contribute at most one 32 KB vertical bank to `MEM` regardless of module size — not about whether a command is required: every RAM module auto-merges.

### 4b.4 `NEW "Sx:",<expr>` — the BASIC area sliding "around" the machine area

The Machine Program Area is always carved at the **bottom** of its target region: from `[target base] + C5H` to `[target base] + <expr> − 1` (with `<expr>` = wanted ML size + C5H). The BASIC program text then starts on the byte **above** that block and grows up; variables still grow down from EFFF. So the ML area is a *fixed low anchor* and the BASIC/variable area is what fills the rest of the merged user span — it "slides" upward by exactly the size of whatever ML block(s) you reserved, and the three targets S0/S1/S2 just let you drop that anchor in three different physical places (internal RAM base, Slot 1 base, Slot 2 base) at the same time.

**Worked example (TRM §2.2, p.128 figure): CE-159 in S1 + CE-1600M in S2**, both as program modules, then:

```
NEW "S1:",&1000     → ML area  A0C5H–AFFFH        (Slot 1, loc A)     — BASIC text now starts B000H
NEW "S2:",&5000     → ML area  80C5H–BFFFH (bank2) + 8000H–8FFFH (bank3, no 2nd +C5H)
NEW "S0:",&1000     → ML area  C0C5H–CFFFH        (internal, bank 0)  — BASIC text in internal RAM starts D000H
```

Three independent fixed ML blocks (one per base + C5H); the BASIC program/variable area occupies every user byte *not* in one of them — literally sliding "around" all three. Note `NEW "S2:",&5000` (≈ 20 KB) covers both banks of the one Slot 2 module: `80C5–BFFF` in bank 2, continuing at `8000–8FFF` in bank 3 with **no** second reserve, because it is one allocation, not a new base. It is continuous in logical addresses only — the CPU sees the two parts one at a time at 8000–BFFF (§4.0).

### 4b.5 The load order (TRM §3.12.2 "Work Area used for Memory")

When several regions are joined, the OS records — in `S0MTb` (F02AH), `S1MTb`/`S1MBb` (F016H/F018H), `S2MTb`/`S2MBb` (F020H/F022H) and the `ADTBL+1…ADTBL+5` byte table (F1D6H–F1DAH, bank number in bits 4–5) — **the order in which the BASIC program is laid down across the banks**. TRM §3.12.2 Example 1 (CE-159 S1 + CE-1600M S2 as *extension* memory): program fills **bank 0 → bank 2 → bank 3 → main memory** in that order; `S1MTb`/`S2MTb` = FEH ("not a program module — used as extension memory"), `ADTBL+3…+5` = 01H/22H/32H (bank 0, bank 2, bank 3). Example 2 (CE-1600M S1 + CE-161 S2 as *program* modules): `S1MTb`/`S1MBb` = 02H/03H (S1 spans ADTBL+2..+3), `S2MTb` = 04H, load order S0 → S1 → S2. The takeaway: "one contiguous user area" is a firmware abstraction over an explicit, recorded bank sequence — the program text really is scattered across banks 0/2/3/main and the ADTBL list is the map.

**Fill order — settled: S2 → S1 → internal RAM.** The Operation Manual, Appendix B, is right: *"BASIC text is written into expansion memory areas in the order S2: → S1: → Internal RAM."* TRM Example 1 (and its `ADTBL` values 01H/22H/32H), which puts S1 (bank 0) first, contradicts this; its exact configuration (a CE-159 in Slot 1) has not been read back. Confirmed from the `ADTBL` the ROM's boot code writes (read back running the real ROM): with RAM in Slot 2 — alone or together with Slot 1 — S0's first run is Slot 2 (bank 2), so S0's header + reserve sit at bank 2 8000H and the first free byte is **bank 2 80C5H**; only with Slot 1 alone is it bank 0 80C5H. Consequence for machine code loaded at 80C5H into the merged S0: it is started with `CALL &80C5` when only Slot 1 holds RAM, but `CALL #2,&80C5` as soon as Slot 2 holds RAM — same address, different bank.

The `ADTBL+n` byte-level encoding (`bank = (b>>4)&3`, low nibble = slot, bit 7 = program-module leading bank), and a step-by-step reconstruction of where each tokenised byte lands — for an emulator that injects a program image directly instead of running `LOAD` — are in `PC-1600-BASIC-Program-Placement.md` §4 and `PC-1600-BASIC-Program-Placement.md`.

### 4b.6 LH5803 view of the same configurations

In MODE 1 / under `XCALL`, the LH5803 sees module RAM at **0000–3FFF** and internal RAM at **4000–7FFF** (§5–§6). The same top-justification applies, shifted by −8000H:

```
Config (b), CE-155 in Slot 1, LH5803 view:
  0000 ┌───────────┐  open bus
  2000 ├───────────┤ ◄─ CE-155 body 2000–3FFF  (= Z-80 A000–BFFF)
  3FFF ├───────────┤
  4000 │ internal  │  4000–7FFF  (= Z-80 C000–FFFF, bank 0)
  7000 │  …work    │  7000–7FFF work area  (= Z-80 F000–FFFF)
  7FFF └───────────┘
```

This is deliberately a PC-1500-shaped map: a flat module window at the bottom, fixed internal RAM above it, work area at the very top (§6's address-by-address comparison). It only holds when the module is a *single flat ≤16 KB region with no banking* — which is exactly the constraint behind ERROR 110 (§8).

### 4b.7 Worked example: CE-1600M in **both** slots — the maximum-RAM configuration

Two genuine CE-1600Ms (32 KB each, flat, two-bank, no vertical banking) + the internal 16 KB is the largest `MEM` a PC-1600 can reach. **Both slots merge automatically at boot** — a CE-1600M carries an *extension-module* header (§3.13.2 type 1), so module detection folds it into the work area at reset for Slot 2 just as for Slot 1. `MEM` reports **77 370 immediately after a reset**, and `INIT "S2:","M"` is a **no-op** in this state (confirmed on the emulator). `INIT "S2:","M"` only matters if the module is *currently* typed as a file or program module — it re-types it back to extension memory. (Contrast the vertical-banked modules below.)

```
   Bank 2  8000–BFFF  Slot 2 CE-1600M, low half   (loc C)   ┐ ← S0 header + reserve at 8000H
   Bank 3  8000–BFFF  Slot 2 CE-1600M, high half  (loc D)   │ one logical
   Bank 0  8000–BFFF  Slot 1 CE-1600M, low half   (loc A)   │ user area,
   Bank 1  8000–BFFF  Slot 1 CE-1600M, high half  (loc B)   │ scattered
   Bank 0  C000–EFFF  internal RAM                          │ across banks,
   Bank 0  F000–FFFF  Work Area (fixed)                     ┘ filled in this order (§4b.5)

   16384 + 32768 + 32768 − 4550 = 77 370   ← MEM, confirmed on the emulator (2 × CE-1600M)
```

**This is the ceiling.** Both slot contributions are already at their architectural cap (Slot 1: only Bank 0 + Bank 1 exist for its window; Slot 2: only vertical bank 0 can be S0 expansion memory — and a CE-1600M *is* exactly one 32 KB vertical bank). A CE-1601M / CE-1650M / *superRAM* in Slot 2 keeps `MEM` at this same figure and adds its extra vertical banks **only as RAM-disk space** (`PC-1600-Bank-Switching.md` Part 2, "Why Slot 1 and Slot 2 contribute so differently"). The one untapped reserve anywhere is Bank 7 ("addressable but unused", §2) — no module uses it.

**Machine-language areas in this configuration.** With both CE-1600Ms merged as expansion memory there are no program modules, so **`NEW "S0:"` is the only ML target** — `NEW "S1:"`/`"S2:"` name *the program module* in that slot (Operation Manual p.233), and `TITLE "S1:"`/`"S2:"` gives ERROR 101 in this state (real hardware, §4.1). Per §4.0, the S0 header + reserve sit at the start of the merged area, so `NEW "S0:",<expr>` carves its ML block from `80C5H` in **bank 2** (Slot 2, loc C — S2 comes first in the fill order, §4b.5) and, if larger, continues in `ADTBL` order — logically continuous, but CPU-contiguous only within one bank (≤ 16 187 bytes in bank 2). Code placed there is started with `CALL #2,&80C5`.

The three targets S0/S1/S2 only coexist when the modules are typed as **program modules** (then they don't count in `MEM`, §4a). They then **accumulate** — issuing them in sequence leaves all three ML areas reserved; only the BASIC program text is cleared by each `NEW` (TRM §2.2's own example does exactly this; confirmed on real hardware — the ML contents survive, §4.1). Each carves `[base]+C5H … [base]+<expr>−1` from the bottom of its own module (`<expr>` = program size + `&C5` = size + 197):

| `NEW` (program modules) | Base | ML area — one module only | Max allocation (logical) | Largest CPU-contiguous piece |
|---|---|---|---|---|
| `NEW "S1:",<expr>` | 8000H | 80C5H → bank 0, then bank 1 (same module) | 32 571 bytes (`<expr>` ≤ `&8000`) | 16 187 bytes (bank 0) |
| `NEW "S2:",<expr>` | 8000H | 80C5H → bank 2, then bank 3 (same module) | 32 571 bytes | 16 187 bytes (bank 2) |
| `NEW "S0:",<expr>` | C000H | C0C5H → internal RAM only (stops below the F000H work area) | ≈ 11.8 KB | ≈ 11.8 KB |

So a single ML allocation never spans more than one module (S0 aside, §4.0), and an ML program addresses at most one bank straight through. For anything larger, split the code per bank and cross with `BANKCALL` (019FH) / `RST 20H` / `BANKCALL2` (0020H).

**Two programs in two slots** — the intended use of the multi-target form (both modules typed as program modules):

```
NEW "S1:",&<sizeA+C5>          ' area A at 80C5H, Bank 0/1
NEW "S2:",&<sizeB+C5>          ' area B at 80C5H, Bank 2/3   (does not disturb area A)
' load program A (e.g. CLOADM "A";#0,&80C5,… or POKE #0,…), load program B into #2
CALL #0,&80C5 [,var]           ' run A
CALL #2,&80C5 [,var]           ' run B
```

All of this is **SC-7852 (Z-80)** code (`CALL` / `PEEK` / `POKE` / `BLOAD` / `CLOADM`); the LH-5803 side is the separate `XCALL` / `XPEEK` / `XPOKE` path with its own address map (§5–§6).

**Effect on the BASIC area — it flows around the reservations; a slot is never lost.** The German TRM §2.2 puts it directly: `NEW` reserves the ML space "*and thereby simultaneously specifies the lower address of the BASIC program area*". Every byte of the ≈ 77 KB user area not inside an ML block stays BASIC-program / variable space; the interpreter tracks the scattered bank order in `ADTBL` (§4b.5) and treats it as one stream. With both modules merged, reserve 8 KB via `NEW "S0:"` (landing in Slot 2's bank 2) and the other 24 KB of that slot is still BASIC space. Rule of thumb:

```
MEM after reservation  ≈  77 370 − <expr>          (<expr> of NEW "S0:"; it already
                                                     includes the 197-byte reserve)
```

S0's 197-byte reserve is paid once either way; a program module carries its own 197 B, outside `MEM`. With two CE-1600Ms there is **no** slot unavailable to BASIC — both are live expansion memory from reset. (A slot only drops out of `MEM` when its module is re-typed as a program module or RAM disk with `INIT`; see §4b.3(d).)

---
