# Sharp LH5801 Assembly Language Guide

Summary: Quick reference card, sdas assembler syntax, idioms, TASM conversion, how to write a user guide. Part of the prompt.
Scope: PC-1500, PC-1500A (LH5801)
Sources: cited inline in the text
Status: cited

> Split from `LH5801_Guide.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: Architecture Overview, Registers and Flags, Addressing Mode Reference, Memory Access and Bank Switching, What Doesn → [LH5801-Architecture.md](../CPU/LH5801-Architecture.md); Instruction Set Reference → [LH5801-Instruction-Set.md](../CPU/LH5801-Instruction-Set.md); PC-1500 System Reference → [PC-1500-System-Variables.md](../Firmware/PC-1500-System-Variables.md); ROM Subroutine Reference → [PC-1500-ROM-Routines.md](../Firmware/PC-1500-ROM-Routines.md).

This guide provides a technical overview of the Sharp LH5801 8-bit microprocessor architecture, registers, flags, and instruction set, based on the PC-1500 Technical Reference Manual and opcode tables.

---

## Quick Reference Card

A concise cheat sheet for writing correct PC-1500 assembly programs from scratch. An AI given this guide should be able to write common code from this section alone.

### Registers

| Reg | Bits | Purpose |
|---|---|---|
| **A** | 8 | Accumulator — all arithmetic and load/store goes through A |
| **XL/XH** | 8+8 | Byte regs; pair **X** = 16-bit data pointer / address |
| **YL/YH** | 8+8 | Byte regs; pair **Y** = 16-bit data pointer / address |
| **UL/UH** | 8+8 | Byte regs; pair **U** = 16-bit; UL is the `lop` counter |
| **S** | 16 | Stack pointer; starts at `0x784F`; decrements on push |
| **P** | 16 | Program counter |
| **T** | 8 | Status register (flags C, IE, Z, V, H in bits 0–4) |
| **PU/PV** | 1+1 | General-purpose flip-flops; used for bank switching |

### Status Flags

| Flag | Bit | Set when… | Important note |
|---|---|---|---|
| **C** | 0 | Carry out from bit 7 in addition; **no borrow** in subtraction | C=1 after CPA/SBC means ≥, not < |
| **IE** | 1 | Interrupts enabled | |
| **Z** | 2 | Result is zero | |
| **V** | 3 | Signed overflow (ADC/SBC/INC/DEC only) | NOT set by AND/OR/EOR |
| **H** | 4 | Half-carry (digit carry bit 3→4) | Used by BCD operations |

### ME0 vs ME1

`(addr)` accesses ME0. `#(addr)` accesses ME1 (ROM/extension). Most instructions have ME0 form only — see Limitations section.

Bank switching: `HIGH_BANK` = `spu` then `spv` → ME1. `LOW_BANK` = `rpu` then `spv` → ME0.

### 15 Most-Used Instructions

| Instruction | Operation | Flags |
|---|---|---|
| `lda (LABEL)` | A = memory at LABEL (ME0) | Z |
| `sta (LABEL)` | memory at LABEL = A | — |
| `ldi a,0xnn` | A = immediate byte | Z |
| `ldi xh,0xnn` then `ldi xl,0xnn` | X = 16-bit immediate | — |
| `adc (x)` | A = A + (X) + C | C,Z,V,H |
| `sbc (x)` | A = A − (X) − NOT(C) | C,Z,V,H |
| `inc a` / `inc x` | A++; or X++ (no flags) | C,Z,V,H / — |
| `dec a` / `dec x` | A--; or X-- (no flags) | C,Z,V,H / — |
| `cpa (x)` | A − (X) → flags; C=1 if A≥(X) | C,Z,V,H |
| `cpi a,0xnn` | A − n → flags | C,Z,V,H |
| `bcr+e` / `bcs+e` | Branch if C=0 / C=1 | — |
| `bzr+e` / `bzs+e` | Branch if Z=0 / Z=1 | — |
| `sjp LABEL` | Call subroutine at LABEL | — |
| `rtn` | Return from subroutine | — |
| `psh u` / `pop u` | Push/pop U pair (LIFO) | — |

### Minimal Program Skeleton

```asm
; Symbol definitions use .equ (with the dot):
MY_CONST     .equ    0x42

            .area   CODE (ABS)
            .org    0x7800          ; user program start (below CPU stack)

MY_PROG:
            ; --- body ---
            sec                 ; C=1 so BASIC writes X back to the variable
            rtn                 ; return to BASIC (called via CALL &7800)
```

Called from BASIC: `CALL &7800`

**Toolchain — building and assembling:**
- `sdaslh5801` is built from the sibling repo `sdcc-pc1500` (public: [github.com/pchambre/sdcc-pc1500](https://github.com/pchambre/sdcc-pc1500), not part of this repository — see this repo's README for the full sibling-repo map), from its `sdcc` checkout (`sdcc-pc1500/sdcc/`). Run `git submodule update --init` first if `sdcc/` isn't checked out yet, then `./configure && make` from inside `sdcc-pc1500/sdcc/`. The built binary ends up at `sdcc-pc1500/sdcc/bin/sdaslh5801` (or `sdcc/bin_vc/sdaslh5801.exe` for the native-Windows MSVC build).
- Assemble a source file directly with `sdaslh5801 -plosgff file.asm`, or use the `lh5801-asm` VS Code extension's **"LH5801: Assemble to BIN"** command, which runs `sdaslh5801` → `sdld` → `makebin` for you and produces a flat, loadable `<name>.bin` beside the source. No separate load-address prompt is needed — it's read straight out of the file's own `.area CODE (ABS)` / `.org` pair, so always include that header. `.lst`/`.ihx`/`.map` files are left in place beside the `.bin` in case a link error needs investigating.
- **Doing the same three steps by hand** (no VS Code, e.g. from a headless agent shell) — confirmed working end to end against a real `sdcc-pc1500` build:
  ```sh
  sdaslh5801 -plosgff file.asm          # -> file.rel, file.lst, file.sym
  sdld -i file file.rel                 # -> file.ihx (Intel hex)
  makebin -p -o 0x<ORG> file.ihx file.bin
  ```
  The `-o 0x<ORG>` on `makebin` is not optional: `makebin` maps Intel-hex addresses onto file offset 0, so a program `.org`'d at, say, `0x7C01` without `-o 0x7C01` produces a ~32 KB file that's almost entirely `0xFF` padding before the real 50-ish bytes of code. `-p` (pack) then truncates the file to the last occupied byte, so the two flags together give exactly the flat, loadable blob the VS Code extension itself produces — verify with `wc -c file.bin` against the `.lst` file's own last address minus `.org`.
- **Disassembly.** There is no maintained stand-alone LH5801 disassembler for arbitrary binaries yet. To read ROM code, use the annotated disassemblies instead of disassembling it yourself: the PC-1500 system ROM (A01/A03/A04) in `Sharp_PC-1500_ROM_Disassembly/PC-1500_ROM-A0x.lh5801.asm` ([github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly](https://github.com/Jeff-Birt/Sharp_PC-1500_ROM_Disassembly); TASM dialect despite the name, with per-revision `.lst` listings for exact addresses), and the PC-1600's LH5803 ROM, which is A04 adapted to the PC-1600, in sdas dialect: `PC-1600-ROM/disasm/new/PC1600-LH5803-C000-FFFF.asm` ([github.com/tinue/PC-1600-ROM](https://github.com/tinue/PC-1600-ROM)).

**File requirements:** ASCII text, Unix (LF) line endings — non-ASCII characters (Unicode arrows, em-dashes) and Windows CRLF line endings both risk parse errors.

### Running a program in the emulator (Calc-U-1600)

The emulator for testing is **Calc-U-1600**, a product of the Calc-U family ([github.com/tinue/Calc-U](https://github.com/tinue/Calc-U), folder `products/calc-u-1600`). It builds a machine from a YAML *preset*: the file extension names the model family (`.pc1500`, `.pc1500a`, `.pc1600`), and the preset names the model, the memory, what to type and which program to load. A program assembled to `myprog.bin` at `0x40C5` (the start of general RAM on a PC-1500 with 8 KB) is started like this:

```yaml
model: PC-1500:A04            # PC-1500[:A01|A03|A04] | PC-1500A | PC-1600[:new|old]
keys:
  - key: cl
  - type: NEW&417D            # protect the program's memory from BASIC
program:
  path: myprog.bin
  format: binary
  address: 0x40C5             # needed if the file has no header
keys:
  - type: CALL&40C5
  - wait: 2                   # seconds of calculator time
```

The preset format, the app and the headless runner are described in Calc-U-1600's own help and developer documentation; a working example is `examples/machine-code/memtest_stock.pc1500` with its source `memtest.asm`.

### Loading a program onto real hardware

Once a program works correctly in the emulator, transfer it to a real PC-1500/PC-1500A over its serial port using `SharpDataExchange` (public repo, not part of this repository: [github.com/tinue/SharpDataExchange](https://github.com/tinue/SharpDataExchange)) and a CE-158X USB serial adapter (Jeff Birt's modern replacement for the original Sharp CE-158, connected via its USB port labeled **U1**; no driver setup needed on modern OSes).

For a raw assembled `.bin` with no CE-158 header, supply the load address explicitly (and a run address if it should auto-start on load):

```sh
java -jar SharpDataExchange.jar put --start-address 00C5 --run-address 00C5 myprog.bin
```

On the PC-1500 itself, **before** running the `put` command above:

```
SETDEV U1,CI,CO
CLOADM
```

(`SETDEV U1,CI,CO` redirects console I/O to the CE-158X's USB port; it must be re-entered after every power cycle or `NEW`. `CLOADM` — not plain `CLOAD`, which only loads BASIC programs — receives machine language.) The PC-1500 needs paced transmission — `SharpDataExchange` applies this automatically; if transfer is unreliable, check the USB cable and CE-158X connection before suspecting the program itself. See `SharpDataExchange/MANUAL.md` for BASIC-program transfer (`get`/`put`), Reserve Area backup, and PC-1600 wiring — this appendix only covers the machine-code-load path relevant to assembly programs.

---

## sdas Assembler Syntax

### Basic Syntax Rules

Confirmed against Calc-U-1600's `examples/machine-code/memtest.asm`, the canonical working sdas source for this project.

- **Comments:** `;` to end of line
- **Labels:** code labels followed by `:`; casing is the programmer's own choice (this guide follows `memtest.asm`'s convention of uppercase labels)
- **Symbol definitions:** `.equ` (with the dot), e.g. `ENTRY .equ 0x00C5`
- **Hex literals:** `0x` prefix, C-style -- `0xC000`, `0xFF`, `0x42`
- **Current location:** a bare `.` refers to the address of the current instruction -- e.g. `OUT_OF_RANGE-.-1` for a relative branch-offset byte
- **No space after a comma** in a two-operand instruction -- `ldi a,0x42`, not `ldi a, 0x42` (matches this project's own disassembler output)
- **Expression syntax in operands:** `(LABEL + 0xnn)` -- e.g. `lda (ARX + 0x07)`
- **Program header:** wrap assembled code in `.area CODE (ABS)` followed by `.org <address>` -- the VS Code extension's "LH5801: Assemble to BIN" command reads the load address straight back out of this pair
- **No `.end` directive** -- sdas has none, and a real `sdaslh5801` build actively rejects a trailing `.end`. Just stop after the last instruction/data byte.
- **File encoding:** ASCII, Unix (LF) line endings

### Assembler Directives

| Directive | Usage | Example |
|---|---|---|
| `.area CODE (ABS)` | Declare an absolute code area (once, before the first `.org`) | `.area CODE (ABS)` |
| `.org 0xnnnn` | Set assembly origin within the current area | `.org 0xC000` |
| `.db 0xnn,...` | Emit byte(s) | `.db 0x55`, `.db 0xCD,0x71` |
| `.dw 0xnnnn` | Emit 16-bit word | `.dw 0xC4AF` |
| `.ascii "..."` | Emit ASCII string (no terminator) | `.ascii "HELLO"` |
| `LABEL .equ value` | Define constant (**dot required**) | `CPU_STACK .equ 0x7800` |
| `.include "file"` | Include another source file (standard sdas `.include`) | `.include "macros.inc"` |

### Standard Library Macros

These small address-arithmetic and bank-switch idioms come up constantly but are not built-in instructions. sdas has real macro support (`.macro`/`.endm`), but the expressions below are simple enough to just write inline wherever they're needed:

| Expression | Meaning |
|---|---|
| `(label)>>8` | High byte of `label`'s address |
| `(label)&0xFF` | Low byte of `label`'s address |
| `(label+n)>>8` | High byte of `label+n` |
| `(label+n)&0xFF` | Low byte of `label+n` |
| `>label` | High byte of `label` (sdas prefix operator, equivalent to `(label)>>8`) |
| `<label` | Low byte of `label` (sdas prefix operator, equivalent to `(label)&0xFF`) |
| `spu` then `spv` | HIGH_BANK -- switch to ME1 |
| `rpu` then `spv` | LOW_BANK -- switch to ME0 |

**Example — loading a 16-bit address into Y:**
```asm
            ldi     yh,(MY_TABLE)>>8
            ldi     yl,(MY_TABLE)&0xFF

; equivalent, using sdas's own prefix operators instead:
            ldi     yh,>MY_TABLE
            ldi     yl,<MY_TABLE
```

Both forms were confirmed byte-identical against a real `sdaslh5801` build (`>`/`<` are `asexpr.c`'s own high/low-byte-select operators, source `sdcc-pc1500/sdcc/sdas/asxxsrc/asexpr.c`, not a project-specific macro) — pick whichever reads better; this guide's own samples use both.

**`.equ` constants support address arithmetic directly**, so a block of related addresses can be defined once relative to a single base and relocated by editing only that base line:
```asm
D           .equ    0x7C01      ; move this one line to relocate the whole block
D_FLAG      .equ    D+0
D_RESULT_HI .equ    D+1
D_RESULT_LO .equ    D+2
```
`D_RESULT_HI` etc. assemble to plain absolute addresses (`0x7C02` here) — this is ordinary constant-folding at assemble time, not a runtime computation, and combines with `>`/`<` normally (`ldi yh,>D_RESULT_HI`).

**The V-prefix instructions** (`vej`, `vmj`, `vzs`, `vzr`) are real sdas mnemonics — ROM vector calls, not bare LH5801 instructions. See the VEJ/VMJ syntax rules in the Instruction Set Reference below.

### Typical Code Structure

```asm
; Symbol definitions -- use .equ (dot required)
MY_PARAM_ADDR   .equ    0x7C10

            .area   CODE (ABS)
            .org    0x7800          ; user RAM area

MY_ROUTINE:
            psh     u               ; save U
            ldi     ul,0x00         ; clear UL
            lda     (MY_PARAM_ADDR) ; load from absolute address
            cpi     a,0x0D          ; compare with carriage return
            bzs     MY_DONE         ; branch if zero set
            sta     (x)             ; store to [X]
            inc     x               ; X = X + 1
MY_DONE:
            pop     u               ; restore U
            sec                     ; C=1: BASIC writes X back to variable
            rtn                     ; return
```

---

## Common Patterns and Idioms

### 1. 16-bit Register Load (Immediate)

There is no `ldi x,0xnnnn`. Load each byte separately:

```asm
    ldi  xh,0x78         ; x = 0x7800
    ldi  xl,0x00
```

### 2. 16-bit Zero Check

There is no 16-bit zero flag. Test both bytes.

**Branch if zero (ORA form):** combine bytes into A via OR; Z=1 only if both are zero.
```asm
    lda  xh
    ora  (XL_addr)      ; need xl in memory; or: sta temp; lda xl; ora (temp)
    bzs  IS_ZERO
```

**Branch if nonzero (CPA form):** compare each byte against 0x00 and branch on first nonzero — no temp memory needed.
```asm
    ldi  a,0x00
    cpa  xh
    bzr  IS_NONZERO     ; xh != 0
    cpa  xl
    bzr  IS_NONZERO     ; xh==0 but xl != 0
    ; both bytes are zero
IS_NONZERO:
```

The CPA form is preferred when X (or another pair) holds both halves in registers and no memory slot is available for the OR trick.

### 3. 8-bit Counted Loop (LOP)

```asm
    ldi  ul,0x09         ; loop 10 times (ul = N-1 for N iterations)
LOOP:
    ; ... loop body ...
    lop  ul,LOOP        ; ul--; branch back if no borrow
```

**LOP iteration count:** `lop` branches on "no borrow" from the decrement. Decrementing from 1 to 0 is **no borrow** (it still branches); only decrementing from 0 to 0xFF is a borrow (falls through). Therefore `ldi ul,N` loops **N+1** times. **To loop exactly N times, use `ldi ul,N-1`.**

| LDI UL value | Iterations |
|---|---|
| 0 | 1 |
| 1 | 2 |
| 9 | 10 |
| 0xFF | 256 |

`lop` uses only UL. For a 16-bit count, use `dec x` + `bzr`.

### 4. Multi-byte Block Copy (LIN / SIN)

```asm
    ldi  xh,SRC>>8      ; x → source
    ldi  xl,SRC&0xFF
    ldi  yh,DST>>8      ; y → destination
    ldi  yl,DST&0xFF
    ldi  ul,COUNT-1     ; lop runs ul+1 times; use COUNT-1 for exactly COUNT iterations
COPY_LOOP:
    lin  x              ; a = (x), x++
    sin  y              ; (y) = a, y++
    lop  ul,COPY_LOOP
```

For ME1 source: use `lin #(x)` (not available — LIN has no ME1 form). Use `lda #(x)` then `inc x` instead.

### 5. Call a ROM Routine via SJP

```asm
    ldi  xh,ARG>>8      ; set up entry registers as required
    ldi  xl,ARG&0xFF
    sjp  SOME_ROM_FUNC  ; push return addr, jump to ROM
    ; return value typically in a or x
```

### 6. Call a ROM Routine via VMJ (inline parameters)

`vmj` takes a plain byte immediate (`0x` prefix, no parentheses). Inline parameter bytes after the call are written directly with `.db`.

```asm
    vmj  0x00            ; CD 00 -- call vmj vector 00
    .db 0x20           ; P1 -- lower bound
    .db 0x7F           ; P2 -- first value ABOVE the range (exclusive)
    .db OUT_OF_RANGE-.-1  ; P3 -- relative forward branch offset if out of range
    ; falls through here if in range
OUT_OF_RANGE:
    ; ...
```

### 7. 16-bit Add A to Register Pair (ADR)

`adr` adds A into the full 16-bit register (A → RL, carry → RH):

```asm
    ldi  a,0x07
    adr  x              ; x = x + 7
```

For signed 16-bit addition of a larger value, load the low byte into A, use ADR, then handle the high byte manually.

### 8. Subtract Without Borrow (SBC with C=1 pre-set)

```asm
    sec                 ; C = 1 (no borrow preset)
    lda  MINUEND
    sbc  (SUBTRAHEND)   ; a = MINUEND - SUBTRAHEND (no borrow)
```

If C was 0 beforehand, you subtract an extra 1. Use `sec` before any standalone subtraction that should not include a borrow.

### 9. Negate A (Two's Complement)

```asm
    eai  0xFF            ; a = a XOR 0xFF (bitwise NOT)
    inc  a              ; a = ~a + 1 = -a
```

Or via subtraction: `sec`, then `ldi (temp),0x00`, then `sbc a` stores 0 - A - NOT(C) = -A.

### 10. Save / Restore Registers (PSH / POP Order)

Stack is LIFO — push order must be reversed on pop:

```asm
    psh  x              ; save x first
    psh  u              ; save u second
    ; ... work ...
    pop  u              ; restore u first (LIFO)
    pop  x              ; restore x second
```

Each `psh Rreg` decrements S by 2 (pushes RH then RL). Each `pop Rreg` increments S by 2 (pops RH then RL). Stack starts at `CPU_STACK + 0x4F` (0x784F).

**Early exit from a loop that uses PSH/POP:** if you jump out of a loop body (e.g. to a failure handler) before the matching `pop` instructions execute, the stack is left with unpopped bytes. Any subsequent `rtn` will pop those bytes instead of the real return address and jump to a garbage address — a hard crash. Always `pop` every register that was `psh`ed before jumping out of a loop, even on the error path.

### 11. BCD Arithmetic (DCA / DCS)

```asm
    sec                 ; no borrow for first digit
    lda  (BCD_A)        ; load BCD byte a
    dca  (BCD_B)        ; a = a + (BCD_B), BCD-adjusted
    sta  (BCD_RESULT)
```

`dca` does BCD addition (packed, 2 digits per byte). `dcs` does BCD subtraction.

### 12. Test a Single Bit

```asm
    bii  (TARGET),0x04   ; Z=1 if bit 2 is clear, Z=0 if set
    bzr  BIT_IS_SET
```

`bii` ANDs the operand with the mask and sets Z only. Neither A nor the operand is modified.

### 13. Find and Test Unused RAM

> **WARNING:** `ldx (x)` and `SBM` do **not exist** on the LH5801. `ldx` only takes register arguments (X, Y, U, S, P) -- there is no memory-indirect form. `SBM` is not a valid LH5801 instruction. `stx DATA_BASE` (STX to absolute address) is also invalid -- STX only takes register arguments. Do not use any of these.

Use this pattern to locate the free memory region between the BASIC program and BASIC variables. The approach below uses only confirmed-valid instructions, matching the style of Calc-U-1600's `examples/machine-code/memtest.asm`:

```asm
; --- Locate TST_START = BASPRG_END + 1 ---
; BASPRG_END is a 16-bit big-endian pointer at 0x7867/0x7868.
; Read it byte-by-byte through a (there is no ldx (addr) form).
; ROM addresses: use .equ for fixed system pointers (never change).
; Scratch variables: declare as labels with .db at end of program
;   (not .equ to hardcoded addresses — that is brittle and error-prone).
BASPRG_ENDH  .equ 0x7867
BASPRG_ENDL  .equ 0x7868
VAR_STARTH   .equ 0x7899
VAR_STARTL   .equ 0x789A

    lda  (BASPRG_ENDH)
    sta  xh
    lda  (BASPRG_ENDL)
    sta  xl
    inc  x                  ; x = BASPRG_END + 1 (16-bit, no flags)
    lda  xh
    sta  (TST_STARTH)
    lda  xl
    sta  (TST_STARTL)

; --- Locate TST_END = VAR_START - 1 ---
    lda  (VAR_STARTH)
    sta  xh
    lda  (VAR_STARTL)
    sta  xl
    dec  x                  ; x = VAR_START - 1
    lda  xh
    sta  (TST_ENDH)
    lda  xl
    sta  (TST_ENDL)

; ... rest of program ...

; Scratch variables — declared as labels, assembled into the binary.
; The assembler assigns their addresses automatically; no hardcoded .equ needed.
TST_STARTH:  .db 0x00
TST_STARTL:  .db 0x00
TST_ENDH:    .db 0x00
TST_ENDL:    .db 0x00
```

**Key addresses:**

| Symbol | Address | Meaning |
|---|---|---|
| `0x7867/0x7868` | `BASPRG_END` | 16-bit big-endian pointer: end of BASIC program |
| `0x7899/0x789A` | `VAR_START` | 16-bit big-endian pointer: start of variable area |

**Notes:**
- These addresses are only valid from a `CALL`ed assembly routine -- BASIC must already be loaded.
- `inc x` / `dec x` operate on the 16-bit register pair without setting flags.
- Variables grow downward from `VAR_START`; your data must fit in the gap.
- For a permanent workspace, use `NEW &<decimal address>` from BASIC to reserve space before loading the program.
- There is no `ldx (addr)` (load X from memory indirect) -- all 16-bit address loading requires two separate `lda`/`sta` byte operations through A.

### 14. X as Bidirectional BASIC Parameter (Input + Result Code)

`CALL addr, VAR` loads the numeric variable into Xreg on entry and — when the routine returns with C=1 — writes Xreg back to the variable. This lets a single variable serve as both the input argument and the return code.

```asm
; BASIC:
;   10 N = 4               ; pass count / receives result
;   20 CALL &7C01, N
;   30 IF N=0 THEN PRINT "OK"
;   40 IF N=1 THEN PRINT "FAIL"
;   50 IF N=2 THEN PRINT "BAD INPUT"
;
; Entry: Xreg = value of N (consumed as input)
; Exit:  Xreg = result code; C=1 so BASIC writes it back to N

MY_ROUTINE:
    ;-- validate: reject zero input --
    ldi  a,0x00
    cpa  xh
    bzr  INPUT_OK       ; xh != 0, input is valid
    cpa  xl
    bzr  INPUT_OK       ; xl != 0, input is valid
    ; input is zero -- return code 2
    ldi  xh,0x00
    ldi  xl,0x02
    sec
    rtn

INPUT_OK:
    ; ... use Xreg as the input value; overwrite it before returning ...

    ; Success path
    ldi  xh,0x00
    ldi  xl,0x00         ; result code 0
    sec
    rtn

FAIL:
    ldi  xh,0x00
    ldi  xl,0x01         ; result code 1
    sec
    rtn
```

**Key points:**
- X is consumed immediately as input; there is no separate "input register" and "output register" -- the same Xreg slot is reused for the return code before `sec; rtn`.
- BASIC reads N once before `CALL` and reads the (overwritten) N once after -- the caller never needs a second variable.
- Return codes are 16-bit; use the high byte for extended codes if needed.

---

### 15. Priming T to an Exact Bit Pattern for a Flag-Behavior Test

There is no immediate-load for T -- the only way to write it is `att` (`a → t`, all 5 bits overwritten unconditionally, see the ATT entry below), so setting T to a literal value always routes through A first. This matters when the routine under test also needs a *specific* value in A (not whatever `att` happened to leave behind), because almost every way of loading a new value into A -- `ldi a,n`, `lda ...`, `tta`, `pop a`, `and`/`ora`/`eor` -- sets the Z flag from the loaded/computed result as a side effect (`ldi RL,n`/`ldi RH,n` into the byte registers are the exception: no flag changes, see the LDI entry below). A careless reload of A after `att` can silently corrupt the very T value the test is trying to hold steady.

The fix is to pick the post-`att` A value so its own Z side effect is a no-op against the T bit pattern already in place -- most simply, by choosing a T value whose Z bit already matches whether the follow-up A load is zero or not:

```asm
; Goal: T = 0x1F (IE|H|V|Z|C all set) going into some instruction under
; test, with A = 0x00 as that instruction's own operand.
            ldi     a,0x1F
            att                 ; T = 0x1F -- direct overwrite, all 5 bits
; A must become 0x00 for the instruction under test, but "ldi a,0x00"
; sets Z from the loaded value (0x00 -> Z=1) -- which 0x1F's own Z bit
; (bit 2) already is, so this is a no-op against T:
            ldi     a,0x00      ; A = 0x00; T is still 0x1F
            adr     u           ; the instruction under test
```

If the needed A value and the needed T pattern don't line up this conveniently, `psh a` / `pop a` (`0xC8` / `0xFD 0x8A`) around the reload is the general-purpose fix -- `pop a` does set Z too, but from the popped value itself, which is exactly what was pushed, so no information is lost; T's other bits (C/V/H/IE) are never touched by push/pop at all. Confirmed against `Core/CPU/LH5801/LH5801.cpp` in the `Calc-U-1600` sibling project (this user's own, not part of this repo) and exercised end to end in `examples/debug/instrquirks_1500a.asm`'s ADR test.

---

## Common Assembler Macros

Recurring address-arithmetic and inline-byte idioms, written as plain sdas expressions/directives (see Standard Library Macros above for the bank-switch pair):

| Idiom | sdas expression |
|---|---|
| High byte of `label` | `(label)>>8` |
| Low byte of `label` | `(label)&0xFF` |
| Forward relative branch offset | `.db label-.-1` |
| Raw byte | `.db n8` |
| Low byte of a 16-bit constant | `.db (n16)&0xFF` |
| Character literal | `.db ch` |
| 16-bit word | `.dw n16` |
| HIGH_BANK (switch to ME1) | `spu` then `spv` |
| LOW_BANK (switch to ME0) | `rpu` then `spv` |

---

## Appendix: Converting a TASM Source to sdas

Older PC-1500 sources (e.g. from `Sharp_CE-158`-style repos, or the PC-1500 ROM disassembly) are often written for TASM (`tasm5801.tab`): uppercase mnemonics/registers, `$`-prefixed hex, `.EQU`/`.ORG`/`.DB`/`.BYTE`/`.DW`/`.WORD`/`.TEXT`/`.ASCII`, no segment concept, trailing `.END`. There is no maintained converter; convert by hand:

- Lower-case mnemonics and registers; `$1234` → `0x1234`.
- `.EQU` → `.equ`, `.DB`/`.BYTE` → `.db`, `.DW`/`.WORD` → `.dw`, `.TEXT`/`.ASCII` → `.ascii`.
- Put `.area CODE (ABS)` before the first `.org`. A second `.ORG` (multi-segment source) needs its own thought.
- Rename the three TASM aliases that have no sdas equivalent: `CALL` → `sjp`, `RET` → `rtn`, `SCF` → `sec`.
- Drop the trailing `.END`; sdas has no such directive and rejects it.
- Preprocessor directives (`#include`/`#define`/`#ifdef`), `.EXPORT` and `MACRO`/`ENDM` blocks need real restructuring, not a syntax rewrite.

Always check that the result assembles with `sdaslh5801`, and compare the bytes with the original where you have them.

---

## Writing a User Guide for Assembly Programs

A PC-1500 assembly program invoked from BASIC (`CALL &addr`) is opaque to the user without documentation. Write the user guide before implementation — it defines the interface contract the code must satisfy.

### What the User Guide Must Cover

1. **Purpose** — one paragraph: what the program does, what problem it solves.
2. **Installation** — how to load into RAM (POKE sequence, `CLOADM`, or tape); which address range it occupies; whether it survives a `NEW` command (it will not if it lives in BASIC program memory).
3. **Invocation** — exact BASIC command(s): e.g., `CALL &7800` or `CALL &7800,x`; any setup required before calling (variable values, mode).
4. **Parameters and return values** — if called via `CALL addr,x`: what X must contain on entry; what X, Y, A contain on return; which BASIC variables are modified.
5. **Keyboard controls** — if interactive: key-by-key table of what each key does.
6. **Display layout** — description of what appears on the 26-character LCD; any special characters or cursor behavior.
7. **Error conditions** — what happens on invalid input; how the user recovers.
8. **Memory map** — start address, end address, total bytes; any fixed RAM locations used that could conflict with BASIC variables.
9. **Known limitations** — what the program cannot do; edge cases; ROM version dependencies (A01 vs A03/A04).
10. **Example session** — short walkthrough: what the user types, what appears on screen.

### Documentation Template

Place this template as a comment block at the top of the `.asm` source file:

```asm
;==============================================================================
; PROGRAM:     <Name>
; VERSION:     1.0
; DATE:        <YYYY-MM-DD>
; AUTHOR:      <Author>
;------------------------------------------------------------------------------
; PURPOSE:
;   <One paragraph describing what the program does and what problem it solves.>
;
; INSTALLATION:
;   Load via: POKE sequence / CLOADM / tape
;   Address range: 0x<start> – 0x<end>  (<N> bytes)
;   Survives NEW: No / Yes (if loaded above BASIC program area)
;
; INVOCATION:
;   CALL &<addr>
;   or: CALL &<addr>,x   (x = <description of entry value>)
;
; PARAMETERS:
;   Entry:  x = <value of numeric VAR, or address of string VAR>
;           a = <allocated size of string VAR, or not used for numeric>
;   Return: x = <result (numeric) or source address (string)>
;           a = <byte count to write back (string only)>
;           C = 1 → BASIC writes Xreg back to VAR; C = 0 → VAR unchanged
;   Modified BASIC variables: <none / list>
;
; KEYBOARD CONTROLS:
;   <key>  : <action>
;   <key>  : <action>
;
; DISPLAY:
;   <Description of LCD layout, e.g.:>
;   Columns 1-10: <field>    Columns 11-26: <field>
;
; ERROR CONDITIONS:
;   <condition> : <result / recovery>
;
; MEMORY MAP:
;   0x<start> – 0x<end>  Code (<N> bytes)
;   0x<start> – 0x<end>  Data / variables (<N> bytes)
;
; KNOWN LIMITATIONS:
;   - <limitation 1>
;   - <limitation 2>
;
; EXAMPLE:
;   > CALL &7800
;   <what appears on screen>
;   <user presses key, what happens next>
;
; ROM VERSION:
;   Tested on A03/A04. May differ on A01 (see #IFNDEF blocks in source).
;==============================================================================
```

### In-Source Documentation Conventions

Consistent with the PC-1500 ROM disassembly conventions used throughout this project:

- **Subroutine header:** 80-character `; ---...---` separator, address (if known), name, one-line description.
- **Entry/exit contract:** `; Entry parameters:` / `; Modified registers:` / `; Error conditions:` blocks before each subroutine.
- **Inline comments:** on any instruction where the intent is not immediately obvious from the mnemonic and operand.
- **Markers:** `; TODO:` for deferred work, `; FIXME:` for known bugs or wrong behavior.

Example:

```asm
;------------------------------------------------------------------------------
; MY_ROUTINE (0x7800)
; Brief: Display the value in a as two hex digits on the LCD.
;
; Entry parameters:
;   a = byte to display
;   x = pointer to matrix column (from vmj(0x8C))
;
; Modified registers:
;   x, a, u
;
; Error conditions:
;   None.
;------------------------------------------------------------------------------
MY_ROUTINE:
    psh  u              ; save u
    ; ... implementation ...
    pop  u
    rtn
```

### Integration with the Assembly Project

The user guide is a deliverable alongside the `.asm` source, not an afterthought:

- **Draft the guide before writing code.** The "Invocation" and "Parameters" sections define the entry-point contract the assembly code must satisfy.
- **The "Memory map" section forces address allocation decisions before coding begins** — avoids conflicts with BASIC variables or other loaded programs.
- **The "Known limitations" section drives test cases** — each limitation should be verified as an edge case during testing.
- **Keep the guide in sync with the code** — if the interface changes during implementation, update the guide comment block first.
