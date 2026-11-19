# PC-1500 ROM Subroutine Reference

Summary: PC-1500 ROM subroutine reference: addresses, calling conventions, register use.
Scope: PC-1500, PC-1500A
Sources: cited inline in the text
Status: draft

> Split from `LH5801_Guide.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: Architecture Overview, Registers and Flags, Addressing Mode Reference, Memory Access and Bank Switching, What Doesn → [LH5801-Architecture.md](../CPU/LH5801-Architecture.md); Instruction Set Reference → [LH5801-Instruction-Set.md](../CPU/LH5801-Instruction-Set.md); PC-1500 System Reference → [PC-1500-System-Variables.md](PC-1500-System-Variables.md); Quick Reference Card, sdas Assembler Syntax, Common Patterns and Idioms, Common Assembler Macros, Appendix: Converting, Writing a User Guide → [LH5801-Assembly-Guide.md](../Programming/LH5801-Assembly-Guide.md).

## ROM Subroutine Reference

The PC-1500 ROM exposes subroutines via three mechanisms:
- **`vmj 0xnn`:** Two-byte call `CD nn`; vectors at `0xFF00+nn`. Valid: even `0x00–0xBE`. Syntax: plain byte immediate with a `0x` prefix, no parentheses.
- **`vej 0xnn`:** Single-byte opcode `nn`; vectors at `0xFF00+nn`. Valid: even `0xC0–0xF6`. Syntax: a plain constant (`vej 0xDE`), not `vej (DE)`. (See VEJ Vector Table above.)
- **`sjp 0xnnnn`:** Direct call to fixed ROM address (math routines).

### Inline Parameter Convention

Many routines consume inline bytes placed immediately after the call opcode. The return address on the stack points past those bytes; RTN resumes at the correct location. Write inline parameter bytes directly with `.db`:

```asm
    vmj  0x00            ; CD 00 -- range-check ul in [P1..P2)
    .db 0x20           ; P1 -- lower bound
    .db 0x7F           ; P2 -- first value ABOVE the range (exclusive)
    .db OUT_OF_RANGE-.-1  ; P3 -- relative forward branch if out of range
    ; falls through here if 0x20 <= ul < 0x7F
OUT_OF_RANGE:
```

### Arithmetic Register (AR-X) Format

AR-X, AR-Y, AR-Z, AR-U, AR-V, AR-W, AR-S are 8-byte BCD float structures at `0x7A00–0x7A37`. Most math calls require `xh = yh = 0x7A` on entry — set with `vmj(0x54)`.

**Numeric format:**

| Offset | Address | Content |
|---|---|---|
| +0 | `7A00` | Exponent |
| +1 | `7A01` | Sign: `0x00`=positive, `0x80`=negative |
| +2–+7 | `7A02–7A07` | BCD mantissa, 12 digits MSB first |

**Character string info (CSI):** marker `0xD0` at `7A04`, then H:L address at `7A05:7A06`, length at `7A07`.

**Binary integer:** marker `0xB2` at `7A04`, value at `7A05:7A06`.

### VMJ Subroutine Table

Source: H-G. Schlieker, *PC-1500 ROM-Unterprogramme* (Bremen, August 1983), which also underlies the ROM disassembly's routine comments. Every address below was checked against the ROM's own vector table at `0xFF00`–`0xFFFF`, which is identical in revisions A01, A03 and A04. That check corrected four addresses Schlieker had wrong (`0x3E`, `0x56`, `0x7E`, and `vej 0xF6` = `0xDDB5`), and showed that `0xAA`/`0xB0` point to CE-150 jump stubs.

> **Syntax reminder:** `vmj 0xnn` (plain byte immediate, `0x` prefix, no parentheses). Example: `vmj 0x92`, not `vmj (0x92)`. The "VMJ" column below shows the vector number as `(0xxx)` for readability, but in source code always write `vmj 0xxx`.

#### Syntax / Token Parsing

| VMJ | Addr | Description | Syntax | Entry | Modified |
|---|---|---|---|---|---|
| `(0x00)` | `0xDCB7` | Range-check UL ∈ [P1..P2): P2 is the first value *above* the range (two `CIN` + `BCR`). Branch P3-relative if out of range or if U holds a token (UH≠0) | `CD 00 P1 P2 P3` | U=token/char | X, A |
| `(0x02)` | `0xDCB6` | Like (0x00) but first loads next token via (0xC0) | `CD 02 P1 P2 P3` | Y→BASIC mem | X, Y, A |
| `(0x04)` | `0xDCC6` | Check UL for EOC (0x3A) or EOL (0x0D); branch P1 if neither | `CD 04 P1` | U=char | X, A; C=1 if EOC |
| `(0x0C)` | `0xDE97` | Get string length at Y; load AR-X with CSI | `CD 0C` | Y→string | X, Y, U, A |
| `(0x0E)` | `0xD461` | Find variable address from coded name in U; P1=type (58=all, 68=numeric, 40=string); P2=error branch | `CD 0E P1 P2` | U=var name, Y→indices | X, Y, U, A |
| `(0x1A)` | `0xD2E6` | Search BASIC line, set memory-map params | `CD 1A` | — | X, Y, U, A |
| `(0x1C)` | `0xFA89` | Find BASIC command start from token in U, using token table at X | `CD 1C` | U=token, X→table | — |
| `(0x20)` | `0xDF72` | Advance Y to next line number (max 77 bytes); Z=1 if within limit | `CD 20` | Y→BASIC | X, Y, U, A |
| `(0x22)` | `0xDF63` | Load next token/char from BASIC into U; load AR-X CSI if string follows | `CD 22` | Y→BASIC | X, Y, U, AR-X; C=1 if string |
| `(0x26)` | `0xDB87` | Check AR-X holds a CSI: if it holds a BCD number (`7A04` < `0xB2`), set UH=`0x11` (ERROR 17), C=0 and branch P1 | `CD 26 P1` | AR-X=value | X, UH, A |
| `(0x28)` | `0xDBB1` | Check variable dimensionality (0x788C): if ≠ 1, set UH=`0x12` (ERROR 18) and branch P1. C=1 if 1-D | `CD 28 P1` | — | X, UH, A |
| `(0x34)` | `0xDF23` | Multi-branch: search A in inline char table; branch to paired offset on match | `CD 34 P1 P2 P3 P4 P5…` | A=char, UH=token flag | X, A; Y/U unchanged |
| `(0x3C)` | `0xFA74` | Find token table for current device (A=(OPN) doubled) | `CD 3C` | A=(OPN) | X, A; C=1 if found |
| `(0xCE)` | `0xD45D` | Find variable address from name at Y-area; same params as (0x0E) | `CE P1 P2` | Y→var name | same as (0x0E) |
| `(0xD2)` | `0xDD1A` | Dispatch on AR-X type: BCD→continue, binary→call (0x10), string→branch P1 | `D2 P1 P2` | AR-X | X, U, A |

#### Variable / Memory Access

| VMJ | Addr | Description | Syntax | Entry | Modified |
|---|---|---|---|---|---|
| `(0x06)` | `0xD065` | Pop 16-bit address from BASIC stack (0x7882) into U; update stack pointer | `CD 06` | — | X, U, A; (0x7882) |
| `(0x0A)` | `0xDE5E` | Decode variable name/address from X into AR-X and A; reads numeric value if numeric var | `CD 0A` | X=var name or addr | all except Y |
| `(0x10)` | `0xDD2D` | Convert U to format per P1: 0x00=BCD→AR-X, 0x40=ASCII→(Y), 0x80=signed int→AR-X, 0xE0=3-digit | `CD 10 P1` | U=int | AR-X, all CPU regs |
| `(0x16)` | `0xDFF5` | Compute distance from X to BASIC program end | `CD 16` | X=addr | U, A |
| `(0x24)` | `0xDEAF` | Load CSI into AR-X[7A04–7A07] from X=address, A=length | `CD 24` | X=addr, A=len | U, A=0xD0 |
| `(0x2A)` | `0xD03E` | Copy system message from ROM page 0xC3xx to Y-buffer; P1=src low byte, P2=count. Known: `5B 09` = " BREAK IN", `64 06` = " ERROR", `61 03` = " IN" | `CD 2A P1 P2` | Y→dest | X, Y, U, A |
| `(0x30)` | `0xDC16` | Decrement BASIC stack pointer (0x7882) by 8; save AR-X to stack | `CD 30` | — | X, UL=0xFF, A |
| `(0x32)` | `0xD071` | Push U (16-bit address) onto BASIC stack; increment (0x7882) by 2 | `CD 32` | U=addr | X, A |
| `(0x36)` | `0xDFOF` | Find string literal or string variable at Y; load AR-X CSI | `CD 36` | Y→input buf or BASIC | X, Y, U, A; C=1 if found |
| `(0x38)` | `0xCE9F` | Get reserve memory start address into X (L-byte always 0x08) | `CD 38` | — | X=reserve start, UH=0x18, A |
| `(0x3A)` | `0xCFFB` | Initialize FOR/GOSUB stack pointers and 0x788A, 0x7B0E | `CD 3A` | — | (0x788A)=0x00, (0x7890)=0x38, (0x7891)=0xFF |

#### Arithmetic

| VMJ | Addr | Description | Syntax | Entry | Modified |
|---|---|---|---|---|---|
| `(0x50)` | `0xDA71` | 16×16-bit integer multiply U×Y → X:Y; C=1 if result > 16 bits | `CD 50` | U, Y=integers | X, Y, U, A |
| `(0x52)` | `0xF663` | Normalize AR-X (exponent/mantissa align); A=sign. Error 0x19→UH+C if overflow | `CD 52` | A=sign, AR-X=raw result | X, Y, U, A |
| `(0x54)` | `0xF7B0` | Set XH=YH=0x7A — required before most AR math calls | `CD 54` | — | XH=0x7A, YH=0x7A only |
| `(0x56)` | `0xF73D` | Copy 8 bytes (XH:10–17) → (YH:00–07); if both→7Axx: AR-Y→AR-X | `CD 56` | X, Y→areas | XL=0x18, YL=0x08, UL=0xFF |
| `(0x58)` | `0xF084` | Division: AR-X = AR-X / AR-Y; div/0 → UH=0x1A, C=1 | `CD 58` | AR-X, AR-Y, XH=YH=0x7A | X=0x7A00, Y=0x7A08, U, A |
| `(0x5E)` | `0xF7A7` | Transfer RNG value (0x7B01–0x7B07) to AR-X | `CD 5E` | YH=0x7A | X=0x7A08, Y, UL |
| `(0x5C)` | `0xF61B` | Generate random number | `CD 5C` | — | — |
| `(0x60)` | `0xF6B4` | Split AR-X into integer (AR-X) and fractional (AR-Y) parts | `CD 60` | XH=YH=0x7A | X=0x7A08, Y=0x7A18, U, A=exp |
| `(0x62)` | `0xF88B` | Clear AR-Y; load 0.6 into AR-Y; C=1 | `CD 62` | XH=YH=0x7A | X, YL=0x13, UL=0xFF, A=0xF5 |
| `(0x64)` | `0xF7B5` | Swap AR-X ↔ AR-S | `CD 64` | XH=YH=0x7A | X=0x7A08, Y=0x7A38, U, A |
| `(0x66)` | `0xF7B9` | Swap AR-X ↔ AR-Y | `CD 66` | XH=YH=0x7A | X=0x7A08, Y=0x7A18, U, A |
| `(0x68)` | `0xF715` | Copy 8 bytes (XH:30–38) → (YH:10–18); if 7Axx: AR-S→AR-Y | `CD 68` | X, Y | XL=0x38, YL=0x18, UL=0xFF |
| `(0x6A)` | `0xF88F` | Write 1.0 to AR-Y; set C=1 | `CD 6A` | XH=YH=0x7A | X=0x7AEF, Y=0x7A13, UL=0xFF, A=0xEC |
| `(0x6C)` | `0xF6FB` | Load sign of AR-X into A; make AR-X absolute | `CD 6C` | X→7Axx | XL=0x01, A=sign |
| `(0x6E)` | `0xF080` | AR-X = 1/AR-X; AR-X=0 → UH=0x26, C=1 | `CD 6E` | AR-X, X/Y→7Axx | X=0x7A00, Y=0x7A08, AR-Y, AR-Z, U=0x0005, A |
| `(0x70)` | `0xF747` | Clear sign+mantissa of AR-Y (7 bytes at XH+0x11) | `CD 70` | X→7Axx | X=0x7A18, UL=0xFF, A=0x00 |
| `(0x72)` | `0xF7CE` | Add decimal mantissa at Y to AR-X (no overflow/sign check) | `CD 72` | X→7Axx, Y free | X, Y, U, A |
| `(0x74)` | `0xF775` | Shift AR (xx01–xx07) right one nibble; XH selects page | `CD 74` | XH=page | X=xx07, A=prev(xx07) |
| `(0x76)` | `0xF75F` | Clear AR (xx01–xx07) to 0x00; XH selects page | `CD 76` | XH=page | X=xx08, A=0x00 |
| `(0x78)` | `0xF72F` | Copy AR sign+mantissa (XH:01–07) → (YH:09–0F) | `CD 78` | X, Y | X=XH08, Y=YH10 |
| `(0x7A)` | `0xF7DD` | Subtract AR-X and AR-Y mantissas; exponent ignored | `CD 7A` | XH=YH=0x7A | X=0x7A00, Y=0x7A10, A=sign |
| `(0x7C)` | `0xF6E6` | XOR signs of AR-X and AR-Y; set both signs to positive | `CD 7C` | XH=YH=0x7A | X=0x7A00, Y=0x7A10, A=XOR |
| `(0x7E)` | `0xF01A` | Multiply: AR-X = AR-X × AR-Y; overflow → V flag | `CD 7E` | AR-X, AR-Y, XH=YH=0x7A | X=0x7A00, Y=0x7A09, U, AR-W/V/U/Z |
| `(0x80)` | `0xF707` | Copy AR-X → AR-S | `CD 80` | — | X=0x7A08, Y=0x7A38; UH, A preserved |
| `(0x82)` | `0xF729` | Copy AR-X sign+mantissa → AR-Y | `CD 82` | XH=YH=0x7A | X=0x7A08, Y=0x7A18, U |
| `(0x96)` | `0xEA78` | Format AR-X for USING output | `CD 96` | AR-X, USING params | X, Y, U, A |
| `(0x9E)` | `0xE4A0` | Compare string at Y with CSI in AR-Y; if equal, AR-X=1 and Z=0 | `CD 9E` | Y→string1, AR-Y=CSI | X, Y, U, A |

#### Display

| VMJ | Addr | Description | Syntax | Entry | Modified |
|---|---|---|---|---|---|
| `(0x42)` | `0xCA58` | Return to RUN/input mode; init stacks, clear LCD, show prompt | `CD 42` | — | — |
| `(0x84)` | `0xEF00` | Disable blinking cursor | `CD 84` | — | (0x787C) bits 0,1 cleared |
| `(0x88)` | `0xEDF6` | Write bit pattern A to LCD matrix column at X (bits 0–6 shown). Bits 0–3 go to (X), bits 4–6 to (X+1) | `CD 88` | X→col, A=bits | X=next col, UH=pattern, A |
| `(0x8A)` | `0xED5B` | Display ASCII char A at matrix column X; bit 7 selects extended charset | `CD 8A` | X→col, A=char | X+=6, A, U |
| `(0x8C)` | `0xEE1F` | Compute matrix column address from cursor pointer (0x7875) | `CD 8C` | (0x7875)=0–0x9C | X=col addr, A |
| `(0x8E)` | `0xEDB1` | Increment cursor pointer (0x7875); clamp at 0x9C; C=1 if clamped | `CD 8E` | — | (0x7875), A=new value, C |
| `(0x90)` | `0xEDAB` | Load cursor pointer (0x7875) into A; C=1 if > 0x9C | `CD 90` | — | A=cursor, C |
| `(0x92)` | `0xED00` | Display text at cursor: U=text address, A=char count; C=1 if display full. **Call exactly once per display update** — multiple sequential calls corrupt display state. Build the entire string in a buffer first, then call once. | `CD 92` | (0x7875)=cursor, U=text, A=count | X=next col, U=last ptr, A |
| `(0x94)` | `0xEC5C` | Copy string (X=addr, UL=length) to output buffer; C=1 if overflow | `CD 94` | X=addr, UL=len | X, Y=next free buf, C |

#### OS / System Control

| VMJ | Addr | Description | Syntax | Entry | Modified |
|---|---|---|---|---|---|
| `(0x12)` | `0xDF93` | Get BASIC program start address into X | `CD 12` | — | X=prog start, A=XH |
| `(0x14)` | `0xDFFA` | Get BASIC program start address (X) and length (U) | `CD 14` | — | X, U, A |
| `(0x18)` | `0xDF80` | Update memory-map for last processed instruction; if C=1 on entry, set bit 7 in YH | `CD 18` | Y→BASIC, C | X, Y, U, A |
| `(0x1E)` | `0xFB2A` | PV-Banking control; A bit 0=1 activates banking; updates (0x79D0) | `CD 1E` | A=control | A=0xFE |
| `(0x3E)` | `0xFB9D` | Trace | `CD 3E` | — | — |
| `(0x40)` | `0xC401` | Enter BASIC interpreter | `CD 40` | — | — |
| `(0x48)` | `0xDCF9` | Return from subroutine; skip inline params via stack-stored distance byte | `CD 48` | stack=return+dist | X, A |
| `(0x4A)` | `0xDCFD` | Like (0x48) but saves/restores Y | `CD 4A` | stack=return+dist+Y | X, Y, A |
| `(0x4C)` | `0xDCE9` | Return from subroutine past last inline param | `CD 4C` | stack=return past params | X, A |
| `(0x4E)` | `0xDCED` | Like (0x4A)+(0x4C): return + restore Y | `CD 4E` | — | X, Y, A |
| `(0x5A)` | `0xE573` | Select the µPD1990AC clock chip's mode through port C (PC3–PC5 = C0–C2 = A bits 3–5): `000` register hold, `001` register shift, `010` time set, `011` time read | `CD 5A` | A=mode | U, Y=0xF008, A |
| `(0xA0)` | `0xE234` | PV-Banking: activate if (0x79D0) bit 0=1 | `CD A0` | — | Z may change |
| `(0xA2)` | `0xE655` | Beep toggle (checks 0x786B bit 0); C=1 if beep now OFF | `CD A2` | — | C |
| `(0xA6)` | `0xE451` | Test BREAK/ON key (bit 1 of 0xF00B); Z=0 if pressed, Z=1 if not pressed | `CD A6` | — | Z |
| `(0xAC)` | `0xE88C` | Delay U × 15.625 ms; Break key can abort early | `CD AC` | U=count | U=0x00FF, A |
| `(0xB2)` | `0xB897` | Set Z=1 if U=0xFFFF | `CD B2` | U | Z |
| `(0xBA)` | `0xF763` | Clear memory block; X=start, UL=count−1 | `CD BA` | X=start, UL=count−1 | X=first byte after, UL=0xFF, A=0x00 |
| `(0xBC)` | `0xE4B7` | Find next lower token table in 0x8000–0xC000 from X | `CD BC` | X→area | X, UH, A |
| `(0xBE)` | `0xE4A8` | Find topmost token table in 0x8000–0xC000; UH=2 if CE-150, 1 if CE-158; C=1 if found | `CD BE` | — | X, UH, A |

#### BASIC Interpreter

| VMJ | Addr | Description | Syntax | Entry | Modified |
|---|---|---|---|---|---|
| `(0xD4)` | `0xDEE3` | Save the position Y (address, line number from `0x789C`, program start from `0x789E`) into a 6-byte slot: P1=`0xA0` previous line, `0xAC` BREAK, `0xB2` ERROR | `D4 P1` | Y=BASIC addr | X, U=0x78A0; Y and C preserved |
| `(0xD6)` | `0xDED1` | Restore a saved position: Y ← address, and line number/program start → `0x789C`–`0x789F`. P1=`0xA6` search result, `0xAC` BREAK, `0xB8` ON ERROR | `D6 P1` | — | X, Y, U, A |
| `(0xD8)` | `0xDF3B` | Check if BASIC program running; Z=1 if NOT running | `D8` | — | A |
| `(0xDA)` | `0xC00E` | Cache variable address from U and length from AR-X to 0x7883–0x7885 | `DA` | U=var addr | A |
| `(0xDC)` | `0xDEBC` | Load X from AR-X CSI address (7A05:7A06); length/flag → A/UL | `DC` | AR-X=CSI | X, U, A |
| `(0xE0)` | `0xCD8B` | Output ERROR 1; return to RUN mode | `E0` | — | — |
| `(0xE2)` | `0xC400` | BASIC interpreter entry | `E2` | — | — |
| `(0xE4)` | `0xCD89` | Output ERROR from UH; return to RUN mode | `E4` | UH=error code | — |

#### Tape / CMT (Rarely useful from assembly)

| VMJ | Addr | Description |
|---|---|---|
| `(0xA4)` | `0xB888` | Load character from tape |
| `(0xA8)` | `0xB88B` | Save character to tape |
| `(0xAA)` | `0xB88E` | File transfer to/from tape (stub → `JMP 0xBD3C`) |
| `(0xAE)` | `0xB891` | Compare checksum of received data |
| `(0xB0)` | `0xB894` | Load/receive program header from tape (stub → `JMP 0xBCE8`) |
| `(0xB6)` | `0xB89D` | Create tape program header |
| `(0xB8)` | `0xB8A0` | Syntax check cassette "-1" operation; update RMT param (0x7879) |

### Absolute ROM Math Routines

Called via `sjp 0xaddr`. Require XH=YH=0x7A (`vmj(0x54)`) and AR-X (or AR-X+AR-Y) to contain BCD float values. Results in AR-X; error code in UH on failure.

| Address | Function | Entry | Returns |
|---|---|---|---|
| `0xEFBA` | X + Y | AR-X, AR-Y | AR-X = AR-X + AR-Y (also `vej 0xF0`) |
| `0xEFB6` | X − Y | AR-X, AR-Y | AR-X = AR-X − AR-Y |
| `0xF01A` | X × Y | AR-X, AR-Y | AR-X = AR-X × AR-Y |
| `0xF084` | X ÷ Y | AR-X, AR-Y | AR-X = AR-X / AR-Y (also `vmj 0x58`) |
| `0xF89C` | X ^ Y | AR-X, AR-Y | AR-X = AR-X ^ AR-Y |
| `0xF0E9` | SQR | AR-X = float | AR-X = √AR-X |
| `0xF161` | LN (natural log) | AR-X = float | AR-X = ln(AR-X) |
| `0xF165` | LOG (base 10) | AR-X = float | AR-X = log₁₀(AR-X) |
| `0xF1CB` | EXP (eˣ) | AR-X = float | AR-X = e^AR-X |
| `0xF1D4` | 10ˣ | AR-X = float | AR-X = 10^AR-X |
| `0xF391` | COS | AR-X = angle | AR-X = cos(AR-X) |
| `0xF39E` | TAN | AR-X = angle | AR-X = tan(AR-X) |
| `0xF3A2` | SIN | AR-X = angle | AR-X = sin(AR-X) |
| `0xF492` | ACS (arccos) | AR-X = value | AR-X = arccos(AR-X) |
| `0xF496` | ATN (arctan) | AR-X = value | AR-X = arctan(AR-X) |
| `0xF49A` | ASN (arcsin) | AR-X = value | AR-X = arcsin(AR-X) |
| `0xF531` | DEG | AR-X = d.mmss | AR-X = decimal degrees (BASIC `DEG`) |
| `0xF564` | DMS | AR-X = decimal degrees | AR-X = d.mmss (BASIC `DMS`) |
| `0xF597` | ABS | AR-X = float | AR-X = \|AR-X\| |
| `0xF59D` | SGN | AR-X = float | AR-X = sign: +1, 0, or −1 |
| `0xF5BE` | INT | AR-X = float | AR-X = integer part (truncated) |

These are Radio Shack's published entry points (*TRS-80 Microcomputer News*, March 1983 and February 1984). Each one matches the BASIC token dispatch table and the routine headers in the ROM disassembly, and all are at the same address in ROM revisions A01, A03 and A04. Two corrections to earlier versions of this table: `0xF161` is **LN** and `0xF165` is **LOG** (they were swapped), and `0xF531` is BASIC `DEG` (d.mmss → decimal degrees), not a degree→radian conversion. Radio Shack notes that the numeric calls work on BCD values only, so convert binary integers first.

**Approximate speed** (operations per second on a stock PC-1500, from Schlieker, *PC-1500 ROM-Unterprogramme*, 1983): SGN 2300 · X+Y 1100 · INT 1100 · X−Y 860 · X×Y 130 · ABS 56 · DMS 56 · 10ˣ 53 · X÷Y 50 · 1/X 50 · SQR 43 · DEG 23 · TAN 14 · EXP 13 · ATN 10 · LOG 9 · LN 8 · SIN 8 · ASN 8 · COS 7 · ACS 7. Transcendental functions cost roughly 100–150 ms each.

### Published Keyboard, LCD, String and Tape Entry Points

Radio Shack published these entry points for the PC-2 (its rebadged PC-1500) in Bruce Elliott's series "PC-2 Assembly Language" (*TRS-80 Microcomputer News*, March 1983 – February 1984). Radio Shack presented them as the entry points guaranteed to stay fixed across ROM revisions. Every system-ROM address below matches a routine header in the ROM disassembly and is the same in revisions A01, A03 and A04. The CE-150 addresses were checked against the CE-150 ROM image. The author says he had not tested the entry/exit conditions himself, so treat any condition marked *(article)* as unverified until you have run it.

#### Keyboard

| Address | Function | Entry | Exit |
|---|---|---|---|
| `0xE243` | Wait for a key (`WAIT_4_KB`) | — | C=0: A = key code. C=1: BREAK was pressed and A=`0x0E`. SHIFT, DEF and SML only change modes and do not return. Auto power-off after about 7 min idle; pressing ON resumes the scan. After a BREAK, clear the interrupt flag with `ani #(0xF00B),0xFD` (`FD E9 F0 0B FD`) *(article)* |
| `0xE42C` | Scan once, no wait (`KEY_2_ASCII`) | — | A = key code, or `0x00` if no key is down (the code path ends `ldi a,0x00`/`rtn`) |
| `0xE33F` | Auto power-off routine | — | — |

**Key codes** returned by `0xE243`/`0xE42C` (row = low nibble, column = high nibble). Codes `0x20`–`0x7A` follow ASCII. The table shows only the non-ASCII codes:

| Code | Key | Code | Key | Code | Key |
|---|---|---|---|---|---|
| `0x01` | (SHIFT) | `0x0D` | ENTER | `0x18` | CL |
| `0x02` | (SML) | `0x0E` | BREAK | `0x19` | RCL |
| `0x08` | ← | `0x0F` | OFF | `0x1A` | CA |
| `0x09` | ⇕ | `0x11`–`0x16` | F1–F6 | `0x1B` | (DEF) |
| `0x0A` | ↓ | `0x1C` | INS | `0x1D` | DEL |
| `0x0B` | ↑ | `0x1F` | MODE | `0x5B` | √ (printed "rad") |
| `0x0C` | → | `0x5D` | π | `0x5E` | ^ |

Keys in parentheses are mode keys that `0xE243` swallows rather than returns.

#### LCD

The **cursor pointer** is `0x7875` and counts in graphic columns (`0x00`–`0x9B`, 156 columns). Characters are 6 columns wide, so a text cursor advances by 6 and graphics advance by 1. If you change `0x7875` and then return to BASIC, also set bit 0 of `0x7874` (`ori (0x7874),0x01`), as BASIC's `CURSOR`/`GCURSOR` do. To reset from machine code, use `ani (0x7874),0xFE` and then write `0x00` to `0x7875` *(article)*.

| Address | Function | Entry | Exit |
|---|---|---|---|
| `0xED57` | Put one character at the cursor | A = ASCII | Cursor unchanged. C=0: cursor in `0x00`–`0x95`. C=1: cursor at `0x96` (last cell) |
| `0xED4D` | Put one character and advance | A = ASCII | Cursor +6 if it was < `0x96`, otherwise wraps to `0x00` |
| `0xED00` | Print n characters at the cursor (`vmj 0x92`) | U = address, A = count (`0x01`–`0x1A`) | Cursor updated. C=1 if the string reached column 26 or overflowed. Text past the 156th dot is dropped |
| `0xED3B` | Print n characters from cursor 0 | U = address, XL = count (`0x01`–`0x1A`) | C=0: fitted in ≤ 25 cells. C=1: reached or passed the 26th |
| `0xEDEF` | Write one graphic column at the cursor | A = bit pattern | Cursor unchanged. A, X, U may change. Y preserved |
| `0xE8CA` | Display the 80-byte buffer `0x7BB0`–`0x7BFF` | Buffer ends with `0x0D` (≤ 79 chars). Y = cursor within buffer. `0x7880` selects the mode (below) | — |

`0x7880` (DISPARAM) modes for `0xE8CA`: `0x40` shows the buffer with Y as cursor. If the text is > 26 chars, it shows the character at Y and the 25 before it. `0x00` shows the first 26 characters and ignores Y. `0x20` shows the number in AR-X (`0x7A00`–`0x7A07`) *(article)*.

**Annunciators** are the two bytes after the LCD matrix in display chip 1/3 (`0x7600`–`0x764D` is the matrix itself). The ROM tests RUN mode with `bii (0x764F),0x40` and sets BUSY with `ori (0x764E),0x01`:

| Byte | b7 | b6 | b5 | b4 | b3 | b2 | b1 | b0 |
|---|---|---|---|---|---|---|---|---|
| `0x764E` | DEF | I | II | III | SMALL | (katakana) | SHIFT | BUSY |
| `0x764F` | — | RUN | PRO | RESERVE | — | RAD | G | DE |

`0x774E`–`0x774F` (the matching bytes in chip 2/4) are unused.

#### Conversions, comparisons, program search

| Address | Function | Entry | Exit |
|---|---|---|---|
| `0xED95` | Two ASCII hex digits (`0-9`,`A-F`) → one byte | X → first digit | A = byte. X += 2. U, Y unchanged |
| `0xD0D2` | Compare two BCD numbers (AR-X vs AR-Y) | A = comparison operator | per ROM |
| `0xD0F9` | Compare two strings | A = comparison operator | per ROM |
| `0xD2EA` | Search for a program line number | U = line number | per ROM |
| `0xD461` | Find the address of a variable (`vmj 0x0E`) | see VMJ table | |

#### String functions

These all work on CSI (character string information) in AR-X/AR-Y (see *Arithmetic Register Format*) and build their result in the string buffer `0x7B10`. Set the string-buffer pointer `0x7894` to `0x10` first. On return UH = error code (`0x00` = OK).

| Address | Function | Entry | Exit |
|---|---|---|---|
| `0xD9DD` | ASC / LEN | CSI in AR-X. YL = `0x60` (ASC) or `0x64` (LEN) | Result in AR-X |
| `0xD9B1` | CHR$ | `0x7A07` = code 0–255 | `0x7B10` = character. `0x7A04`–`0x7A06` = `C1 7B 10`. `0x7A07` = `0x00` if the code was 0, else `0x01` |
| `0xD9D7` | VAL | CSI in AR-X | Number in AR-X |
| `0xD9CF` | STR$ | Number in AR-X | CSI in AR-X, text at `0x7B10` |
| `0xD9F3` | RIGHT$ / LEFT$ / MID$ | YL = `0x02` (RIGHT$) / `0x7A` (LEFT$) / `0x7B` (MID$). `(0x7890)` = `(0x7891)` − 8 (MID$: − 16). `(0x7892)` = `(0x7890)` + 8 (MID$: + 16). X$'s CSI at `(0x7890)`…+7, and for MID$ the Y argument at `(0x7890)`+8…+15. AR-X = Y (RIGHT$/LEFT$) or Z (MID$). Do not alter `0x7890`/`0x7891` *(article)* | CSI in AR-X, text at `0x7B10` |
| `0xD925` | Concatenate | first CSI in AR-X, second in AR-Y (`0x7A10`) | CSI in AR-X, text at `0x7B10` |

#### Cassette (CE-150 ROM)

The flag byte is `0x7879` (`CASS_FLAG`). Bit 7 selects direction: 0 = output/close input, 1 = input. Bit 6 selects 0 = load, 1 = verify. Bit 4 selects the remote: 0 = REMOTE 0, 1 = REMOTE 1. Bit 0 of `0x786B` enables the beep during tape I/O (BASIC `BEEP ON/OFF`). The printer's paper feed is inhibited while tape I/O is active.

| Address | Function | Entry | Exit |
|---|---|---|---|
| `0xBF11` | Motor on | `0x7879` bits 7/4 | — |
| `0xBF43` | Motor off | — | REMOTE 0 always off. REMOTE 1 follows `RMT ON/OFF` |
| `0xBBD6` | Build the 40-byte header image at `0x7B60`–`0x7B87` | A = file mode (`00` machine code, `01` program, `02` reserve, `04` data) | Sync bytes at `0x7B60`–`0x7B67`, mode at `0x7B68`, `0x7B69`–`0x7B87` zeroed |
| `0xBCE8` | Write the header (bit 7 = 0) / read it and search for a name (bit 7 = 1) | Header built. Optional filename at `0x7B69`–`0x7B78` (all zero = take the first file) | Read: header image at `0x7B88`–`0x7BAF`. C=1 on BREAK |
| `0xBD3C` | Write/read file data | X = start, U = byte count − 1 | Write: 2 checksum bytes per 80 data bytes (not counted in U). Read: X = last byte + 1. C=1 means abnormal end: if H=1 BREAK was pressed. If H=0, V=1 is a verify mismatch and V=0 a checksum error |
| `0xBDCC` | Write one byte | A = byte. Header must already be written | — |
| `0xBDF0` | Read one byte | — | A = byte. C=1 on BREAK |
| `0xBBF5` | End tape I/O | `0x7879` bit 7 = 0 to end output, 1 to end input | Serial port reset, paper feed re-enabled, motors off |

The header image in RAM matches the on-tape layout in `Data-Formats/PC-1500-Tape-Format.md`. The output copy starts at `0x7B60` and the input copy at `0x7B88` (+`0x28`), so on input the filename is at `0x7B91`–`0x7BA0`, the start address at `0x7BAA`, and the byte count − 1 at `0x7BAC`. The CE-150 ROM's own `CSAVE` reads `0x7B82` (start) and `0x7B84` (length − 1). The article's "`0x7B85`–`0x7B86`" for the output length is one byte off.

---
