# Machines

The models and what distinguishes them: chips, clocks, power, boot, ROM revisions.

Models covered: **PC-1500** (LH5801, 1981, sold as Tandy PC-2), **PC-1500A** (rewired expansion connector), **PC-1600** (SC-7852 Z-80 plus an LH5803 that runs PC-1500 software, 1986). In Calc-U terms these three are the *model family* of the Calc-U-1600 product; ROM A01/A03/A04 (PC-1500) and New/Old (PC-1600) are *variants*.

**See also:** `../CPU/` for the processors, `../Memory/` for the memory maps, `../Firmware/` for ROM structure.

**Gaps (not yet written):** a PC-1500 machine overview (chips, clock, power, boot; today spread over `../CPU/LH5801-Architecture.md` and `../Memory/PC-1500-Address-Decoding.md`) and a model matrix (PC-1500, PC-1500A, PC-1600 and ROM variants side by side).

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [PC-1600-Machine-Overview.md](PC-1600-Machine-Overview.md) | 1600 | cited | 13 | Chip complement, clock tree, dual-CPU bus sharing, sub-CPU protocol, power rails, boot. |
| [PC-1600-ROM-Versions.md](PC-1600-ROM-Versions.md) | 1600 | ROM-verified | 11 | OLD and NEW BASIC ROM revisions, how to tell them apart, which chips hold which part. |
<!-- files:end -->
