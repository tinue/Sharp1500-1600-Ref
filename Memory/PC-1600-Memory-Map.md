# PC-1600 Memory Map

Summary: Z-80 view in four bank-switched pages, internal RAM layout, comparison with PC-1500(A), summary table.
Scope: PC-1600
Sources: cited inline in the text
Status: cited

> Split from `PC-1600-Memory-Architecture.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §5 → [PC-1600-LH5803-Memory-View.md](../CPU/PC-1600-LH5803-Memory-View.md); §4, §4a → [PC-1600-Program-Areas-and-NEW.md](PC-1600-Program-Areas-and-NEW.md); §4b → [PC-1600-Module-Window-Layout.md](PC-1600-Module-Window-Layout.md); §8 → [PC-1600-MODE0-MODE1.md](../Firmware/PC-1600-MODE0-MODE1.md).

## 1. Overview and Scope

This document is the narrative/comparison layer for the PC-1600's memory system: how the Z-80 sees its bank-switched address space, how the internal RAM at the top of that space is structured, and — the part not covered elsewhere in this project — how the *same physical memory* looks when the machine's second CPU, the LH5803, is running in PC-1500-compatibility mode, and how that compares to a real PC-1500/1500A.

For the exhaustive mechanism-level reference (Port 31H truth tables per address range, the LR38041 gate array's pin-by-pin function, firmware bank-call routines, module header formats, and real module hardware including the CE-1600M/CE-1601M/*superRAM*), see `PC-1600-Bank-Switching.md` — this document draws on it throughout rather than repeating it. For the PC-1500/1500A's own decoder architecture, see `PC-1500-Address-Decoding.md`. For raw connector pinouts across all three machines, see `PC-1500-Connectors.md`.

**Sources for this document specifically:** the PC-1600 Technical Reference Manual §2.1 ("Memory Map"), the paragraph introducing 8 memory banks and internal-RAM layout that follows it, §2.2 ("BASIC Commands Related to Machine Language"), **§3.12** ("Memory": 3.12.1 Slots and Memory Modules, 3.12.2 Work Area used for Memory, 3.12.3 IOCS routines) and **§3.13** ("Memory Module": location / type / header) — the TRM figures behind §2–§4b, not previously transcribed into this project's PC-1600 material — plus **§5.15** and the Operation Manual Appendices **F** (error codes) and **H** (PC-1500 compatibility) for §8, and the Operation Manual's command-dictionary entries for `NEW` (p.233–235), `TITLE` (p.317), `INIT` (p.185–186), `PASS` (p.252) and its **Appendix B** ("Replacing the RAM Modules", p.333) for §4.1. Cross-checked against the existing Service-Manual-sourced content in `PC-1600-Bank-Switching.md`, and against the PC-1600's own German-language user manual (*Bedienungsanleitung*), whose Appendix D (memory map, in German) and Appendix E/H (machine-language commands, PC-1500 compatibility) independently confirm most of the TRM material and correct several claims this document made in earlier revisions — noted inline where that happened.

---

## 2. The Z-80 View: 64KB Sliced Into Four Bank-Switched Pages

The TRM states the mechanism plainly: the Z-80's 64KB address space is segmented into four fixed 16KB pages (0000–3FFF, 4000–7FFF, 8000–BFFF, C000–FFFF), and each page independently selects which physical 16KB block occupies it via the Port 31H bank-select bits (`PC-1600-Bank-Switching.md` Part 2). The TRM's own memory-map figure, reproduced structurally below, lays out which physical block sits in which page for banks 0–6:

| Address range | Bank 0 | Bank 1 | Bank 2 | Bank 3 | Bank 4 | Bank 5 | Bank 6 |
|---|---|---|---|---|---|---|---|
| 0000–3FFF | Internal ROM | — | — | — | — | — | — |
| 4000–7FFF | Internal ROM (cont.) | Module Slot 2 (C) | — | Internal ROM | CE-1600P Printer ROM | — | — |
| 8000–C000 | Module Slot 1 (A) | Module Slot 1 (B) | Module Slot 2 (C) | Module Slot 2 (D) | — | — | Internal ROM |
| C000–FFFF | Internal RAM | — | — | — | — | — | — |

This is consistent with, and confirms, the bank table already in `PC-1600-Gate-Array-and-Chip-Selects.md` Part 1 — the TRM's (A)/(B)/(C)/(D) labels for the 8000–C000 row are exactly that document's "Slot 1a/Slot 1b/Slot 2a/Slot 2b," just drawn as a single unified table instead of split into a bank table plus two "additional banks" side-tables.

**One new fact from the TRM's own prose, not previously documented here:** *"The PC-1600 can address 8 memory banks (bank 0 to bank 7). The first four banks are allocated to RAM. Banks 4 to 6 hold internal system ROMs and peripheral memory. Bank 7 is unused, but is addressable."* Two things worth drawing out:

- "The first four banks are allocated to RAM" is a simplification — banks 0–3 are actually a mix (system/module ROM in their 0000–7FFF halves, RAM in their 8000–FFFF halves) — but it correctly identifies that all the *RAM* in the whole banked address space (module RAM in Slot 1/2, plus the internal 16KB) lives exclusively within banks 0–3.
- **Bank 7 exists, is addressable, and is simply unused** by anything Sharp shipped. This is new information: nothing in the existing bank table accounts for a 7th bank at all. It's a second piece of headroom in the architecture, parallel to (but distinct from) the Port 28H vertical-bank headroom documented in `PC-1600-Bank-Switching.md` Part 2/7a/7b — that headroom is *within* a Slot-2 module's own 32KB footprint; Bank 7 is a whole unused *global* bank slot, addressable by the same 3-bit b1–b3/b4–b6 fields Port 31H already uses for banks 0–6. Nothing in the sources reviewed for this project describes what, if anything, was ever mapped there. Independently confirmed word-for-word by the PC-1600's German user manual, Appendix D: *"Bank 7 ist zwar adressierbar, aber ungenutzt"* ("Bank 7 is indeed addressable, but unused").

---

## 2a. Reconciling the Two TRM Figures, the (A)/(B)/(C)/(D) Labels, and "Page B"

**The apparent page-16-vs-page-17 contradiction is a prose oversimplification, not a real conflict.** (Page numbers here are the Holtkötter PDF's page count, matching how this discussion was raised.) The TRM's memory-map *figure* (PDF p.16, reproduced structurally in §2) is authoritative and correct: Bank 0's 0000–7FFF is 32 KB of internal system ROM — the CS001 ROM, which `PC-1600-Gate-Array-and-Chip-Selects.md` Part 4 flags *"NEVER SWITCHED OUT"* — not RAM. The paragraph on PDF p.17 that says *"Die ersten vier Bänke sind dem RAM zugeordnet"* ("the first four banks are allocated to RAM") is a loose paraphrase that only holds for the *upper* half of banks 0–3 (8000–FFFF): every bank that contains **any** RAM is one of banks 0–3, but banks 0–3 are not all RAM. The 0000–7FFF half of every bank is ROM or unused; RAM begins at 8000 (module RAM) and at C000 (the fixed internal 16 KB).

Concretely, for Bank 0: 0000–7FFF = internal ROM, 8000–BFFF = Slot 1 module RAM (if present), C000–FFFF = internal 16 KB RAM. The figure on p.16 has it right; the sentence on p.17 is imprecise and should not be read as "banks 0–3 are RAM".

**The (A)/(B)/(C)/(D) labels, and references like "Page B, bank 1" — two incompatible conventions are in circulation. Disambiguate before answering.**

1. **TRM p.16 figure convention** — A/B/C/D quarter the *8000–BFFF module-RAM window* (one label per bank × slot). Here "Page B" = Slot 1b RAM. Table below.
2. **CPU-page convention** (used by at least one emulator effort) — A/B/C/D name the four 16 KB *CPU pages*: A = 0000–3FFF (page 0), **B = 4000–7FFF (page 1)**, **C = 8000–BFFF (page 2)**, D = C000–FFFF (page 3). Here "Page B, bank 1" = the 4000–7FFF window with Port 31H's page-1 field = 1, which `PC-1600-Gate-Array-and-Chip-Selects.md` Part 1's summary table *labels* "Slot 2 ROM"; "Page C" = Slot 2 RAM at 8000–BFFF.

   **Do not confirm a "route Page B through the Slot 2 connector, same as Page C" claim — it is wrong, now at schematic level.** The **CE-1600M** (Sharp's 32KB RAM module) and **CE-1620M** (Sharp's 32KB ROM cartridge) schematics both tie their chip-enable to connector **pin 4 (RAMSN)**, which the SC-7852 asserts (RAM1#/RAM2#) only for **8000–BFFF** accesses routed to that slot; neither module has any signal for a 4000–7FFF access, and neither even wires PU (pin 3) or PT (pin 19). The 4000–7FFF window is decoded internally by **CS24** → Memory-PWB ROM only (Part 4/Part 12). The firmware's EXROM / "Page-1 module at 4000H/6000H" concept (Part 6) is real but belongs to the **60-pin system bus**, not the memory slots — the one real 4000–7FFF ROM device (CE-1600P) is exactly such a 60-pin unit. Correct handling for an emulator: the memory-slot connector objects are consulted **only** for 8000–BFFF accesses; 4000–7FFF banks 1–7 are open bus unless internal ROM is mapped there, a 60-pin device answers, or a `SLOT1MAP`/`SLOT2MAP` remap puts slot RAM at Bank 1. Resolved along the way: PT/PU/PVOUT carry the bank number of the page being accessed (`PC-1600-Bank-Switching.md` Part 2); the 32KB memory modules use only PVOUT, which on an 8000–BFFF access is Port 31H **b4**, the 16KB-half select.

   **The one legitimate way Slot 2 content reaches 4000–7FFF** — Sharp's CE-1601M Service Manual §5 map shows a parenthesised `(S2:)` at Bank 1 / 4000–7FFF — is a **mainboard-side remap inside the SC-7852**: `SLOT2MAP` (0199H) sets Port 3CH, one of the SC-7852's own registers, which makes it assert the Slot 2 RAM select for a 4000–7FFF/Bank-1 access. Model this as an effective-address rewrite feeding the ordinary 8000–BFFF slot decode, driven by those registers — never as a connector pin, and never on by default. See `PC-1600-Gate-Array-and-Chip-Selects.md` Part 1, "(S2:) at Bank 1 / 4000–7FFF".

The tell for which convention is in play: "Page C" used for Slot 2 RAM, or "b7" named ⇒ convention 2 (CPU pages). A bare reference with no such context ⇒ assume convention 1 (the TRM figure), below.

**Convention 1 — the TRM figure's 8000–BFFF quarters:**

| TRM label | This project's name | Physical slot | Z-80 window | Bank (Port 31H page-2 field b6:b5:b4) | Contents |
|---|---|---|---|---|---|
| (A) | Slot 1a | Slot 1 | 8000–BFFF | Bank 0 (`000`) | Lower 16 KB of a Slot 1 module |
| (B) | Slot 1b | Slot 1 | 8000–BFFF | Bank 1 (`001`) | Upper 16 KB of a full-size (32 KB) Slot 1 module |
| (C) | Slot 2a | Slot 2 | 8000–BFFF | Bank 2 (`010`) | Lower 16 KB of the Slot 2 module's currently-selected 32 KB vertical bank |
| (D) | Slot 2b | Slot 2 | 8000–BFFF | Bank 3 (`011`) | Upper 16 KB of that same vertical bank |

So **"Page B, bank 1" = Slot 1b**: the upper 16 KB aperture of a full-size Slot 1 RAM module, mapped at Z-80 8000–BFFF whenever Port 31H's page-2 field selects bank 1. It is not a memory region distinct from anything else discussed here — it is one of these four module sub-windows, and it is module RAM (Slot 1), directly usable as program/expansion memory (§4a). The letter and the bank number are redundant: the figure fixes (A)→bank 0, (B)→bank 1, (C)→bank 2, (D)→bank 3, so "Page B" alone already implies bank 1.

**Why the figure also shows a *(C)* at 4000–7FFF in bank 1.** The firmware has an EXROM / "Page-1 module at offset 4000H or 6000H, banks 1–7" concept (F0AEH/F0AFH bitmaps, EXROM1–EXROME, `CALL 02DFH` Creg 01–0E — `PC-1600-Transparent-Banking.md` Part 6), and the p.16 figure's label reflects that firmware model. **It does not follow that a card in the CN-7/CN-8 memory bay drives the 4000–7FFF window** — see the Part 1 footnote †: the wiring decodes this window with CS24 (internal Memory-PWB ROM only), the slots' pin-4 select is 8000–BFFF only, and memory-bay module headers sit at 8000H/A000H/B000H (page 2). Where 4000–7FFF ROM genuinely exists (CE-1600P, bank 4) it arrives via the **60-pin system bus**, a different connector with its own decode. So, reliably: module **RAM** is page 2 (8000–BFFF), Slot 1 → banks 0/1, Slot 2 → banks 2/3 (× Port 28H vertical bank). Module **ROM** at page 1 is a firmware-level model whose physical path the corpus does not tie to the memory slots. "Modules occupy 4 slots, 8000–BFFF, banks 0–3" describes the RAM side — the four A/B/C/D blocks — and Slot 2's 32 KB of that is a single vertical bank of up to eight.

---

## 3. Internal RAM (Bank 0, C000–FFFF): Structure and the PC-1500(A) Parallel

The TRM's internal-RAM figure lays out Bank 0's C000–FFFF exactly as follows:

| Address | Region | Size |
|---|---|---|
| C000H | Header | 8 bytes |
| C008H | Reserve Program Area | 189 bytes |
| C0C5H | Machine Program Area (allocatable) | ⎫ |
| ↕ | BASIC Program Area | ⎬ User Area, 11834 bytes total |
| ↕ | Variables Area | ⎭ |
| (F000H) | Work Area | 4096 bytes, fixed |
| FFFFH | | |

Two figures here directly cross-check against numbers already established elsewhere in this project, from completely independent sources:

- **The 197-byte reserve.** C0C5H − C000H = C5H = **197 decimal**. This is the exact same offset, and the exact same hex constant, as the PC-1500/1500A's own `NEW 0` convention documented in `PC-1500-RAM-Sizing-and-NEW.md` §5.4: *"`NEW 0` will set the start of Basic memory to `[RAM start] + C5`... the first 197 bytes are used by various Basic data structures."* The PC-1600 didn't just inherit a similar idea — it inherited the identical numeric constant, split the same way: an 8-byte header (matching the ROM/RAM module header format documented in `PC-1600-Transparent-Banking.md` Part 6) plus a 189-byte reserve area, 8 + 189 = 197 = C5H. The CE-1601M service manual (`PC-1600-Memory-Modules.md` Part 7a) independently states "Reserve program area = 189 bytes" for its own program-memory mode, confirming the same 189 figure a third time.
- **The user-area byte count — 11834 confirmed, the manual's 12090 is very likely wrong.** This English-language TRM figure gives 11834 bytes, matching the `MEM` figures already tabulated in `PC-1500-RAM-Sizing-and-NEW.md` §5.1 for an empty PC-1600. The PC-1600's own German-language user manual (*Bedienungsanleitung*, Appendix D) instead gives 12090 for the identical configuration, and that number is *arithmetically self-consistent* with its own header(8B)/reserve(189B)/work-area(4096B) breakdown alone (`16384 − 4293 = 12091 ≈ 12090`) — which is exactly why this was flagged as an open discrepancy in an earlier revision of this document. It's since been settled by two independent real-hardware tests, both landing on a fixed 4550-byte overhead rather than 4293: a 16KB-module test (`32768 − 4550 = 28218`, exact) and a Slot 1 (8KB) + Slot 2 (32KB, one vertical bank) test (`57344 − 4550 = 52794`, exact — matching the Sharp-documented CE-1600M+CE-159 combo figure precisely). The same 4550-byte overhead reproducing exactly across three different configurations on the same hardware is strong evidence it's the real figure; the manual's 12090 (implying 4293) is presented as most likely a documentation error, not a genuine ROM-revision difference, though that can't be fully ruled out without testing a second unit. The extra 257 bytes beyond header+reserve+work-area (4550 − 197 − 4096) is most plausibly a fixed system-variable table the TRM's simplified Appendix D diagram doesn't itemize — being present identically whether or not any module is attached rules out anything module-dependent (like a per-slot directory reserve) as the source.

The practical takeaway: **the PC-1600's `NEW &C5`-style reserve-area convention is not a new design for the Z-80 side — it's the PC-1500(A)'s own convention, reused verbatim**, right down to the hex constant. Given the PC-1600 also runs an LH5803 in PC-1500-compatibility mode (§5 below), and Sharp's PC-1500(A) BASIC interpreter and PC-1600's Z-80 BASIC interpreter are separate codebases targeting different CPUs, this is either a deliberate, explicit design choice to keep the convention portable across the product line, or (less likely, given the exact byte-for-byte match including the header/reserve split) a shared heritage in how Sharp's BASIC toolchain group specified the fixed-area layout across pocket computers generally.

---

### 3.1 Where variables live, and how large an array can be (ROM-verified, measured)

**Three kinds of variable, two places.** The single-letter variables `A`–`Z`, `A$`–`Z$` and `@()` are *fixed variables*: `VARADR` (P0-B0 `29D0H`) computes their address in the work area (`F600H`–`F7FFH`, `PC-1600-Work-Area-Map.md` §1) and never searches. Everything else is *variable-area* data: **two-letter variables and every `DIM`med array** (the `@()` array excepted). `VARADR` finds these by walking the variable area upward from `VARPTR` (`F899H`), record = name (2 B) + size (2 B) + data; `VARALLOC` (`2B7CH`) creates one by moving `VARPTR` down.

**`VARPTR` is a *logical* address, not a Z-80 address.** The variable area is accessed only through `VARPEEK`/`VARPOKE`/`VARGET`/`VARLET` (`02A7H`/`02B0H`/`02A4H`/`02ADH`), each of which runs the address through `LOGADR` (`02D7H`) and then page-2 switches (`SELPG2B`, port 31H bits 6–4, saved and restored around the access):

| Logical | Maps to |
|---|---|
| 0000–3FFF | `ADTBL`+3 bank, at Z-80 8000–BFFF |
| 4000–7FFF | `ADTBL`+4 bank, at Z-80 8000–BFFF |
| 8000–BFFF | `ADTBL`+5 bank, at Z-80 8000–BFFF |
| C000–EFFF | internal RAM, directly (no switch; the routines test `H ≥ C0H`) |

The variable area starts at the top (EFFF) and grows down. When internal RAM is full it simply continues in the `ADTBL`+5 bank, then +4, then +3. So variables are **not** confined to the fixed internal RAM: with module RAM merged into S0 they sit in whatever bank their logical address falls in. The bank in `ADTBL`+2 (the first S0 bank, which also holds the header) has no logical mapping for variables: `LOGEND` (`02DAH`) returns 0000 for a program end outside `ADTBL`+3…+5, and `VARALLOC` fails (carry) if the new `VARPTR` would not stay above `LOGEND`.

**Arrays can exceed 16 KB.** `VARGET`/`VARLET` split a copy where it crosses the end of the page-2 window (C000H): they copy the first part, run `LOGADR` on the next logical address, select the next bank and copy the rest. Elements are at most 80 bytes, so one split suffices. `ARRAYIND` (`0259H`) returns a plain 16-bit logical element address and does not care which bank it lands in. The limits come from elsewhere:

1. **Per dimension:** `DIM` rejects an index whose high byte is non-zero (`K_DIM`, P1-B0 `5C3AH` → `ERR13P`, **ERROR 19**). Maximum index 255 (256 elements per dimension); string length `*n` at most 80 (`*81` → ERROR 19).
2. **Total size:** (n+1)·(m+1)·element size + 7 (header) is computed with a 16-bit `MUL16`; a carry gives **ERROR 10**. Element size is 8 for numerics, 16 for strings by default, `*n` up to 80.
3. **Free logical space:** the logical map ends at 61 440 bytes (0000–EFFF), shared with the BASIC program text.

**Measured** (Calc-U-1600, two CE-1600M merged, `NEW0`, `MEM` = 77 370):

| Statement | Bytes | Result |
|---|---|---|
| `DIM A(83,90)` | 61 159 | accepted; all 7 644 elements written and read back, 0 errors (it spans internal RAM and all three logical banks) |
| `DIM A(84,90)` | 61 887 | ERROR 10 (does not fit the logical span) |
| `DIM A$(255)*80` | 20 487 | accepted; 256 strings written and verified, 0 errors |
| `DIM A(255,255)` | ≈ 524 K | ERROR 10 (16-bit overflow) |
| `DIM A(256)`, `DIM A(300,2)`, `DIM A$(255)*81` | – | ERROR 19 |

The largest working size lies between 61 159 and 61 887 bytes, consistent with the 61 440-byte logical span. Although the machine has 77 370 bytes free, **no single array (and no set of variables) can use more than about 61 KB**, because the bank in `ADTBL`+2 is not addressable by the variable routines. **`MEM` ignores variables; `STATUS` has the variable-aware figures.** `MEM` (= `STATUS 0`) counts only the memory behind the end of the program (`(F864):00 − (F867+1)` plus 4000H per unused bank, LH5803 `BCMD_STATUS_FREE` `$CC30`). It stayed at 77 370 with a 61 159-byte array in place. The variable-aware values (measured, S0, two CE-1600M, empty program, `NEW0`):

| Function | Meaning | Empty | After `DIM A(50,50)` | After `DIM A(83,90)` |
|---|---|---|---|---|
| `STATUS 0` / `MEM` | free behind the program, variables not counted | 77 370 | 77 370 | 77 370 |
| `STATUS 258` | **free between program end and variable start, i.e. free after variables** (`P_STATUS2` `$C384`, bank-aware) | 77 370 | 56 555 | 16 211 |
| `STATUS 3` | start of the variables: offset within its bank window (internal RAM reads as 4000H + offset) | 28 416 (6F00H) | 7 601 | 25 |
| `STATUS 257` | hardware bank of the variable start (bank of the `ADTBL` entry its top bits select; the internal-RAM case reads as `ADTBL`+5) | 1 | 1 | 3 |
| `STATUS 1` / `2` / `4` | program size / program end + 1 / last line (as on the PC-1500) | 0 / 198 / 0 | – | – |

There is no `STATUS` for the variable size itself; it is **`STATUS 0` − `STATUS 258`**. Checked: `DIM A(10)` 95 B, `DIM A(10,10)` 975 B, `DIM A(50,50)` 20 815 B, `DIM A$(255)*80` 20 487 B, `DIM A(83,90)` 61 159 B, each = data + the 7-byte header. A two-letter numeric variable costs 15 B (`AB=1`), a two-letter string 23 B (`AB$="HI"`), i.e. 7 + 8 and 7 + 16. So the 61 159 above is the whole array including its header, and the free memory shown by `STATUS 258` (16 211) is what is left after it, even though the array cannot use the bank in `ADTBL`+2 (above).

*Scope:* verified for S0 (`TITLE "S0:"`) only. How variables behave when a program runs in an S1/S2 program area is not examined.

## 6. Comparison to the PC-1500 / PC-1500A

This is the part that isn't a re-statement of anything else in this project — a direct, address-by-address comparison between what the LH5803 sees inside a PC-1600 and what an LH5801 sees inside a real PC-1500/1500A.

| Region | Real PC-1500/1500A (LH5801) | PC-1600 in LH5803 mode | Same or different? |
|---|---|---|---|
| **0000–3FFF** (module window) | Y0, gated by pin 4 (YO) on the 40-pin connector; a module does its own internal sub-decode (`PC-1500A-Rewiring.md` §3.2) | Whichever Slot 1/2 RAM bank Port 31H selected on the Z-80 side | **Same address, same size (16KB), same "raw module window" character** — remarkable given the PC-1600's underlying hardware (Z-80 bank-switched RAM behind two dedicated slot connectors) shares nothing physically with the PC-1500's (a single 40-pin connector with fixed 2KB/16KB strobes). The LH5803 view was deliberately built to present the *same address range* here regardless. |
| **4000–7FFF** (built-in + module RAM area, real PC-1500(A)) | S0–S7 sub-decode: built-in RAM (S0 on PC-1500; S0–S2 on PC-1500A), module-reachable strobes (S1–S4 or S3–S5), then display buffer (S6) and CPU stack/fixed vars/ML area (S7) fixed at the top (`PC-1500-Address-Decoding.md` §2.2–3.1) | **Fixed 16KB internal RAM, unconditionally** — no sub-decode visible in the TRM's coarse bank map, no module extension possible here — but almost certainly still carrying a display-buffer/CPU-stack/fixed-variable region at the top, functionally equivalent to the PC-1500's own S6/S7, by the compatibility requirement alone (see the note in §5) | **Structurally similar, but PC-1600 gives 16KB where the PC-1500(A) gives 4–16KB depending on model/module, and does so entirely without the S1–S4/S3–S5 pin-reassignment story.** A real PC-1500A can put *module* RAM in part of this range (S3–S5 via the connector); a PC-1600 in LH5803 mode cannot — this whole range is hard-wired to the PC-1600's own internal RAM regardless of what's in Slot 1/2, so its capacity is fixed rather than model/module-dependent. |
| **8000–BFFF** (peripheral ROM area) | Y2, PU/PV-banked between CE-150/CE-158 (`LH5801-PU-PV-Signals.md` §4–5) | Same address range, same size (16KB), same two peripherals (CE-150/CE-158), same PVOUT/PV-style bank bit | **Same in every respect that matters** — this is the cleanest match in the whole comparison. The LH5803's native PV output (pin 60) enters the SC-7852 at PVIN (pin 8) and leaves as PVOUT (pin 7), the same pin that carries the Z-80-side bank bit; PU is one net shared by the LH5803 and SC-7852 pin 6 (`../Expansion/PC-1500-Connectors.md` §2.2b). The PC-1500's PU/PV mechanism wasn't reimplemented for the PC-1600 — the same physical CPU flip-flop pins are reused, PV just passing through the SC-7852 instead of going straight to a connector pin. |
| **C000–FFFF** (system ROM) | Y3, PC-1500/1500A system ROM + I/O port (`PC-1500-Address-Decoding.md` §2.1) | Same address range, same size (16KB), fixed internal ROM, no banking | **Same address and size; different content** — necessarily so, since this ROM holds the LH5803-side portion of PC-1600 firmware (16KB per `PC-1600-Gate-Array-and-Chip-Selects.md` Part 1's "80KB Z-80 BASIC + 16KB LH-5803" ROM split), not a literal copy of a PC-1500's system ROM. |

**The overall pattern:** the LH5803 memory map is a *purpose-built compatibility shim*, not a byproduct of shared hardware, and it reproduces the PC-1500's own address ranges and sizes far more faithfully than the coarse TRM bank map alone suggests. 0000–3FFF and C000–FFFF match address-for-address. 8000–BFFF matches address-for-address *and* reuses the literal PU/PV signal path for its bank selection (`LH5801-PU-PV-Signals.md` §3). And 4000–7FFF, on closer inspection (§5's note), is not the odd one out it first appears — it almost certainly still carries the PC-1500's own S6 (display buffer) / S7 (CPU stack, fixed variables) structure at the same relative offset, fixed at the top of the block, for the same reason the other three quadrants are address-faithful: real PC-1500 ROM code touches those addresses literally and unconditionally. What genuinely *is* different in that quadrant is the *growth mechanism*: the PC-1500A's S0–S7 sub-decode and its module-facing pin reassignment (`PC-1500A-Rewiring.md` §3, `PC-1500-Connectors.md` §3) has no PC-1600 equivalent at all — the PC-1600 just gives the whole 16KB as fixed internal hardware, with no model-dependent tiering and no way for a module to extend it.

---

## 7. Summary Table: PC-1600 Views vs. Each Other and vs. PC-1500(A)

| Axis | Z-80 view (native) | LH5803 view (compat. mode) | Real PC-1500/1500A |
|---|---|---|---|
| Addressable space | 64KB × 8 banks (320KB total, mostly ROM/mixed) | 64KB, unbanked from its own view | 64KB |
| Module window | 8000–BFFF, Slot 1/2, bank-switched via Port 31H (+ Port 28H for >32KB) | 0000–3FFF, same window a PC-1500 module would see | 0000–3FFF (Y0) |
| Built-in RAM growth mechanism | N/A — internal RAM is a fixed 16KB bank, no S-block sub-decode | N/A — fixed 16KB, likely still internally reserving a display-buffer/CPU-stack slice at the top (§5), but no S-block sub-decode and no module-extensibility | S0 (PC-1500) → S0–S2 (PC-1500A), `PC-1500A-Rewiring.md` §3 |
| Peripheral-ROM bank select | Port 31H b0 (PVOUT) | LH5803's own native PV pin, relayed | PU/PV CPU flip-flops, direct to connector |
| Reserve-area convention | `NEW "Sx:",expr` = size + C5H (197 bytes), per §3–4 | `NEW`/BASIC commands are Z-80-resident throughout (§5, confirmed by the German user manual) — presumably the same convention, since running MODE 1 programs uses the same BASIC housekeeping | `NEW 0` = `[RAM start]+C5`, `PC-1500-RAM-Sizing-and-NEW.md` §5.4 |
| Compatibility mechanism | N/A (native) | `MODE1` = display/behavior compatibility, confirmed via German user manual §9.2/Appendix H — not a CPU handoff for BASIC itself; genuine LH5803 execution is explicit (`CALL`/`XCALL`, `PEEK`/`XPEEK`, `POKE`/`XPOKE`, port equivalents) | N/A |
| ML-area compatibility | N/A | `&7C00`–`&7FFF` (PC-1500A's ML area) explicitly reserved for PC-1600 system use, confirmed by the German manual — Sharp states the two models are *not* compatible here | `&7C01`–`&7FFF` is the PC-1500A's own ML area (`PC-1500-Address-Decoding.md` §4) |
| Largest documented module | *superRAM*, 512KB (Slot 2, Port 28H extended), `PC-1600-Memory-Modules.md` Part 7b | N/A — module capacity as seen from LH5803 is whatever Z-80-side bank is currently selected, 16KB at a time | CE-155-class, ≤28KB combined with built-in RAM (`PC-1500-Connectors.md` §3.2) |
| Confirmed max user (`MEM`), 16KB module | 32KB raw span, `PC-1500-RAM-Sizing-and-NEW.md` §5.3 (0000–8000H); `MEM` = 28218 confirmed on real hardware, computed by Z-80-resident BASIC regardless of MODE (§5's note) | **Identical to Z-80 view — trivially, since `MEM` is core BASIC housekeeping and never runs on the LH5803**; `MODE1` doesn't reroute it, per §5's revised model | 28KB raw span (Y0 16KB + S0–S5 12KB, deliberately excluding the PC-1500A's own S6/S7) — no confirmed real `MEM` figure for this exact hypothetical configuration |

---
