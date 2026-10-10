# PC-1600 Serial (RS-232C / SIO) — BASIC commands + IOCS routines

Part 1 is the BASIC-level command reference. Part 2 is the machine-language IOCS routine
set (TRM §3.6.3). The line-signal hardware (TC8576F, PRIM, level shifter) is in
`PC-1600-Serial-Hardware-Notes.md`. The comms data format is deferred by TRM §3.6.2 to
§5.7 (pending).

---

## Part 1 — BASIC commands relevant to serial communication

The full user-level description is chapter 12 and the part "Serial communication in practice"
of `$BAS/PC-1600-BASIC-Reference.md` (`SharpBasicReference`), built from the manuals, the TRM, the
Systemhandbücher and the ROM. This part is a compact summary with the ROM evidence. Addresses
are NEW ROM (`B3B` = P1-B3B, `B3` = P1-B3, `B6` = P2-B6). Bits are numbered from 0. The
Operation Manual numbers them from 1 on the SNDSTAT/RCVSTAT/INSTAT pages.

### Common rules

- **One UART, two ports.** `"COM1:"` = RS-232C, `"COM2:"` = SIO, `"COM:"` = the currently
  selected port (F14EH b6). Power-on selects COM2 (COMDEF2, B6 9F29).
- **What a power-off resets** (COMDEF2): the INIT buffer size (back to 40 bytes), SNDSTAT/RCVSTAT
  masks and timeouts, OUTSTAT mode (back to automatic), and SETDEV (back to COM2, no PO/KI).
- **What survives:** SETCOM, PCONSOLE and PZONE. Only a reset copies the full defaults
  (COMDEF1, B6 9F5A).

### INIT "COMn:"

`INIT "COMn:",<size>` (B3B 52BC → CSRCVB B6 9EA4)

- `0` or omitted = the built-in 40-byte buffer at F158–F17F (no user memory).
- Otherwise 80–16383. Out of range → **ERROR 19**. **ERROR 141** only means not enough memory.
- The buffer is taken from S0 free memory (EXROMWK slice 0FH); it holds `size` − 1 bytes.
- **One buffer for both ports**: the device name is not used.
- Refused while any file is open (ERROR 154) and inside FOR…NEXT.
- Clears the buffer and the error flags.
- Undocumented extra form: `INIT "COMn:",size,s1$,s2$` stores two strings of up to 3 characters
  at F135/F138. These appear to be kanji shift sequences.

Example: `INIT "COM1:",1024`

### SETCOM / COM$

`SETCOM "COMn:",[BR],[WL],[PR],[ST],[XO],[SI]` (B3B 5382)

- **BR:** 50–38400, the only field that may be an expression (BAUDCHK 5787, constant 9600H =
  38400). The divisor is round(76800 / BR), so rates snap, e.g. 14400 → 15360.
- **WL** `5`–`8`, **PR** `E`/`O`/`N`, **ST** `1`/`2`, **XO** `X`/`N`, **SI** `S`/`N`: literal
  characters, not expressions. Anything else → ERROR 140.
- **SI** is active only with 7 data bits (`AND 8CH / XOR 88H`, B6 A17C); with 8 bits it is inert.
- Omitted fields keep their value. `SETCOM "COMn:"` alone → `1200,8,N,1,X,S` (B3B 54A3), for
  COM2 too.
- No per-port restriction.
- On the selected port the CPC is reprogrammed at once, and the receive buffer and errors are
  cleared. For the other port the values are only stored.
- `COM$` returns the effective values, so the baud rate is computed back from the divisor.

Example: `SETCOM "COM1:",9600,8,N,1,N,N`

### SNDSTAT / RCVSTAT

`SNDSTAT "COMn:",<protocol>[,<timeout>]` and `RCVSTAT …` (B3B 55B0/55C3 → GETSTATARG 5860)

The protocol is masked with **1CH** (58A9): b2 = CTS, b3 = CD, b4 = DSR. **0 = must be on, 1 =
don't care.** So 24 ≡ 59 (CTS) and 28 ≡ 63 (none). The manual's "set unused bits to 0" and the
TRM's 59/63 are the same settings.

| Bit | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|-----|---|---|---|---|---|---|---|---|
| | ignored | ignored | ignored | DSR | CD | CTS | ignored | ignored |

- **SNDSTAT** = real flow control for PC-1600 → other side. Before every byte the ROM waits
  until the required lines are on (B6 A51E), with the timeout counted per byte → ERROR 143.
- **RCVSTAT** is a filter, **not** flow control. Bytes arriving while a required line is off
  are discarded silently (B3 6407, COM1 only). Its timeout applies while a read waits on an
  empty buffer.
- **Timeout** 0–255 × 0.5 s, 0 = infinite.
- **Power-on defaults:** send = CTS required, receive = nothing required, both infinite. With
  CTS unwired, sending hangs until BREAK.
- **Omitted parameters (ROM quirk, NEW and OLD):** an omitted protocol becomes 04H (CD + DSR
  required). An omitted timeout becomes 3FH (RCVSTAT, 31.5 s) or 3BH (SNDSTAT, 29.5 s), not
  infinite (B3B 5861–586F). Always write both values.
- **COM2:** only the timeout is stored; the protocol is ignored without error.

Examples:

- `SNDSTAT "COM1:",24,0` — wait for CTS before each byte, no timeout.
- `SNDSTAT "COM1:",28,0` — send without any handshake (3-wire cable).
- `RCVSTAT "COM1:",28,0` — accept everything. This is the right setting also when the host uses
  RTS/CTS to send to the PC-1600; flow control in that direction is the PC-1600's RTS, see
  OUTSTAT.

### OUTSTAT

`OUTSTAT "COM1:"[,setting]` (B3B 5511 → CWOUTS B6 9FBE)

With a setting, the value is masked to 2 bits and the lines are fixed (manual mode, F14FH b7).
All automatic RTS/DTR handling is then off.

|   | RTS  | DTR  |
|---|------|------|
| 0 | on (high) | on (high) |
| 1 | on   | off  |
| 2 | off  | on   |
| 3 | off  | off  |

Without a setting: automatic mode, and RTS/DTR go off immediately. From then on:

- **RTS + DTR on** while a port command runs or a port file is open.
- **RTS off** at 8 free bytes in the buffer (B3 64F8), and after every 256-byte record of
  LOAD/INPUT#/COPY (COMRDEND B3 60B8).
- **RTS on again** when the reader drains the buffer to 8 unread bytes, or finds it empty
  (RINGNEXT B6 A0C4).

So in automatic mode RTS means "PC-1600 ready to receive": the flow control for other side →
PC-1600. No effect on COM2.

### INSTAT

`INSTAT "COM1:"` (B3B 5551 → CRCTRL B6 A382)

The state is returned as an integer, with each bit representing a line. **0 = on (high), 1 = off
(low).** 63 = all off, the idle reading with nothing connected. On COM2 the result is always 0.

| Bit | 7      | 6      | 5  | 4   | 3  | 2   | 1   | 0   |
|-----|--------|--------|----|-----|----|-----|-----|-----|
|     | always 0 | always 0 | CI | DSR | CD | CTS | RTS | DTR |

CI comes from the sub-CPU; RTS and DTR are read from the F14FH shadow.

Example: `PRINT INSTAT "COM1:"`

### XON/XOFF and shift in/out

**When the PC-1600 receives:**

- It sends XOFF at exactly 8 free bytes (B3 64CC), from inside the interrupt; only 7 more bytes
  fit after that.
- LOAD, INPUT# and COPY also send XOFF after every 256-byte record.
- It sends XON at 8 unread bytes, or when a read finds the buffer empty.
- One unsolicited XON is sent after every buffer clear (CCLRRB sets F152H b7).
- With X on, received 11H/13H are removed from the data (B6 A0A5). With X off, and always in
  binary file transfers, they are passed on as data.

**When the PC-1600 sends:** a received XOFF pauses before each byte, bounded by the SNDSTAT
timeout.

**Shift in/out** (7 bits only):

- On sending: SO (0EH) before bytes ≥ 80H, SI (0FH) before the next byte < 80H and before CR.
- On receiving: while shifted, 21H–7EH get bit 7 set.

### SETDEV, DEV$, RXD$

`SETDEV "COM1:"[,KI][,PO]` (B3B 54BF → CWDEV B6 A3F1)

- Selects the port: PRIME switches to RS-232C or SIO, then a wait of about 0.1 s.
- Loads the port's SETCOM block and clears the receive buffer.
- **KI:** INPUT reads from the port. **PO:** LPRINT, LLIST and LFILES write to the port.
- Without options, it still selects the port, but routes output back to the printer and input to
  the keyboard.
- `SETDEV "COM:"` → ERROR 155. A COM file open → ERROR 144. A bad option → ERROR 158.
- A bare `SETDEV` with no device is not handled by the native code (the ROM falls through to the
  CE-158 command tables). Use `SETDEV "COM2:"` to release RS-232C. Unverified on hardware.

Example: `SETDEV "COM1:",KI,PO`

**DEV$** has no native handler. Its token E857H is the CE-158 one and goes to the LH5803 function
dispatcher. Unverified on hardware.

**RXD$** (B6 AA5E) uses CRCV1, so it **consumes** one byte. It returns that byte as a 1-character
string.

- Nothing received → 2 blanks.
- Error → `"?"` + 2 blanks, and the buffer and errors are cleared.

### PCONSOLE

Set the line length and end-of-line code for LPRINT/LLIST/LFILES through the serial port.

`PCONSOLE "COM1:",[line length],[EOL code]`

- Line length: 16–255 (0 means no limit)
- EOL code: 0 = CR (default), 1 = LF, 2 = CR/LF

File transfers (SAVE/LOAD/PRINT#/INPUT#) always use CR+LF. Kept per port (F13B/F13C) over
power-off.

Example: `PCONSOLE "COM1:",80,2`

### SAVE / LOAD

`SAVE "COM1:"[,A]` and `LOAD "COM1:"[,R]` (COMWRITE B3 60FD, COMREAD B3 6012)

- **ASCII** (`,A`): CR+LF line ends, 1AH = end of file.
- **Binary:** first byte FFH, then a 16-byte header; the length is in header bytes 5–7.
- Reading is done in records of up to 256 bytes; the whole file never has to fit in the buffer.
- No baud limit is enforced. The manual's 9600/38400/4800 limits are reliability advice.

### Errors

- **142:** parity, framing, overrun, buffer full, a received break, and for file reads also the
  receive timeout. It is reported on the next read, before the data still in the buffer.
- **143:** send timeout (lines or missing XON). Also the receive timeout for INPUT via KI.

---

## Part 2 — Serial IOCS routines (TRM §3.6.3)

**Calling convention:** (1) IOCS number → **C register**; (2) if a channel is needed,
channel number → **D register** (`00H` = `"COM:"`, `01H` = `"COM1:"`, `02H` = `"COM2:"`);
(3) `CALL 01D8H`. Most routines clobber only `AF` and `AF'`. Channel-parameter routines
that take `D` are "RS-232C only" where noted.

| Name | IOCS # | Function | Params | Return |
|---|---|---|---|---|
| **CWCOM** | 01H | set the communication parameters | HL = param-block address, D = channel | — |
| **CRCOM** | 02H | get the comm-param-block address | D = channel | DE = address |
| **CSNDA** | 03H | send one byte on the channel | A = byte | on error: A = error byte (b0 = timeout, b1 = BREAK pressed), error bit set |
| **CRCVA** | 04H | receive one byte; **waits** if the buffer is empty | — | A = byte; CF = 1 on error |
| **CRCV1** | 07H | receive one byte; **no wait** | — | A = byte; ZF = 1 if buffer empty; CF = 1 on error |
| **CSETHS** | 0EH | drive RS and ER high (auto-handshake mode) | — | — |
| **CRESHS** | 0FH | drive RS and ER low (auto-handshake mode) | — | — |
| **CWOUTS** | 10H | set the outgoing control-signal (RS, ER) state | D = channel (RS-232C only), E: b0 = ER, b1 = RS, **b7** = 0 → auto-handshake / 1 → RS·ER follow b1·b0 | — (clobbers DE too) |
| **CRCTRL** | 11H | read the control-signal status | D = channel (RS-232C only) | A, in BASIC `INSTAT` format: b0 ER, b1 RS, b2 CS, b3 CD, b4 IR, b5 CI (bit = 0 → signal high, bit = 1 → low) |
| **CWDEV** | 12H | select a channel and set its I/O-device parameters | A: b0 = KI (input), b2 = PO (print out), b6 = 0 → COM1 / 1 → COM2 | — |
| **CRDEV** | 13H | read the current channel and its device parameters | — | A: b0 KI, b2 PO, b6 (0 = COM1 / 1 = COM2), b7 (0 = CLOSE / 1 = OPEN) |
| **CESND** | 14H | allow sending only while the named incoming signals are high | D = channel (RS-232C only), E: b2 = CS, b3 = CD, b4 = DR (**set a bit to 0 to require that signal**), B = timeout 0–255 in units of 0.5 s (0 = wait forever) | — |
| **CERCV** | 15H | allow receiving only while the named incoming signals are high | as CESND | — |
| **CSBRK** | 16H | send a requested number of break characters | (count) | — |
| **CSRCVB** | 17H | reserve a receive buffer in memory | HL = size: `0000H` → default 40 bytes, else `0050H`–`3FFFH` | A = 00H ok / non-zero = error. Also clears the send + receive buffers and the error flags. |
| **CCLRSB** | 1BH | initialise the send work area | — | — |
| **CCLRRB** | 1CH | clear the receive buffer and error flags | — | — |

### CWCOM parameter block

| Off | Contents |
|---|---|
| +0, +1 | baud-rate divisor = **76800 / baud rate**, little-endian |
| +2 | parameter byte — b0: stop bits (0 = 1, 1 = 2); **b3:b2** char length (`00`→5, `01`→6, `10`→7, `11`→8); b4: parity check enable; b5: parity (0 = odd, 1 = even); b6: XON/XOFF control enable; b7: SIN/SOUT (shift-in/out) control enable |

The BASIC `SETCOM` / `SNDSTAT` / `RCVSTAT` / `OUTSTAT` / `INSTAT` commands (Part 1) are
the high-level face of these routines and the same parameter/status bit layouts.