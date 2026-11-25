# PC-1600 Floppy: CE-1600F / CE-1650F

Summary: Floppy IOCS, disk geometry, logical sectors, FAT, port-level registers 78-7FH, drive-unit hardware.
Scope: PC-1600
Sources: PC-1600 Technical Reference Manual §3.7 (printer IOCS), §3.8 (disk IOCS) — read from the German edition (SYSHB-1600, Holtkötter 1987); plus David von Oheimb, *Das Systemhandbuch für den PC-1600* (OHEIMB-1600, a separate book), ch. 13 "Diskettenlaufwerk", PDF pp. 46–53; plus …
Status: draft

> Split from `PC-1600-Peripherals-Hardware.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: Scope, §1 → [PC-1600-CE-1600P-Printer-Plotter.md](../Peripherals/PC-1600-CE-1600P-Printer-Plotter.md).

## 2. Floppy — CE-1600F / CE-1650F (TRM §3.8)

A 2.5″ floppy drive that connects **through the CE-1600P** (it cannot run standalone).
Its ROM is `EXROM5` (Bank 5); its disk format is the same FAT family as the RAM-disk
memory file (`PC-1600-Filesystem.md`).

> **Bank number note.** The Systemhandbuch's own "13. Diskettenlaufwerk" chapter (Ditze/
> von Oheimb, pp. 46–53) writes the dispatch call as `CALL 4008H, Bank 4` for the disk
> IOCS routines below — but `PC-1600-IOCS.md` §3.8 and this file both independently say
> **Bank 5**, and §1.2.1 above already establishes that the CE-1600P's single 32KB
> physical ROM chip holds printer, cassette, *and* floppy driver code, bank-switched into
> at least two logical banks (4 for printer entry points, per §1.1 above). Given two
> independent sources agree on Bank 5 and "4"/"5" are an easy scan/OCR digit confusion,
> this is very likely a transcription slip in that source, not a real discrepancy —
> flagged for confirmation on real hardware rather than silently corrected. **Resolved:** Ditze's own DISKCOPY program (*Programme, Tips & Tricks für den PC-1600*, 1987, pp. 35–36), which is working code by the same author, encodes the disk call as `E7 05 08 40` = `RST 20H` / `CALL Bank 5, 4008H`. It calls `DREAD` (C=`84H`) and `DWRITE` (C=`85H`) with A=`01` (X:), B=`10H` (16 sectors = 8 KB, spanning two tracks), D = even track `00`–`0EH`, E=`00` and HL = buffer. So **Bank 5** is correct, and one `DREAD` call can run across a track boundary. The buffer is 8 KB+26 bytes reserved with `CALL &02DD,A`, and its address is read from `PTR3` (F034/F035H).

### 2.1 Disk geometry (§3.8.2)

| Property | Value |
|---|---|
| Tracks per side | 16 |
| Sectors per track | 8 |
| Bytes per sector | 512 |
| Capacity per side | 64 KB |
| Sectors per FAT | 1 |
| Number of FATs | 2 |
| Logical sectors per cluster | 1 |
| Max files per side | 48 |

The Systemhandbuch's own summary of this table (ch. 13, "Physikalisches
Aufzeichnungsformat") writes "**10** Spuren, **08** Sektoren, 200H Bytes/Sektor = 64d KB
pro Seite (unformatiert)" — all in hex like the rest of that source, so "10" = `10H` =
16 decimal, consistent with the table above (10H × 8 × 200H = 64 KB checks out).

**DISKCOPY utility.** Undocumented elsewhere in the TRM: `CALL Bank 5, 5FF0H` runs a
built-in whole-disk-copy program (with its own guided UI) — but only when **both** RAM
module slots are fully populated to 64 KB total, since it uses that RAM as an
intermediate buffer for a full disk side.

### 2.2 Logical-sector layout (§3.8.3(1))

| Logical sector | Area |
|---|---|
| 0 | Boot sector (`PC-1600-Filesystem.md` §5.1) |
| 1 | FAT |
| 2 | FAT (backup) — the ROM keeps it identical to sector 1 (observed on emulator disks) |
| 3–5 | Directory (3 sectors × 512 B ÷ 32 B = 48 entries) |
| 6–127 | Data (122 clusters) |

### 2.3 FAT (§3.8.3(3))

Byte 0 = format ID = **F2H** (for this floppy). Bytes 1–122 = one entry per cluster
(clusters 1–122, mapped to logical sectors 6–127):

- `00H` — free
- `01H`–`7AH` — in use; value = next cluster in the chain
- **`F0H` — last cluster of the file** *(note: the RAM-disk uses `FFH` for "last
  cluster", `PC-1600-Filesystem.md` §5.3 — the floppy uses `F0H`)*

### 2.4 IOCS routines (§3.8.4)

**Dispatch:** (1) set parameters; (2) IOCS number → **C**; (3) `CALL Bank 5, 4008H`. The
IOCS work area must be reserved first. **Drive number** (in `A`): `01H` = X drive, `02H`
= Y drive (two drives supported).

**Error code in `A`** (bit set = that error; `A = 00H` on success). Systemhandbuch ch. 13
gives noticeably more precise per-bit meanings than the TRM excerpt previously
transcribed here — kept as the authoritative reading, TRM-style wording in parens where
it differs:

| Bit | Meaning |
|---|---|
| 7 | no floppy in the drive |
| 6 | battery empty/low |
| 5 | disk write-protected (WP tab set) |
| 4 | track not found (head-seek error) |
| 3 | sector not found — disk not formatted |
| 2 | file-end exceeded during the operation |
| 1 | write or read error |
| 0 | hardware error / other |
| *(`A`=00H with CF/error flagged another way)* | verification error (`DVERIFY`/`HFVERIFY` mismatch) |

| Name | # | Function |
|---|---|---|
| DSKINIT | 80H | initialise the drive (A = drive number) |
| CNCTDRV | 81H | how many drives are connected |
| RESTORE | 82H | seek the head to track 0 (may prompt "set diskette for..." if none present) |
| FORMAT | 83H | format the disk |
| DREAD | 84H | read absolute sectors → `(HL)`. **B** = sector count (byte count transferred = count × `200H`); **D** = track number of the first track (`00`–`0FH`); **E** = number of the first sector (`00`–`07H`) |
| DWRITE | 85H | write absolute sectors from `(HL)`; params as `DREAD` |
| DVERIFY | 86H | compare sectors against `(HL)`; params as `DREAD` |
| GETDRVST | 87H | read drive status → `A`: b7 = drive motor off, b6 = no WP (valid only while motor on and disk in drive), b3 = disk in drive, b2 = disk was changed (valid only if b0 set), b0 = a disk operation is in progress |
| HFREAD | 88H | read 100H bytes (half a sector) from track **D**, sector **E**, → `(HL)` |
| HFVERIFY | 89H | compare 100H bytes against `(HL)`; params as `HFREAD` |

### 2.5 Power-on (§3.8.5)

When a drive is attached, the drive runs its own initialisation sequence at power-on
(details not transcribed).

### 2.6 Port-level command/status registers, 78H–7FH (Systemhandbuch Appendix 6)

The DREAD/DWRITE/etc. IOCS routines in §2.4 above are software wrappers around this raw
port interface — the CE-1600P side of the `IO7N`-decoded 70H–7FH range from §3.1.2/§3.1.6
(there described only at the bus-signal level: `D0–D7`/`A0–A2`/`CS0`/`WR`/`RD`). This is
the first source in this corpus to give the actual register meanings at those addresses.
70H–77H is a second, identical port block (mirrors 78H–7FH) — presumably for a second
drive unit, consistent with the two-drive (X/Y) model in §2.4.

| Addr | Op | Function |
|---|---|---|
| 78H | write | command register: `40H` = read, `60H` = write, `A0H` = format |
| 78H | read | motor/disk status: b7 = motor not yet up to speed, b6 = no write-protect, b3 = disk in drive |
| 79H | write | sector register |
| 7AH | write | motor control: b7 = motor on |
| 7AH | read | status: b6 = disk changed, b1 = ready, b0 = error (inverted) |
| 7BH | — | data read/write |
| 7CH–7FH | — | unused |

This is a much simpler abstraction than a raw FDC register set — consistent with §3.1's
own finding that the real FDC gate array lives *inside* the FDU-250 mechanism, reached
over its own 25-pin `CS0`/`A0–A2`/`D0–D7` bus (§3.1.2); this 78H–7FH block is the
CE-1600P-side command/status shim in front of that, which the IOCS routines in §2.4 talk
to directly.

## 3. Peripheral hardware (TRM Ch 8 / Service Manuals)

**Pending.** CE-1600P block diagram / port map (I/O 80–83H), CE-1620M / CE-1601E PROM
programmer, CE-1600L / CE-1601T, CE-1601L–CE-1605L, CE-160CA.

### 3.1 CE-1600F — floppy drive unit (Service Manual, pp. 98–104)

**Source:** `PC-1600_Service_Manual.pdf` pp. 98–104 (CE-1600F chapter, sections 1–8).
This is the electrical/mechanical counterpart to the logical IOCS layer in §2 above — it
describes the drive as seen from the CE-1600P side of the 50-pin cable, not the BASIC/
IOCS interface.

**Key architectural fact for emulation:** almost all of the "smarts" live *inside the
2.5″ drive mechanism itself* (branded **FDU-250**), not on the CE-1600F's own small
interface PCB. The FDC and its peripheral logic are a single 2700-gate gate array
inside the FDU-250, and the read/write amplifier is a second, separate LSI, also inside
the FDU-250 — both are low-voltage parts wired directly onto the bus so they can run off
a low-voltage supply. The CE-1600F's own interface board only adds:
1. a power-on-reset pulse generator (RC delay + diode, produces `REST` from `RSTN`), and
2. a regulated 5VC rail for the R/W-amp LSI, sourced from **Vp (the 6V battery line)**,
   not from Vcc — because Vcc can't supply the current headroom needed to drive it.

This means: a faithful emulation of the CE-1600F needs a model of the FDU-250's FDC
register behaviour (bus-visible via `CS0`/`WR`/`RD`/`A0`–`A2`/`D0`–`D7`), not a model of
discrete interface-board logic — the interface board is just power-sequencing glue.
**Not user-repairable**: Sharp's own service policy is to swap the whole unit if the
Section-7 test program reports a failure (no board-level parts replacement).

#### 3.1.1 Media / drive specs (§1, §5 "FDU-250")

| Property | Value |
|---|---|
| Media | 2.5″ (63.5mm) two-sided floppy disk |
| Drives | one drive per CE-1600F unit |
| Recording method | **GCR (4/5)** |
| Tracks | 16/side (48 TPI track density) |
| Sectors/track | 8 |
| Bytes/sector | 512 |
| Capacity | 64KB per side |
| Transfer speed | 250K bits/sec (25K bytes/sec) |
| Rotation speed | 270 RPM |
| Access time | one step: 80ms (track 0→15); restore 15→0: 170ms; settling: 50ms |
| Motor startup time | 0.5s |
| Power | 6VDC, supplied from the host unit (CE-1600P) over the cable; 2.5W consumption |
| Operating temp / humidity | 10–35°C, 20–80% RH (no condensation) |
| Physical size / weight | 96×122×39mm, 470g |
| Option | CE-1650F = 10-pack of blank 2.5″ two-sided disks |

**GCR (4/5) explained (§5 note):** each 8-bit data byte is split into two 4-bit
nibbles; each nibble is separately encoded onto a 5-bit code on the media. So one
8-bit byte occupies 10 encoded bits on disk — this is the "4/5" ratio. This is a
run-length-limited group code, *not* raw MFM/FM — an emulator that just stores decoded
sector bytes (which is enough for BASIC-level emulation) can ignore this, but it matters
if the disk is ever modeled at the flux/bitstream level.

**One-sided drive, two-sided media:** the drive head only accesses one side at a time
(§1 note: "though the floppy disk drive is for one-sided operation, both sides of the
media can be used") — the user must physically flip the disk to use side B, and the
Service Manual's own test procedure (§7-3) does exactly this: it formats/writes side A,
then has the operator flip the disk and format side B separately with its write-protect
tab set. This confirms the drive has no side-select signal in active use during normal
single-sided operation — consistent with the format-ID byte `F2H` in the FAT
(`PC-1600-Filesystem.md` / §2.3 above) not encoding a side.

#### 3.1.2 Block diagram (§3) — bus signals from the CE-1600P

Signals arriving over the 50-pin connector from the CE-1600P (i.e. from the printer,
which is the only way the floppy attaches — see §2 above): `D0–D7` (8-bit data bus),
`A0–A2` (3-bit register-select), `IO7N`, `WR`, `RD` (I/O control, 3 lines), `RSTN`
(active-low system reset), `Vcc` (+5V logic), `Vp` (+6V, the battery/motor rail).

Inside the CE-1600F, these become, on the FDU-250's own 25-pin connector: `D0–D7`,
`A0–A2`, **`CS0`** (chip-select, decoded from `IO7N`), `WR`, `RD`, `REST` (the
locally-generated reset pulse — see §3.1.3), `+5V`, `+6V`, **`5VB`** (a switched Vcc
tapped through a transistor, gated by the drive's own MOTOR-ON signal), and **`5VC`**
(the regulated R/W-amp supply, §3.1.4). The FDU-250 internally routes these into:
- the **FDC & LOGIC gate array** (2700-gate ASIC) → drives `WD`/`WG`/`RD` to the R/W amp
- the **R/W AMP LSI** → drives the physical read/write and erase heads
- the **SOLENOID CONTROL circuit** → drives a solenoid, used with a cam for head seeking
  (there is no stepper motor — a single motor drives both disk rotation, via a belt, and
  head positioning, via the solenoid/cam)
- the **MOTOR CONTROL circuit** → drives the spindle motor, with an FG (frequency
  generator) tachometer on the motor for speed feedback

#### 3.1.3 Power-on-reset circuit (§4-2, Fig. 1/2)

`RSTN` (active-low, from the CE-1600P) drives a simple RC network: a pull-up resistor
**R5** to Vcc, charging capacitor **C3** to ground, with diode **D4** placed to
discharge C3's charge back through to the Vcc line the moment Vcc drops (so the circuit
re-arms cleanly on power-cycle rather than needing C3 to bleed down passively). The
node between R5/C3/D4 (point "A" in the schematic) is fed out as `REST` to the FDU-250.
Fig. 2 shows the timing: when Vcc rises, point A follows it with a **delay**, and `REST`
is held low (asserted) for a "reset period" that spans that delay before releasing —
i.e. this is a classic power-on-reset delay line whose only job is to hold the FDU-250's
internal FDC gate array in standby until Vcc has stabilized, avoiding a race/glitch in
the FDC at power-up.

#### 3.1.4 Regulated 5VC supply for the R/W amp (§4-3, Fig. 3)

The R/W-amp LSI's 5VC rail is generated **from Vp (+6V, the battery line)**, not from
Vcc — because Vcc alone can't supply enough current headroom for the amp under low-
battery conditions. A three-transistor regulator (**TR1/TR2/TR3**) plus a Schottky diode
**D1** produces 5VC held **0.2–0.3V above** a reference `5VB` (itself a switched-Vcc
signal gated on/off by the drive's own MOTOR-ON control, so the amp's supply only comes
up when the drive is spinning). D1 is specifically a Schottky part chosen for its low
forward-voltage drop, to keep that 0.2–0.3V margin accurate. Test procedure §7-4/7-5
double-checks this in the field: probe the "5VC voltage test location" pad on the
interface PCB and confirm 4.5–5.5VDC while the drive's green access LED is lit, and 0V
once it goes out.

#### 3.1.5 Interface-board component list (§6, §8 parts list)

Discrete parts on the CE-1600F's own small interface PCB (i.e. *not* inside the FDU-250
mechanism): transistors **TR1 = 2SA1286** (PNP), **TR2/TR3 = 2SC2021** (NPN pair);
diodes **D1 = 1S1588L1** (the reset-bypass diode, silkscreened elsewhere as "D4" in the
schematic — Fig. 1/Fig. 3 use different reference labels for what the parts list
consolidates), **D4 = 1SS108** (small-signal reset diode); resistors R1=100KΩ,
R2=470KΩ, R3=4.7KΩ, R4=560Ω, R5=56KΩ; capacitors C1=10µF (tantalum), C2=0.1µF, C3=0.1µF;
an inductor L1=1S158EL1/0.1µH; a status/access **LED = VHPGL9EG2** (green, phototransistor
package) driven off the FDC logic to indicate drive-active; connectors **CON1 = 50-pin**
(to the CE-1600P) and **CON2 = 25-pin** (to the FDU-250 mechanism). This confirms §3.1.2's
claim that the interface board is minimal glue logic — there is no FDC/controller chip
in this parts list at all, only power-sequencing discretes and a status LED.

#### 3.1.6 Connector pinouts

**CON1 (50-pin, CE-1600P ↔ CE-1600F).** Pin numbers from the CE-1600P side: TRM
§9.2(1) CE-1600P Circuit Diagram (printed p.268), the "to CE-1600F (50pin F)" table. It
is legible in a sharp photo of the printed page. The Service Manual's CE-1600F schematic
gives the same signal names but is hard to read at the pin level.

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | D7 | 26 | INTF̄ |
| 2 | D6 | 27 | VGG |
| 3 | D5 | 28 | M1̄ |
| 4 | D4 | 29 | NC |
| 5 | D3 | 30 | PT |
| 6 | D2 | 31 | PU |
| 7 | D1 | 32 | PVOUT |
| 8 | D0 | 33 | FGND |
| 9 | RSTN | 34 | FGND |
| 10 | A7 | 35 | A8 |
| 11 | A6 | 36 | A9 |
| 12 | A5 | 37 | A10 |
| 13 | A4 | 38 | A11 |
| 14 | A3 | 39 | A12 |
| 15 | A2 | 40 | A13 |
| 16 | A1 | 41 | A14 |
| 17 | A0 | 42 | A15 |
| 18 | MREQ | 43 | BFO |
| 19 | IO7N | 44 | IORQ |
| 20 | WR̄ | 45 | WAIT |
| 21 | RD̄ | 46 | ELH̄ |
| 22 | GND | 47 | GND |
| 23 | GND | 48 | Vp |
| 24 | Vcc | 49 | Vp |
| 25 | Vcc | 50 | Vp |

So the 50-pin connector carries the whole Z-80 bus (A0–A15, MREQ, IORQ, M1, WAIT, the
PT/PU/PVOUT bank bits, ELH, BFO), not just the subset the CE-1600F uses. The CE-1600F
uses `D0–D7`, `A0–A2`, `IO7N`, `WR`, `RD`, `RSTN` and `INTF` (its interrupt back to the
CE-1600P), plus `Vp` ×3, `Vcc` ×2 and `GND` ×3, matching §3.1.2. `IO7N` and `RSTN` come
from the CE-1600P gate array (pins 42/41, §1.2.2). The other lines are passed straight
through from the 60-pin bus.

**CON2 (25-pin, to the FDU-250 mechanism):** `+6V`, `+5V`, `GND` (×2), `5VC`, `5VB`,
`RD`, `CS0`, `A0–A2`, `IRQ` (×2 — appears twice in the table), `DACK`, `D0–D7`, `REST`,
`GND`. The presence of `IRQ`/`DACK` lines on this connector (not listed among the
CON1/50-pin signals from the CE-1600P) suggests the FDU-250's internal FDC gate array
has interrupt/DMA-style handshake pins that are either unused or absorbed by the
interface board's glue logic rather than passed through to the CE-1600P — worth
confirming later if a cycle-accurate emulation is attempted.

#### 3.1.7 Test-program behaviour (§7) — useful as a black-box functional spec

Since there's no register-level programming reference for the FDC in the Service
Manual, the Section-7 field-test procedure doubles as a black-box description of what
the drive must do, useful for validating emulator behavior:

- **Test items, in order:** (1) motor on/off + ready-check, (2) head seek, (3) sector
  read/write, (4) sense-media (read+verify, write, read+verify again), (5) sense
  write-protect. Results surface through the IOCS error-code bits already documented in
  §2.4 above.
- **Test flow (flowchart, §7-1):** motor on → poll `READY?` → on error, abort with
  indication; else read data → verify → write data → read back → verify → check
  write-protect → indication. Matches the IOCS routine list in §2.4 (`DSKINIT`,
  `GETDRVST`, `DREAD`/`DWRITE`/`DVERIFY`).
- **Media prep (§7-3):** run `LOAD"X:WMEDIA"` from a test-program disk, then `RUN`; the
  program drives the operator through inserting a **blank** CE-1650F disk side A,
  displays progress ("MEDIA INITIALIZE NOW" ~20s, "WRITE DATA NOW" ~3s, "DATA READ NOW"
  ~7s, each with the green access LED lit for that duration), then prompts to flip the
  disk and format side B separately (write-protected afterwards) — this is the
  authoritative timing reference for how long a real format/write/verify pass takes on
  real hardware, useful for pacing an emulator's I/O completion timing realistically.
- **Operational test (§7-4):** with the real CE-1600F attached, `LOAD"X:CE-1600F"` then
  `RUN` exercises items 1–4 continuously and reports `OK` or an error + printer dump;
  item 5 (write-protect) is a separate manual step using a WP-tabbed side-B disk.
