# Storage

Where programs and data are kept: the RAM disk and the floppy (file system, FAT, floppy IOCS), and how `LOAD`/`SAVE`/`CLOAD` and friends are routed per MODE and peripheral.

**See also:** `../Data-Formats/` for the tape, WAV and serial transfer formats, `../Peripherals/` for the printer, `../Memory/` for where a loaded program ends up.

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [PC-1600-Filesystem.md](PC-1600-Filesystem.md) | 1600 | cited | 24 | File header, FCB, file IOCS, RAM-disk and floppy FAT layout, disk buffer work area. |
| [PC-1600-Floppy-CE-1600F.md](PC-1600-Floppy-CE-1600F.md) | 1600 | draft | 19 | Floppy IOCS, disk geometry, logical sectors, FAT, port-level registers 78-7FH, drive-unit hardware. |
| [PC-1600-Load-Save-Matrix.md](PC-1600-Load-Save-Matrix.md) | 1600 | ROM-verified | 10 | Which load/save command works per MODE x peripheral; how the ROM routes tokens; where results land. |
<!-- files:end -->
