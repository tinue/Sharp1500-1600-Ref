# PC-1500 Key Scan and Key Readiness


## Scope

Researched 2026-11-14 for Calc-U (first step 15 of its phase 6:
key readiness for the PC-1500 typing profile).


How the PC-1500/1500A system ROM reads the keyboard, when a key that goes down is taken
and when it is lost, how the ROM's auto-repeat works, and which point an emulator can
watch to know that the ROM is ready for the next key ("key readiness").

**Sources:** the annotated system ROM disassemblies
`~/Development/sharp/pc1500/disasm/rom/pc1500/a0{1,3,4}/PC-1500-A0x.asm` (line numbers below
are A04 unless stated), the A01/A03/A04 comparison
`~/Development/sharp/pc1500/notes/PC-1500-A0x-Revision-Differences.md`, the LH5801 guide
`PC-1500/Assembly-Programming/LH5801_Guide.md` (this repository), and, for the emulator side and the
timer, Calc-U-1600 at commit `b4ea8c8` (read with `git show b4ea8c8:<path>`).

**Revisions:** the scan logic E23D–E450 is the same in A01, A03 and A04. A diff of the
instruction text of WAITNOKEYS…CHK_BRK between the three files shows only the two changes
already recorded in `PC-1500-A0x-Revision-Differences.md:51-52` (keyboard hook vector at
E2B7, and the `REC/SEC / RTN` exits at E2F4/E33D). The routine addresses are the same in
A01 (`a01/PC-1500-A01.asm:7620-7624`, `:7930` ITA at E427).

---

## 1. Hardware read: one instruction, no latch

- `ISKEY` E418 / `ISKEY_1` E41A (`PC-1500-A04.asm:7941-7956`): writes the strobe pattern
  to ME1 **F00C** (LH5811 port A direction register, `PC1500_PRT_A_DIR` in
  `pc1500/upstream/Sharp_PC-1500_ROM_Disassembly/lib/PC-1500.lib:148`), clears ME1 **F00E**
  (port A data, `PC-1500.lib:150`), waits 3 LOP turns, then reads the sense lines with
  **`ITA`** at **E427** (`PC-1500-A04.asm:7954`) and inverts them (`EAI A,FF`), so a
  non-zero A means a key is down on a strobed line. `ISKEY` strobes all eight lines (A=FF).
  - The disassembly names the operand `ADDIT_9_1`; that is a ROM label that happens to
    sit at F00C (`PC-1500-A04.asm:10521`). The access is ME1 (`FD` prefix), i.e. the I/O
    register, not that ROM code.
- `KEY_2_ASCII` E42C (`:7964-7991`): strobes one line at a time (1, 2, 4 … 80 through
  `ISKEY_1`), finds the first set sense bit, and loads the key code from the table at
  FE80 (`KB_LAYOUT_NORM`, `notes/PC-1500-A04-Symbols.md:1608`); returns C=0 with the code,
  C=1 with no key (header comment, `:7960`).
- `ITA` at E427 is the **only** `ITA` in the system ROM (grep over A01 and A04); the CE-150
  ROM has none; CE-158-HIGH has one at 9828 (`ce158/CE-158-HIGH.asm:4434`), used to read a
  character from RS-232, not the keyboard.
- The ROM reads the matrix level by level: nothing in the ROM stores a key between two
  `ITA`s. A key that is down and released again between two reads is never seen.
  Calc-U-1600 models the read the same way (`Core/PC1500/PC1500Memory.cpp:262-274`: the
  result of `ITA` is the matrix sampled at that moment through DDA/OPA). Whether the real
  keyboard circuit holds anything is not stated in any source in the corpus (open point 1).
- **BREAK/ON is different:** it is tested through bit 1 of ME1 **F00B**, the LH5811
  interrupt-flag register (`CHK_BRK` E451, `:7999-8000`; `LH5801_Guide.md:2400`). That bit
  is a flag the ROM clears itself (`ANI #(F00B),FD` at C4C6 and C4ED, `:768`, `:782`;
  `LH5801_Guide.md:2472`), so a BREAK press is kept until the ROM looks, not lost.

## 2. The key wait loop `WAIT_4_KB` (E243–E33D)

`WAIT_4_KB` E243 (`:7645-7788`) waits for one key and returns its code (C=0) or BREAK (C=1,
A=0E). Its state lives in **CURS_CTRL 7B0E** (`:81`):

| 7B0E bit | Meaning (from the code) | Set | Cleared |
|---|---|---|---|
| 0 | a key has been taken and has not yet been released | E36A when a key is taken (`:7822`); E103 at power-on (`:7423`) | only E2D4, after the release gate (`:7727`) |
| 1 | WAITNOKEYS: return as soon as the release gate ends | E23D (`:7635`) | E24A on every WAIT_4_KB entry (`:7649`) |
| 6 | auto-repeat allowed for the last key | cursor handlers: CBF9 (→ and ←, `:2278`), CC38 ↑ (`:2345`), CC5C/CC6B/CC73 ↓ (`:2369-2381`) | E2FB (`:7752`), C956 INPUT (`:1757`), DC77 (`:6105`), CFFB (`:3244`) |

Callers of `WAIT_4_KB`: CA8F (`EDITOR_ENTRY`, `:2018`), E141 (power-on resume, `:7454`), E409
(after SHIFT/SML/DEF, `:7924`). `WAITNOKEYS` E23D is called from DC7B (`:6106`).

### 2.1 One pass

Each pass starts at `WAIT_4_KB_4` E269 (`:7668`):

1. `VMJ (A6)` = `CHK_BRK`: BREAK → return A=0E, C=1 (E33A, `:7786-7788`).
2. `ISKEY` (`ITA` at E427). Key down → `KEY_2_ASCII` (second set of `ITA`s).
3. Decide (E278–E2A2, E2C4–E301, below).
4. Unless the pass returns: cursor blink and auto-off counter (E2DE–E33D), then
   `AM0` with A=**57H**, `SIE`, **`HLT`** (E29E–E2A8, `:7696-7700`), and back to E269.
   The `HLT` ends with the timer interrupt (vector FFFA → `TIMER_ISR` E22C, which sets TM=0
   and returns, `:7611-7614`); the maskable interrupt E171 would end it too.

So the ROM looks at the keyboard **once per pass**, and a pass is the timer period from
TM=57H to 1FFH plus the loop code. From the LFSR sequence (TRM §2-3-1, as tabled in
Calc-U-1600 `Core/CPU/LH5801/LH5801TimerTable.hpp:31ff.`), 57H is count 63, so the timer
runs **448 steps** to 1FFH. Calc-U-1600 steps the timer every 8 CPU cycles at 1.3 MHz
(`LH5801TimerTable.hpp:17-23`, `Core/PC1500/PC1500Clocks.hpp:9`): 448 × 8 = 3584 cycles ≈
**2.8 ms**, plus the loop code. That divisor was calibrated on the cursor blink, not taken
from a primary source (open point 2). A cross-check that is independent of the divisor: the
auto-off counter 7B0A–7B0C starts at FE1D1D (E25B–E266, `:7658-7665`) and the ROM adds one
per pass (E2DE–E2F0, `:7732-7744`), so auto-off comes after 01E2E3H = 123,619 passes; "about
7 min" (`LH5801_Guide.md:2472`) gives about 3.4 ms per pass.

### 2.2 When a key is taken (the readiness condition)

- **7B0E bit 0 = 0** and a key is down at the `ITA` of step 2: the key is taken in that pass
  (E278 → `WAIT_4_KB_7` E2AC, `:7703-7707`: code to KEY_LAST 7B0F, then the decoder
  `AUTO_OFF_2` E366, which sets bit 0). **One read is enough**: there is no press debounce.
- **7B0E bit 0 = 1, bit 6 = 0** and a key is down: `WAIT_4_KB_16` E2FF (`:7754-7755`)
  reloads the release counter (UH = F8). The key is ignored, for as long as it is held, and
  it is **never delivered**: when it is released the gate runs out (below) without it.
- **Release gate:** bit 0 = 1 and no key down: `INC UH` (E2D0); after **8 key-free passes
  in a row** (UH F8 → 00) bit 0 is cleared (E2D4, `:7725-7727`). Any pass with a key down
  starts the count again. With bit 1 set (`WAITNOKEYS`) the routine then returns
  (E2D8 → E2F2, `:7729-7748`).
- SHIFT, SML and DEF (codes 01, 02, 1B, E3C8–E416, `:7886-7933`) only change state and go
  back to `WAIT_4_KB` (E409) with bit 0 set, so the key after them goes through the same gate.

**Key readiness = the ROM is in `WAIT_4_KB` (PC in E243–E33D) and 7B0E bit 0 = 0.** A key
put down then is taken at the next pass's `ITA` at E427, at most one pass later, if it is
still down then. The bare key-matrix read (the PC-1600 signal) is not enough on the
PC-1500: the `ITA` at E427 also runs during the release gate (bit 0 = 1), where a new key is
swallowed, and it runs from `INKEY$` and TRACE outside the loop (§4).

## 3. Auto-repeat

Only for keys whose handler sets bit 6: the four cursor keys (§2 table). INS and DEL leave
it clear (`BTN_INS` CBC7, `BTN_DEL` CBCF → `BTN_DEL_2` → `EDITOR_1`, `:2235-2258`).

- On a `WAIT_4_KB` entry with bit 6 clear, KEY_REPEAT 7B09 = **60H** (E250–E25A, `:7652-7656`).
- Held, same key, bit 6 set: each pass `INC (7B09)` (E284–E29D, `:7679-7694`). On the carry
  7B09 = **F2H** and KEY_LAST is delivered again (E292–E29B).
- **Delay:** 60H → overflow = **160 passes**. **Rate:** F2H → overflow = **14 passes** per
  repeat. In time: about 0.45–0.55 s and 40–48 ms with the pass of §2.1 (2.8–3.4 ms), plus
  the time the handler takes between two returns. Not measured on hardware (open point 2).
- A different key while bit 6 is set, or the key released: KEY_REPEAT = 60H, bits 5 and 6
  cleared (`WAIT_4_KB_15` E2F6, `:7750-7752`), then the release gate of §2.2.

## 4. Per context

| Context | How keys are read | Source |
|---|---|---|
| Command loop (RUN/PRO/RESERVE prompt) | `EDITOR_ENTRY` CA80 → `WAIT_4_KB` at CA8F; the code is dispatched after the return (RCL CA95, RESERVE change CA99, …) | `:2010-2022` |
| `INPUT` | sets BREAKPARAM \|= 50H, clears 7B0E bits 5–6, then `jmp EDITOR_1` → the same CA8F wait | `:1745-1758` |
| DEF and RESERVE keys | decoded after the CA8F wait (DEF evaluation C529 called from CAD6, `notes/PC-1500-A04-Symbols.md:90`); the DEF key itself toggles a flag and re-enters `WAIT_4_KB` at E409 | `:7886-7924` |
| Running program | only BREAK, through `VMJ (A6)` in the statement loop at C42A (`:623`) and elsewhere (CD7D, E8A3, E8B0); a flag, so not lost (§1) | `:600-640` |
| TRACE, ↓ held | statement loop C419–C428: with 7B0E bit 7 and bits 6+5 set (set by ↓, CC5C/CC6B), one `KEY_2_ASCII`; code 0A lets execution go on, anything else goes to C4A5 (`BCMD_LET_8`) | `:614-622`, `:723` |
| `INKEY$` | one `KEY_2_ASCII` at the moment the statement runs, no gate, no 7B0E | `:5416` (D9AA) |
| ↑/↓ line display in RUN mode | clears bit 6, `WAITNOKEYS` (DC77–DC7B) | `:6105-6106` |
| Keyboard hook | 79D4 = 55H: `WAIT_4_KB` jumps to external code (A03/A04: vector 785B; A01: broken) | `PC-1500-A0x-Revision-Differences.md:51` |

The prompt-readiness window E200–E4FF contains `WAIT_4_KB` E243–E33D, `ISKEY` and
`KEY_2_ASCII` E418–E450.

## 5. A key down when the ROM is not scanning

- Outside `WAIT_4_KB`, `INKEY$` and the TRACE test nothing reads the matrix (§1: one
  `ITA` in the ROM). A key that is down and up again in that time is lost. A key still down
  when `WAIT_4_KB` is entered is taken at its first pass if 7B0E bit 0 = 0; but bit 0 is
  cleared only inside the loop, so after a taken key the next key always needs the release
  gate (8 key-free passes) inside a later `WAIT_4_KB`, and a key held across it is swallowed.
- While the machine is off (auto-off `OFF` at E359, `:7813-7815`) no key is read; ON resumes
  the scan (`LH5801_Guide.md:2472`).
- BREAK is latched in F00B bit 1 (§1).

## 6. For an emulator (Calc-U-1600)

- Today (b4ea8c8) every PC-1500 key except the four cursor keys (Backspace is mapped to
  `left`, `Shared/HostKeyMap.cpp:64`) is one press of 4 frames down and 4 frames up from a
  queue (`Core/PC1500/PC1500Machine.cpp:342-377`, `Shared/MachineSession.cpp:395-406`).
  4 frames down (≈ 86,700 cycles) covers many passes; 4 frames up covers the 8-pass gate,
  but not the time the ROM spends outside `WAIT_4_KB` handling the previous key.
- A readiness signal the emulator can watch: **PC in E243–E33D and RAM 7B0E bit 0 = 0**
  (equivalently: the `ITA` at E427 executed from `ISKEY` at E26D while 7B0E bit 0 = 0). The
  next queued key goes down then and stays down until at least one more `ITA` at E427 has
  run.
- With the keyboard hook active (79D4 = 55H) the signal does not apply.

## Open points

1. Whether the PC-1500 keyboard hardware holds a key press anywhere outside the LH5801 read:
   no PC-1500 keyboard hardware note exists in the corpus. The ROM code needs none.
2. The real timer clock (CPU cycles per TM step), and so the pass length, repeat delay and
   rate in milliseconds: Calc-U-1600's 8 cycles is a calibration; the auto-off figure "about
   7 min" suggests about 3.4 ms per pass. A measurement on hardware would settle it.
3. Code 0A in the TRACE test is taken here from the ↓ handler context; the FE80 table entry
   was not checked.
