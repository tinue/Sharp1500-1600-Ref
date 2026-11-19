# PC-1500 System Reference

Summary: PC-1500 system reference: memory layout, system variables, number formats (from the former LH5801 guide).
Scope: PC-1500, PC-1500A
Sources: cited inline in the text
Status: draft

> Split from `LH5801_Guide.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: Architecture Overview, Registers and Flags, Addressing Mode Reference, Memory Access and Bank Switching, What Doesn → [LH5801-Architecture.md](../CPU/LH5801-Architecture.md); Instruction Set Reference → [LH5801-Instruction-Set.md](../CPU/LH5801-Instruction-Set.md); ROM Subroutine Reference → [PC-1500-ROM-Routines.md](PC-1500-ROM-Routines.md); Quick Reference Card, sdas Assembler Syntax, Common Patterns and Idioms, Common Assembler Macros, Appendix: Converting, Writing a User Guide → [LH5801-Assembly-Guide.md](../Programming/LH5801-Assembly-Guide.md).

## PC-1500 System Reference

### Key RAM Addresses

**Memory layout overview:**

| Range | Size | Purpose |
|---|---|---|
| `0x4000–0x47FF` | 2 KB | Standard user RAM (stock, CE-151, CE-159) |
| `0x4008–0x40C4` | 189 B | Reserve memory area |
| `0x40C5–0x47FF` | ~1.8 KB | BASIC program memory start |
| `0x7000–0x75FF` | 1.5 KB | Shadow RAM (mirrors 0x7600–0x77FF) |
| `0x7600–0x774F` | 336 B | Display buffer |
| `0x7650–0x77AF` | 352 B | Fixed string variables |
| `0x7800–0x784F` | 80 B | CPU stack |
| `0x7860–0x7BFF` | ~1 KB | System variables / BASIC state |
| `0x7A00–0x7A37` | 56 B | Floating-point arithmetic registers (ARX…ARS) |
| `0x7B10–0x7B5F` | 80 B | String buffer |
| `0x7B60–0x7BAF` | 80 B | Output buffer |
| `0x7BB0–0x7BFF` | 80 B | Input buffer |

**System variables (selected):**

| Label | Address | Description |
|---|---|---|
| `RAM_ST` | `0x4000` | Start of RAM (no expansion) |
| `RESMEM_ST` | `0x4008` | Reserve memory area start |
| `PRGMEM_ST` | `0x40C5` | Start of BASIC program memory |
| `RAM_END` | `0x47FF` | End of RAM (stock / CE-151 / CE-159) |
| `SHADOW_RAM` | `0x7000` | Shadow RAM start |
| `DISP_BUFF` | `0x7600` | Display buffer (7600–774F) |
| `STRING_VARS` | `0x7650` | Fixed string variables (7650–77AF) |
| `CPU_STACK` | `0x7800` | CPU stack area (7800–784F) |
| `KATAFLAGS` | `0x785D` | Katakana display flags |
| `BEEP_PTR` | `0x786B` | BEEP and RMT flags |
| `WAIT_CFG` | `0x7871` | WAIT setting |
| `CURSOR_ENA` | `0x7874` | Cursor enable flags |
| `CURSOR_PTR` | `0x7875` | Current display column number |
| `CHARPOS_LCD` | `0x7876` | Character position in display (INPUT statement) |
| `BEEP_FREQ` | `0x7878` | BEEP frequency |
| `DISPARAM` | `0x7880` | Display parameter (determines display at READY) |
| `CURVARADD_H/L` | `0x7883/0x7884` | Current variable address |
| `TRACE_ON` | `0x788D` | TRACE ON/OFF: 00=OFF, >0=ON |
| `USINGF` | `0x7895` | USING format flags |
| `VAR_START_H/L` | `0x7899/0x789A` | Start of variables in main memory |
| `ERL` | `0x789B` | Error code |
| `CURR_LINE_H/L` | `0x789C/0x789D` | Current executing line number |
| `FIXED_VARS` | `0x78C0` | Fixed variables area (78C0–79CF, 272 bytes) |
| `PU_PV` | `0x79D0` | PU/PV flag; ROM bank: 00=ROM1, 01=ROM2 |
| `OPN` | `0x79D1` | Open device: 60=LCD, 5C=CMT, 58=MGP, C4=LPRT, C0=COM |
| `UNDEF_REG_79FF` | `0x79FF` | LOCK mode: 00=LOCK, FF=UNLOCK |
| `ARX` | `0x7A00` | Floating-point accumulator (8 bytes) |
| `ARZ` | `0x7A08` | Scratch FP register (8 bytes) |
| `ARY` | `0x7A10` | Second FP operand (8 bytes) |
| `ARU` | `0x7A18` | Scratch FP register (8 bytes) |
| `ARV` | `0x7A20` | Scratch FP register (8 bytes) |
| `ARW` | `0x7A28` | Scratch FP register (8 bytes) |
| `ARS` | `0x7A30` | Temporary FP storage (8 bytes) |
| `B_STACK` | `0x7A38` | BASIC stack (7A38–7AFF, 200 bytes) |
| `RND_VAL` | `0x7B00` | Random number value (7B00–7B07) |
| `KEY_LAST` | `0x7B0F` | Last pressed key code |
| `STR_BUF` | `0x7B10` | String buffer (7B10–7B5F, 80 bytes) |
| `OUT_BUF` | `0x7B60` | Output buffer (7B60–7BAF, 80 bytes) |
| `IN_BUF` | `0x7BB0` | Input buffer (7BB0–7BFF, 80 bytes) |

### RAM Configurations by Model and Memory Module

Actual RAM start/end addresses depend on both the machine and which memory module (if any) is fitted. `MEM` is the value the BASIC `MEM` command reports with no program loaded.

**Empty machine (no memory module):**

| Model | Start | End | Size | MEM |
|---|---|---|---|---|
| PC-1500 | `0x4000` | `0x4800` | 2k | 1850 |
| PC-1500A | `0x4000` | `0x5800` | 6k | 5946 |
| PC-1600 (LH5803 side) | `0x4000` | `0x8000` | 16k | 11834 |
| PC-1600 (Z80 side) | `0xC000` | `0x10000` | 16k | 11834 |

**Machine plus CE-155 (8k module):**

| Model | Start | End | Size | MEM |
|---|---|---|---|---|
| PC-1500 | `0x3800` | `0x6000` | 10k | 10042 |
| PC-1500A | `0x3800` | `0x7000` | 14k | 14138 |
| PC-1600 (LH5803 side) | `0x2000` | `0x8000` | 24k | 20026 |

**Machine plus a 16k memory module (modern recreation):**

| Model | Start | End | Size |
|---|---|---|---|
| PC-1500 | `0x0000` | `0x4800` | 18k |
| PC-1500A | `0x0000` | `0x5800` | 22k |
| PC-1600 (LH5803 side) | `0x0000` | `0x8000` | 32k |

(Exact `NEW`/MEM figures depend on the specific module's own firmware reserve — see its own documentation.)

Find the actual RAM start address at runtime with `256 * PEEK(&7863)`.

**The `NEW &nnn` reservation formula:** `NEW 0` sets the start of BASIC memory to `[RAM start] + 0xC5` — the first 197 bytes of any RAM bank are reserved for BASIC's own data structures. To reserve additional space for a machine-language program (e.g. 100 bytes), the BASIC start must be `[RAM start] + 197 + 100`, e.g. `NEW &129` on a machine with the 16k module.

When a memory module with onboard firmware is fitted, that firmware needs its own reserve of bytes **on top of** the 197-byte BASIC reserve, so the minimum `NEW` offset is higher accordingly — see the module's own documentation for its specific minimum. A machine-language program loaded alongside it needs `[RAM start] + [module's firmware reserve] + [additional bytes for the program]`.

On the PC-1600, the start is not set with an absolute address, because the LH5803 and Z80 processors see the same physical memory at different address ranges. Instead, reserve an *amount*: 197 bytes plus whatever the assembly program needs (e.g. `NEW "S0:",&<n>`).

**Example — an 18-byte screen-reverse program**, minimum reservation per configuration:
- PC-1500 / CE-158: `NEW &38D7` (add 197 to the program size for the base BASIC reserve)
- PC-1500A / a memory module: `NEW` offset depends on the module's own firmware reserve (see the module's own documentation)
- PC-1600: `NEW "S0:",&D7` (add 197)

### Memory Management

**Key program and memory boundary pointers** (16-bit, big-endian, stored at 0x78xx–0x7Axx):

| Label | Address | Description |
|---|---|---|
| `RAM_ST` | `0x7863` | High byte (page) of user-available RAM start (`&40` stock; `&00` with a 16 KB module). Radio Shack's 1983 map calls it "RAM top" and `0x7864` "RAM bottom" — see `Firmware/PC-1500-BASIC-Pointers.md` §4 |
| `BASPRG_ST` | `0x7865` | BASIC program start address |
| `BASPRG_END` | `0x7867` | BASIC program end address (used by `MEM`) |
| `BASPRG_EDT` | `0x7869` | Editor work pointer, used during line modification |
| `CURVARADD` | `0x7883` | Pointer to the variable currently being accessed |
| `CURVARTYPE` | `0x7885` | Type (byte) of the active variable |
| `DISP_CTRL` | `0x7880` | Display flags: controls LCD refresh and auto-off timers |
| `BREAK_STAT` | `0x7881` | BREAK-key interrupt / execution-pause status |
| `IN_BUF_PTR` | `0x7892` | Cursor into the `0x7Bxx` input buffer area |
| `TRACE_ON` | `0x788D` | Non-zero if `TRON` is active |
| `TRACE_PARAM` | `0x788E` | Vector used for trace output handling |
| `VAR_START` | `0x7899` | Start of dimensioned variables (grows downward from top of RAM) |
| `CURR_LINE` | `0x789C` | Current line number (`0x789E` = start of the program containing it) |
| `PREV_*` | `0x78A0` | Previous line: address, line number, program start (6 bytes) |
| `SRCH_*` | `0x78A6` | Line found by the last search: address, line number, program start |
| `BRK_*` | `0x78AC` | Where BREAK happened: address, line number, program start |
| `ERR_*` | `0x78B2` | Where the last ERROR happened: address, line number, program start |
| `ON_ERR_*` | `0x78B8` | `ON ERROR GOTO` target: address, line number, program start |
| `DATA_PTR` | `0x78BE` | Cursor into `DATA` statements |
| `RAM_END` | `0x7864` | High byte of the physical RAM limit (first page past RAM) |
| `ST_ROM_MOD` | `0x7860` | Page of a write-protected program module found at power-on; `0xFF` = none (`PC-1500-RAM-Sizing-and-NEW.md` §5.6) |
| `WARM_START` | `0x7A20` | Warm-start flag: `0x01` = warm start, else cold start |
| `STK_SAVE` | `0x7A21` | Stack pointer restored during warm start |

**Free memory formula** (equivalent to the BASIC `MEM` command):

```
Free Space = RAM_END − BASPRG_END
```

**Reading free memory in assembly:**

```asm
; Option 1: call the built-in MEM routine — result returned in u (16-bit)
sjp  0xDFEE          ; uh = high byte, ul = low byte of free bytes

; Option 2: read RAM_END high byte directly (PC-1500A / PC-2 variant)
ldi  xh, 0x7A
ldi  xl, 0x13
lda  (x)            ; a = high byte of RAM_END page
```

**Safe region for assembly data under BASIC:**

When an assembly routine runs as a BASIC subroutine (`CALL`), BASIC already occupies `BASPRG_ST` through `BASPRG_END`. The safe, unused region is:

```
[BASPRG_END + 1 .. VAR_START − 1]
```

To compute the start of this region in assembly:

```asm
; Read BASPRG_END (big-endian 16-bit at 0x7867/0x7868).
; There is no ldx (addr) form -- load each byte through a.
lda  (0x7867)
sta  xh
lda  (0x7868)
sta  xl

; Advance past the end marker to get first free byte
inc  x              ; x = BASPRG_END + 1  (safe data start, 16-bit, no flags)
; Store x or use directly as base pointer for user data
```

To protect a fixed block of assembly code at a known offset, use `NEW &<decimal_offset>` from BASIC before running your program. This sets `BASPRG_ST` to that offset, keeping the assembly code below the BASIC program area:

```
NEW &112            ; protect first 112 bytes from BASIC
```

**Warm vs. cold start detection:**

```asm
lda  (0x7A20)       ; load WARM_START flag
cpi  a,0x01
bzs  warm           ; 0x01 → warm start, program memory intact
                    ; else → cold start, memory wiped / unreliable
warm:
    ; ... safe to use existing program/variable state
```

**RAM size detection at reset:**
The ROM scans pages `0x00`–`0x6F` at every hardware reset, writing test patterns (`0x5A` / `0xA5`) and reading them back. The first page that fails marks the physical RAM limit, which is stored in `RAM_END`. This means `RAM_END` automatically reflects installed RAM: ~2 KB stock, or expanded with CE-151/CE-159/a modern recreation/etc.

**Cold-start "NEW0? :CHECK" prompt:** during the hardware-reset routine, the ROM checks the status byte at `0x7A20` (`WARM_START`). If it isn't `0x01`, or specific pointers in the `0x78–0x7A` page are zero, the system treats memory as unreliable (e.g. a RAM card was just swapped) and forces a cold start — displaying `NEW0? :CHECK` and requiring the user to acknowledge that program memory may be lost.

**`NEW` command side-effects on program memory:**

| Command | Effect |
|---|---|
| `NEW` (RUN mode) | Clears variables only; BASIC program preserved |
| `NEW` (PRO mode) | Clears BASIC program; variables preserved |
| `NEW` (RESERVE mode) | Clears the programmed reserve keys/text |
| `NEW 0` | Full reset to default program start (auto-detects internal vs. expansion RAM); wipes all memory |
| `NEW &<offset>` | Sets `BASPRG_ST` to a custom offset, protecting assembly code below it from BASIC; writes `0xFF` at the new start and resets `BASPRG_END`/`BASPRG_EDT`, then fully re-initializes the interpreter |

### I/O Registers (CE1 Peripheral Controller)

| Label | Address | Description |
|---|---|---|
| `PC1500_DIV_RESET` | `0xF004` | Divider reset |
| `PC1500_UREG_OUTP` | `0xF005` | U register output |
| `PC1500_SER_XFR` | `0xF006` | Serial transfer |
| `PC1500_F_REG` | `0xF007` | F register load/divider |
| `PC1500_PRT_C` | `0xF008` | Port C |
| `PC1500_G_REG` | `0xF009` | G register |
| `PC1500_MSK_REG` | `0xF00A` | Mask register |
| `PC1500_IF_REG` | `0xF00B` | Interrupt flag register |
| `PC1500_PRT_A_DIR` | `0xF00C` | Port A direction |
| `PC1500_PRT_B_DIR` | `0xF00D` | Port B direction |
| `PC1500_PRT_A` | `0xF00E` | Port A |
| `PC1500_PRT_B` | `0xF00F` | Port B |

### CE-150 Printer / Plotter Labels

RAM variables (ME0):

| Label | Address | Description |
|---|---|---|
| `USER_CTRX_H/L` | `0x79E0/0x79E1` | CE-150 pen X coordinate counter |
| `USER_CTRY_H/L` | `0x79E2/0x79E3` | CE-150 pen Y coordinate counter |
| `CURR_PEN` | `0x79EC` | Current pen: 00=up, 01=down |
| `PRNT_MODE` | `0x79F0` | Print mode: 00=TEXT, FF=GRAPH |
| `PRNT_COLOR` | `0x79F3` | COLOR setting (0–3) |
| `PRNT_CSIZE` | `0x79F4` | CSIZE setting (0–3) |

ROM entry points (ME1, via `sjp` or called by BASIC):

| Label | Address | Description |
|---|---|---|
| `COLDES` | `0xA519` | Change pen color |
| `PRINT_150` | `0xA781` | Print ASCII character (no LF) |
| `MOTOFF` | `0xA769` | Printer motor OFF |
| `MOTDRV` | `0xA8DD` | Motor drive, move pen |
| `LFEED` | `0xA9F1` | Send one line feed (LF) to printer |
| `NLFEED` | `0xAA04` | Send N line feeds to printer |
| `PENUPDOWN` | `0xAAD9` | Pen up/down (state byte `0x79E9`). `0xAAE3` is a second entry inside the same routine |
| `GRPHPREP` | `0xABEF` | Switch from text to graphics mode |
| `TEXT` | `0xACA6` | TEXT mode |
| `TEXTPREP` | `0xACD3` | Text mode preparation |
| `GRAPH` | `0xACD3` | GRAPH mode |
| `ROTATE` | `0xB15A` | ROTATE setting |
| `COLOR` | `0xB16A` | COLOR setting |
| `CSIZE` | `0xB180` | CSIZE setting |
| `LINE` | `0xB222` | Draw LINE |
| `RLINE` | `0xB224` | Draw RLINE (relative) |
| `LPRINT_150` | `0xB2EC` | LPRINT |
| `CSAVE_150` | `0xB8A6` | CSAVE to tape |
| `CLOAD_150` | `0xB8F9` | CLOAD from tape |
| `MERGE_150` | `0xB994` | MERGE from tape |
| `RMT` | `0xBEF9` | RMT (remote control) |
| `REMOTEON` | `0xBF11` | Remote ON |
| `REMOTEOFF` | `0xBF43` | Remote OFF |

`COLDES`, `LFEED` and `PENUPDOWN` come from Radio Shack's published CE-150 entry points (*TRS-80 Microcomputer News*, March 1983). They were checked against the CE-150 ROM image: `0xA9F1` is an `SJP`/`JMP` target 7 times and `0xAAD9` 13 times, while `0xA951` (the earlier `LFEED` value) is never called. The same list also gives `0xABCB` as "switch printer from graphic to text mode", but that address falls inside a `CPI UL,0x04` instruction at `0xABCA`, so it is not a real entry point. Use `TEXT`/`GRAPH` instead.

### Calling Conventions

There is no hardware ABI. ROM routines use an ad-hoc convention:

- **Parameters:** passed in A, X, Y, U — specific to each routine (see ROM Subroutine Reference)
- **Return values:** typically in A (8-bit result) or X (16-bit result / pointer)
- **Register preservation:** not guaranteed; assume all registers modified unless documented otherwise. The ROM source documents modified registers per routine.
- **Stack:** S starts at `CPU_STACK + 0x4F` = `0x784F`. Each `psh Rreg` decrements S by 2; `psh a` by 1. Each `sjp` decrements S by 2 (return address).
- **Inline parameters:** many VMJ routines take 1–3 bytes of inline data immediately after the `CD nn` opcode, consumed by the subroutine itself. The return address on the stack already points past these bytes when RTN is executed.

### `CALL expression, variable` — BASIC Variable Passing

When BASIC invokes an assembly routine via `CALL addr, VAR`, BASIC marshals the variable into and optionally out of registers. The assembly routine does **not** access the BASIC variable directly.

#### Numeric variable (`VAR` is a numeric variable, range −32768 to 32767)

| Phase | What BASIC does | What the routine sees |
|---|---|---|
| Entry | Loads the variable's current value into **Xreg** | Xreg = variable value |
| Return (C=1) | Copies **Xreg** back into the variable | Routine sets Xreg to result, then `sec` / `rtn` |
| Return (C=0) | Variable is **not** updated | Routine sets `rec` / `rtn` for read-only use |

```asm
; BASIC: CALL &7800, N
; Entry: Xreg = value of N (−32768..32767)
; Return with carry set → Xreg written back to N
MY_ROUTINE:
    ; ... compute result in Xreg ...
    sec                 ; signal BASIC to write Xreg → N
    rtn

; Read-only variant — N is not modified
MY_READONLY:
    ; ... use Xreg, do not want writeback ...
    rec                 ; clear carry — BASIC leaves N unchanged
    rtn
```

#### Non-numeric (string) variable (`VAR` is a string variable)

| Phase | What BASIC does | What the routine sees |
|---|---|---|
| Entry | Loads **leading address** of the string buffer into **Xreg**; loads **size** of the variable into **A** | Xreg = address, A = allocated size |
| Return (C=1) | Copies **A** bytes from the address in **Xreg** into the string variable | Routine sets Xreg = source address, A = byte count, then `sec` / `rtn` |
| Return (C=0) | String variable is **not** updated | Routine sets `rec` / `rtn` |

```asm
; BASIC: CALL &7800, A$
; Entry: Xreg = address of A$ buffer, A = allocated size of A$
; Return with carry set → A bytes from (Xreg) are stored into A$
MY_STR_ROUTINE:
    ; ... Xreg already points to the string buffer ...
    ; ... write result bytes there, put length in A ...
    sec                 ; signal BASIC to update A$
    rtn
```

> **Note:** Using `CALL addr, VAR` where `VAR` is a string that has not been previously defined (dimensioned or assigned) will cause ERROR 7.

#### Summary table

| Variable type | Xreg on entry | A on entry | Writeback condition | What is written back |
|---|---|---|---|---|
| Numeric | Variable value (16-bit signed) | — | C=1 on RTN | Xreg → variable |
| String | Leading address of string buffer | Allocated size | C=1 on RTN | A bytes from (Xreg) → variable |

### VEJ Vector Table (ROM-defined, 0xFFC0–0xFFFE)

The VEJ instruction jumps to the address stored at `0xFF00 + operand`. Valid operands: even values 0xC0–0xF6 (28 entries); the table's last four entries (0xF8–0xFE) are the interrupt and reset vectors, which VEJ can't call.
**Syntax: `vej 0xnn` — a plain constant, e.g. `vej 0xDE`; not `vej (DE)`, which sdaslh5801 reads as a symbol.**

| Syntax | Addr | ROM Function |
|---|---|---|
| `vej 0xC0` | `0xDD08` | Load next token/character into U register |
| `vej 0xC2` | `0xDCD4` | Check if character in U matches inline arg; branch if not |
| `vej 0xC4` | `0xDCD5` | Check if next character in U matches inline arg; branch if not |
| `vej 0xC6` | `0xDD13` | Decrement Y by 2 (token) or 1 (character) |
| `vej 0xC8` | `0xDCC5` | Syntax check: jump forward if not end-of-command |
| `vej 0xCA` | `0xC001` | Transfer X to variable at offset b1 |
| `vej 0xCC` | `0xDDC8` | Load X from variable address at offset b1 |
| `vej 0xCE` | `0xD45D` | Determine address of variable b1; branch if not numeric |
| `vej 0xD0` | `0xD5F9` | Convert AR-X to integer into U; branch on overflow |
| `vej 0xD2` | `0xDD1A` | Reseed AR-X with integer or process CSI |
| `vej 0xD4` | `0xDEE3` | Save BASIC position Y into slot P1 (`A0` previous line, `AC` BREAK, `B2` ERROR) |
| `vej 0xD6` | `0xDED1` | Restore BASIC position into Y and `0x789C`–`0x789F` from slot P1 (`A6` search, `AC` BREAK, `B8` ON ERROR) |
| `vej 0xD8` | `0xDF3B` | Check if program expires (Z=0 if so) |
| `vej 0xDA` | `0xC00E` | Cache variable address from U and length from AR-X |
| `vej 0xDC` | `0xDEBC` | Load CSI from AR-X |
| `vej 0xDE` | `0xD6DF` | Evaluate formula pointed to by Y; jump forward on error |
| `vej 0xE0` | `0xCD8B` | Error check: branch if UH ≠ 0x00 |
| `vej 0xE2` | `0xC400` | Start of BASIC interpreter |
| `vej 0xE4` | `0xCD89` | Output error 1, return to editor |
| `vej 0xE6` | `0xF70D` | Transfer AR-X to AR-Y |
| `vej 0xE8` | `0xF661` | Convert AR-X to absolute BCD form |
| `vej 0xEA` | `0xF79C` | Push AR-X one nibble left |
| `vej 0xEC` | `0xF757` | Clear arithmetic register X (ARX = 0) |
| `vej 0xEE` | `0xF7CC` | AR-X = AR-X + AR-U |
| `vej 0xF0` | `0xEFBA` | AR-X = AR-X + AR-Y (floating-point addition) |
| `vej 0xF2` | `0xEE71` | Clear LCD display. **Does not reset cursor pointer at `0x7875`** — always follow with `ldi a,0x00` then `sta (CURSOR_PTR)`. |
| `vej 0xF4` | `0xDBBC` | Load U with 16-bit value from address w1 |
| `vej 0xF6` | `0xDDB5` | Transfer U to address w1 |
| (vector `0xFFF8`) | `0xE171` | Maskable interrupt routine entry |
| (vector `0xFFFA`) | `0xE22C` | Timer interrupt routine entry |
| (vector `0xFFFC`) | `0xE22B` | Non-maskable interrupt routine entry (executes RTI) |
| (vector `0xFFFE`) | `0xE000` | Reset routine entry |

---
