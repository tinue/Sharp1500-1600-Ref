# Serial and Parallel

RS-232C, the SIO connector and the Centronics port of the PC-1600, and the BASIC commands that drive them.

**Gaps:** the PC-1500 equivalent, the CE-158 interface (RS-232C, Centronics, cassette), has no document of its own; its BASIC commands are in SharpBasicReference (`CE-158-Reference.md`) and its tokens in `../Firmware/PC-1500-Peripheral-Commands.md`.

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [PC-1600-CPC-TC8576.md](PC-1600-CPC-TC8576.md) | 1600 | cited | 28 | TC8576F/AF CPC (UART + Centronics) at 20-23H: pinout, registers, baud rate, how the ROM drives it. |
| [PC-1600-Serial-Commands.md](PC-1600-Serial-Commands.md) | 1600 | cited | 12 | BASIC serial commands: INIT, SETCOM, OUTSTAT, INSTAT, SNDSTAT, RCVSTAT, SETDEV, PCONSOLE. |
| [PC-1600-Serial-Hardware.md](PC-1600-Serial-Hardware.md) | 1600 | cited | 12 | RS-232C/SIO board sharing one TC8576F, level shifter, supply, FTDI how-to. |
<!-- files:end -->
