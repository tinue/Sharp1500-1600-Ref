# Sources

What the documents in this repository are built from. The machine-readable catalogue is
[`sources/sources.yaml`](sources/sources.yaml); each entry has an ID that documents cite as `[S:<ID> p.<n>]`.
Source rank and the handling of conflicts are in [`CONVENTIONS.md`](CONVENTIONS.md).

## Primary sources

| ID | What | Rank |
|---|---|---|
| `ROM-PC1600`, `ROM-PC1500` | ROM dumps from real hardware and their annotated disassemblies (repositories `PC-1600-ROM`, `PC-1500-ROM`, plus Jeff Birt's PC-1500 disassembly). Since September 2026 new PC-1600 facts are checked against the ROM code. | 1 |
| `TRM-1600`, `SYSHB-1600` | The PC-1600 Technical Reference Manual (English) and its German edition, the *System-Handbuch* (Holtkötter 1987, same section numbers). Memory map, IOCS, BASIC interpreter, work area, hardware chapter, Z-80 mnemonic tables. The German scan is cleaner; most transcription was read from it. | 2 |
| `OPMAN-1600` | English user manual (PDF page = printed + 10). | 2 |
| `SM-1600`, `SM-CE1601M` | Service manuals: architecture, schematics, the LR38041 gate array, slot pinouts, CE-1600P and CE-1600F hardware. | 2 |
| `BEDIEN-1600` | German user manual: memory map (App. D), machine-language commands, PC-1500 compatibility (App. E/H). | 2 |
| `TOSHIBA-TC8576`, `HITACHI-HD61102`, `HITACHI-HD61203` | Chip data sheets: the UART/Centronics CPC and the LCD controllers. | 2 |
| `SOFT-INFO` | Sharp SOFTWARE-INFO bulletins 1987-88: dealer errata and tips. Primary Sharp material, but advisory rather than reference-grade. | 2 |
| `BAUM-1600` | Winfried Baum's *PC-1600 Systemhandbuch* (Fischel): a separate third-party book despite the shared title. | 3 |
| `OHEIMB-1600` | David von Oheimb, *Das Systemhandbuch für den PC-1600* (Ditze 1987): a third third-party book with the same name, its own chapters and the I/O, System-RAM and jump-table appendices. Cited by older documents as `SHARP-PC1600-Systemhandbuch.pdf`. | 3 |
| `DITZE-TIPS-1600` | Klaus Ditze, *Programme, Tips & Tricks für den PC-1600* (1987): listings, the disk-MERGE and DISKCOPY routines. | 3 |
| `TRM-1500`, `SM-1500`, `SM-CE150`, `SM-CE161` | PC-1500 Technical Reference Manual and the PC-1500, CE-150 and CE-161 service manuals. | 2 |
| `SCHLIEKER-INTERN`, `SCHLIEKER-ROM` | H.-G. Schlieker's commented PC-1500 ROM (*PC-1500 Intern*) and *ROM-Unterprogramme* (1983). | 3 |
| `ELLIOTT-PC2` | Bruce Elliott's PC-2 assembly-language series, TRS-80 Microcomputer News 1983-84. | 4 |
| `SUPERRAM` | The third-party superRAM manual. | 4 |

The chapter 9 circuit diagrams of the TRM are too coarse in the PDF scan; photos of the printed pages (9.1(1) F.P.C.
p.264, 9.1(4) Connector p.267, 9.2(1) CE-1600P p.268) were used instead. The PC-1500 documents rest on the PC-1500
Technical Reference Manual, the CE-150 Service Manual and the ROM code. Their sources now have IDs (above), but the
documents still cite them in prose.

## Independent validation (`EMU-POCKEMUL`)

PockEmul, a long-running multi-pocket-computer emulator with a working PC-1600 implementation, is **not a primary
source**. It was an executable reference used to cross-check the memory and bank-switching model and to resolve points
the manuals leave ambiguous (keyboard strobe/sense binding, LCD-controller port decode). One of its answers was wrong:
it models the SC-7852 with no wait states, while real-hardware BEEP pitch shows one wait per M1 cycle
([`CPU/PC-1600-SC7852-Z80.md`](CPU/PC-1600-SC7852-Z80.md) 2.3). Where a fact rests on it alone, the document says so.
The scans are not in git.
