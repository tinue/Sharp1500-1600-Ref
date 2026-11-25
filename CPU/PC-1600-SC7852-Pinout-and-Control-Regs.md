# PC-1600 SC-7852: Pinout and Control Registers

Summary: SC-7852 100-pin terminal table and the on-chip control-register block 30H-3FH.
Scope: PC-1600
Sources: cited inline in the text
Status: cited

> Split from `PC-1600-CPU-SC7852-Z80.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.

## 6. The 100-pin package — terminal signals (TRM §7.1.1(2))

Full table as transcribed from the Systemhandbuch scan. "Active level" blank = not
specified / not a simple logic strobe. Overbar shown as a trailing `#`.

| Pin(s) | Symbol | Dir | Active | Function |
|---|---|---|---|---|
| 95–100, 1, 2 | KIN0–KIN7# | In | Low | Keyboard sense, pulled to VCC internally (200–500 kΩ). With **T (pin 87) = low** normal keyboard input (a pressed key pulls its line low). With **T = high** (emulation mode) these lines are used to connect a **Z-80 ICE**. |
| 3 | LHWAIT | Out | High | Wait output to the LH-5803. Goes high when: WAIT input is high; the LH-5803 accesses `**0*H` or `8000H–FFFFH` of ME1 (high for one cycle to insert one wait; TRM PDF p.218); or SC-7852+LH-5803 are in HALT. |
| 4 | φOS | In | — (clock) | LH-5803 basic clock, **1.3 MHz**. Used as the sync signal for the LH-5810-style port and to generate the **217 kHz LCD clock**. |
| 5 | PT | Out | — | Memory-bank signal: bit 2 (MSB) of the accessed page's bank number (Port 31H b3 for 4000–7FFF, b6 for 8000–BFFF). |
| 6 | PU | Out | — | Memory-bank signal: bit 1 of the accessed page's bank number (b2 / b5). |
| 7 | PVOUT | Out | — | Memory-bank signal: bit 0 of the accessed page's bank number (b0, b1, b4 or b7 by page); the LH-5803's PV while it runs. TRM §7.2.1 table, `PC-1600-Bank-Switching.md` Part 2. |
| 8 | PVIN | In | — | LH-5803 **PV** signal input. While the Z-80 runs, PV is held floating and pulled low internally. (See `LH5801-PU-PV-Signals.md`.) |
| 9 | WR# | In/Out | Low | Z-80 running: Z-80 `WR#` is driven out here. LH-5803 running: this line is an input that supplies R/W for the LH-5803. |
| 10–25 | A15–A0 | In/Out | — | Z-80 running: address bus driven out. LH-5803 running: address bus read in. |
| 26–33 | DB7–DB0 | In/Out | — | Data bus. |
| 34 | IORQ# | In/Out | — | Z-80 running: Z-80 `IORQ#` out. LH-5803 running: LH-5803 **ME1** read in here. |
| 35 | MREQ# | Out | — | Z-80 running: Z-80 `MREQ#` out. LH-5803 running: LH-5803 **ME0** read in here. |
| 36 | RD# | In/Out | — | Z-80 running: Z-80 `RD#` out. LH-5803 running: LH-5803 **OD** read in here. |
| 37 | WAIT | In | High | WAIT input to **both** the Z-80 and the LH-5803. Pulled low internally. When high, the CPU's internal clock φ stops (accepted on the H→L edge of φOS). |
| 38 | LHA90 | Out | — | For the RAM3 bank (C000H–FFFFH): input to address A9 of the E000H–FFFFH RAM (the A13A side feeds CE1). Z-80 running: LHA90 = A9. **Exception:** LHA90 is forced high when the LH-5803 accesses 7400H–744FH or 7500H–754FH — i.e. an LH-5803 access to those ranges physically lands on **7600H–764FH / 7700H–774FH** (the PC-1500 display-buffer region; see `PC-1600-LH5803-Memory-View.md` §5). |
| 39 | M1# | Out | Low | Z-80 running: Z-80 `M1#` out. LH-5803 running: generated from the LH-5803 `OPF` signal. |
| 40 | RFSH# | Out | Low | Z-80 `RFSH#`. LH-5803 running: generated from the LH-5803 `OPF` signal. |
| 41 | VDD | — | — | VCC. |
| 42 | IOE | Out | High | Asserted when the LH-5803 accesses `**00H–**0FH` or `8000H–0FFFH` of ME1; sends a WAIT to the LH-5803, issued with a **half-cycle delay**. |
| 43 | CS001# | Out | Low | Z-80 control, ROM select, **0000H–7FFFH bank 0** (main system ROM). |
| 44 | CS123# | Out | Low | (1) Z-80 control, ROM select, 8000H–BFFFH bank 6. (2) LH-5803 control, ROM select, C000H–FFFFH. |
| 45 | CS24# | Out | Low | Z-80 control, ROM select, **4000H–7FFFH bank 3** (sub-banked by A16A). |
| 46–48 | LHS3#, LHS2#, LHS1# | Out | Low | Memory sub-select within 8000H–BFFFH (bank 0), **remapped by bit 6 of I/O 3CH**: b6=0 → LHS1 A800–AFFF, LHS2 B000–B7FF, LHS3 B800–BFFF; b6=1 → LHS1 B000–B7FF, LHS2 A800–AFFF (TRM misprint: FAFF), LHS3 A000–A7FF. LHS1/LHS2 pulled up internally; **LHS3 needs an external pull-up**. The gate array buffers them onto Slot 1 pins 16/17/18 in reverse order, LHS3/LHS2/LHS1 (measured, `PC-1600-Gate-Array-and-Chip-Selects.md` Part 4). |
| 49 | RAM3 | Out | High | Internal 16 KB RAM select, C000H–FFFFH bank 0. |
| 50 | RAM2# | Out | Low | Slot 1 (S1) RAM select, 8000H–BFFFH banks 0/1 (and banks 2/3). |
| 51 | RAM1# | Out | Low | Slot 2 (S2) RAM select, 8000H–BFFFH banks 2/3. |
| 52 | SLCT | In | High | When **low**, all memory/I/O select outputs are suppressed (CS001, CS123, CS24, RAM3, RAM2, RAM1, IOE, IOSU, KA2, KA1, KA0, C/D, IORP). Driven by the sub-controller; high while the system is on. |
| 53 | KA2# | Out | Low | Goes low on a Z-80 I/O **write** to 28H–2FH. |
| 54 | KA1# | Out | Low | Goes low on a Z-80 I/O **read** from 28H–2FH. |
| 55 | KA0# | Out | Low | Goes low on any Z-80 I/O access to 60H–6FH. |
| 56 | CK0 | Out | — | 217 kHz φOS-derived clock to the HD61203 LCD common driver. Emitted only while **bit 4 of Z-80 I/O 37H = 1** (0 at power-on; the power-on routine sets it when it turns the LCD on). |
| 57 | IORP# | Out | Low | Goes low when the Z-80 reads I/O **33H**; used to read data coming back from the LU57813P sub-CPU. |
| 58 | C/D# | Out | High | Goes high when the Z-80 writes I/O **3DH**. Data is latched on C/D's rising edge; the data bus is stable when C/D rises with a half-cycle delay relative to IORQ. |
| 59 | IOSU# | Out | Low | Goes low on any Z-80 I/O access to 20H–27H; selects the TC8576F UART. |
| 60 | E | Out | High | Goes high on any Z-80 I/O access to 40H–5FH; the 6800-family interface strobe to the HD61102 LCD column drivers. Issued a half-cycle **slower** than IORQ. |
| 61 | DMF0 | Out | High | LH-5803 memory-select — high while the LH-5803 accesses memory. |
| 62–70 | PA0–PA7 | In/Out | — | Correspond to the LH-5803 I/O port PA. Used as keyboard strobes; to restore the natural state of a strobe forced low, drive high then switch to input mode (input is pulled up internally). |
| 65 | VSS | — | ±0 V | Ground. |
| 71 | PB2 | In | — | Cassette read (reproduce) signal. Pulled up internally. |
| 72 | PB5 | In/Out | — | PC-1600 input port; a 1/64 s pulse from the LU57813P sub-CPU arrives here. Pulled up. |
| 73 | PB6 | In/Out | — | Keyboard strobe (same usage as PA7–PA0). Pulled up. |
| 74 | PB7 | In | High | Receives the **BREAK/ON** key status from the sub-controller. Pulled down internally. |
| 75 | PC6 | Out | — | **Buzzer drive.** Internal gate: `PC6 = NAND(PB2, PC6', PC7', SD0)` — pulsing any one of those drives the buzzer. |
| 76 | SD0 | Out | — | Cassette **write** output. `SD0 = AND(SD0', PC7')`: TRM p.221 (PDF page) draws a two-input AND gate into a buffer; SD0' is the CE-150 cassette output (the serial block's SDO), PC7' the CE-1600P cassette output (OPC 18H b7, TRM p.244: "This content is sent to the SD0 terminal"). Both idle high (Service Manual §7-6: "The above three signal lines are normally high"), so either writes while the other rests. Wired straight to CMTOUT (CN2-46 → 60-pin pin 29; Service Manual p.50, F.P.C. circuit diagram). |
| 77 | ELH# | Out | — | **Which CPU is running:** low = LH-5803 active, high = Z-80 active. |
| 78 | PCSTB | In/Out | — | Reset → input mode, current state latched in the PB3 flip-flop (externally pulled up on the PC-1600). Normal mode → output: goes high when the Z-80 writes/does-I/O to 18H or the LH-5803 is at F008H in ME1. Not used on the production PC-1600. |
| 79 | RSTIN# | In | Low | Reset input to the SC-7852. Forced low for **30 ms** by the sub-CPU on ACL, RESET, or power-on. |
| 80 | IRQ | In | High | Interrupt to the CPU (Z-80 and LH-5803). Interrupt requests from **PC-1500** peripherals. |
| 81 | INT0 | In | High | Interrupt to the CPU. Requests from the **TC8576F** (UART / comm port). |
| 82 | INT1# | In | Low | Interrupt to the CPU. Requests from **PC-1600** peripherals. Pulled up internally. |
| 83 | INT4# | In | — (edge) | Interrupt on **falling edge**. A 1/64 s pulse from the sub-CPU; externally shorted to PB5. Open-drain CPU output side pulled down externally. |
| 84 | INT6 | In | High | Interrupt to the CPU; takes the sub-CPU's outputs as input. |
| 85 | PCTRL# | Out | Low | Power-down control. Goes low once the Z-80 has completed: (I) write 11H to I/O 37H, (II) `OUT (38H),A`, (III) `HALT` — the sub-CPU having sent a power-off command. |
| 86 | CLK | Out | — | Z-80 clock output, **3.58 MHz** on the PC-1600. |
| 87 | T | In | — | Low = normal mode (CPU runs normally); high = **simulation mode** (Z-80 bus floats; an external Z-80 or Z-80 ICE can be attached — with KIN0–7 used for the connection). Pulled down internally. |
| 88, 89 | XOUT / XIN | Out / In | — | 3.58 MHz Z-80 crystal connects across these. |
| 90 | VDD | — | — | Power input, high side, **4–5.5 V**. |
| 91 | LHMIO | Out | High | Maskable-interrupt output to the LH-5803, wired to its **MI** input (LH-5803 pin 16). Goes high when there is an interrupt request for the LH-5803. |
| 92 | LHNMIO | In/Out | High | Wired to the LH-5803 **NMI** input (pin 15). (1) Goes high when the LH-5803 is at `94**H` with PU = PV high (the CE-158 internal ROM). (2) Becomes an input during reset, so it needs an external pull-up or pull-down; on the PC-1600 it is pulled down (R12). The LH-5803 ROM's NMI handler shows the trap fires on the opcode fetch at **9400H**, not on every 94xxH access, and replaces a CE-158 display-RAM routine (`PC-1600-LH5803.md` §6.1). PU has no input pin here, so the SC-7852 must read the shared PU net on pin 6. |
| 93 | LHOPFI | In | High | Takes the LH-5803's **OPF** (opcode-fetch) output, LH-5803 pin 7. Pulled down internally. Source of M1#/RFSH# while the LH-5803 runs (pins 39/40). |
| 94 | RSTO | Out | High | Reset output to the LH-5803. RSTIN# low makes RSTO high, and it stays high until the Z-80 first hands control to the LH-5803, which then starts to run. |

> **Cross-refs:** the memory-decode outputs (CS001/CS123/CS24/RAM1–3, and the PT/PU/PVOUT bank bits) go to the memory PWB and the slots; LHS1–3 and KA0–2 reach the slots through the LR38041 gate array, which also generates the A16A sub-banking — see `PC-1600-Gate-Array-and-Chip-Selects.md` Parts 3–4 and Part 12. The KA/IOSU/E/IORP/C-D strobes and the interrupt inputs are the I/O-decode side — `PC-1600-IO-Ports.md`.

---

## 7. On-chip I/O and the internal control-register block

TRM §7.1.1(3). "Similar to the Z-80A, the SC-7852 has a 256-byte I/O space (00H–FFH)."

### 7.1 I/O map (range level)

| Range | Assignment |
|---|---|
| 00H–0FH | **Use prohibited** |
| 10H–1FH | LH-5810/LH-5811-compatible port, inside the SC-7852 (**not** synchronised to φOS). The LH-5803 reaches it at ME1 F000H–F00FH (`PC-1600-LH5803.md` §2a) |
| 20H–27H | TC8576F UART select (IOSU#) |
| 28H–2FH | S2 (Slot 2) — KA1#/KA2# strobes |
| **30H–3FH** | **SC-7852 internal LSI control-register port** (see §7.2) |
| 40H–4FH | System reserve (E# strobe region 40H–5FH) |
| 50H | HD61102 LCD column drivers — **both** (IC2) and (IC3) |
| 58H | HD61102 LCD column driver (IC3) |
| 5BH | HD61102 LCD column driver (IC2) |
| (5CH–5FH) | System reserve |
| 60H–6FH | S2 (Slot 2), second window (KA0#) |
| 78H–7FH | CE-1600F (floppy) |
| 80H–83H | CE-1600P (plotter/printer) |
| 84H–BFH | Reserved for future extension |

### 7.2 Internal control registers, 30H–3FH

Read and write at each port do **different** things (the manual lists an `IOR xxx` and an
`IOW xxx` name per address). The `#Rreg` column in the source cross-references the
LH-5803-side ME1 shadow address `#A03xH`.

| Port | Read (`IOR`) | Write (`IOW`) | Purpose |
|---|---|---|---|
| 30H | MOD | MOD | Module control. b0: the LH-5803 ROM clears it around its own LCD / sub-CPU accesses and the CE-158 trap, read as the switch that sends LH-5803 display-RAM writes to the Z-80 (not confirmed) |
| **31H** | MAP | MAP | **Primary bank-select register** — see `PC-1600-Bank-Switching.md` Part 2 |
| 32H | INT | PRI | Read = interrupt-cause register (§5.2); write = interrupt priority |
| 33H | P | CDF | Read = data returning from the LU57813P sub-CPU (via IORP#); write = CDF |
| 34H | LHMSK | LHMSK | LH-5803-side interrupt mask |
| 35H | ZMSK | ZMSK | **Z-80-side interrupt mask** (§5.2) |
| 36H | ADRS | CL1 | Read = address; write = CL1. The LH-5803 NMI handler writes 00H here to acknowledge the `LHNMIO` trap (`PC-1600-LH5803.md` §6.1) |
| 37H | KB | CGC | Read = keyboard; write = CGC register (bit 4 gates CK0 / the LCD clock) |
| 38H | — | STP | **CPU-switch trigger** — `OUT (38H),A` in the Z-80→LH-5803 hand-off sequence (§5.14; `PC-1600-IO-Ports.md` Part 9) |
| 39H | — | VCT | **IM2 interrupt-vector low byte** (§5.1) |
| 3AH | — | KA | "Not used" |
| 3BH | — | KS | "Not used" |
| 3CH | — | SLT | Slot control; **bit 6 remaps LHS1–3** (§6, pin 46–48) |
| 3DH | — | C/D | Hidden-ROM / extended-address latch (`PC-1600-Bank-Switching.md` Part 2); latched on C/D# rising edge; state also mirrored at system address F07DH |
| 3EH, 3FH | — | — | unused |

> **Warning (from the manual):** *"If wrong values are written to an I/O area between 30H
> and 3DH so that the defaults are not correct, the PC-1600 does not operate properly."*
> Emulators and ML programs must preserve the OS's expected contents of this block.

### 7.3 Machine-cycle wait

The "1 WAIT automatically inserted in the machine cycle" note (§2.3) is printed with this
I/O map. Hardware measurement shows it applies to the **M1 (opcode-fetch) cycle** of every
instruction, not just to I/O cycles (§2.3). Whether I/O cycles get a further wait is open
(§12).

---
