# LH5801 Instruction Set

Summary: Complete LH5801 instruction set with opcodes, flags and timing (reference table, exempt from the size cap).
Scope: PC-1500, PC-1500A, PC-1600 (LH5803 side)
Sources: cited inline in the text
Status: cited

> Split from `LH5801_Guide.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: Architecture Overview, Registers and Flags, Addressing Mode Reference, Memory Access and Bank Switching, What Doesn → [LH5801-Architecture.md](LH5801-Architecture.md); PC-1500 System Reference → [PC-1500-System-Variables.md](../Firmware/PC-1500-System-Variables.md); ROM Subroutine Reference → [PC-1500-ROM-Routines.md](../Firmware/PC-1500-ROM-Routines.md); Quick Reference Card, sdas Assembler Syntax, Common Patterns and Idioms, Common Assembler Macros, Appendix: Converting, Writing a User Guide → [LH5801-Assembly-Guide.md](../Programming/LH5801-Assembly-Guide.md).

## Instruction Set Reference

### Compact Instruction Summary

One row per mnemonic; most common forms shown. `●`=may change, `—`=unchanged, `1`=forced set, `0`=forced reset.

| Mnemonic | Common forms | Bytes | Cycles | C | Z | V | H | Notes |
|---|---|---|---|:---:|:---:|:---:|:---:|---|
| `lda` | `reg`, `(addr)`, `#(addr)`, `(Rreg)` | 1–4 | 5–16 | — | ● | — | — | Load A |
| `ldi` | `a,n` / `RL,n` / `RH,n` / `s,pp` | 2–3 | 6–12 | — | ● | — | — | Z only on `ldi a,n` |
| `sta` | `reg`, `(addr)`, `(Rreg)` | 1–4 | 5–16 | — | — | — | — | Store A |
| `ldx` | `y` / `u` / `s` / `p` | 2 | 11 | — | — | — | — | 16-bit load to X |
| `stx` | `y` / `u` / `s` / `p` | 2 | 11 | — | — | — | — | 16-bit store from X |
| `lin` | `x` / `y` / `u` | 1 | 6 | — | ● | — | — | Load A, Rreg++ |
| `lde` | `x` / `y` / `u` | 1 | 6 | — | ● | — | — | Load A, Rreg-- |
| `sin` | `x` / `y` / `u` | 1 | 6 | — | — | — | — | Store A, Rreg++ |
| `sde` | `x` / `y` / `u` | 1 | 6 | — | — | — | — | Store A, Rreg-- |
| `adc` | `reg`, `(addr)`, `#(addr)` | 1–4 | 6–17 | ● | ● | ● | ● | A = A + op + C |
| `adi` | `a,n` / `(Rreg),n` | 2–5 | 7–23 | ● | ● | ● | ● | Add immediate |
| `adr` | `x` / `y` / `u` | 2 | 11 | ● | ● | ● | ● | 16-bit: Rreg = Rreg + A |
| `sbc` | `reg`, `(addr)`, `#(addr)` | 1–4 | 6–17 | ● | ● | ● | ● | A = A − op − NOT(C); C=1=no borrow |
| `sbi` | `a,n` | 2 | 7 | ● | ● | ● | ● | Subtract immediate |
| `dca` | `(Rreg)` | 1–2 | 15–19 | ● | ● | ● | ● | BCD add |
| `dcs` | `(Rreg)` | 1–2 | 13–17 | ● | ● | ● | ● | BCD subtract |
| `inc` | `a` / `RL` / `RH` / `Rreg` | 1–2 | 5–9 | ● | ● | ● | ● | 16-bit form: no flags |
| `dec` | `a` / `RL` / `RH` / `Rreg` | 1–2 | 5–9 | ● | ● | ● | ● | 16-bit form: no flags |
| `cpa` | `reg`, `(addr)`, `#(addr)` | 1–4 | 6–17 | ● | ● | ● | ● | Compare A; C=1 if A≥op |
| `cpi` | `a,n` / `RL,n` / `RH,n` | 2 | 7 | ● | ● | ● | ● | Compare immediate |
| `and` | `(addr)`, `(Rreg)` | 1–4 | 7–17 | — | ● | — | — | A = A & op |
| `ani` | `a,n` / `(Rreg),n` | 2–5 | 7–23 | — | ● | — | — | AND immediate |
| `ora` | `(addr)`, `(Rreg)` | 1–4 | 7–17 | — | ● | — | — | A = A \| op |
| `ori` | `a,n` / `(Rreg),n` | 2–5 | 7–23 | — | ● | — | — | OR immediate |
| `eor` | `(addr)`, `(Rreg)` | 1–4 | 7–17 | — | ● | — | — | A = A ^ op |
| `eai` | `n` | 2 | 7 | — | ● | — | — | A = A ^ n |
| `bit` | `(addr)`, `(Rreg)` | 1–4 | 7–17 | — | ● | — | — | A & op → Z only |
| `bii` | `a,n` / `(Rreg),n` | 2–5 | 7–20 | — | ● | — | — | Bit test immediate |
| `rol` | — | 1 | 8 | ● | — | — | — | Rotate A left through C |
| `ror` | — | 1 | 9 | ● | — | — | — | Rotate A right through C |
| `shl` | — | 1 | 6 | ● | — | — | — | Shift A left; 0→bit0 |
| `shr` | — | 1 | 9 | ● | — | — | — | Shift A right; 0→bit7 |
| `drl` | `(x)` / `#(x)` | 1–2 | 12–16 | — | — | — | — | Digit rotate left (4-bit) |
| `drr` | `(x)` / `#(x)` | 1–2 | 12–16 | — | — | — | — | Digit rotate right (4-bit) |
| `aex` | — | 1 | 6 | — | — | — | — | Swap nibbles of A |
| `tin` | — | 1 | 7 | — | — | — | — | (X)→(Y), X++, Y++ |
| `cin` | — | 1 | 7 | ● | ● | ● | ● | A−(X)→flags, X++ |
| `psh` | `a` / `Rreg` | 2 | 11–14 | — | — | — | — | Push to stack |
| `pop` | `a` / `Rreg` | 2 | 12–15 | — | ● | — | — | Z only on `pop a` |
| `att` | — | 2 | 9 | — | — | — | — | A → T (all flags) |
| `tta` | — | 2 | 9 | — | ● | — | — | T → A |
| `jmp` | `pp` | 3 | 12 | — | — | — | — | Unconditional jump |
| `bch` | `±e` | 2 | 8–9 | — | — | — | — | Unconditional relative |
| `bcs/bcr` | `±e` | 2 | 8–11 | — | — | — | — | Branch on C |
| `bzs/bzr` | `±e` | 2 | 8–11 | — | — | — | — | Branch on Z |
| `bvs/bvr` | `±e` | 2 | 8–11 | — | — | — | — | Branch on V |
| `bhs/bhr` | `±e` | 2 | 8–11 | — | — | — | — | Branch on H |
| `lop` | `ul,e` | 2 | 8–11 | — | — | — | — | UL--; branch if no borrow |
| `sjp` | `pp` | 3 | 19 | — | — | — | — | Call subroutine |
| `vej` | `0xC0–0xF6` | 1 | 17 | — | 0 | — | — | ROM vector call (1-byte); syntax: `vej 0xnn` (even, `0xC0`–`0xF6`) |
| `vmj` | `0x00–0xBE` | 2 | 20 | — | 0 | — | — | ROM vector call (2-byte); syntax: `vmj 0xnn` no parens |
| `vcs/vcr` | `i` | 2 | 8/21 | — | 0 | — | — | Conditional vector call on C |
| `vzs/vzr` | `i` | 2 | 8/21 | — | 0 | — | — | Conditional vector call on Z |
| `vhs/vhr` | `i` | 2 | 8/21 | — | 0 | — | — | Conditional vector call on H |
| `vvs` | `i` | 2 | 8/21 | — | 0 | — | — | Conditional vector call on V |
| `rtn` | — | 1 | 11 | — | — | — | — | Return from subroutine |
| `rti` | — | 1 | 14 | ● | ● | ● | ● | Return from interrupt (restores T) |
| `sec/rec` | — | 1 | 4 | 1/0 | — | — | — | Set/reset carry |
| `sie/rie` | — | 2 | 8 | — | — | — | — | Set/reset interrupt enable |
| `spu/rpu` | — | 1 | 4 | — | — | — | — | Set/reset PU flip-flop |
| `spv/rpv` | — | 1 | 4 | — | — | — | — | Set/reset PV flip-flop |
| `sdp/rdp` | — | 2 | 8–9 | — | — | — | — | Set/reset display (LCD on/off) |
| `am0/am1` | — | 2 | 9 | — | — | — | — | A → timer (bit8=0/1) |
| `atp` | — | 2 | 9 | — | — | — | — | A → output port |
| `ita` | — | 2 | 9 | — | ● | — | — | Input port → A |
| `cdv` | — | 2 | 8 | — | — | — | — | Clear clock divider |
| `nop` | — | 1 | 5 | — | — | — | — | No operation |
| `hlt` | — | 2 | 9 | — | — | — | — | Halt until interrupt |
| `off` | — | 2 | 8 | — | — | — | — | Power off (reset BF) |

---

### Notation and Conventions

| Symbol | Meaning |
|---|---|
| **RL** | XL, YL, or UL (low byte of a register pair) |
| **RH** | XH, YH, or UH (high byte of a register pair) |
| **Rreg** | X, Y, or U (16-bit register pair) |
| **(Rreg)** | Contents of memory at address in Rreg, accessed via ME0 |
| **#(Rreg)** | Contents of memory at address in Rreg, accessed via ME1 |
| **(pp)** | Memory at absolute 16-bit address `pp`, ME0 |
| **#(pp)** | Memory at absolute 16-bit address `pp`, ME1 |
| **n / i** | 8-bit immediate data |
| **pp** | 16-bit immediate address (high byte `a` first, then low byte `b`) |
| **e** | 8-bit relative offset |
| **→** | Data transfer direction |
| **∧** | AND |
| **∨** | OR |
| **⊕** | Exclusive OR |

**Flag columns:** `C` = Carry, `Z` = Zero, `V` = Overflow, `H` = Half Carry.
`●` = may change, `—` = unchanged, `1` = forced set, `0` = forced reset.

**Opcode prefix `FD`:** Instructions prefixed with `0xFD` are two-byte instructions where `0xFD` is the first byte.

**Register encoding in opcodes:** Most instructions encode the register pair in bits 5:4 of the opcode: `00`=X, `01`=Y, `10`=U. The encoding `11` (V) is **undocumented** and not guaranteed on all hardware revisions. These are marked **(undoc)** below.

---

### Add, Subtract, and Logical Instructions

#### ADC — Add with Carry
`a = a + [operand] + C`
**Flags:** C, V, H, Z may change.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `adc xl` | A = A + XL + C | `0x02` | 1 | 6 |
| `adc yl` | A = A + YL + C | `0x12` | 1 | 6 |
| `adc ul` | A = A + UL + C | `0x22` | 1 | 6 |
| `adc xh` | A = A + XH + C | `0x82` | 1 | 6 |
| `adc yh` | A = A + YH + C | `0x92` | 1 | 6 |
| `adc uh` | A = A + UH + C | `0xA2` | 1 | 6 |
| `adc (x)` | A = A + (X) + C  (ME0) | `0x03` | 1 | 7 |
| `adc (y)` | A = A + (Y) + C  (ME0) | `0x13` | 1 | 7 |
| `adc (u)` | A = A + (U) + C  (ME0) | `0x23` | 1 | 7 |
| `adc (pp)` | A = A + (pp) + C (ME0) | `0xA3 a b` | 3 | 13 |
| `adc #(x)` | A = A + (X) + C  (ME1) | `0xFD 0x03` | 2 | 11 |
| `adc #(y)` | A = A + (Y) + C  (ME1) | `0xFD 0x13` | 2 | 11 |
| `adc #(u)` | A = A + (U) + C  (ME1) | `0xFD 0x23` | 2 | 11 |
| `adc #(pp)` | A = A + (pp) + C (ME1) | `0xFD 0xA3 a b` | 4 | 17 |

---

#### ADI — Add Immediate
`adi a,n`: `a = a + n + C` (carry is included when operand is accumulator).
`adi (Rreg),n`: `[operand] = [operand] + n` (no carry, result stored back to memory).
**Flags:** C, V, H, Z may change.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `adi a,n` | A = A + n + C | `0xB3 n` | 2 | 7 |
| `adi (x),n` | (X) = (X) + n  (ME0) | `0x4F n` | 2 | 13 |
| `adi (y),n` | (Y) = (Y) + n  (ME0) | `0x5F n` | 2 | 13 |
| `adi (u),n` | (U) = (U) + n  (ME0) | `0x6F n` | 2 | 13 |
| `adi (pp),n` | (pp) = (pp) + n (ME0) | `0xEF a b n` | 4 | 19 |
| `adi #(x),n` | (X) = (X) + n  (ME1) | `0xFD 0x4F n` | 3 | 17 |
| `adi #(y),n` | (Y) = (Y) + n  (ME1) | `0xFD 0x5F n` | 3 | 17 |
| `adi #(u),n` | (U) = (U) + n  (ME1) | `0xFD 0x6F n` | 3 | 17 |
| `adi #(pp),n` | (pp) = (pp) + n (ME1) | `0xFD 0xEF a b n` | 5 | 23 |

---

#### DCA — Decimal Add
BCD addition between accumulator and memory, including carry. The operation:
1. `a = a + 0x66`
2. `a = a + [operand] + C`
3. `a = a + DA` (decimal compensation based on C and H flags)

**Flags:** C, V, H, Z may change.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `dca (x)` | A = A + (X) BCD (ME0) | `0x8C` | 1 | 15 |
| `dca (y)` | A = A + (Y) BCD (ME0) | `0x9C` | 1 | 15 |
| `dca (u)` | A = A + (U) BCD (ME0) | `0xAC` | 1 | 15 |
| `dca #(x)` | A = A + (X) BCD (ME1) | `0xFD 0x8C` | 2 | 19 |
| `dca #(y)` | A = A + (Y) BCD (ME1) | `0xFD 0x9C` | 2 | 19 |
| `dca #(u)` | A = A + (U) BCD (ME1) | `0xFD 0xAC` | 2 | 19 |

---

#### ADR — Add Register (16-bit)
Adds the accumulator to the full 16-bit register pair. `RL + a → RL`, then `RH + C → RH`.

**Flags: UNCHANGED — this contradicts the Sharp Technical Reference Manual's own text**, which documents ADR as publishing C/V/H/Z from the internal 8-bit low-byte addition (as this entry itself used to say). Real-hardware testing settled it the other way: silicon preserves the caller's flags across ADR, full stop. This was confirmed by a reproducible bug — the PC-1500's own ROM key-dispatch path relies on carry surviving an `adr y`/`rtn` pair to redraw the display correctly after Up/Down in PRO mode; an ADR that clobbers flags (as MAME's implementation still does, as of this writing) breaks that redraw. Treat any emulator/tool that clobbers C/V/H/Z on ADR as buggy, not the manual's description as authoritative.
- Empirical test + write-up: sibling project `Calc-U-1600` (this user's own, not part of this repo), `examples/debug/adrtest_1500a.asm` (single-purpose: SEC then `adr x` with a guaranteed-no-carry add, reads carry back) and `examples/debug/instrquirks_1500a.asm` (broader 3-instruction test, see the DRL/DRR entries below); background in that project's `docs/Up-Down-Key-Investigation.md`, "The ADR conflict".

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `adr x` | X = X + A (16-bit) | `0xFD 0xCA` | 2 | 11 |
| `adr y` | Y = Y + A (16-bit) | `0xFD 0xDA` | 2 | 11 |
| `adr u` | U = U + A (16-bit) | `0xFD 0xEA` | 2 | 11 |

---

#### SBC — Subtract with Carry
`a = a - [operand] - NOT(C)` (equivalently, `a = a + complement([operand]) + C`).
**Flags:** C, V, H, Z may change. **C=1 means no borrow.**

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `sbc xl` | A = A - XL - NOT(C) | `0x00` | 1 | 6 |
| `sbc yl` | A = A - YL - NOT(C) | `0x10` | 1 | 6 |
| `sbc ul` | A = A - UL - NOT(C) | `0x20` | 1 | 6 |
| `sbc xh` | A = A - XH - NOT(C) | `0x80` | 1 | 6 |
| `sbc yh` | A = A - YH - NOT(C) | `0x90` | 1 | 6 |
| `sbc uh` | A = A - UH - NOT(C) | `0xA0` | 1 | 6 |
| `sbc (x)` | A = A - (X) - NOT(C)  (ME0) | `0x01` | 1 | 7 |
| `sbc (y)` | A = A - (Y) - NOT(C)  (ME0) | `0x11` | 1 | 7 |
| `sbc (u)` | A = A - (U) - NOT(C)  (ME0) | `0x21` | 1 | 7 |
| `sbc (pp)` | A = A - (pp) - NOT(C) (ME0) | `0xA1 a b` | 3 | 13 |
| `sbc #(x)` | A = A - (X) - NOT(C)  (ME1) | `0xFD 0x01` | 2 | 11 |
| `sbc #(y)` | A = A - (Y) - NOT(C)  (ME1) | `0xFD 0x11` | 2 | 11 |
| `sbc #(u)` | A = A - (U) - NOT(C)  (ME1) | `0xFD 0x21` | 2 | 11 |
| `sbc #(pp)` | A = A - (pp) - NOT(C) (ME1) | `0xFD 0xA1 a b` | 4 | 17 |

---

#### SBI — Subtract Immediate
`a = a - n - NOT(C)`
**Flags:** C, V, H, Z may change. **C=1 means no borrow.**

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `sbi a,n` | A = A - n - NOT(C) | `0xB1 n` | 2 | 7 |

---

#### DCS — Decimal Subtract
BCD subtraction. `a = a - [operand] - NOT(C)` with decimal adjustment.
**Flags:** C, V, H, Z may change. **C=1 means no borrow.**

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `dcs (x)` | A = A - (X) BCD (ME0) | `0x0C` | 1 | 13 |
| `dcs (y)` | A = A - (Y) BCD (ME0) | `0x1C` | 1 | 13 |
| `dcs (u)` | A = A - (U) BCD (ME0) | `0x2C` | 1 | 13 |
| `dcs #(x)` | A = A - (X) BCD (ME1) | `0xFD 0x0C` | 2 | 17 |
| `dcs #(y)` | A = A - (Y) BCD (ME1) | `0xFD 0x1C` | 2 | 17 |
| `dcs #(u)` | A = A - (U) BCD (ME1) | `0xFD 0x2C` | 2 | 17 |

---

#### AND — Logical AND (Accumulator)
`a = a and [operand]`
**Flags:** Z only.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `and (x)` | A = A & (X)  (ME0) | `0x09` | 1 | 7 |
| `and (y)` | A = A & (Y)  (ME0) | `0x19` | 1 | 7 |
| `and (u)` | A = A & (U)  (ME0) | `0x29` | 1 | 7 |
| `and (pp)` | A = A & (pp) (ME0) | `0xA9 a b` | 3 | 13 |
| `and #(x)` | A = A & (X)  (ME1) | `0xFD 0x09` | 2 | 11 |
| `and #(y)` | A = A & (Y)  (ME1) | `0xFD 0x19` | 2 | 11 |
| `and #(u)` | A = A & (U)  (ME1) | `0xFD 0x29` | 2 | 11 |
| `and #(pp)` | A = A & (pp) (ME1) | `0xFD 0xA9 a b` | 4 | 17 |

---

#### ANI — AND Immediate
`ani a,n`: `a = a & n`.
`ani (Rreg),n`: `[operand] = [operand] & n` (result stored back to memory).
**Flags:** Z only.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `ani a,n` | A = A & n | `0xB9 n` | 2 | 7 |
| `ani (x),n` | (X) = (X) & n  (ME0) | `0x49 n` | 2 | 13 |
| `ani (y),n` | (Y) = (Y) & n  (ME0) | `0x59 n` | 2 | 13 |
| `ani (u),n` | (U) = (U) & n  (ME0) | `0x69 n` | 2 | 13 |
| `ani (pp),n` | (pp) = (pp) & n (ME0) | `0xE9 a b n` | 4 | 19 |
| `ani #(x),n` | (X) = (X) & n  (ME1) | `0xFD 0x49 n` | 3 | 17 |
| `ani #(y),n` | (Y) = (Y) & n  (ME1) | `0xFD 0x59 n` | 3 | 17 |
| `ani #(u),n` | (U) = (U) & n  (ME1) | `0xFD 0x69 n` | 3 | 17 |
| `ani #(pp),n` | (pp) = (pp) & n (ME1) | `0xFD 0xE9 a b n` | 5 | 23 |

---

#### ORA — Logical OR (Accumulator)
`a = a OR [operand]`
**Flags:** Z only.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `ora (x)` | A = A \| (X)  (ME0) | `0x0B` | 1 | 7 |
| `ora (y)` | A = A \| (Y)  (ME0) | `0x1B` | 1 | 7 |
| `ora (u)` | A = A \| (U)  (ME0) | `0x2B` | 1 | 7 |
| `ora (pp)` | A = A \| (pp) (ME0) | `0xAB a b` | 3 | 13 |
| `ora #(x)` | A = A \| (X)  (ME1) | `0xFD 0x0B` | 2 | 11 |
| `ora #(y)` | A = A \| (Y)  (ME1) | `0xFD 0x1B` | 2 | 11 |
| `ora #(u)` | A = A \| (U)  (ME1) | `0xFD 0x2B` | 2 | 11 |
| `ora #(pp)` | A = A \| (pp) (ME1) | `0xFD 0xAB a b` | 4 | 17 |

---

#### ORI — OR Immediate
`ori a,n`: `a = a | n`.
`ori (Rreg),n`: `[operand] = [operand] | n`.
**Flags:** Z only.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `ori a,n` | A = A \| n | `0xBB n` | 2 | 7 |
| `ori (x),n` | (X) = (X) \| n  (ME0) | `0x4B n` | 2 | 13 |
| `ori (y),n` | (Y) = (Y) \| n  (ME0) | `0x5B n` | 2 | 13 |
| `ori (u),n` | (U) = (U) \| n  (ME0) | `0x6B n` | 2 | 13 |
| `ori (pp),n` | (pp) = (pp) \| n (ME0) | `0xEB a b n` | 4 | 19 |
| `ori #(x),n` | (X) = (X) \| n  (ME1) | `0xFD 0x4B n` | 3 | 17 |
| `ori #(y),n` | (Y) = (Y) \| n  (ME1) | `0xFD 0x5B n` | 3 | 17 |
| `ori #(u),n` | (U) = (U) \| n  (ME1) | `0xFD 0x6B n` | 3 | 17 |
| `ori #(pp),n` | (pp) = (pp) \| n (ME1) | `0xFD 0xEB a b n` | 5 | 23 |

---

#### EOR — Exclusive OR (Accumulator)
`a = a XOR [operand]`
**Flags:** Z only.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `eor (x)` | A = A ^ (X)  (ME0) | `0x0D` | 1 | 7 |
| `eor (y)` | A = A ^ (Y)  (ME0) | `0x1D` | 1 | 7 |
| `eor (u)` | A = A ^ (U)  (ME0) | `0x2D` | 1 | 7 |
| `eor (pp)` | A = A ^ (pp) (ME0) | `0xAD a b` | 3 | 13 |
| `eor #(x)` | A = A ^ (X)  (ME1) | `0xFD 0x0D` | 2 | 11 |
| `eor #(y)` | A = A ^ (Y)  (ME1) | `0xFD 0x1D` | 2 | 11 |
| `eor #(u)` | A = A ^ (U)  (ME1) | `0xFD 0x2D` | 2 | 11 |
| `eor #(pp)` | A = A ^ (pp) (ME1) | `0xFD 0xAD a b` | 4 | 17 |

---

#### EAI — Exclusive OR Accumulator Immediate
`a = a XOR n`
**Flags:** Z only.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `eai n` | A = A ^ n | `0xBD n` | 2 | 7 |

---

#### INC — Increment
For 8-bit operands (A, RL, RH): flags C, V, H, Z may change.
For 16-bit operand (Rreg): no flag changes.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `inc a` | A = A + 1 | `0xDD` | 1 | 5 |
| `inc xl` | XL = XL + 1 | `0x40` | 1 | 5 |
| `inc yl` | YL = YL + 1 | `0x50` | 1 | 5 |
| `inc ul` | UL = UL + 1 | `0x60` | 1 | 5 |
| `inc xh` | XH = XH + 1 | `0xFD 0x40` | 2 | 9 |
| `inc yh` | YH = YH + 1 | `0xFD 0x50` | 2 | 9 |
| `inc uh` | UH = UH + 1 | `0xFD 0x60` | 2 | 9 |
| `inc x` | X = X + 1 (16-bit, no flags) | `0x44` | 1 | 5 |
| `inc y` | Y = Y + 1 (16-bit, no flags) | `0x54` | 1 | 5 |
| `inc u` | U = U + 1 (16-bit, no flags) | `0x64` | 1 | 5 |

---

#### DEC — Decrement
For 8-bit operands (A, RL, RH): flags C, V, H, Z may change.
For 16-bit operand (Rreg): no flag changes.

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `dec a` | A = A - 1 | `0xDF` | 1 | 5 |
| `dec xl` | XL = XL - 1 | `0x42` | 1 | 5 |
| `dec yl` | YL = YL - 1 | `0x52` | 1 | 5 |
| `dec ul` | UL = UL - 1 | `0x62` | 1 | 5 |
| `dec xh` | XH = XH - 1 | `0xFD 0x42` | 2 | 9 |
| `dec yh` | YH = YH - 1 | `0xFD 0x52` | 2 | 9 |
| `dec uh` | UH = UH - 1 | `0xFD 0x62` | 2 | 9 |
| `dec x` | X = X - 1 (16-bit, no flags) | `0x46` | 1 | 5 |
| `dec y` | Y = Y - 1 (16-bit, no flags) | `0x56` | 1 | 5 |
| `dec u` | U = U - 1 (16-bit, no flags) | `0x66` | 1 | 5 |

---

### Compare and Bit Test Instructions

#### CPA — Compare Accumulator
Subtracts operand from A to set flags; A is not modified.
`a - [operand]` → flags only.
**Flags:** C, V, H, Z may change.

**Flag Table for `cpa`:**

| Condition | C | Z |
|---|:---:|:---:|
| **A > operand** | 1 | 0 |
| **A == operand** | 1 | 1 |
| **A < operand** | 0 | 0 |

*V and H are also updated but are typically ignored for simple comparisons.*

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `cpa xl` | `0x06` | 1 | 6 |
| `cpa yl` | `0x16` | 1 | 6 |
| `cpa ul` | `0x26` | 1 | 6 |
| `cpa xh` | `0x86` | 1 | 6 |
| `cpa yh` | `0x96` | 1 | 6 |
| `cpa uh` | `0xA6` | 1 | 6 |
| `cpa (x)` | `0x07` | 1 | 7 |
| `cpa (y)` | `0x17` | 1 | 7 |
| `cpa (u)` | `0x27` | 1 | 7 |
| `cpa (pp)` | `0xA7 a b` | 3 | 13 |
| `cpa #(x)` | `0xFD 0x07` | 2 | 11 |
| `cpa #(y)` | `0xFD 0x17` | 2 | 11 |
| `cpa #(u)` | `0xFD 0x27` | 2 | 11 |
| `cpa #(pp)` | `0xFD 0xA7 a b` | 4 | 17 |

---

#### CPI — Compare Immediate
Subtracts immediate `n` from the operand to set flags; operand is not modified.
`[operand] - n` → flags only.
**Flags:** C, V, H, Z may change.

**Flag Table for `cpi`:**

| Condition | C | Z |
|---|:---:|:---:|
| **Operand > n** | 1 | 0 |
| **Operand == n** | 1 | 1 |
| **Operand < n** | 0 | 0 |

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `cpi a,n` | `0xB7 n` | 2 | 7 |
| `cpi xl,n` | `0x4E n` | 2 | 7 |
| `cpi yl,n` | `0x5E n` | 2 | 7 |
| `cpi ul,n` | `0x6E n` | 2 | 7 |
| `cpi xh,n` | `0x4C n` | 2 | 7 |
| `cpi yh,n` | `0x5C n` | 2 | 7 |
| `cpi uh,n` | `0x6C n` | 2 | 7 |

---

#### BIT — Bit Test (Accumulator AND Memory)
ANDs the accumulator with memory; only the Z flag is updated. Neither A nor memory is modified.
`a and [operand]` → Z flag only.
**Flags:** Z only.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `bit (x)` | `0x0F` | 1 | 7 |
| `bit (y)` | `0x1F` | 1 | 7 |
| `bit (u)` | `0x2F` | 1 | 7 |
| `bit (pp)` | `0xAF a b` | 3 | 13 |
| `bit #(x)` | `0xFD 0x0F` | 2 | 11 |
| `bit #(y)` | `0xFD 0x1F` | 2 | 11 |
| `bit #(u)` | `0xFD 0x2F` | 2 | 11 |
| `bit #(pp)` | `0xFD 0xAF a b` | 4 | 17 |

---

#### BII — Bit Test Immediate
ANDs the operand with immediate `n`; only the Z flag is updated.
`[operand] and n` → Z flag only.
**Flags:** Z only.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `bii a,n` | `0xBF n` | 2 | 7 |
| `bii (x),n` | `0x4D n` | 2 | 10 |
| `bii (y),n` | `0x5D n` | 2 | 10 |
| `bii (u),n` | `0x6D n` | 2 | 10 |
| `bii (pp),n` | `0xED a b n` | 4 | 16 |
| `bii #(x),n` | `0xFD 0x4D n` | 3 | 14 |
| `bii #(y),n` | `0xFD 0x5D n` | 3 | 14 |
| `bii #(u),n` | `0xFD 0x6D n` | 3 | 14 |
| `bii #(pp),n` | `0xFD 0xED a b n` | 5 | 20 |

---

### Transfer and Search Instructions

#### LDA — Load Accumulator
`[operand] → a`
**Flags:** Z only.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `lda xl` | `0x04` | 1 | 5 |
| `lda yl` | `0x14` | 1 | 5 |
| `lda ul` | `0x24` | 1 | 5 |
| `lda xh` | `0x84` | 1 | 5 |
| `lda yh` | `0x94` | 1 | 5 |
| `lda uh` | `0xA4` | 1 | 5 |
| `lda (x)` | `0x05` | 1 | 6 |
| `lda (y)` | `0x15` | 1 | 6 |
| `lda (u)` | `0x25` | 1 | 6 |
| `lda (pp)` | `0xA5 a b` | 3 | 12 |
| `lda #(x)` | `0xFD 0x05` | 2 | 10 |
| `lda #(y)` | `0xFD 0x15` | 2 | 10 |
| `lda #(u)` | `0xFD 0x25` | 2 | 10 |
| `lda #(pp)` | `0xFD 0xA5 a b` | 4 | 16 |

---

#### LDE — Load and Decrement
Loads memory at Rreg into A, then decrements Rreg by 1.
`(Rreg) → a`, `Rreg - 1 → Rreg`
**Flags:** Z only.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `lde x` | `0x47` | 1 | 6 |
| `lde y` | `0x57` | 1 | 6 |
| `lde u` | `0x67` | 1 | 6 |

---

#### LIN — Load and Increment
Loads memory at Rreg into A, then increments Rreg by 1.
`(Rreg) → a`, `Rreg + 1 → Rreg`
**Flags:** Z only.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `lin x` | `0x45` | 1 | 6 |
| `lin y` | `0x55` | 1 | 6 |
| `lin u` | `0x65` | 1 | 6 |

---

#### LDI — Load Immediate
Loads an immediate value into the accumulator, a register byte, or the stack pointer.
- `ldi a,n`: Z changes. `n → a`
- `ldi RL,n` / `ldi RH,n`: No flag changes. `n → register`
- `ldi s,pp`: No flag changes. `pp → s` (16-bit)

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `ldi a,n` | `0xB5 n` | 2 | 6 |
| `ldi xl,n` | `0x4A n` | 2 | 6 |
| `ldi yl,n` | `0x5A n` | 2 | 6 |
| `ldi ul,n` | `0x6A n` | 2 | 6 |
| `ldi xh,n` | `0x48 n` | 2 | 6 |
| `ldi yh,n` | `0x58 n` | 2 | 6 |
| `ldi uh,n` | `0x68 n` | 2 | 6 |
| `ldi s,pp` | `0xAA a b` | 3 | 12 |

---

#### LDX — Load X Register (16-bit)
Transfers a 16-bit register or the stack/program counter into Xreg.
`[operand] → x`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `ldx y` | X = Y | `0xFD 0x18` | 2 | 11 |
| `ldx u` | X = U | `0xFD 0x28` | 2 | 11 |
| `ldx s` | X = S (Stack Pointer) | `0xFD 0x48` | 2 | 11 |
| `ldx p` | X = P (Program Counter) | `0xFD 0x58` | 2 | 11 |

---

#### STA — Store Accumulator
`a → [operand]`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `sta xl` | `0x0A` | 1 | 5 |
| `sta yl` | `0x1A` | 1 | 5 |
| `sta ul` | `0x2A` | 1 | 5 |
| `sta xh` | `0x08` | 1 | 5 |
| `sta yh` | `0x18` | 1 | 5 |
| `sta uh` | `0x28` | 1 | 5 |
| `sta (x)` | `0x0E` | 1 | 6 |
| `sta (y)` | `0x1E` | 1 | 6 |
| `sta (u)` | `0x2E` | 1 | 6 |
| `sta (pp)` | `0xAE a b` | 3 | 12 |
| `sta #(x)` | `0xFD 0x0E` | 2 | 10 |
| `sta #(y)` | `0xFD 0x1E` | 2 | 10 |
| `sta #(u)` | `0xFD 0x2E` | 2 | 10 |
| `sta #(pp)` | `0xFD 0xAE a b` | 4 | 16 |

*Note: `sta VH` (opcode `0x38`) is functionally identical to `nop`.*

---

#### SDE — Store and Decrement
Stores A to memory at Rreg, then decrements Rreg by 1.
`a → (Rreg)`, `Rreg - 1 → Rreg`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `sde x` | `0x43` | 1 | 6 |
| `sde y` | `0x53` | 1 | 6 |
| `sde u` | `0x63` | 1 | 6 |

---

#### SIN — Store and Increment
Stores A to memory at Rreg, then increments Rreg by 1.
`a → (Rreg)`, `Rreg + 1 → Rreg`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `sin x` | `0x41` | 1 | 6 |
| `sin y` | `0x51` | 1 | 6 |
| `sin u` | `0x61` | 1 | 6 |

---

#### STX — Store X Register (16-bit)
Transfers Xreg to another 16-bit register, the stack pointer, or the program counter.
`x → [operand]`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `stx y` | Y = X | `0xFD 0x5A` | 2 | 11 |
| `stx u` | U = X | `0xFD 0x6A` | 2 | 11 |
| `stx s` | S = X (Stack Pointer) | `0xFD 0x4E` | 2 | 11 |
| `stx p` | P = X (Program Counter — indirect jump) | `0xFD 0x5E` | 2 | 11 |

---

### Stack Instructions

#### PSH — Push to Stack
Pushes the accumulator or a 16-bit register pair onto the stack.
- `psh a`: `a → (s)`, `s - 1 → s`
- `psh Rreg`: `RL → (s)`, `s - 1 → s`, `RH → (s)`, `s - 1 → s`

**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `psh a` | `0xFD 0xC8` | 2 | 11 |
| `psh x` | `0xFD 0x88` | 2 | 14 |
| `psh y` | `0xFD 0x98` | 2 | 14 |
| `psh u` | `0xFD 0xA8` | 2 | 14 |

---

#### POP — Pop from Stack
Pops the accumulator or a 16-bit register pair from the stack.
- `pop a`: `s + 1 → s`, `(s) → a`. **Z flag changes.**
- `pop Rreg`: `s + 1 → s`, `(s) → RH`, `s + 1 → s`, `(s) → RL`. **No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `pop a` | `0xFD 0x8A` | 2 | 12 |
| `pop x` | `0xFD 0x0A` | 2 | 15 |
| `pop y` | `0xFD 0x1A` | 2 | 15 |
| `pop u` | `0xFD 0x2A` | 2 | 15 |

---

### Register Transfer Instructions

#### ATT — Accumulator to T Register
Loads the T (status flags) register from the accumulator.
`a → t`
**No flag changes** (but all flags are overwritten with the value of A).

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `att` | `0xFD 0xEC` | 2 | 9 |

---

#### TTA — T Register to Accumulator
Transfers the T (status flags) register to the accumulator.
`t → a`
**Flags:** Z changes based on the value of T.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `tta` | `0xFD 0xAA` | 2 | 9 |

---

### Block Transfer and Search Instructions

#### TIN — Transfer and Increment
Copies one byte from memory at X to memory at Y, then increments both pointers.
`(x) → (y)`, `x + 1 → x`, `y + 1 → y`
**No flag changes.**

Typically used in a `lop` loop for block memory copies.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `tin` | `0xF5` | 1 | 7 |

---

#### CIN — Compare and Increment
Compares A with the byte at memory X (like CPA), then increments X.
`a - (x)` → flags, `x + 1 → x`
**Flags:** C, V, H, Z may change (same table as CPA).

Typically used in a `lop` loop for block memory searches.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `cin` | `0xF7` | 1 | 7 |

---

### Rotate and Shift Instructions

#### ROL — Rotate Left Through Carry
Rotates the accumulator left through the carry flag. The carry becomes the new bit 0; the old bit 7 becomes the new carry.
`C ← a[7:0] ← C`
**Flags:** C changes.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `rol` | `0xDB` | 1 | 8 |

---

#### ROR — Rotate Right Through Carry
Rotates the accumulator right through the carry flag. The carry becomes the new bit 7; the old bit 0 becomes the new carry.
`C → a[7:0] → C`
**Flags:** C changes.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `ror` | `0xD1` | 1 | 9 |

---

#### SHL — Shift Left
Shifts the accumulator left. Bit 7 moves into carry; 0 is shifted into bit 0.
`C ← a[7:0] ← 0`
**Flags:** C changes.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `shl` | `0xD9` | 1 | 6 |

---

#### SHR — Shift Right
Shifts the accumulator right. Bit 0 moves into carry; 0 is shifted into bit 7.
`0 → a[7:0] → C`
**Flags:** C changes.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `shr` | `0xD5` | 1 | 9 |

---

#### DRL — Digit Rotate Left

**✅ CONFIRMED on real PC-1500A hardware.** Three mutually incompatible readings of DRL/DRR existed across emulators; a real-silicon test settled it:

With `a = 0x12` and `(Xreg) = 0x34` going in, DRL produces `a = 0x34`, mem `= 0x41`. That is **whole-byte swap: A becomes the entire old memory byte**; memory becomes a merge of its own old low nibble with A's old opposite nibble, and A's other old nibble is genuinely discarded, not conserved anywhere. The two readings this ruled out:

| Reading | Seen in | `a` after DRL | mem after DRL | `a` after DRR | mem after DRR |
|---|---|---|---|---|---|
| **whole-byte swap (confirmed)** | MESS/MAME, PockEmul, forever1500, this project's own core | `0x34` | `0x41` | `0x34` | `0x23` |
| 3-nibble rotate — **ruled out** | (an earlier guess in this project's own core, before this test) | `0x32` | `0x41` | `0x14` | `0x23` |
| Z80 RLD/RRD semantics — **ruled out** | — | `0x13` | `0x42` | `0x14` | `0x23` |

**Transfer diagram** (left rotation between the accumulator and memory at Xreg, in units of 4 bits / one BCD digit):
- `Mem[old]` (the entire old byte) → `a` (A becomes the whole old memory byte, high nibble included)
- `Mem[3:0]` (old) → `Mem[7:4]` (new) (memory's own old low nibble rotates up into its new high nibble)
- `a[7:4]` (old) → `Mem[3:0]` (new) (A's old high nibble becomes the new memory low nibble)
- `a[3:0]` (old) — discarded; not conserved anywhere

**No flag changes.** Only operates on `(Xreg)` or `#(Xreg)`.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `drl (x)` | ME0 | `0xD7` | 1 | 12 |
| `drl #(x)` | ME1 | `0xFD 0xD7` | 2 | 16 |

Confirmed by sibling project `Calc-U-1600` (this user's own, not part of this repo) running `dev/hardware-checks/instrquirks_1500a.asm` / `.bin` (preset `instrquirks.pc1500a`) on a real PC-1500A and PEEKing the result bytes — see that file's own header comment for the full discriminating-test writeup. `Core/CPU/LH5801/LH5801.cpp`'s `drlMerge`/`drrMerge` implement this reading, and the hardware run confirms it.

---

#### DRR — Digit Rotate Right

**✅ CONFIRMED on real PC-1500A hardware** — see the DRL entry immediately above for the full discriminating-test table and provenance. With `a = 0x12` and `(Xreg) = 0x34` going in, DRR produces `a = 0x34`, mem `= 0x23` — same whole-byte-swap reading as DRL. (DRR's own memory-byte result happens to be identical under all three readings that were considered, so DRL's accumulator result did the actual discriminating; DRR was captured alongside it as a direct cross-check.)

**Transfer diagram** (right rotation between the accumulator and memory at Xreg, in units of 4 bits):
- `Mem[old]` (the entire old byte) → `a` (A becomes the whole old memory byte, low nibble included)
- `Mem[7:4]` (old) → `Mem[3:0]` (new) (memory's own old high nibble rotates down into its new low nibble)
- `a[3:0]` (old) → `Mem[7:4]` (new) (A's old low nibble becomes the new memory high nibble)
- `a[7:4]` (old) — discarded; not conserved anywhere

**No flag changes.** Only operates on `(Xreg)` or `#(Xreg)`.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `drr (x)` | ME0 | `0xD3` | 1 | 12 |
| `drr #(x)` | ME1 | `0xFD 0xD3` | 2 | 16 |

---

#### AEX — Accumulator Exchange Nibbles
Swaps the high and low 4-bit nibbles of the accumulator.
`a[7:4] ↔ a[3:0]`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `aex` | `0xF1` | 1 | 6 |

---

### CPU Control Instructions

#### SEC — Set Carry
Sets the carry flag. `1 → C`
**Flags:** C = 1.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `sec` | `0xFB` | 1 | 4 |

---

#### REC — Reset Carry
Resets the carry flag. `0 → C`
**Flags:** C = 0.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `rec` | `0xF9` | 1 | 4 |

---

#### SIE — Set Interrupt Enable
Sets the IE flag, enabling maskable and timer interrupts. `1 → IE`
**Flags:** IE = 1 (other flags unchanged).

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `sie` | `0xFD 0x81` | 2 | 8 |

---

#### RIE — Reset Interrupt Enable
Resets the IE flag, disabling maskable and timer interrupts. `0 → IE`
**Flags:** IE = 0 (other flags unchanged).

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `rie` | `0xFD 0xBE` | 2 | 8 |

---

#### SPU — Set PU Flip-Flop
Sets the general-purpose flip-flop PU. `1 → PU`
Used in the PC-1500 for ROM bank switching.
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `spu` | `0xE1` | 1 | 4 |

---

#### RPU — Reset PU Flip-Flop
Resets the general-purpose flip-flop PU. `0 → PU`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `rpu` | `0xE3` | 1 | 4 |

---

#### SPV — Set PV Flip-Flop
Sets the general-purpose flip-flop PV. `1 → PV`
Used in the PC-1500 for external device selection.
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `spv` | `0xA8` | 1 | 4 |

---

#### RPV — Reset PV Flip-Flop
Resets the general-purpose flip-flop PV. `0 → PV`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `rpv` | `0xB8` | 1 | 4 |

---

#### SDP — Set Display
Sets the DISP flip-flop, enabling the LCD display. `1 → DISP`
Causes the CPU's internal LCD backplate signals (H0–H7) to generate an on-pattern.
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `sdp` | `0xFD 0xC1` | 2 | 9 |

---

#### RDP — Reset Display
Resets the DISP flip-flop, disabling the LCD display. `0 → DISP`
Causes the CPU's internal LCD backplate signals to generate an off-pattern.
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `rdp` | `0xFD 0xC0` | 2 | 8 |

---

#### AM0 — Accumulator to Timer (bit 8 = 0)
Transfers A to the lower 8 bits of the 9-bit timer register TM. Bit 8 of TM is cleared.
`a → TM[7:0]`, `0 → TM[8]`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `am0` | `0xFD 0xCE` | 2 | 9 |

---

#### AM1 — Accumulator to Timer (bit 8 = 1)
Same as AM0, but bit 8 of TM is set.
`a → TM[7:0]`, `1 → TM[8]`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `am1` | `0xFD 0xDE` | 2 | 9 |

---

#### ATP — Accumulator to Port
Sends the contents of A onto the data bus. The CPU simultaneously asserts clock `Pφ`, which can be used as a latch clock for an external output port IC.
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `atp` | `0xFD 0xCC` | 2 | 9 |

---

#### ITA — Input to Accumulator
Reads the 8-bit input port (IN0–IN7) into the accumulator.
`IN0–IN7 → a`
**Flags:** Z changes.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `ita` | `0xFD 0xBA` | 2 | 9 |

---

#### CDV — Clear Divider
Clears (resets) the internal clock divider. Effectively resets the CPU clock timing.
`0 → divider`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `cdv` | `0xFD 0x8E` | 2 | 8 |

---

#### NOP — No Operation
Performs no operation. Equivalent to `sta VH` (storing A to the undocumented V-register high byte has no effect).
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `nop` | `0x38` | 1 | 5 |

---

#### HLT — Halt
Stops CPU instruction execution. Only the internal clock divider continues running. The CPU resumes automatically when an interrupt occurs.
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `hlt` | `0xFD 0xB1` | 2 | 9 |

---

#### OFF — Power Off (BF Flip-Flop Reset)
Resets the BF (battery-backed) flip-flop. On the PC-1500, this is used to signal a power-off request. The CPU checks the BFI input pin to resume.
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `off` | `0xFD 0x4C` | 2 | 8 |

---

### Jump Instructions

#### JMP — Unconditional Jump
Jumps to the absolute 16-bit address `pp`.
`i → PH`, `j → PL` (where `pp` = high byte `i`, low byte `j`)
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `jmp pp` | `0xBA a b` | 3 | 12 |

---

#### BCH — Branch Unconditional (Relative)
Jumps unconditionally by adding or subtracting the immediate offset `e` from the program counter.
Range: -255 < e < 255.
**No flag changes.**

| Format | Operation | Opcode | Bytes | Cycles |
|---|---|---|---|---|
| `bch+e` | P = P + e (forward) | `0x8E e` | 2 | 8 |
| `bch-e` | P = P - e (backward) | `0x9E e` | 2 | 9 |

---

#### BCS / BCR — Branch on Carry Set / Reset
Conditional relative branch based on the Carry flag.
**No flag changes.** Cycles: 8 if no branch, 10 (forward) or 11 (backward) if taken.

| Format | Condition | Opcode | Bytes |
|---|---|---|---|
| `bcs+e` | Branch forward if C = 1 | `0x83 e` | 2 |
| `bcs-e` | Branch backward if C = 1 | `0x93 e` | 2 |
| `bcr+e` | Branch forward if C = 0 | `0x81 e` | 2 |
| `bcr-e` | Branch backward if C = 0 | `0x91 e` | 2 |

---

#### BHS / BHR — Branch on Half-Carry Set / Reset
Conditional relative branch based on the Half-Carry flag.
**No flag changes.** Cycles: 8 if no branch, 10/11 if taken.

| Format | Condition | Opcode | Bytes |
|---|---|---|---|
| `bhs+e` | Branch forward if H = 1 | `0x87 e` | 2 |
| `bhs-e` | Branch backward if H = 1 | `0x97 e` | 2 |
| `bhr+e` | Branch forward if H = 0 | `0x85 e` | 2 |
| `bhr-e` | Branch backward if H = 0 | `0x95 e` | 2 |

---

#### BZS / BZR — Branch on Zero Set / Reset
Conditional relative branch based on the Zero flag.
**No flag changes.** Cycles: 8 if no branch, 10/11 if taken.

| Format | Condition | Opcode | Bytes |
|---|---|---|---|
| `bzs+e` | Branch forward if Z = 1 | `0x8B e` | 2 |
| `bzs-e` | Branch backward if Z = 1 | `0x9B e` | 2 |
| `bzr+e` | Branch forward if Z = 0 | `0x89 e` | 2 |
| `bzr-e` | Branch backward if Z = 0 | `0x99 e` | 2 |

---

#### BVS / BVR — Branch on Overflow Set / Reset
Conditional relative branch based on the Overflow flag.
**No flag changes.** Cycles: 8 if no branch, 10/11 if taken.

| Format | Condition | Opcode | Bytes |
|---|---|---|---|
| `bvs+e` | Branch forward if V = 1 | `0x8F e` | 2 |
| `bvs-e` | Branch backward if V = 1 | `0x9F e` | 2 |
| `bvr+e` | Branch forward if V = 0 | `0x8D e` | 2 |
| `bvr-e` | Branch backward if V = 0 | `0x9D e` | 2 |

---

#### LOP — Loop
Decrements UL by 1. If no borrow (UL was > 0), branches backward by `e`. If borrow (UL underflowed), falls through to the next instruction.
`ul - 1 → ul`; if no borrow: `p - e → p`
**No flag changes.**

This instruction is used to implement counted loops. Load UL with the loop count before the loop body, then place `lop` at the end.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `lop ul,e` | `0x88 e` | 2 | 8 (exit) / 11 (loop) |

---

### Subroutine and Vector Jump Instructions

#### SJP — Subroutine Jump (Call)
Pushes the return address onto the stack, then jumps to absolute address `pp`.
`PL → (s)`, `s-1 → s`, `PH → (s)`, `s-1 → s`, `i → PH`, `j → PL`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `sjp pp` | `0xBE a b` | 3 | 19 |

---

#### VEJ — Vector Subroutine Jump (1-byte)
Single-byte subroutine call. Pushes the return address, then jumps to the address stored at the vector table entry `(0xFF00 + operand)`.
The vector table occupies addresses `0xFFC0–0xFFF6` in the PC-1500 ROM.
There are 28 valid VEJ operands: the even values `0xC0`–`0xF6`. The vectors at `0xFFF8`–`0xFFFE` (interrupts, reset) can't be called with VEJ: the opcodes `0xF8`–`0xFE` are other instructions (`0xF9` REC, `0xFB` SEC, `0xFD` the prefix), and sdaslh5801 refuses them.
**Flags:** Z is reset.

**Syntax: `vej 0xnn` — a constant expression, written like any other number.** e.g. `vej 0xF2`. `vej (0xF2)` works too (a parenthesised expression), but **`vej (F2)` does not**: sdaslh5801 reads `F2` as a symbol name and fails with "VEJ Vector Must Be A Constant" (every vector starts with a letter, C–F). Checked against sdaslh5801 (`m5801mch.c`, `S_TYPVEJ`).

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `vej 0xnn` | `nn` (where nn = 0xC0..0xF6, even) | 1 | 17 |

**PC-1500 VEJ Vector Table (partial -- ROM-defined subroutines):**

| Syntax | Addr | PC-1500 Function |
|---|---|---|
| `vej 0xC0` | `0xDD08` | Load next token/character to U register |
| `vej 0xC2` | `0xDCD4` | Check if character in U matches argument; branch if not |
| `vej 0xC4` | `0xDCD5` | Check if next character in U matches argument; branch if not |
| `vej 0xC6` | `0xDD13` | Decrement Y register by 2 (token) or 1 (character) |
| `vej 0xC8` | `0xDCC5` | Syntax check: jump forward if not end-of-command |
| `vej 0xCA` | `0xC001` | Transfer X register to variable at offset `b1` |
| `vej 0xCC` | `0xDDC8` | Load X register from variable address at offset `b1` |
| `vej 0xCE` | `0xD45D` | Determine address of variable `b1`; branch if not numeric |
| `vej 0xD0` | `0xD5F9` | Convert AR-X to integer into U register; branch on overflow |
| `vej 0xD2` | `0xDD1A` | Reseed AR-X with integer or process CSI |
| `vej 0xD4` | `0xDEE3` | Save BASIC position Y into slot P1 (`A0` previous line, `AC` BREAK, `B2` ERROR) |
| `vej 0xD6` | `0xDED1` | Restore BASIC position into Y and `0x789C`–`0x789F` from slot P1 (`A6` search, `AC` BREAK, `B8` ON ERROR) |
| `vej 0xD8` | `0xDF3B` | Check if program expires (Z=0 if so) |
| `vej 0xDA` | `0xC00E` | Cache variable address from U register and length from AR-X |
| `vej 0xDC` | `0xDEBC` | Load CSI from AR-X |
| `vej 0xDE` | `0xD6DF` | Evaluate formula pointed to by Y; jump forward on error |
| `vej 0xE0` | `0xCD8B` | Error check if UH ≠ 0x00 |
| `vej 0xE2` | `0xC400` | Start of BASIC interpreter |
| `vej 0xE4` | `0xCD89` | Output error 1, return to editor |
| `vej 0xE6` | `0xF70D` | Transfer AR-X to AR-Y |
| `vej 0xE8` | `0xF661` | Convert AR-X to absolute BCD form |
| `vej 0xEA` | `0xF79C` | Push AR-X one nibble left |
| `vej 0xEC` | `0xF757` | Clear arithmetic register X |
| `vej 0xEE` | `0xF7CC` | AR-X = AR-X + AR-U |
| `vej 0xF0` | `0xEFBA` | AR-X = AR-X + AR-Y (floating-point addition) |
| `vej 0xF2` | `0xEE71` | Clear LCD display. **Does not reset cursor pointer at `0x7875`** — always follow with `ldi a,0x00` then `sta (CURSOR_PTR)`. |
| `vej 0xF4` | `0xDBBC` | Load U register with 16-bit value from address `w1` |
| `vej 0xF6` | `0xDDB5` | Transfer U register to address `w1` |
| (vector `0xFFF8`) | `0xE171` | Maskable interrupt routine entry |
| (vector `0xFFFA`) | `0xE22C` | Timer interrupt routine entry |
| (vector `0xFFFC`) | `0xE22B` | Non-maskable interrupt routine entry (executes RTI) |
| (vector `0xFFFE`) | `0xE000` | Reset routine entry |

---

#### VMJ — Vector 2-Byte Subroutine Jump
Two-byte vector call. Jumps to the address stored at `(0xFF00 + i)`. Immediate value `i` may be any even value from `0x00` to `0xF6`.
**Flags:** Z is reset.

**Syntax: `vmj 0xnn` — a plain byte immediate with a `0x` prefix, no parentheses.**
This differs from VEJ: VMJ takes a bare immediate operand, not a parenthesized argument.
Use `vmj 0x92`, not `vmj (0x92)`.

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `vmj 0xnn` | `0xCD 0xnn` | 2 | 20 |

---

#### VCS / VCR — Conditional Vector Jump on Carry
Vector subroutine jump conditional on the Carry flag. When the condition is false, falls through to the next instruction.
**Flags:** Z is reset if taken.
Cycles: 8 (not taken) / 21 (taken).

| Format | Condition | Opcode | Bytes |
|---|---|---|---|
| `vcs i` | Jump if C = 1 | `0xC3 i` | 2 |
| `vcr i` | Jump if C = 0 | `0xC1 i` | 2 |

---

#### VHS / VHR — Conditional Vector Jump on Half-Carry
Vector subroutine jump conditional on the Half-Carry flag.
**Flags:** Z is reset if taken.
Cycles: 8 (not taken) / 21 (taken).

| Format | Condition | Opcode | Bytes |
|---|---|---|---|
| `vhs i` | Jump if H = 1 | `0xC7 i` | 2 |
| `vhr i` | Jump if H = 0 | `0xC5 i` | 2 |

---

#### VZS / VZR — Conditional Vector Jump on Zero
Vector subroutine jump conditional on the Zero flag.
**Flags:** Z is reset if taken.
Cycles: 8 (not taken) / 21 (taken).

| Format | Condition | Opcode | Bytes |
|---|---|---|---|
| `vzs i` | Jump if Z = 1 | `0xCB i` | 2 |
| `vzr i` | Jump if Z = 0 | `0xC9 i` | 2 |

---

#### VVS — Conditional Vector Jump on Overflow Set
Vector subroutine jump if V = 1.
**Flags:** Z is reset if taken.
Cycles: 8 (not taken) / 21 (taken).

| Format | Condition | Opcode | Bytes |
|---|---|---|---|
| `vvs i` | Jump if V = 1 | `0xCF i` | 2 |

---

### Return Instructions

#### RTN — Return from Subroutine
Returns to the caller by popping the return address from the stack into P.
`s + 1 → s`, `(s) → PH`, `s + 1 → s`, `(s) → PL`
**No flag changes.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `rtn` | `0x9A` | 1 | 11 |

---

#### RTI — Return from Interrupt
Returns from an interrupt service routine. In addition to restoring P from the stack, also restores T (the status register) from the stack, restoring all flags to their pre-interrupt state.
`s + 1 → s`, `(s) → PH`, `s + 1 → s`, `(s) → PL`, `s + 1 → s`, `(s) → t`
**All flags restored from stack.**

| Format | Opcode | Bytes | Cycles |
|---|---|---|---|
| `rti` | `0x8A` | 1 | 14 |

---
