# PC-1500 CE-158 Interface

Summary: CE-158 RS-232C/Centronics interface hardware: ROM banks, LH5811 and CDP1854A UART addresses, port bit meanings, behaviour on the PC-1600.
Scope: PC-1500, PC-1500A; on the PC-1600 in MODE 1
Sources: ROM:PC-1500-ROM/disasm/ce158/CE-158-LOW.asm and CE-158-HIGH.asm; SM-CE158; TRM-1500 p.108; MAN-CE158
Status: draft

## 1. Scope

The hardware side of the CE-158. Its BASIC commands are in SharpBasicReference
(`CE-158-Reference.md`), its keyword tokens in `../Firmware/PC-1500-Peripheral-Commands.md`.
Cassette and the CE-158X addendum are not covered yet.

## 2. Address map

| Space | Address | What |
|---|---|---|
| ME0 | 8000–9FFF, PV = 1 | ROM, 16 KB as two 8 KB banks; PU selects the bank (PU = 0: first half of the dump, `CE-158-LOW`) |
| ME1 | D000–D00F | LH5811 (port C D008, DDB D00D, port A D00E, port B D00F) |
| ME1 | D200–D203 | UART **CDP1854A**: D200 data write, D201 control write, D202 data read, D203 status read (A0 = RSEL) |
| ME1 | DE00–DFFF | interrupt-ID register; the ROM never reads it, the UART is polled |

[ROM:PC-1500-ROM/disasm/ce158/CE-158-LOW.asm] names the equates (`CE158_UART_DATAW` …,
`CE158_PRT_A` …). The bank-switch mechanism (keyword dispatch through LOW's `MAIN_ENTRY`, the
`SPU`/`RPU` trampoline at 7A28H) is described in the disassembly's notes.

## 3. Port bits

- **Modem inputs** PA2–PA4 are active low.
- **PA6/PA7** are read at initialisation as a strap; 1/1 selects the CDP1854 status decode.
- **Baud-rate code** = PC0–PC4 plus PA7.
- **Centronics:** data is inverted; STROBE = PC6; BUSY = PB7 (1 = ready).
- The parallel port's end code is LF (`CONSOLE 80,1`).
- `SETDEV` flushes the receive buffer, so a peer that sends before it loses those bytes.

## 4. On the PC-1600

In MODE 1 the LH5803 ROM sets PV itself from the `CALLH` parameter block's `PARBAN` (E224H), so
the CE-158 gets real PV/PU levels (`../CPU/PC-1600-LH5803.md`). Open: on the PC-1600,
`SETDEV KI` followed by `INPUT` does not reach the CE-158 in Calc-U-1600 (`RINKEY$` does);
possibly the PC-1600's own `SETDEV` takes the keyword. Not checked on hardware.
