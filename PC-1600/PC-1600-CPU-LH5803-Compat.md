# PC-1600 CPU: LH-5803 compatibility co-processor

## Scope

The LH-5803 side of the PC-1600: its memory map, how it differs from the PC-1500's
LH-5801, the Z-80↔LH-5803 call bridge, and the rules for running PC-1500/1500A software
(MODE 1). The **LH-5801 instruction set** is shared and lives in
`../PC-1500/Assembly-Programming/LH5801_Guide.md` — only the deltas are here.

**Sources:** PC-1600 Technical Reference Manual §5.14 (SC-7852↔LH-5803, the `CALLH`
parameter block), §5.15 (compatibility with the PC-1500/1500A) — read from the German
Systemhandbuch scan; §7.1.4 / §7.2.3 (the bus mapping and the LH-5803 memory map,
already in `PC-1600-Machine-Overview.md` §3 and `PC-1600-Memory-Architecture.md` §5–6).

---

## 1. What the LH-5803 is for

The PC-1600 has two main CPUs sharing one bus; only one runs at a time
(`PC-1600-Machine-Overview.md` §3). The SC-7852 (Z-80) is the normal main CPU. Control is
switched to the **LH-5803** to (a) drive PC-1500 peripherals (CE-150, CE-158, CE-162E)
and (b) run LH-5801/5803 machine code — user `XCALL` programs and `CLOAD`ed PC-1500
programs.

- Clock: **1.3 MHz** (2.6 MHz crystal ÷ 2).
- The LH-5803 is a successor to the LH-5801 and supports the LH-5801 instruction set (per
  TRM §7.1.2). Documented behavioural deltas from the LH-5801 used on a real PC-1500:
  reversed address byte order (**hi, lo**), inverted A15 as seen from the SC-7852 side,
  and the ME0/ME1 usage in `PC-1600-Machine-Overview.md` §3. Any timing differences are
  not documented.

## 2. Memory map

The LH-5803 sees a plain 64 KB space (TRM §7.2.3):

| LH-5803 address | Contents | = SC-7852 view |
|---|---|---|
| 0000H–3FFFH | Slot 1 / Slot 2 module RAM (whichever bank Port 31H last selected) | Z-80 8000H–BFFFH |
| 4000H–7FFFH | internal 16 KB RAM (fixed, no banking) | Z-80 C000H–FFFFH, Bank 0 |
| 8000H–BFFFH | CE-158 ROM (`PVOUT`=1) / CE-150 ROM (`PVOUT`=0) — CE-158 in the lower 8 KB, CE-150 in the upper 8 KB | same physical peripheral ROM |
| C000H–FFFFH | internal ROM (16 KB, the LH-5803 half of PC-1600 firmware) | Z-80 Bank-6-class system ROM |

Bank selection in 8000H–FFFFH is completed by the LH-5803's own **PV** signal — the same
physical CPU flip-flop as on the PC-1500 (`../PC-1500/Memory-Architecture/PU-PV-Signals.md` §3),
passed through the SC-7852 (PVIN pin 8 → PVOUT pin 7; the LR38041 gate array has no PV pin).
PU is one net shared by the LH-5803 and SC-7852 pin 6 (`../Shared/Expansion-Connectors.md`
§2.2b). The SC-7852 also decodes PU and PV itself, for the CE-158 trap in §6.1. The full narrative, the address-by-address comparison to
a real PC-1500/1500A, and the open question about the S6 display-buffer / S7 stack region
inside 4000H–7FFFH are in `PC-1600-Memory-Architecture.md` §5–6.

## 2a. I/O the LH-5803 shares with the SC-7852

The LH-5803 has no I/O space; it reaches the SC-7852's ports as ME1 addresses. The ROM
uses these forms:

| LH-5803 ME1 | = Z-80 port | Used for | Evidence |
|---|---|---|---|
| `#(F000H)`–`#(F00FH)` | 10H–1FH, the LH-5810-compatible block (MSK, IF, DDA, DDB, OPA, OPB, OPC) | keyboard strobes, the 1/64 s pulse on PB5 (`DELAY64` EEB2H/EEECH), IF in the interrupt handler, BREAK (`CHK_BRK` E451H) | pin 78 PCSTB "goes high when the Z-80 writes 18H … or the LH-5803 is F008H of the ME1"; pin 4 φOS "used for the sync signal of the internal LH-5810 corresponding port" (TRM §7.1.1(2)) |
| `#(0021H)`, `#(0023H)`, `#(0033H)` | 21H/23H (TC8576F), 33H (sub-CPU answer) | sub-CPU commands (`SUBCMD` E530H) | ROM |
| `#(A030H)`–`#(A03FH)` | 30H–3FH | control registers | TRM I/O-map table (PDF p.222) |
| `#(A058H)`/`#(A059H)`, `#(8055H)`/`#(8059H)` | 55H–59H, the HD61102s | LCD writes and busy polls (`LCD1500_ALL` E84AH, `LCD1500_BYTE` E7E1H) | ROM; the SC-7852 evidently ignores A8–A14 here |

The TRM's I/O-map table (PDF p.222) lists LH-5803 addresses only for 30H–3FH; the
10H–1FH row ("port corresponding to LH-5810 (LH-5811) contained in the SC7852, not
synchronized with φOS") has none, and §7.9 describes those registers from the Z-80 side
only. The F000H mapping rests on the pin descriptions above and the ROM.

The LH-5803's input port `IN0–IN7` (`ITA`) is wired to the keyboard sense lines
(`PC-1600-Keyboard.md` §2).

**Instruction differences (TRM §7.1.2, PDF p.223):** `SDP`, `RDP` and **`OFF`** execute
as NOPs on the LH-5803. A PC-1500 program's `OFF` does not power anything down.

**Interrupt inputs (PDF p.224):** NMI (pin 15) vectors through FFFCH/FFFDH ("a high
input state causes an interrupt … unconditionally accepted"); MI (pin 16) through
FFF8H/FFF9H when IE is set. The SC-7852 drives them from `LHNMIO`/`LHMIO` (pins 92/91);
IRQ (pin 80) is "an interrupt to the CPU (Z-80, LH-5803)" from PC-1500 peripherals.

## 3. The Z-80 → LH-5803 bridge: `CALLH` (TRM §5.14)

`CALLH` at **01C6H** hands control from the SC-7852 to an LH-5803 machine subroutine and
returns when it finishes. Parameters go in a work-area block; addresses are given
SC-7852-view (LH-5803-view in parentheses):

| Name | Addr | Content |
|---|---|---|
| **CMDZ** | F002H (7002H) | operation mode — **20H** = do *not* pass registers into the LH-5803; **30H** = load PARA…PARUH (F005H–F00BH) into the LH-5803 registers before entry |
| PARA | F005H (7005H) | → LH-5803 `A` |
| PARXL / PARXH | F006H / F007H | → `XL` / `XH` |
| PARYL / PARYH | F008H / F009H | → `YL` / `YH` |
| PARUL / PARUH | F00AH / F00BH | → `UL` / `UH` |
| PARPCL / PARPCH | F00CH / F00DH | subroutine entry address, low / high byte — **an LH-5803-view address** |
| PARBAN | F00EH (700EH) | subroutine bank — **00H = PV(0), 01H = PV(1)** |

**On return** the LH-5803 registers are written back to memory:

- `CMDZ = 20H`: F005H = `A`, F004H = `STATUS (T)`.
- `CMDZ = 30H`: F005H = `A`, F004H = `STATUS (T)`, F006H–F00BH = `XL, XH, YL, YH, UL, UH`.

Clobbers all Z-80 registers.

**Confirmed working on real hardware** by `../../PC-1600-ROM/dumper/pc1600-rom-dumper.asm`
(menu option 3): a 2-byte LH-5801 stub (`lda (x)` / `rtn`, opcodes `05 9A`) placed in the
shared `4000H–7FFFH`/`C000H–FFFFH` RAM, called via `CMDZ=30H` with `PARXL`/`PARXH` as the
source-byte pointer and the fetched byte read back from `PARA`, dumped the LH-5803's own
private 16KB ROM (`C000H–FFFFH`, LH-5803 view) byte-for-byte. `PARBAN=00H` worked with no
issues — consistent with neither the stub's home nor the ROM being PV-banked. Unlike Port
3DH (which needed careful write/read ordering plus `DI`/`EI`), a straightforward `DI`/
`EI` around each `CALL 01C6H` was sufficient with no further iteration — `CALLH` hands the
entire bus to the LH-5803 for its duration, so the Z-80 core structurally can't take an
interrupt mid-handoff the way it could mid-write for a plain `OUT`. One 16384-byte dump
(16384 `CALLH` round-trips) took ~30 seconds.

The BASIC-level equivalents (TRM Appendix E/H) are `XCALL` (run LH-5803 code) vs. `CALL`
(Z-80 code), `XPEEK`/`XPOKE` vs. `PEEK`/`POKE`, `XPEEK#`/`XPOKE#` vs. `PEEK#`/`POKE#`.

## 4. MODE 0 / MODE 1

The complete list of what the MODE 1 flag changes, with ROM addresses, and the
POKE-forced MODE 1 are in `PC-1600-MODE0-MODE1.md`. This section is the summary.

`MODE0` / `MODE1` are the two **display modes**, set by the BASIC `MODE` command (not the
physical `[MODE]` key, which is the PRO/RUN/RESERVE editor toggle). Confirmed from the
PC-1600 German user manual, §9.2 / Appendix H (`PC-1600-Memory-Architecture.md` §5):

- **MODE 1** = 26 × 1 — only the bottom of the four display lines is used, for PC-1500
  program compatibility; character codes `&27` / `&5B` / `&5D` are remapped to their
  PC-1500 meanings.
- BASIC's command set and dispatcher are **Z-80-resident in both modes** — MODE 1 is
  compatibility by shared command set + adjusted behaviour, not a handoff of the
  interactive session to a separate interpreter. Genuine LH-5803 execution is always
  explicit (`XCALL` / `XPEEK` / `XPOKE`), or baked into a loaded PC-1500 program's
  tokenized bytecode.

**Confirmed by the ROM disassembly** (`~/Development/sharp/pc1600/disasm/rom/pc1600/new/`):
- The statement loop and the statements are Z-80 code in both modes. MODE 1 `PRINT` is
  the Z-80's own PC-1500-style routine (`PRINT1500`, P1-B0 `647DH`), not the LH-5803's.
- The LH-5803 ROM (a modified A04) runs only what the Z-80 hands it through `CALLH`: one
  PC-1500 statement per call (`X_EXCOMM`: the CE-150/CE-158 commands, `CSAVE`/`CLOAD`/
  `MERGE`/`CHAIN`/`LLIST` through those peripherals), plus the shared arithmetic,
  functions and `USING`. So the LH-5803 gets the bus only for these calls, but they are
  frequent: every relational operator (`CMPNUM`/`CMPSTR`, P1-B3 `5D3FH`/`5D47H`), `^`,
  `AND`/`OR` and the functions (`FUNC`, `5D1DH`) run on it. An integer `FOR…NEXT` loop
  doesn't: `NEXT` adds with Z-80 code (bank 6) and compares inline (P1-B0 `5AA1H`), and
  falls back to `CMPNUM` only when the step overflows the integer range (`5A96H`).
- MODE 1 is `BMODE` (F1BCH) b6. What it changes on the Z-80 side, beyond the display:
  `INIT "Sx:"` is refused (error 110, rom3b `62BAH`); `NEW addr` is accepted only in
  MODE 1 (`4351H`); `PC15MAP` (P0-B0 `1676H`) narrows `ADTBL` to the one program area the
  LH-5803 sees; the cassette driver switches to the PC-1500 tape format (see
  `Shared/Data-Formats/WAV-Cassette-Format-1500-1600.md`).
- **`MODE 1` chooses the program area itself and ignores the previous `TITLE`**
  (`PC15MAP`, P0-B0 `1676H`, via `RAMODSET` `163FH`). It refuses (error 110) only when
  S0 spans more than one module bank (`S0MTb` ≠ 5). Otherwise:
  - S0 is internal RAM only (no module folded into it): a **one-bank program module in
    S1** becomes the area (`TITLE` := 1); else one in **S2** (`TITLE` := 2); else S0
    (`TITLE` := 0). S1 is preferred over S2, whatever `TITLE` said before.
  - S0 has one module bank: base page 80H (a full 16 KB window) → S0; otherwise a
    one-bank program module at `ADTBL` entry 4 in S1, then S2 (`ISMOD4` `1733H`), else S0.
  - The slots not chosen are hidden: their `SxMTb` := FFH (`S1NOPRG`/`S2NOPRG`
    `1760H`/`175AH`), so `TITLE "Sx:"` for them fails with error 101 (65H, `SELPRG`
    `1EEFH` via `SLOTSTAT`). A multi-bank program module is simply hidden; it doesn't
    block MODE 1. `ADTBL` is cut down to the chosen entry (`ADTBLONE` `16D1H` /
    `ADTBLCLR3` `1729H`), and F860H–F863H get the chosen area in PC-1500 form
    (`PC15MAPSET` `173BH`).
  - Back to MODE 0 (`RAMODSET` with A = 0) runs `SSLOTMP` again and `SELPRG 0`: the
    descriptors are rebuilt and `TITLE` is reset to S0.

## 5. Running PC-1500/1500A BASIC programs (TRM §5.15(1))

1. Put the PC-1600 in **MODE 1** before starting the program.
2. **MODE 1 prerequisites (TRM §5.15(1); Op. Manual App. H):** no RAM module larger than
   16 KB in Slot 1, and **no module at all in Slot 2** — *unless* the modules are used
   purely as a RAM disk (CE-1600M in Slot 1, CE-1600M or CE-161 in Slot 2), in which case
   the RAM disk must have been formatted (`INIT "Sn:","F"`) while in **MODE 0**. The
   Operation Manual adds that a ≤ 16 KB module must be present; the ROM doesn't check
   that — MODE 1 without any module is accepted (`RAMODSET` P0-B0 `163FH` → `PC15MAP`
   `1676H` refuse only when S0 spans more than one module bank).
   - **Failure = `ERROR 110`** ("Cannot set MODE 1"). The firmware's real gate is that
     the RAM the LH5803 sees at 0000–3FFF must resolve to **one flat, non-bank-switched
     region of ≤ 16 KB**. Any bank-switched module (CE-1600M's PVOUT half-select,
     CE-1601M's Port 28H vertical banks, a CE-163's address-strobe latch) fails, in
     *either* slot, and a two-module combination fails if it includes such a module even
     when the other module is a plain ≤ 16 KB card. Full analysis, the observed-vs-manual
     reconciliation table, and the mechanism are in
     `PC-1600-Memory-Architecture.md` §8; the flat LH5803-view map MODE 1 depends on is
     §4b.6 there.
3. **Renamed commands** — a PC-1500 program must use the PC-1600 name:

   | PC-1500 / 1500A | PC-1600 |
   |---|---|
   | `LCURSOR` | `TAB` |
   | `LINE` | `LLINE` |
   | `CALL` | `XCALL` |
   | `POKE` / `PEEK` | `XPOKE` / `XPEEK` |
   | `POKE#` / `PEEK#` | `XPOKE#` / `XPEEK#` |

   Cassette-loading auto-renames all of these **except `LCURSOR`** (change it to `TAB`
   by hand). Keyboard entry: rename all by hand.
4. Cassette load of a PC-1500 program: via CE-150 / CE-162E — OK; via CE-1600P interface
   — a program can be loaded in MODE 1 but **not data**.
5. `TIME = 0` is valid on the PC-1500 but an **error** on the PC-1600.
6. New PC-1600 reserved words (`NAME`, `AS`, `XOR`, …) — rename any that a PC-1500
   program used as variable names.
7. The BASIC work-area layout differs, so PC-1500 BASIC programs (and especially their
   machine-language parts) **may not run cleanly**.
8. **`7C01H`–`7FFFH`** — the PC-1500A's own user/ML area — is the **PC-1600 system work
   area**. A PC-1500 program that uses that range will not run.
9. An array variable cannot be the `INPUT`-target variable when the statement runs on a
   CE-158.

## 6. Running PC-1500/1500A peripherals (TRM §5.15(2))

- **RAM modules** work only in the memory slots — Slot 1: CE-1600M, CE-161, CE-159,
  CE-155, CE-151; Slot 2: CE-1600M, CE-161.
- **CE-150 / CE-158 / CE-162E:**
  - *MODE 0:* `LLIST` / `CSAVE` / `CLOAD` / `CSAVEM` / `CLOADM` cannot run on these; any
    command with a **non-standard-variable** operand errors (`LPRINT A1` fails — use
    `A = A1 : LPRINT A`); `TERMINAL` and `DTE` cannot run on the CE-158.
  - *MODE 1:* only the subset that PC-1500 BASIC itself supports (`LPRINT TIME$` fails,
    `TIME$` being unknown to PC-1500 BASIC).
- **CE-153:** its bundled utility program cannot be used on the PC-1600 (see TRM §5.12,
  the CE-153 control utility for the PC-1600).
- **CE-150 vs CE-1600P:** different plottable width → output layout can differ. CE-150 is
  X = 0..216 units ≈ 42.75mm on 56mm tape; CE-1600P is X = 0..960 units ≈ 190mm on A4
  (shared scale 0.198mm/unit — see `PC-1600-Peripherals-Hardware.md` §1.0 and
  `SharpBasicReference/CE-150-Reference.md`). Adjust with `PCONSOLE "LPT1:"` and `PAPER`.
  The CE-150 has two remote-control outputs, the CE-1600P only one.

### 6.1 The CE-158 display-shift trap (LH-5803 NMI)

The PC-1600 intercepts one routine of the CE-158 ROM in hardware. SC-7852 pin 92
(`LHNMIO`, wired to the LH-5803 NMI input) "goes high when the LH-5803 is 94\*\*H and when
PU = PV is high (CE-158 internal ROM)" (Service Manual §9-1, PDF p.27). PU = PV = 1 is the
CE-158's high 8 KB bank (`../PC-1500/Memory-Architecture/PU-PV-Signals.md` §5).

The NMI vector (FFFCH) points at `NMI_HANDLER` (C440H) in the LH-5803 ROM, the same code
in both ROM revisions. Its C44AH–C489H is a **byte copy of the CE-158 high bank's
93FAH–9439H**. That routine moves the two halves of the PC-1500 display RAM (7600H–764DH,
7700H–774DH) by the column count it pushes at 93FAH. The handler:

1. clears port 30H b0 (`P_MOD`), which the ROM treats as the switch that sends LH-5803
   display-RAM writes to the Z-80 for mirroring onto the LCD;
2. drops the 3-byte interrupt frame (P, T) and pops the byte the CE-158 pushed at 93FAH;
3. runs its copy of 93FAH–9439H;
4. redraws the whole PC-1500 window once (`LCD1500_ALLY`), which sets port 30H b0 again;
5. writes port 36H (`CL1`, acknowledges the NMI), `SIE` in place of `RTI`, and jumps to
   943AH, where the CE-158 code continues in the same bank.

So the many single-byte display writes of this routine are replaced by one redraw. The
reason (speed of the per-write mirroring) is inferred, not documented. On a real PC-1500
nothing raises the NMI: the A04 handler is only `RTI`.

**What it tells about the trap decode** (from the code; not measured):

- It fires on the **opcode fetch at 9400H**: the handler expects 93F9H–93FEH to have run
  (it pops the byte pushed at 93FAH) and redoes 9400H–9403H itself.
- It is **not every 94xxH access**. After the handler, port 30H b0 is set again, PU = PV = 1,
  and the CE-158 runs on at 943AH inside 94xxH; its 9331H also jumps to 9472H. A page-wide
  decode would fire again at once. Either the decode is the one address 9400H, or it fires
  on the step from 93FFH into 9400H.
- **PU is decoded**, per the Service Manual's wording. The SC-7852 has no PU input pin, so
  it must read the shared PU net on pin 6. (The CE-158 low bank, PU = 0, executes code all
  over 94xxH and has an operand byte at 9400H.)

**Real-world trigger (emulator, 2026-10-07):** the CE-158 terminal's horizontal scroll.
`TERMINAL` or `DTE` in MODE 1, F4 (Ent) in the menu, then received lines longer than 26
characters: each scroll step enters 93F9H and traps at 9400H (36 traps for 62 received
characters). The CE-158 demo's `LPRINT`/`SETDEV` path also reaches 93F9H, but in the
low bank (PU = 0), where no trap fires.

Open, testable in MODE 1 without a CE-158: `SPU`, `SPV`, jump to 9400H vs. 9401H; the
same with `RPU`; and with port 30H b0 cleared, to see whether `P_MOD` b0 also gates the
trap.

## Cross-references

- `../PC-1500/Assembly-Programming/LH5801_Guide.md` — the shared LH-5801/5803 instruction set.
- `PC-1600-Machine-Overview.md` §3–4 — dual-CPU bus mapping, `ELH#`, the physical
  hand-off sequence.
- `PC-1600-Memory-Architecture.md` §5–6 — the LH-5803-view memory map narrative and the
  PC-1500 comparison.
- `../PC-1500/Memory-Architecture/PU-PV-Signals.md` — the PV bank-select mechanism.
- `~/Development/sharp/pc1600/notes/LH5803-A04-Crosscheck.md` — `rom1500.bin` vs. real
  PC-1500 A04 ROM (68–71 % identical; consolidated-dispatcher change).
