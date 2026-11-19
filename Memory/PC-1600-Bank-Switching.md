# PC-1600 Bank Switching

Summary: Port 31H bank register, truth tables, memory map by bank, auxiliary ports, the ~77 KB maximum.
Scope: PC-1600
Sources: - Service_Manual.pdf -- hardware architecture, schematics, gate array, slot pinouts - SHARP-PC1600-Systemhandbuch.pdf -- firmware, OS calls, module headers, software
Status: cited

> Split from `PC-1600-Memory-Bank-Switching.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §8 → [PC-1600-LH5803-Memory-View.md](../CPU/PC-1600-LH5803-Memory-View.md); §1, §3, §4, §5, §11, §12 → [PC-1600-Gate-Array-and-Chip-Selects.md](PC-1600-Gate-Array-and-Chip-Selects.md); §9 → [PC-1600-IO-Ports.md](../IO-Ports/PC-1600-IO-Ports.md); §7, §7a, §7b, §10 → [PC-1600-Memory-Modules.md](../Expansion/PC-1600-Memory-Modules.md); §6 → [PC-1600-Transparent-Banking.md](../Firmware/PC-1600-Transparent-Banking.md).

**Sources:**
- `Service_Manual.pdf` -- hardware architecture, schematics, gate array, slot pinouts
- `SHARP-PC1600-Systemhandbuch.pdf` -- firmware, OS calls, module headers, software

---

## Part 2: Memory Map and Bank Switching Mechanism

The Z-80 has 16 address lines = 64KB address space, divided into four 16KB pages. Bank switching expands this to 320KB across 8 banks (Bank 0--7).

### Port 31H (IOW MAP / IOR MAP) -- The Primary Bank Select Register

Writing to Z-80 I/O port 31H selects which bank appears in each page:

| Bit | Function |
|-----|----------|
| b0 | Bank select for 0000-3FFF **only** (1 bit, independent of b7 below) |
| b1 | Bank select for 4000-7FFF, LSB of the 3-bit field b3:b2:b1 |
| b2 | Bank select for 4000-7FFF, middle bit |
| b3 | Bank select for 4000-7FFF, MSB |
| b4 | Bank select for 8000-BFFF, LSB of the 3-bit field b6:b5:b4 |
| b5 | Bank select for 8000-BFFF, middle bit |
| b6 | Bank select for 8000-BFFF, MSB. (The LHS1/LHS2/LHS3 remap is bit 6 of Port **3CH**, not this bit -- Part 4.) |
| b7 | Bank select for C000-FFFF **only** (1 bit, independent of b0 above) |

**The bank lines PT / PU / PVOUT are not register bits.** The SC-7852 has three bank-signal outputs (pins 5–7: PT, PU, PVOUT) for eight register bits. They output the **bank number of the page being accessed**, MSB first: PT = bit 2, PU = bit 1, PVOUT = bit 0 of that bank number. So a 4000–7FFF access puts b3/b2/b1 on PT/PU/PVOUT, an 8000–BFFF access puts b6/b5/b4 there, and a 0000–3FFF or C000–FFFF access drives only PVOUT (b0 or b7). This is Sharp's own table (TRM §7.2.1, "SC-7852 Access Memory Areas and Contents of I/O Port 31H", PDF p.232), which has PT/PU/PVOUT output columns for every page. (Its page-2 bank-7 row prints PVOUT = 0, a misprint.) It is also what the peripherals need: the CE-1600P selects its ROM on PT high / PU low and uses PV to pick bank 4 or 5 (`PC-1600-CE-1600P-Printer-Plotter.md` §1.2.2), and the memory modules use PVOUT as the page-2 LSB (Part 7). An earlier revision of this table named b1 "PU" and b2 "PT"; that naming is wrong. While the LH-5803 runs, PVOUT carries the LH-5803's PV instead (Part 8).

**Correction (2026):** an earlier revision described b0/PVOUT as governing *both* 0000-3FFF and C000-FFFF together, and had PVOUT as a fourth input to the 4000-7FFF and 8000-BFFF bank number — both self-contradictory with the separate "b7 selects C000-FFFF" line. The **PC-1600 Technical Reference Manual's own §7.2.1 table** ("SC-7852 memory-access spaces and contents of I/O port 31H") settles it: each page uses one exact, non-overlapping bit field — **b0** alone for 0000-3FFF (bank 0/1), **b3:b2:b1** for 4000-7FFF (bank 0-7), **b6:b5:b4** for 8000-BFFF (bank 0-7), **b7** alone for C000-FFFF (bank 0/1); no bit is shared between pages. (The TRM table carries the same "C"-for-"4" typo in the bank-4 row that the truth tables below note.) The corrected model above and the two truth tables reflect this; an independent emulator implementation agrees (`README.md` — *Sources & validation*). Treat the four-independent-fields model as settled.

**Example** (from Systemhandbuch):

```asm
3E 2E    LD A,2EH       ; = 0010 1110 binary
D3 31    OUT (31H),A    ; b4-b6=010: 8000-BFFF -> Bank 2
                        ; b1-b3=111: 4000-7FFF -> Bank 7
```

### Bank Selection Truth Tables

**Address range 0000-3FFF (Page 0):**

| b0 | Selected Bank |
|----|---------------|
| 0 | Bank 0 (PVOUT=0) |
| 1 | Bank 1 (PVOUT=1) |

**Address range 4000-7FFF (Page 1) — corrected, see note above:**

| Bank | b3 (→ PT) | b2 (→ PU) | b1 (→ PVOUT) |
|------|----|---------|---------|
| 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 1 |
| 2 | 0 | 1 | 0 |
| 3 | 0 | 1 | 1 |
| 4 | 1 | 0 | 0 |
| 5 | 1 | 0 | 1 |
| 6 | 1 | 1 | 0 |
| 7 | 1 | 1 | 1 |

Plain 3-bit binary value of b3:b2:b1; b0 not involved. The arrows show which bus line carries each bit during a 4000–7FFF access. (The original table's "C" row is corrected to "4" here — it was a straight binary-count table miscopied with a stray hex digit.)

**Address range 8000-BFFF (Page 2) — corrected, see note above:**

| Bank | b6 | b5 | b4 |
|------|----|----|----|
| 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 1 |
| 2 | 0 | 1 | 0 |
| 3 | 0 | 1 | 1 |
| 4 | 1 | 0 | 0 |
| 5 | 1 | 0 | 1 |
| 6 | 1 | 1 | 0 |
| 7 | 1 | 1 | 1 |

Plain 3-bit binary value of b6:b5:b4; b0–b3 not involved. During an 8000–BFFF access PT/PU/PVOUT carry b6/b5/b4 (the TRM table's PT/PU/PVOUT columns are bus outputs, not extra inputs).

**Address range C000-FFFF (Page 3):**

| b7 | Selected Bank |
|----|---------------|
| 0 | Bank 0 |
| 1 | Bank 1 |

### Memory Map by Bank

| Address Range | Bank 0 | Bank 1 | Bank 2 | Bank 3 |
|---------------|--------|--------|--------|--------|
| 0000-3FFF | System ROM (CS001) **NEVER SWITCHED OUT** | (Slot 2) | -- | -- |
| 4000-7FFF | System ROM (BASIC, Editor) | Slot 1b or Slot 2a when remapped (`SLOT1MAP`/`SLOT2MAP`) † | -- † | System ROM (CS24; b2 of Port 3DH selects Bank 3b, the chip's other 16 KB) |
| 8000-BFFF | Slot 1a (RAM2) | Slot 1b (RAM2) | Slot 2a (RAM1) | Slot 2b (RAM1) |
| C000-FFFF | Internal 16KB RAM (RAM3) | **`b7`=1: open.** The TRM §7.2.1 table only lists `b7` as a "bank 0/1" select for the page, and no Sharp manual reviewed for this project (TRM, Service Manual, German user manual) says what bank 1 holds. The chip-select table (Part 4) gives **RAM3** for C000–FFFF **Bank 0** only, and no other internal chip select covers C000–FFFF on the Z-80 side, so nothing on the mainboard answers when `b7`=1. Whether a device on the 60-pin system bus can respond there, and which bus signal would tell it to, is undocumented. It is also a rarely-exercised path — `b7`=1 swaps out the F000–FFFF IOCS/BASIC work area (`PC-1600-Work-Area-Map.md`), so the firmware could only use it transiently. | -- | -- |

**† A memory-bay card never decodes a 4000–7FFF access itself — confirmed at schematic level.** (Bank 1 there holds slot RAM only through the SC7852's Port 3CH remap below; Bank 2 is empty in Sharp's own map, TRM §7.2.1.) Part 4's chip-select table decodes the entire 4000–7FFF window with **CS24** alone (SC7852 pin 45), and Part 12 wires CS24 only to the internal Memory-PWB ROM (IC5) — it never reaches the slot connectors. The **CE-1600M schematic** (Sharp's own 32KB RAM module, Part 7) and the **CE-1620M schematic** (Sharp's 32KB ROM cartridge for the memory bay) both tie their chip-enable to connector **pin 4 (RAMSN = RAM1#/RAM2#)**, which the SC7852 asserts only for the **8000–BFFF** window. Neither module has any connector signal telling it a 4000–7FFF access is in progress, and neither wires PU (pin 3) or PT (pin 19) at all. Memory-bay module headers are at 8000H/A000H/B000H (Part 6), i.e. page 2, matching. The one concrete 4000–7FFF ROM device, the CE-1600P (bank 4), is a **60-pin system-bus** unit. The firmware's "Page-1 module / EXROM at offset 4000H or 6000H, banks 1–7" machinery (Part 6: F0AEH/F0AFH bitmaps, EXROM1–EXROME, `CALL 02DFH` Creg 01–0E) is real but belongs to the **60-pin system bus**, not the 40-pin memory slots. **For an emulator: memory-slot connectors are consulted only for 8000–BFFF accesses; never route 4000–7FFF through them.** (PT/PU/PVOUT carry the bank number of the page being accessed — Part 2. The 32KB memory modules use only PVOUT, which on an 8000–BFFF access is b4, the LSB of that bank field. See Part 7's connector table.)

Additional banks in 4000-7FFF:

| Bank | Contents |
|------|----------|
| 3b | Hidden BASIC ROM: the second half of the 32 KB CS24 chip, a sub-bank of Bank 3 selected by Port 3DH bit b2 = 0 (see *Auxiliary Bank Control Ports*). **Confirmed on real hardware** by `../../PC-1600-ROM/dumper/pc1600-rom-dumper.asm`; the captured `PC1600-P1-B3B.BIN` is distinct from Bank 3's content. Early dumps read Bank 3 here because the dumper wrote Port 3DH without updating the firmware's copy at F07DH. The IM2 interrupt entry (`INTHND`, P0-B0 `082CH`, taken by the keyboard scan / 1/64 s tick) saves F07DH, forces 3DH = 04H to run the dispatcher in bank 3, then restores Port 3DH **from the saved F07DH value** — so after the first interrupt the port was back at 04H (Bank 3). The firmware itself always writes both (`LD (F07DH),A` / `OUT (3DH),A`, e.g. `ROMSELN` 08A5H, `SELJROM` 077EH), and the dumper now does the same. **Write F07DH together with Port 3DH and the selection survives interrupts and IOCS calls** (`RST 18H`/`BANKJP` 0A92H saves and restores 31H and F07DH the same way). BANKSET (08E7H) touches only Port 31H, never 3DH. |
| 4 | CE-1600P Plotter/Centronics ROM |
| 5 | CE-1600P Floppy (5000-5FFF) / Cassette (6000-7FFF) |

Additional banks in 8000-BFFF:

| Bank | Contents |
|------|----------|
| 4 | **Kanji character ROM, 16KB × 8 sub-banks (128KB), Japan-only.** From the CE-1601M Service Manual §5 memory map ("PC-1600 kanji memory ROM 16KB×8 bank", marked *1 = Japan only). Port 31H page-2 field = 4. Independent of Bank 4 in the 4000–7FFF field (CE-1600P ROM) — different window, different bit-field, no conflict. The 8-way sub-bank mechanism is not legible in that scan (plausibly Port 28H reused, or Port 3DH address latching). |
| 6 | Display routines, timer/serial control, char/token tables (CS123) |
| 7 | Unused, but addressable (confirmed by TRM §2.1's own prose; see `PC-1600-Memory-Map.md` §2) |

**Slot RAM at page 0/page 1, Bank 1: the `SLOT1MAP`/`SLOT2MAP` remap.** Sharp's own maps show slot RAM outside page 2: TRM §7.2.1 has "Slot 2 S2 (C)" at 4000–7FFF Bank 1, and the CE-1601M Service Manual §5 map has a parenthesised `(S2:)` there. TRM §3.12.3 (PDF p.140–141) gives the mechanism, two IOCS routines that set Port 3CH (`SLOTMAP`, copy at F08DH):

| Call | A | Effect | Port 3CH bit |
|---|---|---|---|
| `SLOT1MAP` 0196H | 01H | Slot 1's second 16 KB (1b) also at **Bank 1, page 1** (4000–7FFF) | b2 |
| `SLOT2MAP` 0199H | 01H | Slot 2's first 16 KB (2a) also at **Bank 1, page 0** (0000–3FFF) | b5 |
| `SLOT2MAP` 0199H | 02H | Slot 2a at **Bank 1, page 1** and Slot 2b at **Bank 1, page 0** (Slot 2a is not mapped to page 1 if Slot 1 already uses it) | b4 |
| either | 00H | normal: slot RAM only in page 2 | cleared |

The module is unaware — the SC7852 asserts its ordinary RAM1#/RAM2# select (pins 51/50) for the remapped access; Port 3CH is one of its own registers, and the LR38041 sees neither RAM1#/RAM2# nor A14/A15. For an emulator this is a mainboard-side address rewrite feeding the 8000–BFFF slot decode, never a connector pin. No ROM bank calls either routine; they exist for user programs. **Open:** the boot code writes Port 3CH = 1BH, 1AH or 5BH (P0-B0 `03E1H`–`03EEH`, after probing Slot 1), all with b4 set. If b4 is active-high, Slot 2 is remapped into Bank 1 of pages 0/1 by default. Not checked on hardware.

### Auxiliary Bank Control Ports

Port 31H is not the only bank register. Ports 3DH and 28H are **second-level bank selects**: each only has an effect while Port 31H has a particular bank mapped.

| Register | Selects | Scope |
|---|---|---|
| 31H | bank 0–7 per 16 KB page | whole address space |
| 3DH | ROM half (b2: Bank 3 / 3b; b1: kanji ROM in Bank 4 of page 2) | only when the matching bank is selected in 31H |
| 28H | vertical bank 0–7 inside the Slot 2 module | only 8000–BFFFH, Banks 2/3 |

**Port 3DH (IOW C/D):**
- Bit b2 normally set. Clearing b2 selects hidden BASIC ROM on Bank 3 -> Bank 3b at 4000-7FFF
- Cannot be read via IN instruction; readable from system address F07DH
- **Always write F07DH as well.** The interrupt entry (`INTHND`, 082CH) restores Port 3DH from F07DH on exit, so a port write without the mirror is undone by the next interrupt
- Bits D0-D2 written here are latched by the gate array into outputs A14A-A16A, extra address lines outside the Z-80 bus. A16A is the top address bit of the 32 KB CS24 ROM, so it picks Bank 3 or Bank 3b (two 16 KB halves) at 4000-7FFF. None of A14A-A16A reaches a connector, so a peripheral ROM cannot be sub-banked this way (`PC-1600-Expansion-Bus.md` §1)

**Port 28H (Slot 2 sub-banking) -- "vertical bank" select:**
- Write-only, `OUT (28H),A` in Z-80 assembler. Confirmed by two independent sources now: the CE-1601M Service Manual's memory-map figure (*"The vertical bank of S2 is selected when data of 0 to 7 are written in 28H of the I/O space"* -- an OCR-garbled scan renders this "0 to 9", but is settled by the second source), and the *superRAM* modern-module manual (§8, "Memory Map"), which states outright: *"in 256KB Mode it takes values between 0 and 7 (8 vertical banks 32KB each result in 256KB). So in 512KB Mode it takes values between 0 and 15."* Confirmed: **0-7**, 8 vertical banks.
- This is a **second, independent bank-select axis for Slot 2's 8000-BFFF window**, orthogonal to Port 31H's b4-b6 field (Part 2 above). Port 31H's field selects among the *global* 8 banks for the whole 8000-BFFF page, of which only Bank 2 and Bank 3 physically route to Slot 2 (RAM1) at all -- call this the "horizontal" axis (2 usable positions for Slot 2, 16KB each = 32KB reachable per module without touching Port 28H). Port 28H then multiplexes *within* whatever module sits in Slot 2, selecting one of up to 8 "vertical banks" -- each vertical bank being a distinct 32KB unit occupying that same Bank-2/Bank-3 footprint. Confirmed against the CE-1601M's own chip layout (a 64KB module built from two 32Kx8 SRAM chips occupies exactly *two* vertical banks, 0 and 1) and, independently, against the *superRAM*'s own memory map (Part 7b): 8 vertical banks x 32KB = **256KB, the officially-supported ceiling for Slot 2**. An independent emulator implementation lands on the same 8-bank / 32KB / 256KB figure (`README.md` — *Sources & validation*).
- **Only vertical bank 0 is usable as directly-addressable program or expansion memory** (i.e. through ordinary `BANKSET`/Port 31H access); vertical banks 1-7 are reachable only through the file system (RAM-disk), because the OS's program/expansion-memory bank management drives Port 31H alone and has no notion of also holding Port 28H at a particular value -- only the file-system driver issues explicit `OUT 28H` writes per access. Stated directly by both the CE-1601M manual and the *superRAM* manual (§8: *"only vertical bank 0 can be configured as main memory expansion (S0)"*). This is also why Mode A-D of the CE-1601M (Part 7a) always reserves at least 32KB -- vertical bank 0 -- for program/expansion use, with any additional 32KB blocks (vertical banks 1+) usable only as a RAM file.
- **The 512KB figure is now directly confirmed, not just plausible**, by a real product: the *superRAM* module (Part 7b) uses vertical-bank values 8-15 for its 512KB mode, on the exact same Port 28H mechanism -- the PC-1600's own firmware `INIT` command simply never generates or validates values above 7, since Sharp never shipped a module needing them; a small patch routine (loaded and `CALL`ed, not a ROM modification) is sufficient to retarget the file-system header/capacity fields to the wider range. Nothing about Port 28H itself, or the Z-80 I/O space, imposes an 8-bank ceiling -- that was purely a consequence of Sharp's own modules never using more than a 3-bit vertical-bank field.

**Counter-example: the CE-163 does not actually speak this protocol, and firmware has no way to manage it as if it did.** Full mechanism in `PC-1500-Bank-Switching.md` §9-10; summarized here because it's the clearest illustration of what "vertical bank switching" requires a module to actually implement, versus what merely *works* in Slot 2 by coincidence.

The CE-163 is a PC-1500-era 2x16K RAM module -- a single flip-flop latch that reacts to a select-strobe pulse on connector pin 18, sampling **A0** at that moment as the bank bit. It predates Port 28H entirely and was designed for the PC-1500's S3/S5 memory-mapped strobe, not for any I/O-port protocol. It happens to be usable in PC-1600 Slot 2 only because of an unrelated quirk: a Z-80 `OUT (n),A` places the port number itself on address lines A0-A7 during the I/O cycle, and the PC-1600 doesn't decode A0-A2 within the 28H-2FH range -- they pass straight to the connector. So `OUT &28,0` and `OUT &29,0` differ, from the CE-163's perspective, only in A0 -- indistinguishable from two ordinary memory writes. **The module never reads the data byte Port 28H actually carries the vertical-bank number in; it only reacts to which of two adjacent port addresses was used.**

This is why firmware can't detect or drive it the way it does a CE-1601M-class module:

- **No module header to key off.** Boot-time detection (`SLOTST`, the F0AE/F0AF bitmaps, the 8-byte 43H/16H ID header, Part 6 above) is Sharp's own module-identification convention. The CE-163 carries none of it -- to a boot-time probe it looks like plain unbanked SRAM at whatever bank happens to be selected, not a self-describing bank-switched device.
- **A real vertical-bank probe would never even trigger it.** Enumerating banks the documented way means `OUT (28H), n` for n = 0..7 -- port address fixed at an even value (&28), only the *data* byte changes. The CE-163 ignores the data byte outright and only cares about A0, which stays 0 throughout that whole loop. Its second bank is reachable only via the accident of the *odd port number* &29 -- not a vertical-bank value in any sense the firmware's own protocol defines.
- **Wrong granularity even if detected.** The real protocol assumes up to 8 uniform 32KB banks, addressed by an 8-bit value; the CE-163 has exactly 2 banks of 16KB, selected on a completely different axis (an address bit, not a data value). There's no mapping from "vertical bank N" to "CE-163 state" that the OS's RAM-disk bank-walking logic could use even if it tried.

So this isn't firmware declining to exploit a capability that's present -- the CE-163 was never built to implement Sharp's vertical-bank protocol, and the property letting it work at all in Slot 2 is a side effect of Z-80 I/O-address encoding that has nothing to do with Port 28H's actual, documented semantics. Auto-detection and OS-managed banking are only possible for devices that declare themselves the way Sharp's own module family (CE-1600M, CE-1601M, and modern work-alikes like *superRAM*) does.

### Why Slot 1 and Slot 2 contribute so differently to BASIC main memory (`MEM`)

A frequent point of confusion, worth stating explicitly: **a large Slot 2 module (128KB, 256KB, 512KB -- any size) can never contribute more than 32KB to `MEM`, while a Slot 1 module of the same physical size contributes its full capacity automatically.** This isn't a quirk of any specific module -- it follows directly from the bank table above.

- **Slot 1's RAM sits at Bank 0's 8000-BFFF quadrant (Slot 1a)** -- the *same* global Bank 0 that houses the fixed internal RAM at C000-FFFF. Bank 0 is the default/reset-state bank for both pages, and `BFFF`+1 = `C000`, so a Slot 1 module and internal RAM are automatically one contiguous span with **zero configuration** -- no `INIT`, no bank-switching. This matches the CE-1600M's own documented Slot 1 figure exactly: *"When in Slot 1: Bank 0 and Bank 1 accessible. User area: up to 44,612 bytes"* -- no `INIT` step mentioned, because none is needed. Its ceiling here is Slot 1's own native two-bank capacity (Bank 0 + Bank 1 at 8000-BFFF, 32KB) -- there's no "Slot 1c/1d" in the architecture, so 32KB is the natural cap regardless of what a larger Slot 1 module might otherwise support.
- **Slot 2's RAM sits at Bank 2/Bank 3 -- a different global bank, not selected by default.** Page 2's bank register has to be repointed at Bank 2 and left there for any of it to be BASIC-addressable. The *boot-time module detection* does this automatically for **every** RAM module -- a flat CE-1600M merges at reset in Slot 2 just as in Slot 1, and a **vertical-banked** module (CE-1601M, CE-1650M, *superRAM*, 128KB+) merges its vertical bank 0 the same way (emulator: `MEM` = 77370 straight after reset with a CE-1600M in Slot 1 and either a CE-1600M or a CE-1601M in Slot 2). `INIT "S2:","M"` is then a no-op; `INIT` only re-types a module as RAM disk (`"F"`), program memory (`"P"`) or back to expansion memory (`"M"`). Either way the ceiling is exactly **one vertical bank (32KB)** -- per the rule already established above (*"only vertical bank 0 can be configured as main memory expansion (S0)"*), independent of the module's actual physical capacity. The rest is reachable only through the file system, one vertical bank at a time via `OUT 28H`, never as live program/array memory -- the OS's ordinary bank management drives page 2's register alone and never holds Port 28H at a particular value outside a transient file access (Part 2 above).

**Worked confirmation:** a real test -- a 128KB Slot 2 module (vertical bank 0 merged, the rest RAM disk) plus a CE-155 (8KB) in Slot 1 -- reported `MEM` = 52794 after `NEW`, matching the Sharp-documented CE-1600M+CE-159 combo figure exactly. The model predicts this precisely: raw total 16384 (internal) + 8192 (Slot 1) + 32768 (Slot 2, one vertical bank) = 57344, minus the fixed 4550-byte overhead confirmed in `PC-1600-Memory-Map.md` §3 (header + reserve + work area + a ~257-byte fixed system-variable table not itemized in the TRM's simplified diagram) = **52794**, exact. The two additions are independent and simply stack; Slot 1 isn't "unlocking" more of Slot 2 -- it's contributing its own, architecturally uncapped share through a completely different, automatic path.

### The theoretical maximum: ~77KB, not 64KB

Since both slots' contributions are independently capped (Slot 1 at 32KB -- Bank 0 + Bank 1 are the only two global banks ever assigned there; Slot 2 at 32KB -- one vertical bank, regardless of physical module size) and add on top of the fixed 16KB internal RAM, the ceiling is:

```
16384 (internal) + 32768 (Slot 1, capped) + 32768 (Slot 2, capped at one vertical bank)
= 81920 raw bytes - 4550 fixed overhead (confirmed exactly across three configurations, PC-1600-Memory-Map.md §3)
= 77370 bytes theoretical
```

This exceeds the Z-80's own 64KB address space because `MEM` counts total storage reachable via the OS's transparent bank-switching (already evidenced by the Slot-1 32KB and Slot-2 `S0:` 32KB examples above individually, and by the 16KB+16KB and 8KB+32KB real-hardware tests both landing exactly on the 4550-overhead model), not bytes simultaneously visible in the address space at one instant.

**Confirmed:** the exact `77370` figure is reported by an emulator for the canonical maximal config — **CE-1600M in *both* slots**, both merged automatically at boot (no `INIT` needed; `INIT "S2:","M"` is a no-op in this state), `MEM` = 77370 straight after reset — matching the arithmetic on the nose (`16384 + 32768 + 32768 − 4550`). Worked out in full, with the machine-language-area and BASIC-area consequences, in `PC-1600-Module-Window-Layout.md` §4b.7. The *superRAM* manual's own screenshots (Part 7b) show the same configuration built from a different module pair — a 32KB `S0:` expansion from Slot 2 plus a 32KB module in Slot 1 — reporting **`MEM` = 77114**, ~256 bytes under 77370; that gap is specific to the *superRAM* module's own firmware/header reserve, not the architecture (a plain CE-1600M has only the standard 8-byte header, hence the exact 77370). Either way, a module larger than 32KB in either slot adds nothing further to `MEM` -- the excess is permanently RAM-disk-only. The one piece of genuinely untapped headroom: Bank 7 is documented ("addressable but unused," confirmed independently by both the TRM and the PC-1600's German user manual) but nothing -- no Sharp module, no known modern one -- has ever been built to use it; if one existed, it could in principle add up to another 16KB (a single bank, not a full slot-pair) to this ceiling, but this is speculative, not an achieved figure.

---
