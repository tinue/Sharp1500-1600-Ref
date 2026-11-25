# PC-1600 Program Areas and NEW

Summary: NEW across S0/S1/S2, where ML programs land, TITLE and program areas, program vs expansion memory.
Scope: PC-1600
Sources: cited inline in the text
Status: cited

> Split from `PC-1600-Memory-Architecture.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §5 → [PC-1600-LH5803-Memory-View.md](../CPU/PC-1600-LH5803-Memory-View.md); §1, §2, §2a, §3, §6, §7 → [PC-1600-Memory-Map.md](PC-1600-Memory-Map.md); §4b → [PC-1600-Module-Window-Layout.md](PC-1600-Module-Window-Layout.md); §8 → [PC-1600-MODE0-MODE1.md](../Firmware/PC-1600-MODE0-MODE1.md).

## 4. The `NEW` Command Across S0/S1/S2, and Where Machine-Language Programs Land

The TRM generalizes the PC-1500(A)'s single-target `NEW <expr>` into a three-target form:

```
NEW {"S0:" | "S1:" | "S2:"}, <expression>
```

where `<expression>` is "(the desired machine language program area size in bytes) plus C5H" — the same C5H constant as §3, now explicitly parameterized per target: **S0:** (internal RAM), **S1:** (Slot 1 module), **S2:** (Slot 2 module). Executing it allocates from `[slot's own base address] + C5H` up to `[base + expression] − 1`.

**Worked example from the TRM**, with a CE-159 program module in Slot 1 and a CE-1600M program module in Slot 2:

```
NEW "S1:",&1000
NEW "S2:",&5000
NEW "S0:",&1000
```

yields these machine-language program areas:

| Command | Resulting area | Bank |
|---|---|---|
| `NEW "S1:",&1000` | A0C5H–AFFFH | Bank 0 |
| `NEW "S2:",&5000` | 80C5H–BFFFH | Bank 2 |
| (continuation) | 8000H–8FFFH | Bank 3 |
| `NEW "S0:",&1000` | C0C5H–CFFFH | Bank 0 |

Two things worth noting:

- **CE-159's program area starts at A0C5H, not 80C5H** — i.e. this particular Slot-1 module's own address window begins at &A000, not &8000 (a half-size, 8KB-class module footprint, distinct from a full 16KB Slot 1a/1b pairing). This is module-specific, not a general Slot-1 property — `PC-1600-Bank-Switching.md`'s own bank table shows Slot 1a/1b spanning the full 8000–BFFF across banks 0/1 for a full-size module.
- **CE-1600M's program area spans two banks** (Bank 2's 80C5H–BFFFH, continuing into Bank 3's 8000H–8FFFH with no further +C5H offset, since it's a continuation of the same allocation, not a new base) — a &5000-byte (~20KB) `NEW` allocation on a 32KB module covers both of that module's banks. It is continuous only in the area's *logical* addresses; to the CPU the two parts are separate pages at the same 8000–BFFF window (§4.0).

This C5H-offset convention is identical in spirit to the PC-1500/1500A's own module-`NEW`-offset practice (`PC-1500-RAM-Sizing-and-NEW.md` §5.4, §5.5) — allocate the fixed reserve first, then give BASIC/ML the rest — just generalized here to name which of three physical targets (S0/S1/S2) the reserve applies to, since the PC-1600 (unlike the PC-1500/1500A) has two independent module slots plus internal RAM, all needing this same bookkeeping simultaneously.

### 4.0 One `NEW` = one module, at most two banks (S0 excepted)

**Slot vs. bank.** A *slot* is a physical module connector; a *bank* is a 16 KB page selected into the 8000–BFFF window (Port 31H page-2 field). A 32 KB module fills **two banks behind the same window** — Slot 1: banks 0 + 1; Slot 2: banks 2 + 3 (for a vertical-banked module, of the selected vertical bank). A module ≤ 16 KB is a single bank.

**`NEW "S1:"` / `NEW "S2:"` allocate inside exactly one physical module** — the program module in that slot (Operation Manual p.233: *"S1: is the program module currently in slot 1"*). The ML area starts at that module's base + C5H and can never run past the end of that module. **Within the module it may cover both banks** — that is what the TRM's `NEW "S2:",&5000` does (bank 2 → bank 3).

**S0 is the exception.** S0 is internal RAM *plus* any module RAM merged in as expansion memory (TRM §3.12.1), and its header + reserve sit at the start of the merged user area (§4b.3(b)). So a `NEW "S0:"` allocation counts from there and — if large enough — runs from a module on into internal RAM, or across both modules, in `ADTBL` order (§4b.5). This follows from the manual's area-relative addressing and the moved header; the TRM's only `NEW "S0:"` example uses program modules, where S0 is internal RAM alone (C0C5H…), so it is not yet confirmed by example or test.

**Logical vs. CPU addresses.** `NEW`'s `<address>` is a **logical, area-relative** address (*"relative addresses from the top of memory (0)"*, lower bound 197, upper bound 65535 — Operation Manual p.233–234). The firmware maps each area's logical space onto its bank list (`ADTBL`; ROM `LOGADR` 02D7H converts logical → physical + bank). An allocation is therefore always continuous *logically*, but only partly continuous *to the CPU*:

| Allocation crosses… | CPU-contiguous? | Why |
|---|---|---|
| bank → bank of the **same** module (e.g. bank 2 → bank 3) | **No** | both banks sit at 8000–BFFF; only one is mapped at a time — after BFFF the CPU sees C000 (internal RAM), not the next bank |
| module (page 2) → internal RAM (page 3), S0 only | **Yes**, while page 2 holds that bank | e.g. CE-155 at A000–BFFF followed by internal C000–EFFF; top-justification (§4b.2) makes BFFF→C000 seamless |

So the largest block an ML program can address straight through inside a module is **one bank**: 80C5–BFFF = **16 187 bytes** in the module's leading bank, 16 384 in a following bank. Code bigger than that must be split per bank and cross over with `BANKCALL` (019FH) / `RST 20H` / `RST 18H`, or keep its code in one bank and switch Port 31H to reach data in the other (with `DI`/`EI` around the access — `PC-1600-Gate-Array-and-Chip-Selects.md` Part 4).

### 4.1 Program areas, `TITLE`, and what each `NEW` form clears

Each of S0/S1/S2 is a separate **program area**: its own header + reserve, optional ML area, and one BASIC program (`INIT` "P": *"A single program can be written to the module"*). Operation Manual Appendix B: *"Until specified with the TITLE command, program modules are independent of the internal user RAM when installed."*

**`TITLE` selects the current program area** (Operation Manual p.317). Documented forms: `TITLE "S0:"` (internal RAM — the default after ALL RESET), `TITLE "S1:"`, `TITLE "S2:"`, and `TITLE ?`, which returns 0/1/2. The selection is the byte at F1D5H (`PC-1600-Work-Area-Map.md` §3.12). Selecting a slot that doesn't hold a program module gives **ERROR 101** (confirmed on real hardware with no program areas defined: `TITLE "S1:"`/`"S2:"` → ERROR 101, `TITLE "S0:"` works).

**A bare `TITLE` is identical to `TITLE "S0:"`**, although the manual doesn't list that form (the CE-1601M manual uses it: `TITLE` ⏎ `NEW` ⏎). The handler in the hidden BASIC ROM (`rom3b.asm`, 4264H) reads the character after the keyword: `?` prints `(F1D5H)+'0'`; end of line (0DH) jumps straight to 1F30H; otherwise it parses the `"Sn:"` device and calls the common routine 1EEFH with A = n. In 1EEFH, A = 0 branches to that same 1F30H (`XOR A` / `LD (F1D5H),A`, then set up S0's program bounds), and A = 1/2 checks the slot's module type and exits with A = 65H (= 101) when it isn't a program module. So bare `TITLE` and `TITLE "S0:"` run the same code. It is accepted without error on real hardware.

**What the `NEW` forms do** (Operation Manual p.233–234, MODE 0):

| Form | Area affected | ML allocation |
|---|---|---|
| `NEW` | the `TITLE`-selected area | kept at the previous value |
| `NEW "Sn:"` | the named area, regardless of `TITLE` | kept |
| `NEW "Sn:",<address>` | the named area | upper bound set to `<address>` (relative to the area base; lower bound 197) |
| `NEW 0` | the `TITLE`-selected area | reset to 0 — BASIC starts at 197 |

The manual says `NEW` "clears all BASIC and machine programs", but **real-hardware testing shows `NEW` clears only the BASIC program; an ML area reserved earlier with `NEW …,&xxx` keeps its allocation *and its contents* intact.** Read the manual's "machine programs" as "the ML area is no longer yours to rely on", not as the bytes being erased. So plain `NEW` and `NEW 0` are *not* equivalent: only `NEW 0` gives the ML area back to BASIC.

**Related restrictions:**

- `INIT "Sn:",…` (p.185–186, MODE 0 only) refuses a module that already holds programs or files (clear with `KILL`, or `NEW` on that module), a write-protected module, or **a program module currently selected with `TITLE`**. A CE-159 must be all program memory or all expansion memory.
- `PASS` (p.252) protects *all* programs in memory and, while set, blocks `NEW`, `TITLE`, `LIST`, `(C)SAVE`, `(C)LOAD`, `MERGE` and `CHAIN` — so the current program area is frozen as well.
- Installing an *expansion* (non-backed-up) module brings up `NEW 0?: CHECK`; a program module doesn't (Appendix B).

**Open:** whether `MEM` reports the free space of the S1/S2 area when `TITLE` selects it. The manuals only describe `MEM` as "free user memory" (Appendix B).

---

## 4a. Program Memory, Expansion Memory, and the RAM File: the Firmware's Central Distinctions

The PC-1600 firmware draws a hard line between RAM the CPU addresses directly and RAM reached only through the file system; on the CPU-addressable side it further separates **program memory** from **expansion memory**, and almost every "why does `MEM` report *X*" question resolves to which of these three a byte falls in:

- **Work area / expansion memory** — the RAM that holds the *currently active* BASIC program, its variables, and the machine-language area: §3's internal 11,834-byte user area, plus any module RAM glued onto it. "Expansion memory" is the manual's term for that glued-on module part. Directly CPU-addressable: the OS points the page-2/page-3 bank registers at it and *leaves them there*, so BASIC and ML code touch it as ordinary memory with no per-access bank juggling for the program text and ML area, but the variable area (two-letter variables, arrays) is reached through logical addressing with a page-2 switch per access (§3.1). **This is the one and only thing `MEM` counts.** Module RAM is folded in **automatically at boot** — a CE-1600M in either slot, Slot 1 modules generally, and vertical bank 0 of a vertical-banked Slot 2 module (CE-1601M, …) alike. `INIT "S2:","M"` (and the (32−*n*) remainder of `INIT "S2:","P",n`) only re-types a module that is currently a program module or RAM disk back to expansion memory — see §4b.3(d). Its module-side bookkeeping lives in main-unit RAM, so a Slot 2 module's expansion-memory contribution does **not** survive a battery swap. **Ceiling ≈ 77 KB**: internal 16 KB + one 32 KB Slot 1 span + one 32 KB Slot 2 vertical bank (`PC-1600-Bank-Switching.md` Part 2, "the theoretical maximum").
- **Program memory** — a *separate, resident program-storage area*, set up by `INIT "S2:","P"` (or the *n* KB named in `INIT "S2:","P",n`). Also directly CPU-addressable when active, but it holds a parked BASIC program rather than extending the current work area, so **`MEM` never reflects it** — allocating it leaves `MEM` unchanged. `TITLE`-named, cleared with `NEW 0`, held in the module SRAM so it *does* survive a battery swap. Internally it has the same fixed layout as §3's internal RAM: an 8-byte header + a 189-byte "Reserve Program Area" + the **"BASIC text area"** (the tokenized program lines themselves) — the CE-1601M manual names those two sub-regions, but the only term that matters at the `INIT` level is "program memory".
- **RAM file / RAM disk (data storage)** — reached *only* through the file system (`SAVE`/`LOAD`/`FILES`/`KILL`/`PRINT#`/`INPUT#`…). The file-system driver is the only code that issues per-access `OUT (28H)` vertical-bank writes, so it can walk all 8 vertical banks of a Slot 2 module (256 KB), of which only vertical bank 0 is ever eligible to become program or expansion memory. `DSKF` reports its free space; `MEM` never sees it.

`INIT "S2:","P",n` (CE-1601M Mode D, `PC-1600-Memory-Modules.md` Part 7a) makes the split explicit — it partitions one module's vertical bank 0 into *n* KB of program memory + (32−*n*) KB of expansion memory, and hands vertical bank 1 to a 32 KB RAM file, in one command. So `MEM` rises by exactly (32−*n*) KB: plain `INIT "S2:","P"` is the *n* = 32 case (all program memory, `MEM` unchanged) and plain `INIT "S2:","M"` is the *n* = 0 case (all expansion memory, `MEM` +32 KB). All of this on a module already formatted with `INIT "S2:","F"`; on a blank one `"P"`/`"M"` make no RAM file (`PC-1600-Memory-Modules.md`, the note under Part 7a's table). This is why a 256 KB Slot 2 module adds at most 32 KB to `MEM` with the remainder data-storage-only. `INIT "S2:","P",n` is a *vertical-banked-module* mechanism — a flat 32 KB extension-type module (CE-1600M) in Slot 2 just merges its whole 32 KB at boot with no `INIT` step, the same way a Slot 1 module does (Slot 1's two banks sit in global Bank 0/1 alongside internal RAM, contiguous).

---
