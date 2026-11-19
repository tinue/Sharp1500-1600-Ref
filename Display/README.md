# Display

The LCD: controllers, frame buffer, the LCD IOCS routines, the character generator.

**Gaps:** the PC-1500 display (26-character viewport onto an 80-character buffer) has no document of its own; facts are in `../Programming/prompts/PC-1500-BASIC-Prompt.md` and `../Firmware/PC-1500-System-Variables.md`. The PC-1600 character-code table (TRM 10.1) is still to be transcribed.

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [HD61102-HD61203-Datasheet-Facts.md](HD61102-HD61203-Datasheet-Facts.md) | 1600 | cited | 12 | Hitachi HD61102/HD61203 datasheet facts: registers, instruction set, read pipeline, duty and scan, reset, timing. |
| [PC-1600-Display-Hardware.md](PC-1600-Display-Hardware.md) | 1600 | cited | 12 | Panel, HD61203 + 2xHD61102 topology, I/O ports 50-5BH, frame-buffer model, PC-1500 compatibility, open items. |
| [PC-1600-Display-IOCS.md](PC-1600-Display-IOCS.md) | 1600 | cited | 10 | LCD IOCS routines (text, cursor, scroll, status line, graphics), LCD work area, 6x8 character generator. |
<!-- files:end -->
