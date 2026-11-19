# Keyboard

Key scanning, key codes, auto-repeat and key readiness. The PC-1500 reads the matrix directly; the PC-1600 scans through the sub-CPU.

**Gaps:** the PC-1600 key-code value table (TRM 10.2, matrix position to character) is pending; it is not needed for emulation.

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [PC-1500-Keyboard-Scan.md](PC-1500-Keyboard-Scan.md) | 1500 | ROM-verified | 12 | ROM key scan loop, release gate, auto-repeat, key readiness for an emulator. |
| [PC-1600-Keyboard.md](PC-1600-Keyboard.md) | 1600 | cited | 15 | Scan mechanism via sub-CPU, port wiring, key IOCS, scan matrix, work area, translation tables, ON/BREAK. |
<!-- files:end -->
