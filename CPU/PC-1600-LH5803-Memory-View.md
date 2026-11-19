# PC-1600 LH5803 Memory View

Summary: How the LH5803 sees memory: same silicon, different address space; dual-processor hand-off.
Scope: PC-1600
Sources: cited inline in the text
Status: cited

> Split from `PC-1600-Memory-Architecture.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §1, §2, §2a, §3, §6, §7 → [PC-1600-Memory-Map.md](../Memory/PC-1600-Memory-Map.md); §4, §4a → [PC-1600-Program-Areas-and-NEW.md](../Memory/PC-1600-Program-Areas-and-NEW.md); §4b → [PC-1600-Module-Window-Layout.md](../Memory/PC-1600-Module-Window-Layout.md); §8 → [PC-1600-MODE0-MODE1.md](../Firmware/PC-1600-MODE0-MODE1.md).
> Split from `PC-1600-Memory-Bank-Switching.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §2 → [PC-1600-Bank-Switching.md](../Memory/PC-1600-Bank-Switching.md); §1, §3, §4, §5, §11, §12 → [PC-1600-Gate-Array-and-Chip-Selects.md](../Memory/PC-1600-Gate-Array-and-Chip-Selects.md); §9 → [PC-1600-IO-Ports.md](../IO-Ports/PC-1600-IO-Ports.md); §7, §7a, §7b, §10 → [PC-1600-Memory-Modules.md](../Expansion/PC-1600-Memory-Modules.md); §6 → [PC-1600-Transparent-Banking.md](../Firmware/PC-1600-Transparent-Banking.md).

## 5. The LH5803 View: Same Silicon, Different Address Space

The PC-1600 carries two CPUs sharing one bus (`PC-1600-LH5803-Memory-View.md` Part 8): the Z-80-compatible SC7852 (the machine's primary CPU — BASIC's own command loop runs here, always, per the note below) and an LH5803, present specifically to execute PC-1500-compatible code — genuine LH5801 assembly, either from `CLOAD`ed PC-1500 programs or from PC-1500-era peripheral ROMs like CE-150/CE-158. Only one CPU runs at a time — `ELH` (pin 58 on the 60-pin system bus, `PC-1600-Connectors.md` §4.0) selects which — but that exclusivity is a hardware bus-arbitration fact, not evidence for how long any given handoff lasts.

The TRM gives the LH5803's own memory map as a **separate figure**, not a re-labeling of the Z-80's — the LH5803 sees a plain, unbanked-from-its-own-perspective 64KB space (bank 0–3 shown, but see below for what "bank" means here):

| LH5803 address | Contents | Z-80-side equivalent |
|---|---|---|
| 0000–3FFF | Module Slot 1 / Module Slot 2 | Z-80's 8000–BFFF (Slot 1/2 RAM) |
| 4000–7FFF | Internal RAM (fixed, no banking) | Z-80's C000–FFFF, Bank 0 only |
| 8000–A000 | CE-158 ROM (when PVOUT=1) | same physical ROM chip as CE-158's Z-80-side mapping |
| A000–C000 | CE-150 ROM (when PVOUT=0) | same physical ROM chip as CE-150's Z-80-side mapping |
| C000–FFFF | Internal ROM (fixed) | Z-80's Bank-6-class system ROM (CS123-equivalent) |

This matches `PC-1600-LH5803-Memory-View.md` Part 8's existing summary table exactly (0000–3FFF = Z-80's 8000–BFFF; 4000–7FFF = Z-80's C000–FFFF; 8000–BFFF = CE-150/CE-158 by PVOUT; C000–FFFF = ROM), and the TRM figure adds the concrete sub-split of 8000–BFFF (CE-158 in the lower 8KB, CE-150 in the upper 8KB) and shows this "4 banks" (0–3) structure is really **2 module slots × 2 PVOUT states**, not a Port-31H-style page-bank system of its own — the LH5803 doesn't do the Z-80's four-independent-pages bank switching at all. Its 0000–3FFF is whichever Slot-1/Slot-2 RAM bank the Z-80 side last selected via Port 31H (the LH5803 rides on the same physical RAM chip-selects, RAM1/RAM2, that the Z-80 uses); its 4000–7FFF is unconditionally the internal RAM's Bank 0 (no LH5803-side equivalent of switching in Bank 1); its 8000–BFFF split is driven purely by PVOUT, the same physical bit Port 31H's b0 also drives for the Z-80's own page 0/3 select.

**Why this specific remapping.** The LH5803 is present to execute genuine PC-1500-compatible LH5801 machine code — user `ML`/`XCALL` programs, and peripheral-ROM-provided BASIC command implementations reached via the `CALLH`-class fallback (see the revised model below). Its memory map is therefore not an independent design — it's built to make the PC-1600's actual physical memory *look like a PC-1500's memory map from the LH5803's point of view*, address for address, wherever practical, so that code written against real PC-1500 absolute addresses keeps working unmodified. §6 makes this comparison explicit.

**Confirmed model of MODE0/MODE1, from the PC-1600's own German user manual (*Bedienungsanleitung*, §9.2, Appendix H).** Two earlier revisions of this document guessed at this mechanism from indirect evidence; the manual settles it directly, and the confirmed picture is different from both guesses:

- **`MODE0`/`MODE1` are officially called "Anzeige-Modi" (display modes)**, switched by the BASIC command `MODE` — and this is explicitly *not* the same thing as the physical `[MODE]` key, which the manual documents separately as a PRO/RUN/RESERVE edit-mode toggle. The manual itself anticipates the confusion: *"Die zwei Anzeige-Modi werden MODE 0 und MODE 1 genannt, was Sie vielleicht verwirren... mag."* ("The two display modes are called MODE 0 and MODE 1, which might confuse you...").
- **MODE 1 is 26×1: only the bottom of the four display lines is used**, specifically for PC-1500 program compatibility — confirming the display-restriction hypothesis raised earlier in this conversation. Character codes `&27`/`&5B`/`&5D` are also remapped to their PC-1500-specific meanings (insert symbol, root sign, etc.) while in MODE 1.
- **BASIC's command set and interpreter are Z-80-resident in both modes, at the dispatcher level.** Appendix H states plainly: *"BASIC-Programme, die auf dem PC-1500 geschrieben worden sind, laufen grundsätzlich auch auf dem PC-1600, sofern dieser im MODE 1 betrieben wird. Die überwiegende Mehrheit der BASIC-Befehle stimmt bei beiden Rechnern überein."* ("PC-1500-written BASIC programs generally also run on the PC-1600, provided it's run in MODE 1. The vast majority of BASIC commands agree between the two machines.") This is compatibility by *shared command set and adjusted behavior*, not by handing the interactive session to a separate interpreter.
- **`SETCOM` (and by extension, other peripheral-provided commands) genuinely dispatches to the attached peripheral's own ROM — confirmed by necessity, via a modern device.** `SETCOM` appears as one ordinary command in the PC-1600's own command list (Appendix G: *"SETCOM: Setzt Protokoll für serielles Interface"*), unlike the explicit `CALL`/`XCALL`-style split — meaning any per-peripheral dispatch is automatic (detected from what's physically attached, the same way boot-time module detection works, `PC-1600-Transparent-Banking.md` Part 6), not exposed in the syntax. This resolves what would otherwise be an open question: **CE-158X**, a modern recreation of the CE-158 with a modified ROM adding USB support (an additional serial port neither the real CE-158's original ROM nor the PC-1600's own native ROM could possibly have any knowledge of, since USB postdates both by decades), works correctly on a PC-1600 — including through `SETCOM`/`SETDEV` reaching its USB channel. That's only possible if those commands genuinely execute CE-158X's own (modified) ROM code when it's present; a fixed native PC-1600 implementation with hardcoded knowledge of the real CE-158's registers has no code path that could reach a port invented after the fact. So: the plain PC-1500's peripheral-ROM-precedence mechanism (`LH5801-PU-PV-Signals.md` §4–5 — a peripheral's own BASIC-command-table implementation takes precedence over the base ROM's) survives intact into the PC-1600, generalized through the `CALLH`-class dispatch — a peripheral's ROM can extend or override BASIC command behavior in ways the base PC-1600 firmware has no knowledge of, not just reproduce PC-1500-era behavior faithfully.
- **Genuine cross-CPU access is explicit and programmer-facing**, not inferred by any dispatcher: `CALL` (Z-80 machine program) vs. `XCALL` (LH-5801/3-coded machine program), `PEEK`/`POKE` (Z-80-managed address) vs. `XPEEK`/`XPOKE` (LH-5801-managed address), and the port equivalents `PEEK#`/`POKE#` vs. `XPEEK#`/`XPOKE#` — a full, confirmed table in Appendix E/H. This is the actual mechanism for touching the LH5803 side of the machine: a specific command, chosen by the programmer or already baked into a loaded PC-1500 program's tokenized bytecode, not a fallback triggered by an unrecognized command name.
- **MODE 1 and modules.** The manual says a module under 16KB must be present (CE-151, CE-155, CE-159 or CE-161) and that no module produces an error. The ROM disagrees: a module is **not** required, but if one is fitted it must be at most 16 KB (one bank). The ROM's gate (`MODE` → `RAMODSET` P0-B0 `163FH` → `PC15MAP` `1676H`) refuses only when S0 spans more than one module bank (`S0MTb` ≠ 5); with no module, S0 is internal RAM and `MODE 1` is accepted (§8).
- **Confirms, with the exact address range, what §3's earlier note could only infer architecturally:** Appendix H, "Inkompatibilität zum PC-1500A" — *"Der beim PC-1500A für den Anwender frei benutzbare Speicher im Adreßbereich &7C00 bis &7FFF steht dem Anwender beim PC-1600 nicht mehr zur Verfügung, weil dieser Bereich für Systemzwecke benötigt wird. Aus diesem Grunde können die Modelle PC-1500A und PC-1600 nicht als kompatibel angesehen werden."* ("The memory freely usable on the PC-1500A at `&7C00`–`&7FFF` is no longer available to the user on the PC-1600, because this range is needed for system purposes. For this reason, the PC-1500A and PC-1600 cannot be considered compatible [in this respect].") — the PC-1500A's own machine-language area (`PC-1500-Address-Decoding.md` §4) is explicitly, by name, reserved on the PC-1600, not merely "probably reserved by architectural necessity" as guessed earlier.

**Consequence for `MEM`:** the real-hardware test that prompted this section — a stock PC-1600 with a plain (non-vertical-banked, CE-163-class) 16KB `S0:`-expanded module in Slot 2 reporting **`MEM` = 28218 in both MODE 0 and MODE 1** — is now explained simply: `MEM` is native, always-Z-80-resident BASIC housekeeping, run by the identical routine regardless of which display mode is active. The identical figure isn't architecturally significant, just the same command computing the same thing every time.

The address-adjacency fact is still real and still explains why the *number itself* is what it is: Slot 2's window (Z-80 8000–BFFF, page 2) sits directly below internal RAM (Z-80 C000–FFFF, page 3) — `BFFF`+1 = `C000` — so a module that fits within one 16KB bank merges into one physically contiguous 32KB span with internal RAM and needs no page switching at all. (Larger merged spans do need it, and the ROM does it per access: see §3.1.) With fixed overhead (header + 197-byte reserve + 4096-byte work area) totaling either 4293 or 4550 bytes depending on which of §3's two conflicting baselines is used, paid once at the bottom of that span:

```
16384 − 4550 = 11834   (internal RAM alone — matches the real-hardware-anchored baseline)
32768 − 4550 = 28218   (16KB module + 16KB internal RAM, contiguous — matches the observed figure exactly)
```

Whether a 32KB+ `S0:` allocation (spanning two Z-80 banks, needing genuine dynamic bank-switching mid-array-access) behaves identically is settled in §3.1: it does. The ROM switches page 2 per variable access, and arrays larger than 16 KB work (measured, two CE-1600M).

**Correction on "4000–7FFF: fixed, no banking" — this does not mean flat, undifferentiated RAM.** The TRM figure this section is built on only resolves the LH5803's memory map down to 4000H/8000H-level bank boundaries — the same coarse granularity as the Z-80's own top-level figure in §2, not the fine S0–S7/V2/V3-level detail the PC-1500's own TRM chip-select tables give (`PC-1500-Address-Decoding.md` §2.2 and its two Chip-Select Table appendices). Absence of sub-decode *in this figure* is not evidence of absence *in the hardware*.

In fact it almost certainly isn't flat. Whatever Sharp adapted at the system-ROM level for PC-1600 integration (§ above), *user* PC-1500 programs still run at their original absolute addresses and expect the machine's low-level behavior to match — including code that writes the display buffer at `&7600–&774F` and touches the CPU stack/fixed variables from `&7800` up (`LH5801-Assembly-Guide.md`'s memory map — the real PC-1500's S6/S7 region, `PC-1500-Address-Decoding.md` §2.2–2.3). The PC-1600's *native* Z-80-side display path is entirely different hardware — I/O-port-mapped HD61202 controllers (ports 50–5BH, `PC-1600-IO-Ports.md` Part 9), not memory-mapped SC882G chips. Nothing about the PC-1600's own design puts real display hardware at address `&7600` in any CPU's memory map by coincidence — if a PC-1500 program writing to that literal address is going to produce anything on screen, *something* has to translate those writes into HD61202 I/O accesses. Two mechanisms are structurally possible and neither is confirmed by any source reviewed for this document:

1. A **hardware shim** in the SC-7852, watching LH5803 accesses to that address range and translating them to HD61202 I/O writes on the fly. (Partly what happens: the SC-7852 remaps LH5803 accesses with `LHA90`, pin 38, and port 30H b0 appears to send LH5803 display writes to the Z-80 for mirroring; one CE-158 routine is trapped wholesale, `PC-1600-LH5803.md` §6.1.)
2. A **software shim** — that range is ordinary RAM from the LH5803's side, and separate PC-1600 firmware (running in compat mode alongside/around the literal PC-1500 ROM code, not part of it) periodically copies it out to the HD61202 controllers.

Either way, the practical conclusion is the same: **the top slice of the LH5803's 4000–7FFF block is not generic, free capacity** — it's functionally playing the same role a real PC-1500's S6 (display buffer) and S7 (CPU stack, fixed variables, machine-language area) do, reserved by the compatibility requirement itself, not by anything visible in the coarse TRM bank map. This is corrected in the capacity comparison, §7.

**Partially confirmed, directly, since first writing the above.** The PC-1600's own German user manual, Appendix H, states outright that `&7C00`–`&7FFF` — the PC-1500A's machine-language area specifically — is *not* available to the user on the PC-1600, reserved instead "für Systemzwecke" (for system purposes), and that this is exactly why Sharp does not consider the PC-1500A and PC-1600 compatible on this point (quoted in full in §5). That confirms the S7-equivalent portion of the speculation above by name and address range. It does **not** independently confirm anything about the S6-equivalent display-buffer region (`&7600`–`&774F`) specifically, or say anything about *how* writes there (if they're still memory-mapped at all) reach the PC-1600's actual I/O-port-mapped HD61202 display hardware — that half of the speculation remains open.

---

## Part 8: Dual-Processor Architecture (Z-80 + LH-5803) (formerly Bank-Switching Part 8)

The second processor (LH-5803) provides PC-1500 compatibility.

### LH-5803 Memory Map

| Address Range | Contents |
|---------------|----------|
| 0000-3FFF | Same as Z-80's 8000-BFFF (S1/S2 modules) |
| 4000-7FFF | RAM 16KB (same as Z-80's C000-FFFF) |
| 8000-BFFF | CE-150 (PVOUT=0) or CE-158 (PVOUT=1) |
| C000-FFFF | ROM 16KB (CS123) |

### Key Differences from Z-80

- Addresses stored in reversed byte order (hi-lo vs Z-80's lo-hi)
- Bit b15 is inverted
- Both CPUs share the same bus -- cannot operate simultaneously
- One is always in HALT while the other runs

### Calling LH-5803 from Z-80

Set parameters at:
- **F002H:** 20 = no params, 30 = pass registers (F005-F00BH)
- **F00C/H:** Start address (LH-5803 notation)
- **F00EH:** Bank (00=RPV, 01=SPV)

Execute: `CALL 01C6H` (CALLH)

### LH-5803 Memory Enable Signals

| Signal | Pin | Function |
|--------|-----|----------|
| ME0 | 29 | Accesses 64KB area for program counter P and stack S |
| ME1 | 30 | Accesses second 64KB area for CPU data commands |

**PV signal** (pin 60): Internal flip-flop output, sent directly to PVOUT of SC7852. When Z-80 operates, PV floats and is pulled down internally.

---
