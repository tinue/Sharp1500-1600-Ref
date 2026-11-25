# I/O Ports

Port maps and what the bits do. PC-1600: range map, the LH5810-compatible block 10-1FH, interrupt causes 32H/35H, buzzer, timer/RTC/analog, and the memory-management ports.

**See also:** `../Serial-Parallel/` (TC8576 at 20-23H), `../Display/` (LCD ports 50-5BH), `../Storage/PC-1600-Floppy-CE-1600F.md` (floppy ports 78-7FH), `../Peripherals/` (printer ports 80-83H), `../Memory/PC-1600-Bank-Switching.md`.

**Gaps:** the PC-1500 document (`PC-1500-LH5811-and-ME1.md`) holds only measured facts so far: the full LH5811 register description is not transcribed. The CE-150 side is in `../Peripherals/PC-1500-CE-150-Hardware.md`.

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [PC-1500-LH5811-and-ME1.md](PC-1500-LH5811-and-ME1.md) | 1500+1600 | draft | 3 | Where the PC-1500's own LH5811 answers in ME1, what unclaimed ME1 reads, the buzzer on PC6 and its measured tone timing. |
| [PC-1600-IO-Ports.md](PC-1600-IO-Ports.md) | 1600 | cited | 30 | I/O range map, LH5810-compatible port 10-1FH, TC8576 select, 30-3FH, LCD ports, buzzer, timer/RTC/analog, memory-management ports. |
<!-- files:end -->
