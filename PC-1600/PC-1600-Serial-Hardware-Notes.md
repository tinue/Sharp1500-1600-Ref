# PC-1600 Serial Hardware (RS-232C / SIO) + Wiring Notes

## 1. Serial hardware architecture (TRM §7.6)

The PC-1600 has **two serial ports — RS-232C and SIO** — but only **one** serial engine:
the **TC8576F** UART LSI (a single-chip CMOS device holding the RS-232C ART = async
receiver/transmitter, its baud-rate generator, and a Centronics parallel
transmit/receive interface). Because there is only one channel, **RS-232C and SIO cannot
be used at the same time.**

- **Port select:** the BASIC `OPEN` / `SETDEV` commands, or the hardware `PRIM` signal
  (LR38041 gate array pin 17). `PRIM` **high** → RS-232C; `PRIM` **low** → SIO. Power-on
  and reset pull `PRIM` low (SIO is the default).
- With `PRIM` high (RS-232C): the RS-232C interface supply `VDD` (≈ 6.0 V) is applied,
  `SDF`/`RDF` (SIO lines) go low, and the UART's `TXD`/`RXD` are placed **inverted** on
  the RS-232C `TXD`/`RXD` lines.
- With `PRIM` low (SIO): `VDD` is cut, and the UART's `TXD`/`RXD` are placed **inverted**
  on the SIO's `SDF`/`RDF` lines. RS-232C outputs are held high-impedance or low.
- **Gate-array routing table (LR38041):**

  | Line | PRIM = low (SIO) | PRIM = high (RS-232C) |
  |---|---|---|
  | output SDA | LOW | TXD# |
  | output SDF | TXD# | LOW |
  | input RXD | RDF | RDA |

- **RS-232C line levels:** conform to EIA/JIS, level-shifted by the hybrid IC **BX7269W**
  — incoming ±V shaped to 0/VCC logic, outgoing logic converted to VDD…VCC swing. `VEE`
  (≈ −8.5 V) provides the negative side.
- **Power note:** RS-232C draws more than SIO (it needs `VDD` generation). After an
  RS-232C session, switch back to SIO to save battery.

### 1.1 BX7269W signal mapping (main-board wiring diagram)

The BX7269W does not just level-shift `TXD`/`RXD` — every RS-232C control line is routed
through it, one gate-array-side pin per RS-232C-side pin. Confirmed from the PC-1600
main-board wiring diagram (2026-09-04 scan):

| Gate-array side (CN2 pin) | IC1 (BX7269W) input | IC1 output | RS-232C connector (CN4) | V.24 circuit |
|---|---|---|---|---|
| SDA (CN2-2) | SDA | SD | TxD | 103 |
| RDA (CN2-3) | RDA | RD | RxD | 104 |
| RTS (CN2-4) | RTS | RS | RTS | 105 |
| CSA (CN2-5) | CSA | CS | CTS | 106 |
| DRA (CN2-6) | DRA | DR | DSR | 107 |
| CDA (CN2-7) | SLCT | CD | DCD | 109 |
| DTR (CN2-9) | DIR | ER | DTR | 108 |
| QI (CN2-13) | — | CI/RR | (RI-related) | 125 |

So **DTR is level-shifted through the same BX7269W chip** as TxD/RxD (via IC1's `DIR`
pin), not handled by separate discrete logic. `Q1`/`C1`, wired between `PRI(CN2-8)` and
IC1, are most likely the charge-pump oscillator that generates `VEE`, but this is
tentative — not confirmed against the TRM.

**SIO bypasses the level shifter entirely:** `SDF(CN2-11)` and `RDF(CN2-12)` route
directly from the gate array to the 5-pin SIO connector without passing through IC1 —
physical confirmation that SIO stays at TTL/CMOS levels and only the RS-232C path needs
level shifting.

### TC8576F pinout (as wired in the PC-1600)

Partial, from TRM §7.6. The complete 44-pin table, including the parallel side and the
RS-232C CS/CD/DR inputs the ROM reads through FAULT/`/SLCT`/`/PE`, is in
`PC-1600-CPC-TC8576.md` §2.

| Pin | Symbol | Dir | Active | Function |
|---|---|---|---|---|
| 1 | (NC) | — | — | not used |
| 2 | RD# | In | Low | CPU reads data/status from the TC8576F |
| 3 | WR# | In | Low | TC8576F takes data/control words from the CPU |
| 4 | CS# | In | Low | chip select; high tri-states the data bus and blocks RD/WR. Driven by `IOSU#` (SC-7852 pin 59, low on I/O 20H–27H). |
| 5, 6 | A1, A0 | In | — | register select (with RD#/WR#) — see the truth table in `PC-1600-IO-Ports.md` §3 |
| 7, 18 | GND | pwr | — | |
| 8 | INT | Out | High | logical OR of RXRDY, TXRDY, PRRDY, PTRDY → SC-7852 `INT0` (pin 81) |
| 9–16 | D7–D0 | I/O | — | data bus |
| 17 | VCC | pwr | — | |
| 42 | RESET# | In | Low | resets the IC; low suppresses all functions |
| 43 | P5V | I/O | — | parallel mode, tied to GND; `CDS`=1 → 1-bit output port, `CDS`=0 → input voltage supply for an external device |
| 44 | PE | I/O | — | parallel-mode paper-end; `CDS`=1 → 1-bit output port, `CDS`=0 → receives PE from an external device |

**Baud rate:** IC clock ÷ programmable 4-bit prescaler → SYS-CLK ÷ programmable 12-bit
divider → any rate **50–38400 baud**. The clock into the UART is `CLK1` from the gate
array (CL2, 1.2288 MHz, passed through while the system is on). The ROM sets the
prescaler to ÷2, so baud = 76800 / divisor. The full pinout, the parameter/command byte
formats and the ROM's programming sequence are in
[`PC-1600-CPC-TC8576.md`](PC-1600-CPC-TC8576.md). BASIC-level control (`SETCOM`, `SNDSTAT`, …): `PC-1600-Serial-Commands.md`.

## 2. FTDI USB/UART wiring (practical)

> Extracted from the "PC-1600: USB Serial Adapter" section of
> `sharp-pocket-computer/SharpCommunicator/HardwareNotes.md` (in the separate, public
> `sharp-pocket-computer` repository — [github.com/tinue/sharp-pocket-computer](https://github.com/tinue/sharp-pocket-computer),
> not part of this repository — left unchanged there). That file's "PC-1500/A:
> CE-158X" section was not copied — it documents a modern third-party clone board, not
> original Sharp hardware. Referenced photos (`pictures/Pin_Adapter.jpg`,
> `pictures/Calculator.jpg`) remain in the original repository.

The Sharp PC-1600 has a serial device built in. It uses fairly standard 5V logic, and can be interfaced
with currently available FTDI adapters. When using an original (non-cloned) FTDI adapter, no additional
logic chips or inverters are required.

Components used:

- 1mm pins, bent 90 degrees
- A small board for soldering the pins. Search for "1.27mm 2.54mm Adapter Board" on the merchant site of your choice.
  While no 15 pin boards were found, 12 pins are enough for the signals that are required.
- USB/UART cable: "FTDI TTL-232R-5V-WE", i.e. 5V logic and wire ends.

Before the USB / UART adapter can be used, it needs to be reprogrammed using a Windows
machine. The signals of the RX, TX, RTS and CTS pins need to be inverted. This
can be done with a utility provided by FTDI. This is a one-time operation, because the
change is persistent even after unplugging the cable.

The wiring is as follows (pin 1 is the rightmost pin of the PC-1600's 15-pin serial connector):

| Pin | Signal PC-1600 | Connect this cable of the USB/UART | USB/UART wire color |
|-----|----------------|------------------------------------|---------------------|
| 2   | TX             | RX                                 | yellow              |
| 3   | RX             | TX                                 | orange              |
| 4   | RTS            | CTS                                | brown               |
| 5   | CTS            | RTS                                | green               |
| 7   | SG (ground)    | Ground                             | black               |

Note: Do not connect the red cable (5V) of the adapter.

## RTS/CTS with this cable on macOS and Linux

*Corrected 2026-10-10. The earlier version of this section said the Mac's driver does not wait for
CTS. The analysis below makes a driver bug unlikely. Nothing below has been retested on the
PC-1600 yet.*

**The original observation.** On an Apple-Silicon Mac, data sent *to* the PC-1600 was lost with
RTS/CTS flow control enabled: the Mac apparently did not wait for CTS. The other direction
(PC-1600 to Mac) worked. The workaround was to run the transfer on a Raspberry Pi.

**How RTS/CTS works here.** Each direction uses one wire of the pair; the sender does not
"request" with RTS and wait for an answer.

| Direction | Wire | PC-1600 setting |
|---|---|---|
| Mac → PC-1600 | PC-1600 RTS (pin 4) → adapter CTS | `OUTSTAT "COM1:"` (automatic mode) and `RCVSTAT "COM1:",28,0` |
| PC-1600 → Mac | adapter RTS → PC-1600 CTS (pin 5) | `SNDSTAT "COM1:",24,0` |

In automatic mode the PC-1600 drops its RTS at 8 free buffer bytes and after every 256-byte record
of LOAD/INPUT#. The adapter must then stop. `RCVSTAT` is not involved in this direction; it only
makes the PC-1600 discard bytes that arrive while its own CTS input is off.

**What the drivers do with the FT232R.** This comes from disassembling and reading the drivers.

- **macOS, built-in AppleUSBFTDI (DriverKit):** `CRTSCTS` puts the chip into hardware RTS/CTS mode,
  and the chip gates sending on CTS by itself.
  - Setting only output CTS flow control (`CCTS_OFLOW`) is dropped and never reaches the chip.
  - `IXON` on its own never reaches the chip either. `IXON` + `IXOFF` together does work.
  - With XON/XOFF active the driver deletes every received 11H/13H, even data bytes.
  - Errors are reported per USB packet of up to 62 bytes, not per byte.
- **FTDI's own macOS VCP driver (1.6.0):** unsuitable. It hardcodes the XON/XOFF characters to
  04H/05H and never reports receive errors.
- **Linux `ftdi_sio`:** `CRTSCTS` works in the chip, and wins over `IXON`. `IXON` switches on the
  chip's own XON/XOFF; this is correct since a 2018 fix.
- **FT232R chip:** about 183 baud to 3 Mbaud, so the PC-1600's 50–150 baud rates are unusable.
  128-byte receive and 256-byte transmit buffers. FTDI does not document how many characters
  still go out after CTS drops.

**Likely causes of the original failure:**

- the program set only `CCTS_OFLOW` instead of the full `CRTSCTS`;
- an older macOS version;
- a PC-1600 setting such as `RCVSTAT "COM1:",24` (which can discard data) or OUTSTAT left in manual mode.

Retest with the full `CRTSCTS`, `OUTSTAT "COM1:"`, `RCVSTAT "COM1:",28,0`, `INIT "COM1:",1024`
and a file larger than the buffer (e.g. 8 KB).
