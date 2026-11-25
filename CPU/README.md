# CPU

The processors: LH5801 (PC-1500, PC-1500A, and the PC-1600's LH5803 side), the Z-80-compatible SC-7852, and the 4-bit LU-57813P sub-CPU.

- Writing LH5801 code: the instruction set and architecture are here; the programming guide and paste-ready prompt are in `../Programming/`.
- The PC-1600's second CPU view of memory: `PC-1600-LH5803-Memory-View.md` (and `../Memory/` for the Z-80 view).

**Gaps:** none known; the SC-7852 open items are listed in `PC-1600-SC7852-Z80.md` section 12.

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [LH5801-Architecture.md](LH5801-Architecture.md) | 1500+1600 | cited | 8 | LH5801 registers, flags, addressing modes, ME0/ME1, limitations (what the CPU lacks). |
| [LH5801-Instruction-Set.md](LH5801-Instruction-Set.md) | 1500+1600 | cited | 45 | Complete LH5801 instruction set with opcodes, flags and timing (reference table, exempt from the size cap). |
| [LH5801-PU-PV-Signals.md](LH5801-PU-PV-Signals.md) | 1500+1600 | cited | 12 | The PU/PV flip-flop pins of the LH5801 and their role on the expansion connector (PV path in the PC-1600). |
| [PC-1600-LH5803-Memory-View.md](PC-1600-LH5803-Memory-View.md) | 1600 | cited | 16 | How the LH5803 sees memory: same silicon, different address space; dual-processor hand-off. |
| [PC-1600-LH5803.md](PC-1600-LH5803.md) | 1600 | cited | 18 | The LH5803 side: memory map, deltas to the LH5801, the CALLH parameter block, PC-1500 compatibility rules. |
| [PC-1600-SC7852-Pinout-and-Control-Regs.md](PC-1600-SC7852-Pinout-and-Control-Regs.md) | 1600 | cited | 14 | SC-7852 100-pin terminal table and the on-chip control-register block 30H-3FH. |
| [PC-1600-SC7852-Z80.md](PC-1600-SC7852-Z80.md) | 1600 | cited | 27 | The Z-80-compatible SC-7852 as a CPU: registers, instruction set, timing, wait state, interrupts, RST map. |
| [PC-1600-SubCPU-LU57813P.md](PC-1600-SubCPU-LU57813P.md) | 1600 | cited | 21 | The 4-bit LU-57813P sub-CPU: pinout, power states, interrupts, command handshake and command set. |
<!-- files:end -->
