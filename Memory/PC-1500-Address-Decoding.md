# PC-1500 / PC-1500A Address Decoding and Physical Memory Map

Summary: Address decoder, physical RAM chips, the machine-language area at &7C01, superseded hypotheses.
Scope: PC-1500, PC-1500A
Sources: cited inline in the text
Status: cited

> Split from `PC-1500-Address-Decoding.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §5 → [PC-1500-RAM-Sizing-and-NEW.md](PC-1500-RAM-Sizing-and-NEW.md); Appendix: Reading, Appendix: PC-1500A Chip, Appendix: PC-1500 Chip → [PC-1500-Chip-Select-Tables.md](PC-1500-Chip-Select-Tables.md); §3 → [PC-1500A-Rewiring.md](../Expansion/PC-1500A-Rewiring.md).

## 1. Overview

The Sharp PC-1500 and PC-1500A use a 16-bit address bus giving a 64KB address space. This document covers the machine's actual address-decoder hardware and physical RAM layout: the top-level 16KB blocks and their sub-decoding into 2KB strobes (§2), why the PC-1500A's expansion connector was rewired relative to the PC-1500, using the CE-155 module as a worked example (§3), the origin and exact boundary of the PC-1500A's separate machine-language area (§4), and RAM-sizing / `NEW`-offset calculations that follow directly from the chip population described in §2–§3 (§5).

For how multiple 16KB memory banks are switched into the &0000–&3FFF window in software (POKE triggers, the CE-163 and its modern recreations, firmware pointer save/restore), see `PC-1500-Bank-Switching.md`, which builds on the decoder facts established here.

---

## 2. Address Decoder Architecture and Physical RAM

### 2.1 Top-level 16KB blocks (Y0–Y3)

The **TC40H139F** decodes address lines AD14/AD15 into four 16KB blocks. This decoder is identical on both models:

| Block | Range | PC-1500 | PC-1500A |
|---|---|---|---|
| Y0 | 0000H–3FFFH | Module unit user memory area | Optional user memory (module slot) |
| Y1 | 4000H–7FFFH | Module unit user RAM area (further decoded below) | (further decoded below) |
| Y2 | 8000H–BFFFH | Module unit optional ROM area — CE-150/CE-153/CE-158 system program & I/O port | Same |
| Y3 | C000H–FFFFH | System program ROM + I/O port | PC-1500A system program, I/O port; CE-158 I/O port/UART also appears here |

System ROM part reads cleanly as **SC61328F** in a typed Sharp Service Manual excerpt (the most legible of several sources; other hand-drawn/scanned schematics elsewhere in this document read it as SC61329F or SC613128 — same chip). I/O port chip is documented as both **LH5810 and LH5811** across Sharp's own material, and this isn't a transcription conflict: an older PC-1500 Service Manual (predating the PC-1500A, consistent with the PC-1500's early A01/A03 ROM era) shows LH5810, while direct teardown of two separate units (a PC-1500 and a PC-1500A, both presumably later-production/A04-era) shows LH5811 in both. Both parts are genuine, from different production eras.

### 2.2 Sub-blocks of Y1 (S0–S7)

The **TC40H138F** further decodes AD11–AD13 within Y1 (4000H–7FFFH) into eight 2KB sub-blocks, S0–S7 (active only while Y1 is asserted). The address range each strobe covers is fixed and identical on both models — what differs between models is which of these ranges is populated with built-in RAM vs. left available for expansion modules:

| Signal | Range | PC-1500 usage | PC-1500A usage |
|---|---|---|---|
| S0 | 4000H–47FFH | Standard user memory (built-in) | Standard user memory (built-in) |
| S1 | 4800H–4FFFH | Optional user memory (module slot) | Standard user memory (built-in) |
| S2 | 5000H–57FFH | Optional user memory (module slot) | Standard user memory (built-in) |
| S3 | 5800H–5FFFH | Optional user memory — also the CE-163-style bank-select trigger | Optional user memory (module slot) |
| S4 | 6000H–67FFH | Optional user memory (module slot) | Optional user memory (module slot) |
| S5 | 6800H–6FFFH | Not used | Optional user memory — also the CE-163-style bank-select trigger |
| S6, 7000H–75FFH | — | Inhibited | Inhibited |
| S6/V2, 7600H–76FFH | — | Display-driver RAM (LCD chips 1 & 3) | Display-driver RAM (LCD chips 1 & 3) |
| S6/V3, 7700H–77FFH | — | Display-driver RAM (LCD chips 2 & 4) | Display-driver RAM (LCD chips 2 & 4) |
| S7 | 7800H–7FFFH | 7800H–7BFFH standard user and system memory; 7C00H–7FFFH inhibited (mirror of 7800H–7BFFH, see §2.3) | Standard user and system memory, including the machine-language area (&7C01–&7FFF, see §4) |

A second-stage TC40H139F, gated by S6, splits it into 2Y2 (V2, display chips 1 & 3) and 2Y3 (V3, display chips 2 & 4).

*Source: PC-1500 Technical Reference Manual §4-3 for the decoder ICs; the PC-1500A's usage-category labels (the "standard"/"optional"/"inhibited" column above) are transcribed directly from a photographed page of the PC-1500A TRM's own memory-map figure.*

### 2.3 Physical RAM chips

Confirmed by direct teardown of both a PC-1500 unit and a PC-1500A unit, and — for the PC-1500A — independently by a Sharp circuit block diagram that labels each RAM chip's chip-select input.

**PC-1500** (3.5KB total physical RAM):

| Chip | Capacity | CPU window | Role |
|---|---|---|---|
| HM6116 (×1) | 2048B | S0, &4000–&47FF | User RAM — 1850B free for BASIC after the reserve area |
| TC5514 (×2, 1K×4bit each) | 1024B | S7, &7800–&7FFF (see note below) | System memory + part of fixed variables |
| SC882G display chips (×4) | 512B | S6/V2+V3, &7600–&77FF | Rest of fixed variables + display buffer |

**S7 is chip-selected across its full 2KB, but only holds 1KB of distinct storage.** The TC5514 pair has 10 address lines (A0–A9); S7 is a 2KB block, needing 11 (A0–A10) to address every byte uniquely. The chip-select schematic shows the pair fed by a single, ungated wire straight off Y7 — no logic conditions the select on A10. Since the chips have no A10 pin at all, they simply can't distinguish it: they respond to *any* access anywhere in the 2KB S7 window, decoding only A0–A9. The practical result is that **&7800–&7BFF and &7C00–&7FFF are not independent — they're the same 1024 physical bytes, mirrored**, at a fixed offset of &400 (a write to any address *n* in &7C00–&7FFF lands on the same cell as address *n*−&400 in &7800–&7BFF). This is why the PC-1500's own TRM decode table marks the upper half of S7 (&7C00–&7FFF) "inhibited" while listing &7600–&7BFF as standard user and system memory (see the PC-1500 Chip-Select Table appendix): it's not merely unpopulated, a write anywhere in the upper half would silently corrupt whatever system data occupies the corresponding byte in the lower half. A separate Sharp Service Manual independently confirms this with its own memory-map diagram, marking &7C00–&7FFF with the caption **"Inhibit to use by redundancy"** — Sharp's own term for the same mechanism, from a source unrelated to the TRM table.

**PC-1500A** (8.5KB total physical RAM):

| Chip | Capacity | CPU window | Role |
|---|---|---|---|
| HM6116 (×3, "User RAM") | 6144B | S0+S1+S2, &4000–&57FF | Standard/contiguous BASIC RAM |
| HM6116 (×1, "System RAM") | 2048B | S7, &7800–&7FFF | System memory + machine-language area |
| SC882G display chips (×4) | 512B | S6/V2+V3, &7600–&77FF | Same as PC-1500, unchanged |

The PC-1500A simply populates four of the eight possible 2KB blocks (S0, S1, S2, S7) with an identical, off-the-shelf 2K×8 SRAM part (reused four times), where the PC-1500 only populated one full block (S0) and half of another (S7, via a narrower 1K×4bit part).

### 2.4 Which strobes are qualified by ME0

The LH5801 drives ME0 for `(addr)` accesses and ME1 for `#(addr)` accesses, on the same 16 address lines. Whether a chip answers in ME1 at all, and so whether ME1 "mirrors" ME0 there, depends on whether its chip select includes ME0. The "Chip select circuit" schematic (PC-1500A TRM p.163; the PC-1500's own sheet has the same structure) shows exactly where ME0 enters:

| Decoder input | Driven by |
|---|---|
| TC40H139F half 1: 1G̅ (enable) | **BF0** (CPU flip-flop output, reset by `OFF`) |
| TC40H139F half 1: 1A / 1B | AD14 / AD15 |
| TC40H138F: G1 (active-high enable) | **ME0** |
| TC40H138F: G2A̅ | 1Y1 (&4000–&7FFF) |
| TC40H138F: G2B̅ | resistor / diode / Zener network to Vcc and GND (not explained in the source; most likely a supply-sense input that deselects RAM when power fails) |
| TC40H138F: A / B / C | AD11 / AD12 / AD13 |
| TC40H139F half 2: 2G̅ / 2A / 2B | S6 / AD8 / DME0 |

ME0 goes to **one** pin: the '138's G1. So the ME0 check is inherited by everything downstream of the '138, and by nothing else:

| Strobe | Range | Goes to | ME0-qualified? |
|---|---|---|---|
| S0–S2 | &4000–&57FF | built-in user RAM (S1/S2 also on 40-pin pins 16/17 on the PC-1500) | **yes**, via '138 G1 |
| S3–S5 | &5800–&6FFF | module unit (40-pin pins 16–18 / 5) | **yes**, via '138 G1 |
| S6 → V2/V3 | &7600–&77FF (mirrored &7000–&75FF) | display chips | **yes**, via '138 G1, and again through DME0 on 2B |
| S6 · WEX | &7000–&77FF | I/O port interrupt input | **yes**, via '138 G1 |
| Y7 | &7800–&7FFF | system RAM | **yes**, via '138 G1 |
| Y0 (1Y0) | &0000–&3FFF | module unit (40-pin pin 4) | **no**, only BF0 |
| Y2 (1Y2) | &8000–&BFFF | module unit (40-pin pin 19) | **no**, only BF0 |
| 1Y3 | &C000–&FFFF | system ROM (CS613128F) **and** I/O port (LH5811) | **no**, only BF0 |

This is the hardware behind the TRM table footnote *"S0–S7, V2, and V3 are applicable only for the ME0 area"* (appendices below).

Consequences:

- **&4000–&7FFF never answers in ME1.** All built-in RAM (user, system, display) and every 2KB module strobe S1–S5 sit behind the '138, so `#(&4000)`…`#(&7FFF)` select nothing on the mainboard. A module chip wired to one of these strobes is ME0-only too, even when the module has no ME logic of its own. **CE-151** (S1/S2 only) and **CE-155/CE-159's** three S-strobe chips therefore cannot appear in ME1.
- **Y0 and Y2 carry no ME qualification, so a module must use DME0.** The 40-pin connector has no raw ME0 or ME1 pin. Its only ME-area signal is **DME0** (pin 6; also pin 56 on the 60-pin bus). A module on Y0 or Y2 that ignores DME0 answers in both ME0 and ME1. The **CE-155/CE-159** fourth chip (&3800–&3FFF: Y0 + its own '138 decode) does take DME0, so it is ME0-only, like the module's three S-strobe chips. The whole CE-155 is therefore absent from ME1.

**DME0 vs. ME0.** PC-1500 Technical Reference Manual p.75 (PDF p.80): *"Since a slow access memory usually consists of dynamic logic, it needs a precharge time. Thus, the I/O port controller issues the memory enable signals DME0 and DME1 to the dynamic memory, including the precharge time. DME0 is for ME0 and DME1 is for ME1."* So:

- **ME0** is the CPU's own memory enable for ME0 cycles. The mainboard's static RAMs are selected through it (TC40H138F G1).
- **DME0** is issued by the I/O port controller (the "I/O PC" block on the schematic) for the same ME0 cycles, timed for slow, dynamic memory: it includes the precharge time and works with the WAIT mechanism (W0/W1). The display chips are such parts, which is why their decoder half takes DME0 (2B), not ME0.
- **Which address space** an access targets is the same for both: DME0 is asserted only for ME0 cycles, as DME1 is only for ME1 cycles. They differ in timing, not in which space they select. For decoding, and for an emulator that does not model wait states, DME0 = ME0.
- Gating a Y0 or Y2 chip with DME0 therefore makes it ME0-only, exactly as ME0 would. DME0 is what reaches the 40-pin connector, so it is what a module can use.
- **1Y3 cannot tell the ROM and the LH5811 apart by ME.** It feeds both, and the ROM lives in ME0 while the LH5811 is accessed with ME1. So each part must take ME0/ME1 (or DME0) on a pin that this sheet does not show. Whether the system ROM also appears in ME1 cannot be decided from this schematic.
- **BF0 gates every top-level strobe.** After `OFF` resets the BF flip-flop, no ROM, RAM, display or module select can be asserted. The '138 hangs off 1Y1, so it is disabled too.

---

## 4. The Machine-Language Area (&7C01–&7FFF)

### 4.1 What it is

The PC-1500A's own TRM decode table (§2.2) explicitly marks &7800–&7FFF (S7) as "standard user and system memory," with a nested annotation naming **"MACHINE LANGUAGE AREA (7C01H–7FFFH)"** — an intentional Sharp designation, not a reconstruction from pointer addresses.

It is architecturally a separate story from the S1/S2 standard-RAM growth in §3, not a continuation of it. S5, S6, and S7 never appear on any connector pin (only S1–S4, YO, and Y2 reach the expansion bus) — so growing usable capacity at &7800+ required no pin reshuffling of any kind, unlike S1/S2, which are wired out to external modules. This block sits entirely on the mainboard side of the connector.

### 4.2 Why exactly &7C01

On the plain PC-1500, S7 is chip-selected across its full 2KB but only backed by 1024 bytes of distinct storage (§2.3): the TC5514 pair's missing 11th address line means &7C00–&7FFF exactly mirrors &7800–&7BFF, byte for byte, at a fixed &400 offset. &7C00 specifically aliases &7800 — the very first byte of that block.

The PC-1500A drops in a full 2K×8 HM6116 at that same socket instead of the TC5514 pair — the same part already used for S0–S2 — which fully decodes all 11 address lines and gives &7C00–&7FFF genuinely independent storage for the first time. Declaring that newly-independent region the machine-language area is the natural next step; the interesting question is why the boundary is &7C01 rather than the round number &7C00.

What makes this a hard constraint rather than just an aliasing curiosity is that the PC-1500 and PC-1500A run the **identical** system ROM — not a ported or adapted variant. (The PC-1500 briefly shipped with earlier ROM revisions A01 and A03 before A04 became standard; the PC-1500A shipped with A04 from the start, and A04 is confirmed to run unmodified on both models. Whether A03 would run on a PC-1500A is untested.) A literal-operand search of the disassembly turned up no instruction referencing &7800 or &7C00 directly — the mechanism responsible reaches that address by computed, auto-incrementing addressing, not a literal operand. Tracing it down (via ROM disassembly, real-hardware testing, and the `pc1500emu` emulator) surfaces a confirmed, specific reason.

**The confirmed mechanism: the input-buffer-clear routine, and why the tokenizer needs its guarantee.** `INBUF_CLR_1` ($D02B, "Clear input buffers with 0D and initializes Input buffer pointers") sets X=&7BB0 and A=&0D, then falls into a generic fill loop (`DEL_DIM_VAR_4` at $D0B0: `SIN X` — store A at (X), increment X — looped `UL+1` times via `LOP UL,...`). The fill count is `UL=&50` (80) on A03/A04, so the loop runs 81 times, writing &0D to every address from &7BB0 up to and including **&7C00**. This runs on every input-buffer clear — confirmed live in the emulator with `pc1500emu`'s scriptable command pipe: POKE-ing an arbitrary value into &7C00 and then pressing CL or Enter reliably resets it back to &0D, matching the exact hands-on behavior observed on real PC-1500 and PC-1500A units — PEEK &7C00 always reads back 13 regardless of what was POKEd, on both real machines and the emulator.

That extra 81st byte matters because of how the line tokenizer consumes the buffer it fills. `TOK_INBUF_1`/`TOK_INBUF_2` ($F959/$F961) — the routine that tokenizes a typed line after Enter — starts at `INBUFPTR` (&7BB0) and walks forward with `LIN Y` in a loop, comparing each byte against `$27` (comment handling) and `$0D`, stopping only when it hits `$0D`. **This scan has no independent length bound** — termination depends entirely on encountering a `$0D` byte somewhere in memory. A line that completely fills the 80-byte buffer (&7BB0–&7BFF) with no `$0D` inside it would leave this scan nothing to stop it at &7BFF; the guaranteed &0D at &7C00 is what gives even a maximally-full 80-character line a guaranteed terminator immediately past the buffer.

So &7C00 isn't just at risk of aliasing — it's the **actively-used terminator byte one past the 80-byte input/display buffer**, re-stamped with CR on every buffer clear and read by the tokenizer's unbounded scan, on both models, by the exact same ROM code. That's the real, confirmed reason the PC-1500A's TRM withholds it from the machine-language area: a user ML program stored at &7C00 would be silently overwritten by this routine the next time the user returns to the ready prompt, and the tokenizer depends on it staying &0D.

**Why the fix works identically on the PC-1500, via the alias rather than despite it.** The ROM code is model-agnostic: it issues 81 sequential `SIN X` stores starting at &7BB0, oblivious to what's physically behind the top address. On the PC-1500A, &7C00 is genuine independent RAM, so the 81st write lands in its own byte. On the PC-1500, the TC5514 pair only decodes A0–A9, so &7C00 and &7800 share the same low-10-bit pattern and are physically the same SRAM cell (§2.3's mirroring) — the 81st write is electrically indistinguishable from a store to &7800. That means the exact byte the tokenizer's scan needs at "&7C00" is guaranteed &0D on the PC-1500 too, automatically, via the alias — with no model-specific code required. Sharp's fix doesn't need to special-case the PC-1500's aliasing; it works *because of* it, using one instruction sequence on both models. &7800 specifically is documented in this repo's own `LH5801-Assembly-Guide.md` memory map as the base of `CPU_STACK` (&7800–&784F, 80 bytes) — not generic filler, but the CPU's own return-address stack — which turns out to be exactly why the incidental overwrite there is safe; see below.

**Confirming this via the A01/A03 boundary.** A01's version of `INBUF_CLR_1` uses `UL=&4F` instead of `UL=&50` — one byte shorter, so its loop stops at &7BFF and never reaches &7C00/&7800 at all. This is confirmed directly by the project's own `Original_ROMs/A03-A01_Diff.txt`, which independently isolates this as the *only* byte difference in `INBUF_CLR_1` between A01 and A03: `$D037 $50→$4F`. On a PC-1500 running A01, a full 80-character line with no embedded `$0D` leaves the tokenizer's unbounded scan nothing to stop it at &7BFF — it runs into &7C00–&7FFF, the mirror of &7800–&7BFF, which holds real, documented state (the CPU stack at &7800–&784F, then system variables/BASIC state from &7860 onward per `LH5801-Assembly-Guide.md`'s memory map), not garbage; whether it finds a `$0D` quickly depends on what that state holds, and only running through the entire mirrored 2KB without one would carry it past &7FFF into Y2 (the &8000+ module/ROM area). A03/A04's one-byte extension closes this gap directly at its source. This lines up cleanly with the earlier explanation: the same fix, applied once in the shared ROM, closes the gap on the PC-1500A by writing directly to independent RAM at &7C00, and on the PC-1500 by writing to &7800 through the alias.

**Why the incidental overwrite of &7800 — and the A01 overrun risk it guards against — are both harmless in practice.** `LH5801-Assembly-Guide.md` documents the LH5801's stack pointer `S` as starting at `&784F` and *decrementing* on every push, so the CPU stack grows downward from &784F toward &7800. That makes &7800 the extreme floor of the 80-byte stack reserve — reachable only after roughly 40 nested two-byte pushes (subroutine calls/interrupts) with no intervening pops, a depth ordinary BASIC/ROM execution never approaches. More directly: `INBUF_CLR` (and the tokenizer scan it guarantees a terminator for) only ever runs when clearing the input buffer or returning to the READY prompt — precisely the moments the call stack is back at the top-level command loop, shallow, with `S` sitting at or near its base &784F. The one address this routine's incidental write reaches is, at the exact moment it writes there, never holding live stack data. The same logic bounds the A01 overrun risk from the paragraph above: even in the rare case of an unterminated 80-character line, the tokenizer's scan starts reading the stack region at exactly the same shallow-stack moment, so it's reading mostly-stale/idle stack bytes rather than an actively in-use call chain — not a guarantee of immediately finding `$0D`, but not a scan into meaningfully "live" data either.

Sharp didn't design two independent RAM expansions: they replaced small, oddly-sized parts (one HM6116 + two TC5514) with four of one cheap, standard, off-the-shelf chip, and exposed what that gave them beyond &7C00 — the one byte the shared ROM's input-buffer-clear routine still actively claims, as the tokenizer's guaranteed terminator. The pin-16/17/18 rewiring in §3 was the necessary side effect on the module-facing side of that swap; the machine-language area was the side effect on the system-RAM side, with &7C00 itself withheld because the identical ROM genuinely, repeatedly writes to it on both models.

Total PC-1500A physical RAM: 8192B (S0+S1+S2+S7, four HM6116) + 512B (unchanged display-driver RAM) = **8704B ≈ 8.5KB** — the figure the standard-RAM comparison in `LH5801-PU-PV-Signals.md` §8 refers to, distinct from the 6KB contiguous "standard user memory" figure that `MEM` actually reports.

---

## Appendix: Superseded Hypotheses

Three plausible-but-wrong hypotheses arose while researching §3–§4, kept here because each is the kind of thing a reasonable person would derive from partial evidence and get wrong the same way.

**"Sharp added the entire &7600–&8000 RAM chip and declared the leftover the machine-language area."** Plausible reading: since &7C01 sits inside a block adjacent to the display-buffer region, it's tempting to assume the ML area comes from claiming the *whole* &7600–&8000 range on a shared chip that also backs the display. This is wrong: &7000–&75FF is inhibited (not RAM at all), and &7600–&77FF belongs to the LCD driver chips specifically, not a general-purpose RAM chip shared with system memory (§2.2). The ML area is entirely within S7 (&7800–&7FFF), a separate block from the display region, and never involves display-buffer capacity at all.

**"A single, larger HM6264 (8K×8) chip replaces the PC-1500's HM6116+TC5514 combination, mapped into two non-contiguous CPU windows via internal address-line remapping."** This looked attractive because the totals matched exactly (8192 bytes = 6144B standard RAM + 2048B system RAM, with zero remainder) and because "one bigger chip" is a natural guess when total capacity increases cleanly. It's wrong: both a Sharp circuit block diagram and an independent teardown of a second PC-1500A unit confirm **four separate, ordinary HM6116 chips**, each with its own chip-select wired straight to one of the decoder's existing S0/S1/S2/S7 strobes — reusing one off-the-shelf part four times rather than introducing a differently-shaped chip that needs to answer two disjoint address windows. The lesson: matching totals is necessary but not sufficient evidence for a specific physical implementation when a decoder already provides one chip-select per block for free.

**"&7C01 (rather than &7C00) is a reserve-area convention, matching the same off-by-one pattern seen elsewhere in this document (e.g. `NEW &C5`)."** This looked attractive because the document already establishes a real, repeated pattern of "reserve up to and including a marker byte, then usable space starts one byte later," and &7C01 fits that shape numerically. It's wrong, or at least unmotivated: `NEW &C5`'s 197-byte reserve is a BASIC-interpreter convention describing where a *program* may safely start within a bank — it has no connection to why one specific *hardware* byte at the edge of the S7 block would need protecting. The confirmed explanation (§4.2) is that the shared ROM's input-buffer-clear routine (`INBUF_CLR_1`/`DEL_DIM_VAR_4`, $D02B/$D0B0) genuinely writes &0D to &7C00 on every buffer clear, on both models, as part of an 81-byte fill loop starting at &7BB0 — confirmed by ROM disassembly and by matching live POKE/PEEK behavior on real PC-1500/PC-1500A hardware and in `pc1500emu`. On the plain PC-1500, that same write incidentally also lands on &7800 (the TC5514 pair's missing 11th address line means the two addresses are the same physical cell), but the ROM's dependency on &7C00 is real and active, not merely a legacy aliasing risk. The rest of the newly-independent region, from &7C01 onward, is never touched by this or any other found routine, so it's safe to expose. The lesson: a numeric pattern matching a real convention elsewhere in the same system is suggestive, not sufficient, when a more specific hardware/firmware mechanism (here, an active OS buffer terminator, confirmed by tracing the actual write) directly explains the same number.
