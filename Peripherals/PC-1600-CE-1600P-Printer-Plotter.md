# PC-1600 CE-1600P: Printer / Plotter

Summary: CE-1600P printer/plotter: IOCS, plot geometry, hardware, Centronics parallel mode on the same ports.
Scope: PC-1600
Sources: PC-1600 Technical Reference Manual §3.7 (printer IOCS), §3.8 (disk IOCS) — read from the German edition (SYSHB-1600, Holtkötter 1987); plus David von Oheimb, *Das Systemhandbuch für den PC-1600* (OHEIMB-1600, a separate book), ch. 13 "Diskettenlaufwerk", PDF pp. 46–53; plus …
Status: draft

> Split from `PC-1600-Peripherals-Hardware.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §2, §3 → [PC-1600-Floppy-CE-1600F.md](../Storage/PC-1600-Floppy-CE-1600F.md).

## Scope

The printer/plotter (CE-1600P) and floppy (CE-1600F) IOCS routines and hardware, plus
the peripheral-device hardware chapter (TRM Ch 8) as it is processed. Memory modules have
their own document (`PC-1600-Memory-Modules.md`); the serial interface has
`PC-1600-Serial-Commands.md` / `PC-1600-Serial-Hardware.md`.

**Sources:** PC-1600 Technical Reference Manual §3.7 (printer IOCS), §3.8 (disk IOCS) —
read from the German edition (SYSHB-1600, Holtkötter 1987); plus David von Oheimb, *Das
Systemhandbuch für den PC-1600* (OHEIMB-1600, a separate book), ch. 13 "Diskettenlaufwerk", PDF pp. 46–53; plus `PC-1600_Service_Manual.pdf`'s
CE-1600P chapter (pp. 63–72, electrical hardware; §1.2 below) and CE-1600F chapter
(pp. 98–104, electrical/mechanical hardware; §3.1 below).
Processed so far: TRM **§3.7**, TRM **§3.8**, Service Manual **CE-1600P ch.** (§1.2),
Service Manual **CE-1600F ch.** (§3.1), TRM **§9.2(1)** CE-1600P circuit diagram (ROM
part, 50-pin CON1 table, §1.2.1 / §3.1.6). Pending: TRM Ch 8 (general peripheral hardware
chapter); CE-1600P's own mechanical/pen-mechanism repair chapter (out of scope for
emulation, not transcribed).

---

## 1. Printer / plotter — CE-1600P (TRM §3.7)

The CE-1600P is an A4 4-colour pen plotter-printer with a built-in cassette interface
(and it hosts the CE-1600F floppy). Its ROM lives in **Bank 4** (`EXROM4`,
`PC-1600-Transparent-Banking.md` Part 6); its work-area state is in
`PC-1600-Work-Area-Map.md` §3.4 (F182H–F194H) and §3.7 (F9E0H–F9F8H).

### 1.0 Plot geometry

- **Plottable width (X):** X = 0 to 960 plotter units ≈ **190mm**, the pen clips at this
  edge. Scale = **0.198mm per unit** (190 / 960). The CE-150 shares this same step
  (`SharpBasicReference/CE-150-Reference.md`: 216 units ≈ 42.75mm) — same mechanism, just
  a wider carriage on A4 stock. The CE-1600P's wider travel makes it the better source
  for the mm/unit figure.
- **Y:** no fixed page length in roll mode (`MODE` b1 = 1, `PC-1600-Work-Area-Map.md`
  §3.4); `PSCRL` (IOCS 0AH) sets the Y-direction print area on the paper. Cut-sheet
  mode (`MODE` b1 = 0) is bounded by the sheet.

### 1.1 Two call mechanisms

**§3.7.1 — direct-call routines** (`CALL <Bank 4, address>`):

| Name | Address | Function | Params | Return |
|---|---|---|---|---|
| **PCHEK** | Bank 4, `4020H` | is the printer ready? | — | A: b3 = not initialised, b6 = pen-change status, b7 = printer battery low (b4, b5 always 0). Clobbers all registers. |
| **POUT** | Bank 4, `4023H` | send one character code | E = char code | CF=0 ok; CF=1 = error or BREAK; A = 00H (BREAK pressed) or an error code (same codes as BASIC). Clobbers all registers. |
| **PKOUT** | Bank 4, `4026H` | send one character code (kana variant) | E = char code | as POUT |

> **Mandatory cleanup.** Immediately after *any* printer IOCS routine you **must** call
> **Bank 4, `4029H`** and then **Bank 4, `6777H`**. These do the post-processing (turn
> off the printer-motor power and the interrupt control). Skip them and the motor stays
> powered and the keyboard stops accepting input.

**§3.7.2 — dispatched routines**: put the **IOCS number in `C`** and `CALL Bank 4,
`4008H``. All registers are destroyed. Error code as in BASIC. Routines marked **(G)**
work only in graphics mode.

| # | Name | Function |
|---|---|---|
| 00H | PINIT | initialise the printer |
| 01H | PTEXT | select text mode |
| 02H | PGRAPH | select graphics mode |
| 03H | PCSIZE | set character size |
| 04H | PCOLOR | set pen colour |
| 06H | PWIDTH | set characters per line |
| 07H | PLEFTM | set the left margin |
| 08H | PPITCH | set character pitch + line height |
| 09H | PPAPER | set paper type |
| 0AH | PSCRL | set the Y-direction print area on the paper |
| 0BH | PEOL | set the action taken on a CR code (0DH) |
| 0CH | PZONE | set the print-zone length for `LPRINT` |
| 0DH | PPENUP | raise / lower the pen |
| 0EH | PROTATE | set print direction |
| 0FH | PLTYPE (G) | set line type |
| 10H | PHOME (G) | pen up → origin |
| 11H | PSORGN (G) | define the current pen position as the origin |
| 12H / 13H | PAMVUP / PRMVUP (G) | move pen up, absolute / relative coords |
| 14H / 15H | PAMVDN / PRMVDN (G) | move pen down, absolute / relative coords |
| 16H | PTEST | run the print test |
| 17H | PTAB | move pen to a tab position |
| 18H | ALLOFF | turn off the printer-motor power |
| 1AH–1DH | PCUP / PCDOWN / PCLEFT / PCRIGHT | move pen up, one character step, up/down/left/right |
| 1EH–21H | PGUP / PGDOWN / PGLEFT / PGRIGHT | move pen up, one graphics-dot step, up/down/left/right |
| 22H | PCHGPEN | change pen |
| 28H | PRESET | reset the printer-IOCS work area to its All-Reset state |
| 29H | PCR | pen → left end (carriage return) |
| 2AH | PDIRC | set the character print direction (graphics mode) |
| 2BH | PCRLF | pen → left end of the next line (CR + LF) |
| 2CH | PMYFD | how many lines can the pen move in −Y? |
| 2DH | PPYFD | how many lines can the pen move in +Y? |
| 2FH / 30H | PBOXA / PBOXR | draw a box, absolute / relative coords |
| 31H | HARESET | initialise the printer hardware |

The `LPRINT` / `LLINE` / `GLCURSOR` / `COLOR` / `LF` / `ROTATE` / `CSIZE` / `PZONE` BASIC
commands are the high-level face of these; the work-area bytes they set
(`PC-1600-Work-Area-Map.md` §3.4) are the same state.

### 1.2 CE-1600P hardware (Service Manual, pp. 63–72)

**Source:** `PC-1600_Service_Manual.pdf` pp. 63–72 (CE-1600P chapter §1–§7, excluding the
purely mechanical FPC-rework steps in §6-1–6-3 and everything past §7-1, which are
disassembly/soldering instructions for a bench technician, not relevant to emulation).
This is the electrical counterpart to the IOCS layer in §1.0/1.1 above, and it also
covers the printer's own stepper-motor mechanism (PTMPG3308A) and the CMT (cassette)
interface, which the TRM excerpt processed so far does not.

**Key architectural fact:** the CE-1600P is not just a printer — it's the **hub** for
all three "external" peripherals: printer, cassette (CE-152), and floppy (CE-1600F).
None of the three can be used standalone; all are driven from the PC-1600 through the
CE-1600P's 32KB ROM and gate array. The CE-1600P has **no local power switch/logic of
its own that operates without the host**: `VCC` to the CE-1600P is only supplied while
the PC-1600 main unit is powered on (§5-1) — so a battery-only, host-off CE-1600P is
inert for printer/cassette/floppy purposes; the *only* thing that keeps working with
the host off is its own NiCd recharge circuit.

#### 1.2.1 Block diagram (§2)

Physical connectors: a **60-pin male** to the PC-1600 main unit, a **60-pin female**
pass-through to the system/expansion bus (so peripherals can still be daisy-chained past
the CE-1600P), and a **50-pin female** to the CE-1600F floppy (matches
`PC-1600-Floppy-CE-1600F.md` §3.1.2's 50-pin CON1 description from the floppy side).

Internal blocks, all tied together by the **LR38045 gate array**:
- **32KB ROM** — the Service Manual block diagram says SC27C256. The TRM §9.2(1) circuit
  diagram labels it a mask ROM, "32 KB M-ROM SC53257F 5216". It holds the
  printer/cassette/floppy driver software; chip-select generated by the gate array's
  `CSNO` line (see §1.2.2 pin table).
- **PTMPG3308A** — the 4-color plotting printer mechanism (mechanical detail in §1.2.4).
- **Driver LB1247 (×2)** — power drivers between the gate array's logic-level outputs and
  the printer's stepper-motor coils / the remote relay (§1.2.3).
- **Cassette interface** — read/write/remote circuitry for the CE-152 cassette recorder,
  talking to the gate array over `REM`/`MIC`/`EAR` (§1.2.5).
- **Power supply** — takes `VBAT` from the PC-1600 and the EA-160 AC adaptor, produces
  `VP` (+6V, motor/printer rail) and `VCC` (§1.2.6).

#### 1.2.2 LR38045 gate array (§3-1) — port map and pin description

This gate array **is** the CE-1600P's I/O controller: it holds the ROM/FDD chip-select
decoders, the interrupt controller, the CMT read/write front-end, and the two 8-bit
output latches that drive the printer motors — there is no separate "printer
controller" chip; PB/PC are bit-banged directly by IOCS software through this gate
array. For emulation, this table **is** the printer/cassette/floppy-select register
map as seen from the CPU:

| Port addr | Op | Data (D7 → D0) |
|---|---|---|
| 80H write (FF1) | set IRQ-enable bits | 0, *, Printer-CR-INT-en, Printer-SW-INT-en, FD-INT-en, Reverse-PF-key-INT-en, PF-key-INT-en, CC-key-en |
| 80H read (FF1) | read back IRQ-enable bits | same bit layout, reflects current FF1 |
| 81H write, D0, `WR` | **FD reset** (low active — note: this is the one write operation on this table that is *active-low*, everything else on the table is active-high as seen from the CPU) | — |
| 81H read (`PA0–7`) | read pending-interrupt/key status | CMT-input, (0), Printer-CR, Print-SW, FD-INT, Reverse-PF-key, PF-key, CC-key |
| 82H write (FFD → `PB0–7N`) | **Z-motor** phases + CMT/remote control | CMT-in-Enable, *, RMT-OFF, RMT-ON, Motor-ZD, Motor-ZB, Motor-ZC, Motor-ZA |
| 82H read (FFE → `PB0–7N`) | read back PB latch | same layout |
| 83H write (FFE → `PC0–7N`) | **X-motor + Y-motor** phases, packed 4+4 bits on one port | Motor-YD, Motor-YB, Motor-YC, Motor-YA, Motor-XD, Motor-XB, Motor-XC, Motor-XA |
| 83H read (FF3 → `PC0–7N`) | read back PC latch | same layout |

So: **Z-motor (pen up/down + color change) is entirely on port 82H**, while **X-motor
(carriage) and Y-motor (paper feed) share port 83H**, 4 bits each — an emulator's
plotter-stepper model should treat writes to 83H as *simultaneously* updating both X and
Y coil state from one byte, not as two separate operations.

**Bit-name translations (Systemhandbuch Appendix 6, "I/O-Adressen").** The service
manual's own pin/signal names above are cryptic; the Systemhandbuch's port appendix gives
plain-language meanings for the same 80H–83H bits, confirming the mapping end to end:

Bit-for-bit match against the 80H write (FF1) row in §1.2.2's table above:

| Bit | Service-manual name | Appendix 6 meaning |
|---|---|---|
| b5 | Printer-CR-INT-en | print head at the left home-stop/carriage-return position |
| b4 | Printer-SW-INT-en | print switch |
| b3 | FD-INT-en | floppy-drive interrupt ("Disk") |
| b2 | Reverse-PF-key-INT-en | reverse paper-feed key |
| b1 | PF-key-INT-en | paper-feed key |
| b0 | CC-key-en | **C**olor-**C**hange key ("Farbwechsel-Taste") — confirms the abbreviation |

Plus, from the 81H-read and 82H rows: `CMT-input` (81H read b7) = cassette-recorder
receive line; `CMT-in-Enable` (82H b7) = cassette-recorder interface enable.

### 1.3 Centronics parallel-printer mode (Appendix 6) — same ports, alternate function

Ports 80H–83H are **dual-purpose**: besides the plotter-control function in §1.2.2, the
same four addresses also serve a **Centronics parallel-printer interface** — not
documented anywhere else in this corpus. Presumably the gate array's `DC3` decoder
(§1.2.2's internal-block description) selects between the two personalities based on a
mode bit elsewhere (not identified by this source); this needs confirmation against real
hardware or a ROM disassembly.

| Addr | Op | Plotter-mode meaning (§1.2.2) | Centronics-mode meaning |
|---|---|---|---|
| 80H | write | interrupt mask (6 key/status bits) | interrupt mask — only b3 (Disk) is called out |
| 81H | write, b0 | FD reset | FD reset (same) |
| 81H | read | interrupt cause, mirrors 80H's bit layout | b3 = disk interrupt, b0 = **Busy** |
| 82H | — | CMT-interface enable + RMT ON/OFF + pen (Z) motor, 4 bits | **handshake lines**: b5 = `EXPRM`, b4 = `STROBE` |
| 83H | — | X/Y motor phases, 4+4 bits | **parallel data** byte |

The Centronics-mode 82H handshake bits (`STROBE`/`EXPRM`) and 83H parallel-data byte are
exactly the classic Centronics protocol signals — this all but confirms the CE-1600P can
drive a generic Centronics parallel printer directly, alongside its own plotter mechanism
and the CE-1600F floppy, through the same 60-pin connector block.

**Gate array pin description (64-pin gate array, LR38045):**

| Pin(s) | Symbol | I/O | Function |
|---|---|---|---|
| 1–8 | `PC7N–PC0N` | Out | 8-bit output port, address 83H (X/Y motor phases, via FF3) |
| 9–16 | `PB7N–PB0N` | Out | 8-bit output port, address 82H (Z motor phases + CMT/RMT, via FF2) |
| 18–20 | `PUI`, `PTI`, `EZI` | In | `PU`/`PT`/`ELH` signal inputs — used to generate the 32KB ROM select (`CSNO`) |
| 21–22 | `MINI`, `IORQ` | In | `M1`/`IORQ` inputs — used to generate `IO7N` and the gate array's internal enable |
| 23 | `MRQI` | In | `MREQ` input, used for `CSNO` generation |
| 24 | `RSTI` | In | Reset input — triggers internal FF1–3 reset *and* the 2.5″ FDD reset (`RSTN`) |
| 25–26 | `VCC`, `GND` | — | Power |
| 27 | `IRQ` | Out | Interrupt out, N-channel open-drain, pulled up to Vcc on the PC-1600 side |
| 28–29 | `RDNI`, `WRNI` | In | `RD`/`WR` inputs |
| 30–39 | `A0I–A7I`, `A14I`, `A15I` | In | Address bus input |
| 40 | (NC) | | |
| 41 | `RSTN` | Out | 2.5″ FDD reset out — unconditionally asserted on any reset, must be **cleared by software** (address 81H, D0, `WR`) — matches §3.1.3's floppy-side reset-input behaviour |
| 42 | `IO7N` | Out | 2.5″ FDD select, decoded over address range **70H–7FH** |
| 43 | `CSNO` | Out | 32KB ROM select: asserted when `ELH`/`MREQ`/`PT` are high **and** `PU` is low, over address range **4000H–7FFFH**; `PV` low selects the printer, `PV` high selects the FDD/CMT — i.e. `PV` is the printer-vs-(floppy/cassette) arbitration line within that address window |
| 44–51 | `DB0–DB7` | I/O | Data bus |
| 52–57, 60 | `PA0I–PA5I`, `PA6I` | In | Input port (address 81H read); interrupt-controlled by FF1 (address 80H), maps to Q0–Q6 |
| 58 | `GND` | | |
| 61 | `PA7B` | Out | CMT-interface output — the amplified/waveform-shaped cassette read signal (see §1.2.5) |
| 62, 64 | `PA6N` (out), `PA7I` (in) | | Together form a feedback amplifier when an external feedback resistor is connected between them (§1.2.5, Fig. 6) |

Internally, `Bu` is the bidirectional 8-bit I/O buffer, `Mu` a multiplexer selecting
FF1/FF2/FF3/PA-port for reads, `FF1–FF3` the three 8-bit output latches (interrupt
enables, PB, PC respectively), `DC1–DC3` the three address decoders (`DC1`→ROM select
`CSNO`, `DC2`→FDD select `IO7N`, `DC3`→ selects which of FF1–FF3/PA-port is targeted by
a given read or write), `INT` the interrupt OR-tree (any enabled+asserted `PA0–6I` bit
drives `IRQ`), and `RST` the reset circuit. **PA/PB/PC are active-high inside the gate
array but are inverted to active-low outside it** (`PB0N`, `PC0N` etc. — the `N` suffix
marks the inverted, externally-visible signal) — e.g. setting bit Q0 of FF2 to `1`
drives the external `PB0N` pin low.

The reset circuit can also assert `RSTN` (and thus reset the floppy) **purely by
software**, without needing the hardware `RSTI` input — i.e. IOCS can force a floppy
reset at address 81H even absent a hardware reset condition.

#### 1.2.3 Printer drive IC (LB1247) and remote relay (§3-2)

Each **LB1247** package contains 8 driver circuits; the CE-1600P uses two: **driver 1**
drives the X-motor and Z-motor coils, **driver 2** drives the Y-motor coils plus the
remote relay (2 of driver 2's 8 outputs are unused for the relay function). Each driver
is a simple active-low-in/open-collector-out stage: the output transistor conducts
(pulling the load to `VP`) whenever the gate-array's PB/PC output to that driver is
**low** — consistent with the "N"-suffixed, active-low PB0N–PC0N signals described in
§1.2.2. To boost torque on the Y-motor specifically, a 5V zener diode (**HZ5C1**,
containing a reverse-surge-absorbing diode) is inserted across two of driver 2's
`VCC2` pins.

**Remote relay** (drives the CE-152 cassette's motor via the `REM` line): a two-coil
**latching** relay (**AG8229** or **G5AK-287P**) — it needs a single ON or OFF *pulse*
through driver 2 to change state (not a held level), and that pulse must be **wider
than the relay's minimum spec (>5ms)**; the CE-1600P uses **~10ms** pulses in practice.
This matters for emulation: a model of the remote-control bits (`RMT-ON`/`RMT-OFF` on
port 82H, §1.2.2) needs to treat them as edge/pulse-triggered latch-set commands, not as
level-held motor-enable bits.

#### 1.2.4 Printer mechanism — PTMPG3308A (§7-1)

Three stepping motors — **X** (carriage/horizontal pen movement), **Y** (paper
feed/vertical), **Z** (pen up-down + color change) — each with 4 coils (A/B/C/D) plus a
common return, driven via the LB1247s above. **X and Y run 1-2 phase excitation; Z runs
2-2 phase excitation.** A carriage-position-detector switch (CR/home-position sensor) is
wired to the gate array's `PA5I` input (§1.2.2's "Printer-CR" status bit).

**Drive pulse trains (§Circuit-Diagram/§3):**

X/Y motor, 1-2 phase excitation, 8-step sequence (A/B/C/D = coil on/off per step,
rotation is counter-clockwise, giving **+X = clockwise carriage motion**, **+Y =
reverse paper feed**):

| Step | A | B | C | D |
|---|---|---|---|---|
| 1 | ON | OFF | OFF | ON |
| 2 | OFF | OFF | OFF | ON |
| 3 | OFF | ON | OFF | ON |
| 4 | OFF | ON | OFF | OFF |
| 5 | OFF | ON | ON | OFF |
| 6 | OFF | OFF | ON | OFF |
| 7 | ON | OFF | ON | OFF |
| 8 | ON | OFF | OFF | OFF |

Z motor, 2-2 phase excitation, 4-step sequence (rotation counter-clockwise = **pen
down**):

| Step | A | B | C | D |
|---|---|---|---|---|
| 1 | ON | OFF | OFF | ON |
| 2 | OFF | ON | OFF | ON |
| 3 | OFF | ON | ON | OFF |
| 4 | ON | OFF | ON | OFF |

**Motor/detector wiring → connector pin map** (17-pin Molex 15046-17A right-angle wafer):
pins 1–5 = Z-motor A(yellow)/B(blue)/C(white)/D(red)/COM(black); pins 6–10 = Y-motor,
same colour/letter order; pins 11–15 = X-motor, same order; pins 16–17 = carriage
position detector, A(yellow)/B(gray).

**Mechanical/timing specs relevant to emulation:**

| Property | Value |
|---|---|
| Pen moving speed, X | 650 steps/sec (1-2 phase) / 325 steps/sec (2-2 phase) |
| Pen moving speed, Y | 650 steps/sec |
| Pen moving distance / step, X | 0.1mm (0.2mm during initialization) |
| Pen moving distance / step, Y | 0.1mm |
| Pen plotting speed | 65mm/s (axis-aligned), 92mm/s (45°) |
| Plotting range, X | 192mm = 1920 steps; home position 14±1mm from edge; paper guide width 220mm |
| Plotting range, Y (A4/letter) | ≥25.4mm margin top/bottom, 2–16mm margin left/right |
| Plotting range, Y (roll paper) | 214±2mm width, 2–16mm margin left/right (roll positioning tolerance) |
| Print pitch / paper-feed pitch | 1.2mm ±10% / 2.4mm ±10% |
| Character sizes 1–9 | 160/80/53/40/32/26/22/20/17 chars-per-line; height 1.2–10.8mm; width 0.8–7.2mm (full table: size→chars/line→height→width, linear scaling by size index) |
| Print speed | avg 14 cps (char size 1, full 96-char ASCII set), avg 7 cps (char size 2) |
| Max print positions | 80 (char size 2); selectable 160/120/40/etc. depending on size |
| Recommended pen | water-based ballpoint, ⌀5×23.3mm (+0/−0.1mm), rated life ≥250m (~43,000+ characters at 2.4mm height using EA4AR1 roll paper) |

These numbers are consistent with, and more detailed than, the plot-geometry figures
already recorded in §1.0 above (960 units ≈ 190mm ⇒ ~0.198mm/unit vs. this section's
1920 steps ≈ 192mm ⇒ 0.1mm/step — the IOCS-level "plotter unit" is 2 physical motor
steps, matching the "0.2mm during initialization" note for coarse moves).

#### 1.2.5 CMT (cassette) interface (§4)

Three sub-circuits, all ultimately routed through the gate array's `PA7B`/`PA7I`/`PA6N`
pins (§1.2.2):

- **Write circuit:** converts the CMT-OUT logic-level signal (4.7Vpp = Vcc swing) down
  to cassette mic-input level (**8.5mVpp / 3mVrms**, ~600Ω output impedance) through a
  discrete low-pass filter → high-frequency compensation (+6dB boost above ~1.5kHz to
  offset the low-pass filter's rolloff at 3kHz) → attenuation → DC-decoupling chain
  (R1=12kΩ, C1, R2=6.8kΩ, R3=680Ω, C2=0.047µF).
- **Read circuit:** the cassette `EAR` signal is amplified/waveform-shaped by a
  NAND-gate-based comparator/hysteresis circuit **inside the gate array itself**
  (same circuit topology as the CE-150's read amp, per the doc) and comes out on `PA7B`;
  external passives are a 1MΩ feedback resistor, 0.1µF coupling cap, 100kΩ/1kΩ divider
  into `EAR`.
- **Remote circuit:** see §1.2.3 above (latching relay via LB1247 driver 2).

**Signal encoding — important for tape-format compatibility:** *Write* uses **PWM,
"1600 method"** only. *Read* supports **both PWM "1600 method" AND "1500 method"** — i.e.
the CE-1600P's cassette read path is backward-compatible with PC-1500-era tape
recordings, even though it can only *write* the newer 1600-style encoding. See
`Data-Formats/WAV-Cassette-Format-1500-1600.md` for the two encodings themselves; this
confirms at the hardware level why that doc treats 1500 and 1600 cassette formats as
related-but-distinct, and specifically that a real CE-1600P is asymmetric (reads both,
writes only the new one).

#### 1.2.6 Power supply (§5)

- **Battery/adaptor front end:** the EA-160 AC adaptor's rectified ~8.4V feeds a diode
  network before becoming `VP` (6.4V) and charging the internal NiCd pack (`AAx5`,
  i.e. 5 AA NiCd cells): **D1** (Schottky, RK-13, 1.7A) blocks reverse current from
  battery into the adaptor and enables efficient recharging; **D2/D3** drop the adaptor
  voltage below the printer's max drive voltage (7.15V); **D4** blocks reverse current
  from `VP` into the NiCd pack while the adaptor is in use; **D5** (Schottky) blocks
  reverse current from `VBAT` (supplied by the PC-1600 host) back into `VP`, to avoid
  draining the CE-1600P's own battery while the adaptor is in use; **D6** (11DQ03, 1A,
  ×2) bypasses D4/D5 so that when the CE-1600P is running on its *own* battery (no
  adaptor), the host's main-unit battery isn't also drained supplying `VBAT` — the
  printer's min. drive voltage is 5.0V, so the CE-1600P's own low-battery cutoff is set
  to **5.65V pack / 1.13V per cell**.
- **VCC to the CE-1600P:** ORed from the CE-1600P's own `VBAT` and the PC-1600's `VBAT`
  supply, then regulated to **4.7V** before being supplied to the CE-1600P's logic.
  **When the PC-1600 main unit is powered off, `VCC` is not supplied at all** — this is
  the hardware confirmation of §2's/§1.2's "cannot operate standalone" note: the printer
  logic (gate array, ROM) is entirely dependent on the host being on, even though motor
  power (`VP`) can come from the CE-1600P's own battery/adaptor.
- **AC adaptor (EA-160) spec:** 100VAC 50/60Hz 20VA in; 8.4VDC/1A rated out (2A peak,
  ~2.5A short-circuit/overcurrent cutoff), chopper-type regulator, 67.2×115.2×53.5mm,
  695g.
- **Current budget (§5-2, at VP=6V):** PC-1600 host itself draws max 50mA (RS-232 idle).
  On the CE-1600P side: gate array (LR38045) max 3.25mA @1.3MHz, ROM (SC27C256) max
  3.20mA @400kHz, driver (LB1247) max 100mA; under active printing load, current rises
  to 803mA (45° dotted-line pattern) / 638mA (ASCII text) / 605mA ("555..." pattern) /
  242mA (carriage return only), with worst-case combined totals up to ~959mA. At
  character size "2": max continuous printing time is ~28min (45° dotted line), ~34min
  (ASCII text), ~35min ("555...") per charge; rechargeable pack capacity is 500mAh;
  max. printable characters ≈10,000 and max. printable lines ≈240 per charge at 5 cps
  (assuming a 1-second carriage-return pause per 40-character line).
