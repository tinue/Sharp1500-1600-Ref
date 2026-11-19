# LH5801 Architecture

Summary: LH5801 registers, flags, addressing modes, ME0/ME1, limitations (what the CPU lacks).
Scope: PC-1500, PC-1500A, PC-1600 (LH5803 side)
Sources: cited inline in the text
Status: cited

> Split from `LH5801_Guide.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: Instruction Set Reference → [LH5801-Instruction-Set.md](LH5801-Instruction-Set.md); PC-1500 System Reference → [PC-1500-System-Variables.md](../Firmware/PC-1500-System-Variables.md); ROM Subroutine Reference → [PC-1500-ROM-Routines.md](../Firmware/PC-1500-ROM-Routines.md); Quick Reference Card, sdas Assembler Syntax, Common Patterns and Idioms, Common Assembler Macros, Appendix: Converting, Writing a User Guide → [LH5801-Assembly-Guide.md](../Programming/LH5801-Assembly-Guide.md).

## Architecture Overview

The Sharp LH5801 is an 8-bit CMOS microprocessor designed for low-power portable applications, most notably used in the Sharp PC-1500 (Radio Shack PC-2) pocket computers.

- **Data Bus:** 8-bit parallel.
- **Address Space:** 128 KB (split into two 64 KB banks: ME0 and ME1).
- **Machine Cycle:** Typically 1.3 MHz (with a 2.6 MHz crystal).
- **Instruction Set:** 82 documented instructions.

## Registers and Flags

### Internal Registers

| Symbol | | Name | Bits | Description |
|---|---|---|---|---|
| **P** | | Program counter | 16 | Indicates the address next to the address the CPU is now executing. It will be incremented by 1 when the next instruction is fetched. |
| **S** | | Stack pointer | 16 | Indicates the stack address. |
| **A** | | Accumulator | 8 | Used for retention of operational result or for data transfer with the external memory. |
| **Xreg** | XL | Data register | 8 | XL, XH, YL, YH, UL, UH comprise independent 8-bit registers. Also used as 16-bit data pointers Xreg, Yreg, and Ureg when used in a pair. |
| | XH | | 8 | |
| **Yreg** | YL | Data register | 8 | |
| | YH | | 8 | |
| **Ureg** | UL | Data register | 8 | |
| | UH | | 8 | |
| **TM** | | Timer counter | 9 | When 0 is set to TM, it stops the counter action. When anything other than 0 is set, it puts the counter into action. When TM turns full of 1 with the interrupt enable flag IE on, CPU executes an interrupt processing. |
| **PU** | | — | 1 | General-purpose flip-flop. |
| **PV** | | — | 1 | General-purpose flip-flop. |
| **DISP** | | — | 1 | LCD on/off control. |
| **T** | | Status register | 8 | Low order 5 bits represent one of five states of the operational result. |

P and S are internally split as `PH:PL` and `SH:SL` (high byte : low byte).

### Status Register (T)

```
Bit:  7   6   5   4   3   2   1   0
      0   0   0   H   V   Z  IE   C
```

| Bit | Flag | Name | Description |
|---|---|---|---|
| 7–5 | — | (unused) | Always 0. |
| 4 | **H** | Half Carry | Set if there is a carry from bit 3 to bit 4 (digit-to-digit carry). |
| 3 | **V** | Overflow | Set if a signed arithmetic overflow occurs (carry from bit 6 XOR carry from bit 7). |
| 2 | **Z** | Zero | Set if the result of an operation is zero. |
| 1 | **IE** | Interrupt Enable | Set to enable maskable and timer interrupts. |
| 0 | **C** | Carry | Set if there is a carry out from bit 7. **In subtractions, C=1 means NO BORROW.** |

### Carry Logic in Subtraction/Comparison
Unlike many common CPUs, the LH5801 Carry flag acts as a "No Borrow" bit during subtraction (`sbc`, `sbi`, `dcs`, `cpa`, `cpi`).
- **C = 1**: Result was positive or zero (no borrow occurred).
- **C = 0**: Result was negative (borrow occurred).

## Addressing Mode Reference

| Mode | Syntax | Example | Notes |
|---|---|---|---|
| Immediate 8-bit | `ldi a,0xnn` | `ldi a,0x42` | Literal byte value |
| Immediate 16-bit | `ldi s,0xnnnn` | `ldi s,0x7800` | S only; byte regs use 8-bit form |
| Register (byte) | `lda xl` | `lda uh` | XL, XH, YL, YH, UL, UH |
| ME0 absolute | `lda (0xnnnn)` | `lda (0x7800)` | Parentheses = memory access in ME0 |
| ME0 register indirect | `lda (x)` | `lda (u)` | Parens around 16-bit reg |
| ME0 absolute (label) | `lda (LABEL)` | `lda (ARX)` | Label resolves to 16-bit address |
| ME0 indirect + offset | `lda (LABEL+0xnn)` | `lda (ARX+0x07)` | Offset expression in parens |
| ME1 absolute | `lda #(0xnnnn)` | `lda #(LABEL)` | `#` prefix = ME1 bank |
| ME1 register indirect | `lda #(x)` | `lda #(u)` | Not all instructions have ME1 form |
| Post-increment load | `lin x` | `lin u` | A = (Rreg), Rreg++ |
| Post-decrement load | `lde x` | `lde u` | A = (Rreg), Rreg-- |
| Post-increment store | `sin x` | `sin y` | (Rreg) = A, Rreg++ |
| Post-decrement store | `sde x` | `sde u` | (Rreg) = A, Rreg-- |
| Relative branch | `bzs+e` / `bzs-e` | `bzs LABEL` | Assembler computes ±offset |

**Note:** `sta` syntax is symmetric with `lda` — `sta (LABEL)` stores A to ME0 address, `sta #(x)` stores to ME1.

**ME1 restriction:** Not all instructions support the ME1 `#(...)` form. Only: `lda/sta`, `adc/sbc`, `and/ora/eor`, `cpa/bit/bii`, `adi/ori/ani`, `dca/dcs`. `ldi`, `inc Rreg`, `dec Rreg`, `lin/sin/lde/sde`, `tin/cin` have no ME1 form.

---

## Memory Access and Bank Switching

The LH5801 uses two memory enable signals, **ME0** and **ME1**, allowing access to two 64 KB banks.

- **(addr)**: Access memory at `addr` in the **ME0** bank.
- **#(addr)**: Access memory at `addr` in the **ME1** bank.
- **(Rreg)**: Indirect access through register pair X, Y, or U in **ME0**.
- **#(Rreg)**: Indirect access through register pair X, Y, or U in **ME1**.

### Bank Switching (PC-1500)
Firmware often uses the `PU` and `PV` bits to control bank selection for specific hardware modules.
- **HIGH_BANK**: `spu` then `spv` (Set PU and PV)
- **LOW_BANK**: `rpu` then `spv` (Reset PU and Set PV)

---

## What Doesn't Exist — LH5801 Limitations

Critical for AI code generation: the LH5801 cannot do these things. Do not hallucinate instructions for them.

- **No 16-bit arithmetic on X/Y/U directly** — except `inc Rreg`, `dec Rreg`, `adr Rreg` (A → Rreg), and `sbr Rreg` (A from Rreg); there is no `ADD x,y` or `ldi x,0xnn`.
- **No 16-bit load immediate** — `ldi` only loads 8-bit values into byte registers (XL, XH, etc.) or a 16-bit address into S. To set X to 0xC000 you must write `ldi xh,0xC0` then `ldi xl,0x00`.
- **No memory-to-memory copy** — all copies must go through A: `lda (src)` then `sta (dst)`. Use `tin` in a loop for block copies.
- **No multiply or divide** — use ROM math routines (see ROM Subroutine Reference) or implement in software.
- **No bitwise NOT of A** — use `eai 0xFF` (XOR A with 0xFF) to invert all bits.
- **No stack pointer arithmetic** — there is no `ADD s,n`. Adjust S by using `ldx s` / `adr x` / `stx s`.
- **No conditional call or return** — all conditionals are relative branches (`bzs`, `bcr`, etc.). To call conditionally: branch over an `sjp`; to return conditionally: branch over an `rtn`.
- **No indirect jump through register** — `jmp` always uses an absolute address. `stx p` (opcode `0xFD 0x5E`) loads P from X and can be used as a register-indirect jump. `vej` is ROM-vector only.
- **No SBR instruction for all pairs** — `sbr` exists as the 16-bit subtract-register counterpart to `adr` but is undocumented; do not rely on it.
- **ME1 access is instruction-specific** — only the `#(addr)` / `#(Rreg)` forms of LDA/STA/ADC/SBC/AND/OR/EOR/CPA/BIT/BII/ADI/ORI/ANI/DCA/DCS access ME1. `ldi`, `inc`, `dec`, `tin`, `cin`, `lin`, `sin`, `lde`, `sde` have no ME1 form.
- **Flag V is only set by arithmetic** — `adc`, `sbc`, `inc` (8-bit), `dec` (8-bit). Logical operations (`and`, `ora`, `eor`, `ani`, etc.) do not set V.
- **`lop` only loops on UL** — cannot use XL, YL, or any other register as a loop counter with `lop`. To loop on another register, use `dec` + conditional branch.
- **No `FSM`/`SSM` block search** — the LH5801 has `cin` (compare-and-increment), but there is no single-instruction string search; build loops with `cin` + `lop`.
- **C=1 means NO BORROW in subtraction** — this is the inverse of many CPUs. After `cpa`/`sbc`/`cpi`: C=1 → result ≥ 0 (no borrow), C=0 → result < 0 (borrow).

---
