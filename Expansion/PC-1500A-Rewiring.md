# PC-1500 to PC-1500A Pin Rewiring

Summary: Why and how the PC-1500A rewired the expansion connector; the CE-155 worked example; why only 4 KB.
Scope: PC-1500, PC-1500A
Sources: cited inline in the text
Status: cited

> Split from `PC-1500-Address-Decoding.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §1, §2, §4, Appendix: Superseded → [PC-1500-Address-Decoding.md](../Memory/PC-1500-Address-Decoding.md); §5 → [PC-1500-RAM-Sizing-and-NEW.md](../Memory/PC-1500-RAM-Sizing-and-NEW.md); Appendix: Reading, Appendix: PC-1500A Chip, Appendix: PC-1500 Chip → [PC-1500-Chip-Select-Tables.md](../Memory/PC-1500-Chip-Select-Tables.md).

## 3. The Expansion Connector and the PC-1500 → PC-1500A Pin Rewiring

### 3.1 What changed

The PC-1500 exposes its expansion bus on a 40-pin edge connector (confirmed by physical pin count on a real PC-1500A; full 40-pin table, plus the PC-1600's slot connectors, in `PC-1500-Connectors.md`). Four pins carry different signals depending on the model:

| Pin | PC-1500 signal | PC-1500A signal |
|---|---|---|
| 5 | S4 (&6000–&67FF) | NC |
| 16 | S1 (&4800–&4FFF) | S3 (&5800–&5FFF) |
| 17 | S2 (&5000–&57FF) | S4 (&6000–&67FF) |
| 18 | S3 (&5800–&5FFF) | S5 (&6800–&6FFF) |

This is a **connector pinout change, not a change to the decoder itself.** &5800–&5FFF is called S3 on both models — the TC40H138F's own address-to-strobe mapping doesn't move. What moves is which physical connector pin a given strobe is routed to. A module whose hardware is hard-wired to a specific physical pin therefore sees a different named strobe (and needs a different POKE address) depending on which machine it's plugged into, even though its own circuitry is completely unchanged.

### 3.2 Why: the CE-155 worked example

The CE-155 is a plain 8KB RAM module, useful here because it has no bank-switching logic of its own — just fixed chip-select wiring, which makes the effect of the pin reassignment directly visible.

**On the PC-1500:**
- &3800–&3FFF (2KB) — the top of the module's own internal &0000–&3FFF window, gated by YO (pin 4), entirely internal to the module slot.
- &4800–&5FFF (6KB) — three external chip-select pins: pin 16 (S1), pin 17 (S2), pin 18 (S3).

Built-in RAM occupies only &4000–&47FF (S0, 2KB) — exactly the gap between the module's two windows. Module (8KB) + built-in (2KB) tile the address space with no gaps or overlap.

**How the module narrows YO's 16KB down to just its own 2KB.** Three of CE-155's four RAM chips get an already-narrowed, individually-dedicated chip-select pin straight from the mainboard (S1, S2, S3) — no extra decode logic needed. The fourth lives inside the module's own raw &0000–&3FFF (YO) allocation, a 16KB window with no pre-narrowing from the mainboard side. CE-155 solves this the same way the mainboard solves the analogous problem for S0–S7: an onboard 138-family decoder takes AD11–AD13 on its select inputs (producing its own local Y0–Y7, exactly mirroring the mainboard's own S0–S7 decoder design) and YO on one of its enable inputs — gating the whole decoder active only while the CPU is actually addressing this module's slot. The chip is selected by (module's own decoded) Y7 specifically, the last of the eight possible 2KB sub-positions, landing exactly on &3800–&3FFF. Because the select logic and the enable logic are on separate pins of the same chip — matching how the mainboard's own decoder separates AD11–AD13 (select) from Y1 (enable), §2.2 — the module correctly restricts itself to just its 2KB allocation rather than mirroring across the other 14KB of its YO window or, worse, responding to the same AD11–AD13 pattern anywhere else in the 64KB address space.

**On the PC-1500A**, the CE-155's wiring is physically unchanged — it has no idea which model it's in. But pins 16/17/18 now carry S3/S4/S5 instead of S1/S2/S3, so the identical module now decodes:
- &3800–&3FFF (2KB) — unchanged, still YO-gated.
- &5800–&6FFF (6KB) — pin 16 → S3, pin 17 → S4, pin 18 → S5.

Total capacity is still exactly 8KB — the module's second window just slides up by 4KB. This is confirmed directly by the PC-1500A's own TRM decode table (§2.2): S0–S2 are labeled "standard user memory" and S3–S5 "optional user memory" — the same category used for module-facing blocks on the PC-1500.

**The cause:** built-in RAM on the PC-1500A grew to occupy S1 and S2, which used to be (and on the PC-1500 still are) driven out to external modules via pins 16–18. Left unchanged, a CE-155 in a PC-1500A would try to decode RAM at addresses the mainboard's own built-in RAM chips were now also driving — a bus conflict. Sharp's fix cost nothing on the module side: reroute which strobes reach those three physical pins so the module's fixed 3-pin skeleton lands on the next three free blocks (S3/S4/S5) instead.

This also explains why pin 18 specifically ends up as the CE-163's bank-select trigger on both models (see `PC-1500-Bank-Switching.md` §9): whichever strobe lands on pin 18 is, by construction, always the *last* of the module's three "extra" 2KB blocks — structurally no different from S1/S2, just conventionally the one banking modules commandeer as a side-channel trigger instead of using for storage.

### 3.3 Why the shift could only be 4KB

The direct cause is simpler than a decoder-availability argument: the PC-1500A has exactly **four** identical RAM chips (§2.3 — three "User RAM" + one "System RAM," all HM6116, confirmed by the block diagram). One of those four is not optional. S7 has to be populated by *something*, because fixed, ROM-referenced system pointers and variables physically live there (§4) — there is no version of this machine that skips populating S7. That leaves exactly three chips free for standard/expandable user RAM, and three chips wired to three chip-selects lands on exactly S0+S1+S2 — 6KB, not more, because there was never a fourth chip available to spend on S3. Extending standard RAM into S3 wasn't merely inconvenient for the module-facing pin rewiring; there was no fifth chip to do it with in the first place.

This is also consistent with (and independently confirmed by) a decoder-availability argument: had built-in RAM absorbed S3 too, a CE-155-class module's pins 16/17/18 would need to shift one block further, into S4/S5/**S6**. But S6 is not an ordinary block — &7000–&75FF is inhibited outright, and &7600–&77FF is committed to display-driver RAM (§2.2). There is no fourth free ordinary block to shift into. The 3-pin rewiring scheme works for exactly one 4KB (2-block) shift, because the block immediately past the shifted-to window is off-limits twice over. Both explanations point at the same 6KB boundary; the chip-count argument is the more direct cause, since it doesn't depend on Sharp having *wanted* to go further and being blocked — there simply wasn't a fourth chip on the table to try.

This is confirmed against real hardware: a stock PC-1500A reports `MEM` = 5946. Built-in contiguous RAM (S0+S1+S2) is 6144 bytes. `NEW` on the PC-1500A defaults to `NEW &C5` (197 decimal) rather than `NEW 0` — the first 197 bytes of the RAM area are a reserve area, not available to BASIC programs. 6144 − 197 = 5947, one byte off from the reported 5946 — within the documented `MEM` = `RAM_END − BASPRG_END` inclusive/exclusive rounding (see `PC-1500-BASIC-Pointers.md` §7).

---
