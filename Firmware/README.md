# Firmware

The ROM and what it does: IOCS routines, jump tables, system variables and pointers, the BASIC tokenizer, MODE 0/1 behaviour.

- Routine and table *contents* are in the annotated disassemblies (`PC-1600-ROM`, `PC-1500-ROM`, Jeff Birt's PC-1500 disassembly), not here; `PC-1600-ROM-Disassembly.md` and `PC-1500-ROM-Overview.md` explain how to read them.
- BASIC language references are in SharpBasicReference.

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [PC-1500-BASIC-Pointers.md](PC-1500-BASIC-Pointers.md) | 1500 | draft | 9 | ROM pointers and system variables of the BASIC interpreter. |
| [PC-1500-Peripheral-Commands.md](PC-1500-Peripheral-Commands.md) | 1500 | draft | 6 | CE-150/CE-158 peripheral token table (overlaps SharpBasicReference Token-Mapping-Analysis). |
| [PC-1500-ROM-Overview.md](PC-1500-ROM-Overview.md) | 1500 | draft | 7 | Guide to the structure of the PC-1500 ROM disassembly. |
| [PC-1500-ROM-Routines.md](PC-1500-ROM-Routines.md) | 1500 | draft | 26 | PC-1500 ROM subroutine reference: addresses, calling conventions, register use. |
| [PC-1500-System-Variables.md](PC-1500-System-Variables.md) | 1500 | draft | 20 | PC-1500 system reference: memory layout, system variables, number formats (from the former LH5801 guide). |
| [PC-1500-Tokenizer.md](PC-1500-Tokenizer.md) | 1500 | draft | 6 | How the ROM tokenizes BASIC input at $F957. |
| [PC-1600-IOCS.md](PC-1600-IOCS.md) | 1600 | draft | 7 | IOCS calling conventions and the master routine index (section 3.1-3.13). |
| [PC-1600-MODE0-MODE1.md](PC-1600-MODE0-MODE1.md) | 1600 | ROM-verified | 18 | Everything the MODE 1 flag switches, located in the ROM; XCALL/XPEEK/XPOKE; ERROR 110 analysis. |
| [PC-1600-ROM-Disassembly.md](PC-1600-ROM-Disassembly.md) | 1600 | cited | 3 | Pointer to the real-hardware ROM dumps and their annotated disassemblies (PC-1600-ROM). |
| [PC-1600-ROM-Jump-Table.md](PC-1600-ROM-Jump-Table.md) | 1600 | cited | 14 | Fixed ROM jump table 0000H-0312H. |
| [PC-1600-Transparent-Banking.md](PC-1600-Transparent-Banking.md) | 1600 | cited | 6 | Firmware view of banking: system calls, RST shortcuts, ROM module headers, slot management, boot sequence. |
| [PC-1600-Work-Area-Map.md](PC-1600-Work-Area-Map.md) | 1600 | cited | 36 | F000H-FFFFH BASIC/IOCS work area: structure, PTR1-PTRG, every named variable by subsystem. |
<!-- files:end -->
