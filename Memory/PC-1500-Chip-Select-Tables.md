# PC-1500 / PC-1500A Chip-Select Tables

Summary: Decoder notation and the PC-1500 and PC-1500A chip-select tables, reproduced from the TRM.
Scope: PC-1500, PC-1500A
Sources: cited inline in the text
Status: cited

> Split from `PC-1500-Address-Decoding.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §1, §2, §4, Appendix: Superseded → [PC-1500-Address-Decoding.md](PC-1500-Address-Decoding.md); §5 → [PC-1500-RAM-Sizing-and-NEW.md](PC-1500-RAM-Sizing-and-NEW.md); §3 → [PC-1500A-Rewiring.md](../Expansion/PC-1500A-Rewiring.md).

## Appendix: Reading the Decoder Notation (1Y0, 2Y2, etc.)

§2.1–2.2's tables list each address block as, e.g., `Y0 (1Y0)`, `S0 (Y0)`, or `V2 (2Y2)`. This notation appears directly in the source TRM figure and is worth decoding once, since three different things are packed into it.

**The unmarked name is the signal name; the parenthesized name is the decoder pin.** Throughout this document, "S3," "Y1," "V2," and so on are the *logical* names used consistently regardless of model or physical implementation — this is what the rest of the document always refers to (the pin-rewiring discussion in §3, the CE-155 example). The bank-switching mechanics in `PC-1500-Bank-Switching.md` §4 and §9 also just say "S3" or "S5." The parenthesized form — `1Y0`, `Y0`, `2Y2` — is the actual output pin of the physical decoder chip that generates that signal. It only shows up in the reference tables in §2.1–2.2, where it matters which chip and which pin produce a given line.

**The overline (bar) means active-low.** A decoder output is asserted — meaning "this address range is selected" — by being driven *low*, and sits high otherwise. This is standard behavior for the 74139/74138 decoder family that Sharp's TC40H139F and TC40H138F belong to, and it's why these outputs wire directly into memory chips' select pins without an inverter in between: chip-select inputs are conventionally active-low too.

**The numeric prefix ("1Y0" vs. "2Y2") identifies which half of a dual decoder chip is being used — not two separate chips.** The TC40H139F is a *dual* 2-line-to-4-line decoder: one physical package contains two independent decoder circuits, and the 74139-family datasheet convention labels their outputs `1Y0–1Y3` (first internal decoder) and `2Y0–2Y3` (second internal decoder). Concretely:

- **Decoder half 1** of a single TC40H139F, fed by AD14/AD15, produces the top-level 16KB blocks `Y0 (1Y0)` through `Y3 (1Y3)` (§2.1).
- **Decoder half 2** of that *same physical chip* is reused elsewhere on the board to further split S6 into the two display-driver sub-windows: `V2 (2Y2)` and `V3 (2Y3)` (§2.2). This is the "second-stage decoder" mentioned there — the same IC, its other independent half, doing an unrelated job.

The TC40H138F (producing S0–S7) is a *single* 3-to-8 decoder — only one decoder circuit per chip — so its outputs carry no numeric prefix at all; there's nothing to disambiguate.

**Three columns applying to one address range means a cascaded decode tree, not three unrelated signals.** &7600–&76FF, for example, lists Y1, S6, and V2 together because each decoder stage's *enable* input is wired to the previous stage's output:

1. **Y1 (1Y1)** says "this address is somewhere in &4000–&7FFF" — true just enough to enable the next stage.
2. **S6 (Y6)**, enabled by Y1, narrows it to "somewhere in &7000–&77FF."
3. **V2 (2Y2)**, enabled by S6, narrows it one more step to specifically &7600–&76FF.

All three lines must be simultaneously low before the actual display-driver chip-select fires — each row only "counts" because the row above it already gated it on.

---

## Appendix: PC-1500A Chip-Select Table (TRM Figure, Reproduced)

Reproduced from the photographed TRM page described in §2.2/§2.1 — a bad scan, so treat this as a draft pending correction against the original. Merged cells reflect the source figure's own grouping (e.g. "STANDARD USER MEMORY" spanning S0–S2 as one label, not three separate ones); bars denote active-low, per the notation appendix above.

<table>
<thead>
<tr><th>Y-block</th><th>S-block</th><th>V</th><th>Address</th><th>Description</th></tr>
</thead>
<tbody>
<tr>
<td>Y0 (<span style="text-decoration:overline">1Y0</span>)</td>
<td></td><td></td>
<td>0000H–<br>3FFFH</td>
<td>OPTIONAL USER MEMORY</td>
</tr>
<tr>
<td rowspan="10">Y1 (<span style="text-decoration:overline">1Y1</span>)</td>
<td>S0 (<span style="text-decoration:overline">Y0</span>)</td><td></td>
<td>4000H–<br>47FFH</td>
<td rowspan="3">STANDARD USER MEMORY</td>
</tr>
<tr>
<td>S1 (<span style="text-decoration:overline">Y1</span>)</td><td></td>
<td>4800H–<br>4FFFH</td>
</tr>
<tr>
<td>S2 (<span style="text-decoration:overline">Y2</span>)</td><td></td>
<td>5000H–<br>57FFH</td>
</tr>
<tr>
<td>S3 (<span style="text-decoration:overline">Y3</span>)</td><td></td>
<td>5800H–<br>5FFFH</td>
<td rowspan="3">OPTIONAL USER MEMORY</td>
</tr>
<tr>
<td>S4 (<span style="text-decoration:overline">Y4</span>)</td><td></td>
<td>6000H–<br>67FFH</td>
</tr>
<tr>
<td>S5 (<span style="text-decoration:overline">Y5</span>)</td><td></td>
<td>6800H–<br>6FFFH</td>
</tr>
<tr>
<td rowspan="3">S6 (<span style="text-decoration:overline">Y6</span>)</td>
<td></td>
<td>7000H–<br>75FFH</td>
<td>INHIBITED</td>
</tr>
<tr>
<td>V2 (<span style="text-decoration:overline">2Y2</span>)</td>
<td>7600H–<br>76FFH</td>
<td rowspan="3">STANDARD USER AND SYSTEM MEMORY<br><small>(nested annotation, aligned with the S7 row below: <b>MACHINE LANGUAGE AREA (7C01H–7FFFH)</b>)</small></td>
</tr>
<tr>
<td>V3 (<span style="text-decoration:overline">2Y3</span>)</td>
<td>7700H–<br>77FFH</td>
</tr>
<tr>
<td>S7 (<span style="text-decoration:overline">Y7</span>)</td><td></td>
<td>7800H–<br>7FFFH</td>
</tr>
<tr>
<td>Y2 (<span style="text-decoration:overline">1Y2</span>)</td>
<td></td><td></td>
<td>8000H–<br>BFFFH</td>
<td>CE-150: system program, I/O port<br>CE-153: I/O port<br>CE-158: system program</td>
</tr>
<tr>
<td>Y3 (<span style="text-decoration:overline">1Y3</span>)</td>
<td></td><td></td>
<td>C000H–<br>FFFFH</td>
<td>PC-1500A: system program, I/O port<br>CE-158: I/O port, UART</td>
</tr>
</tbody>
</table>

*Footnote in the source: "S0–S7, V2, and V3 are applicable only for the ME0 area." The V3 row's decoder pin is `2Y3` — the original address-map scan showed V3 also labeled `2Y2` (the same as V2), which is a genuine error in that source table, not a scan-reading problem: confirmed against the separate "Chip select circuit for the PC-1500A" schematic (TRM p.163), which explicitly shows two distinct NAND gates driven by `2Y2` and `2Y3` respectively, producing "To Display chip 1,3" and "To Display chip 2,4."*

**Further confirmed by that same schematic** (TC40H139F + TC40H138F chip-select circuit, TRM p.163):
- TC40H138F's select inputs are wired exactly as expected: A=AD11, B=AD12, C=AD13. Its enables are G2A̅ = Y1 (1Y1, the &4000–&7FFF block), matching §2.2's "active only while Y1 is asserted", and **G1 = ME0**. An earlier revision of this bullet put Y1 on G1. With ME0 on G1, every S-strobe and Y7 is ME0-only; §2.4 covers this.
- The system ROM chip's designation is legible here as **CS613128F** — converging with the "SC61328F"/"SC61329F"/"SC613128" readings from other low-quality sources elsewhere in this document; all are almost certainly the same part, read slightly differently off different scans.
- **LH5811** (I/O port) is confirmed again as a direct schematic destination — consistent with teardown of this specific unit, though see §2.1 for why LH5810 also appears in older Sharp material.
- **Y7 feeds "System RAM" directly**, consistent with §2–4 throughout. Y6 (the S6 block, &7000–&77FF) separately feeds a NAND gate together with a signal labeled **WEX**, whose output goes to the I/O port — a Sharp Service Manual excerpt for the PC-1500 describes this exact mechanism in words: *"With low state of AD11 and high state of AD12 and AD13, S6 goes to the low state to receive the interrupt input from an option into the I/O port (7000~77FF address setup)."* This is a legitimate function spanning the *entire* S6 block, not something specific to any sub-range within it — see the PC-1500 Chip-Select Table appendix below for why &7000–&75FF specifically is the part marked "redundant," which turns out to be a separate, unrelated mechanism.

---

## Appendix: PC-1500 Chip-Select Table (TRM Figure, Reproduced)

Same TRM figure format as the PC-1500A table above, this one for the plain PC-1500. Reproduced from a photographed TRM page; treat as a draft pending correction against the original.

<table>
<thead>
<tr><th>Y-block</th><th>S-block</th><th>V</th><th>Address</th><th>Description</th></tr>
</thead>
<tbody>
<tr>
<td>Y0 (<span style="text-decoration:overline">1Y0</span>)</td>
<td></td><td></td>
<td>0000H–<br>3FFFH</td>
<td>OPTIONAL USER MEMORY</td>
</tr>
<tr>
<td rowspan="11">Y1 (<span style="text-decoration:overline">1Y1</span>)</td>
<td>S0 (<span style="text-decoration:overline">Y0</span>)</td><td></td>
<td>4000H–<br>47FFH</td>
<td>STANDARD USER MEMORY</td>
</tr>
<tr>
<td>S1 (<span style="text-decoration:overline">Y1</span>)</td><td></td>
<td>4800H–<br>4FFFH</td>
<td rowspan="5">OPTIONAL USER MEMORY</td>
</tr>
<tr>
<td>S2 (<span style="text-decoration:overline">Y2</span>)</td><td></td>
<td>5000H–<br>57FFH</td>
</tr>
<tr>
<td>S3 (<span style="text-decoration:overline">Y3</span>)</td><td></td>
<td>5800H–<br>5FFFH</td>
</tr>
<tr>
<td>S4 (<span style="text-decoration:overline">Y4</span>)</td><td></td>
<td>6000H–<br>67FFH</td>
</tr>
<tr>
<td>S5 (<span style="text-decoration:overline">Y5</span>)</td><td></td>
<td>6800H–<br>6FFFH</td>
</tr>
<tr>
<td rowspan="3">S6 (<span style="text-decoration:overline">Y6</span>)</td>
<td></td>
<td>7000H–<br>75FFH</td>
<td>INHIBITED</td>
</tr>
<tr>
<td>V2 (<span style="text-decoration:overline">2Y2</span>)</td>
<td>7600H–<br>76FFH</td>
<td rowspan="3">STANDARD USER AND SYSTEM MEMORY (1.5K)<br><small>(spans 7600H–7BFFH: V2, V3, and the lower half of S7)</small></td>
</tr>
<tr>
<td>V3 (<span style="text-decoration:overline">2Y3</span>)</td>
<td>7700H–<br>77FFH</td>
</tr>
<tr>
<td rowspan="2">S7 (<span style="text-decoration:overline">Y7</span>)</td><td></td>
<td>7800H–<br>7BFFH</td>
</tr>
<tr>
<td></td>
<td>7C00H–<br>7FFFH</td>
<td>INHIBITED</td>
</tr>
<tr>
<td>Y2 (<span style="text-decoration:overline">1Y2</span>)</td>
<td></td><td></td>
<td>8000H–<br>BFFFH</td>
<td>CE-150: system program, I/O port<br>CE-153: I/O port<br>CE-158: system program</td>
</tr>
<tr>
<td>Y3 (<span style="text-decoration:overline">1Y3</span>)</td>
<td></td><td></td>
<td>C000H–<br>FFFFH</td>
<td>PC-1500: system program, I/O port<br>CE-158: I/O port, UART</td>
</tr>
</tbody>
</table>

*Footnote in the source: "S0–S7, V2, and V3 are applicable only for the ME0 area." Two typos in Sharp's original table are corrected here rather than reproduced: the Y2 row's end address is printed as `8FFFH` (implying a 4KB block, inconsistent with the fixed 16KB Y-block architecture established throughout this document) and is given here as `8000H–BFFFH`; V3's decoder pin is printed as `2Y2` (duplicating V2's) and is given here as `2Y3`, per the same reasoning and schematic evidence as the PC-1500A table above. Both are confirmed typos in the source document itself, not scan-reading errors — kept corrected rather than reproduced faithfully.*

**The key structural difference from the PC-1500A table**: only the *upper half* of S7 (&7C00–&7FFF) is marked **INHIBITED** here; &7600–&7BFF (V2, V3, and the lower half of S7) is a single 1.5K "standard user and system memory" region, per the TRM memory-map table on p.93. There is no machine-language-area annotation on the PC-1500 at all. §2.3 explains the inhibited half in hardware terms: the TC5514 pair's missing 11th address line means &7C00–&7FFF mirrors &7800–&7BFF, so exposing the upper half as independent user memory would let a write silently corrupt whatever system data occupies the same aliased cell. "Inhibited" here means "unsafe for general use," not "physically unpopulated."

**Independently confirmed by a second Sharp source.** A Sharp Service Manual for the PC-1500 (a different document from the TRM table reproduced above) includes its own memory-map diagram, which marks &7C00–&7FFF with diagonal hatching and the caption **"Inhibit to use by redundancy"** — Sharp's own term for exactly the address-line-aliasing mechanism derived independently in §2.3. The same hatching and caption also cover &7000–&75FF (see below) — Sharp uses one label for both mirrored regions.

**Confirmed by the PC-1500's own "Chip select circuit" schematic** (same TC40H139F + TC40H138F structure as the PC-1500A, now available in a clean scan):
- S0's destination is labeled **"To RAM3 (TC5517AF)"** — a different part number than the HM6116 identified by teardown and the text-sourced chip description in §2.3. Both are 2K×8 CMOS SRAM and functionally interchangeable; this is most likely Sharp's official BOM reference designator vs. whichever second-sourced part actually shipped in a given production run, not a contradiction.
- The line feeding "RAM 1, 2" is labeled **"To RAM 1, 2 (TC5514P)"** — confirms the exact part number (including the "P" package suffix) for the system-RAM pair identified in §2.3.
- **CS613128F** (ROM) and **LH5810** (I/O port) both appear again — LH5810, not LH5811 as an earlier revision of this section stated from a harder-to-read scan; see §2.1 for why both parts are genuinely correct, just from different production eras.
- S6's own select condition is spelled out precisely: "with low state of AD11 and high state of AD12 and AD13, S6 goes to the low state" — confirming A=AD11 (least significant), B=AD12, C=AD13 (most significant) for the TC40H138F's select inputs, consistent with binary index 6 = 110 (C,B,A).

**The V2/V3 display-RAM mirroring mechanism, precisely.** The same Service Manual spells out exactly how V2/V3 are generated, resolving the mirroring question raised earlier in this document:
- The second TC40H139F decoder half (producing 2Y2/2Y3, i.e. V2/V3) is enabled ("2G active") only when S6 (Y6) is selected.
- Its select inputs are **2A = AD8** and **2B = DME0** (the I/O port controller's ME0 enable for slow, dynamic memory, see §2.4; not a raw address bit) — not AD9 or AD10, which is where the "narrow one more level" pattern used everywhere else in this document (§2.2's cascaded decode) would have predicted them to be.
- V2 fires when AD8 is low and DME0 is high; V3 fires when AD8 is high and DME0 is high.

Because AD9 and AD10 are never examined anywhere in this chain — not by S6's own selection (already narrowed to the whole 2KB block by AD11–AD13 alone) and not by the V2/V3 sub-decode (only AD8 and DME0) — the V2/V3 pattern repeats identically across all four 512-byte quarters of the 2KB S6 block: the "real" occurrence at &7600–&77FF, plus mirrored copies at &7000–&71FF, &7200–&73FF, and &7400–&75FF. This is exactly the "Inhibit to use by redundancy" hatching on the memory-map diagram, and it means the earlier explanation in this document — that &7000–&75FF is inhibited *because* it's where the WEX-qualified I/O port interrupt access happens — was wrong. That WEX/I-O-port mechanism is real (see next paragraph) but applies uniformly to the *entire* &7000–&77FF range, hatched or not, so it can't be what distinguishes the hatched sub-range from the display-active one. The display-RAM mirroring is the actual, distinguishing cause.

**S6's separate, legitimate function.** The same source states S6's purpose directly: *"With low state of AD11 and high state of AD12 and AD13, S6 goes to the low state to receive the interrupt input from an option into the I/O port. (7000~77FF address setup)"* — S6, combined with a signal labeled **WEX** through a NAND gate, lets an optional external peripheral's interrupt line reach the I/O port controller. This is a real, intentional function of the whole S6 block, coexisting with (not explaining) the display-RAM mirroring described above — accessing anywhere in &7000–&77FF both potentially touches the (mirrored, for 3/4 of the range) display RAM *and* participates in this interrupt-forwarding path. "WEX" most plausibly stands for something like "write enable, external," though this is speculation, not a sourced expansion.

---
