# Open Questions

Contradictions, unknowns and missing documents, with a proposed test where one exists. The detail stays in the
document that owns the question (its `Open items`, `TODO` or `Open questions` section); this page is the overview. When
a question is settled, strike it in the owning document and remove it here.

## Missing documents (not started)

| Topic | What is missing | Where the facts are today |
|---|---|---|
| Machines | PC-1500 machine overview; a model matrix (PC-1500, PC-1500A, PC-1600, ROM variants) | `CPU/LH5801-Architecture.md`, `Memory/PC-1500-Address-Decoding.md` |
| Display | PC-1500 display; PC-1600 character-code table (TRM 10.1) | `Programming/prompts/PC-1500-BASIC-Prompt.md`, `Firmware/PC-1500-System-Variables.md` |
| IO-Ports | PC-1500 I/O ports (LH5810 as used on the CE-150) | `Peripherals/PC-1500-CE-150-Hardware.md` |
| Serial-Parallel | CE-158 interface (RS-232C, Centronics, cassette) | SharpBasicReference `CE-158-Reference.md`, `Firmware/PC-1500-Peripheral-Commands.md` |
| Keyboard | PC-1600 key-code value table (TRM 10.2); not needed for emulation | |
| Expansion | PC-1600 expansion bus electrical and timing detail (stub) | `Expansion/PC-1600-Connectors.md` |
| Programming | Z-80 toolchain and worked examples; PC-1600 BASIC authoring prompt | `Programming/PC-1600-Z80-Assembly-Guide.md` ("Still to write") |
| Sources | The PC-1500 sources have IDs in `sources/sources.yaml` now; the PC-1500 documents still cite them in prose and could move to `[S:<ID> p.<n>]` | |

The scans are catalogued with their local paths in `sources/sources.yaml` (checked 2026-11-25).

## Conflicts between sources

| Question | Detail | Test |
|---|---|---|
| Work-area readings | `F05EH`, `F05FH`/`F060H`, `F079H` bits 4/7 and the plotter ranges `F180H`-`F195H`, `F9E0H`-`F9F9H` have two or three readings across the TRM and Systemhandbuch Appendix 7. `Firmware/PC-1600-Work-Area-Map.md` ("Open items"). | Check against the ROM disassembly. |
| 128 KB floppy geometry | First data sector `0008H` (Systemhandbuch) or `000BH` (ROM dump). `Storage/PC-1600-Filesystem.md` ("Open items"). | Read the geometry table in the ROM. |
| Media-ID table pointer | `4242H` vs the ROM table's own `5006H` base. Same document. | ROM. |
| Keyboard translation tables | Pointer-byte roles differ between 3.2.2 and 3.2.6. `Keyboard/PC-1600-Keyboard.md` ("TODO"). | ROM. |
| DSTB timing | TRM figure (13 / 26 us) matches the ROM's PR2/PR3 only at K=1; the ROM uses K=2 (27.7 / 52.1 us). `Serial-Parallel/PC-1600-CPC-TC8576.md` section 12. | Logic-analyser capture of DSTB. |
| MSK (1AH) b7: RD or CL1 | TRM Appendix 6 names it RD; the CE-150 tape code needs it to follow the serial clock (CL1), and a real MODE 1 CSAVE through the CE-150 works. `IO-Ports/PC-1600-IO-Ports.md` §2.1, §2.7. | Read 1AH in a loop on hardware while the serial clock runs (after a 14H write). |
| TC8576 data-sheet slips | Five slips in the Toshiba sheet; the reading used is given in the document, same section. | |

## Unknowns by topic

- **CPU:** whether I/O cycles get an additional wait on top of the one per M1 cycle (test: a port-heavy BEEP-style loop timed on hardware); undocumented Z-80 opcodes and flag bits 3 and 5 (NMOS, CMOS Z84C00 or neither); `IN r,(C)` and block-I/O address-bus contents; interrupt causes bit 3 ("from LH-5801") and bit 5 ("key input"); `DD`/`FD` edge cases. `CPU/PC-1600-SC7852-Z80.md` section 12.
- **I/O ports:** edge versus level behaviour of 32H/35H (bits 0-3, 5-7); ADC range and scaling for the analog inputs; the F register (17H) tone path while serial data is sent; the per-port decode of 50-5FH on real hardware. `IO-Ports/PC-1600-IO-Ports.md` ("TODO").
- **Display:** which segments of the Japanese romaji/kana indicators X35 and X59 light; how the status-line Y6f / X49-X64 wiring is driven in software; IC2/IC3 ADC pin levels; `LINE`/`BOX` entry address versus the `CALL &0124` example. `Display/PC-1600-Display-Hardware.md` ("TODO").
- **Storage:** `DIRSFT`/`CLSSFT` meaning; whether `SET DMA` is a real DMA address; attribute-byte b1 (`"I"`). `Storage/PC-1600-Filesystem.md` ("Open items").
- **Memory:** program-area behaviour at bank boundaries (`BLOAD` of a file larger than one bank, `NEW` vs `NEW0` inside a program module, whether S0's header moves to bank 2). The tests that were run are in `sources/evidence/program-area-tests/`.
- **Firmware:** the F9E0H-F9EFH overload (which alias is live in which printer mode); the `CRSRY`/`CRSRX` labelling; what F000H-F05BH holds beyond PTR1-PTRG. `Firmware/PC-1600-Work-Area-Map.md`.
- **Machines:** the power-on sequence (TRM 3.5) and 5.14 are not yet transcribed into `Machines/PC-1600-Machine-Overview.md`.

## Housekeeping

- Statuses of the PC-1500 documents were assigned from what each document says about its own sources; review them when the
  PC-1500 sources are catalogued.
- `Firmware/PC-1500-Peripheral-Commands.md` overlaps SharpBasicReference's `Token-Mapping-Analysis.md`: keep only what it
  has beyond that, or drop it.
- `Programming/prompts/PC-1500-BASIC-Prompt.md` has two sections numbered 20 and no section 1; renumber when the prompt is next
  edited (the numbers are referenced inside the prompt).
