# PC-1600 — loading and saving: MODE × periphery × command

Which program/data transfer commands work on the PC-1600, per MODE (0 = native, 1 =
PC-1500 compatible) and per attached peripheral, and where the result ends up. Derived
from the fully commented "new" ROM disassembly (`~/Development/sharp/pc1600/disasm/rom/pc1600/new/`,
CE-1600P banks in `disasm/rom/ce1600p/new/`). Bank names as there: P0-B0, P1-B0, P1-B3, rom3b =
P1-B3B, P2-B6, B5 = the CE-1600P ROM's bank 5, LH5803 = the LH-5803's own ROM. CE-158 addresses
are from its annotated ROM (`~/Development/sharp/pc1500/disasm/rom/ce158/CE-158-LOW.asm`).

Assumption throughout: the memory configuration allows MODE 1 (no more than 16 KB base
memory added), so the configuration form of ERROR 110 doesn't occur. Note that error
110 (6EH) has a **second meaning**, "command needs MODE 1" / "not in MODE 1"; that form
appears in the tables.

## 1. How the ROM routes the commands

- **`LOAD`/`SAVE`/`BLOAD`/`BSAVE`** are built-in keywords (tokens F295H/F299H/F290H/F291H,
  handlers in rom3b). None of them tests MODE.
- **The cassette keywords** `CLOAD` F089H, `CSAVE` F095H, `MERGE` F08FH, `CHAIN` F0B2H are
  the PC-1500 CE-150 token values. The built-in token table (P2-B6 `B6DEH`) holds only
  their names, with bank byte 80H (no handler). The token lookup `COMMADR` (P0-B0 `112FH`)
  then tries, in this order:
  1. for F0xxH tokens, if `OPN` selected a PC-1500 device (`OPNDV` F9D1H ≥ 40H and ≠ 60H,
     e.g. `OPN "CMT"` = 5CH): the PC-1500 tables first; if it selected a module device
     (e.g. `OPN "CAS1:"` = 0BH → module 0DH, the cassette module): that module's table
     first. The default (`OPNDV` = 60H, LCD) skips this step;
  2. the built-in table (names only for these tokens, so the search goes on);
  3. the ROM module tables — the CE-1600P cassette module (B5 `6000H`, token table
     `6024H`) has handlers for `CHAIN`, `CLOAD`, `CSAVE`, `MERGE`, `RMT` and F2AEH/F2AFH;
  4. the PC-1500 peripheral tables through the LH-5803 (`TOK1500`, P1-B3 `5DF6H` →
     LH5803 `E043H`): the CE-150 / CE-158 ROMs. Execution goes through `EXCOMM1500`
     (P1-B3 `5E1DH`); the LH5803's `X_CHKTOK` (`$CDDD`) refuses `CSAVE`, `CLOAD`,
     `MERGE`, `CHAIN` and `LLIST` (list at `$CE3B`) in MODE 0 with 6EH. `EXCOMM1500`
     likewise refuses the CE-158's `TERMINAL`/`DTE` (E883H/E884H) in MODE 0.

  So with a CE-1600P attached, it takes the cassette keywords in both MODEs.
- **`PRINT #…` / `INPUT #…`** (rom3b `ROUTEIO` `7E91H`): `#-0`/`#-1` or `#` + a
  non-digit becomes token **F2AEH** (`PRINT`) / **F2AFH** (`INPUT`) and goes to the ROM
  modules when the cassette module is present (ROM4MAP b3 / ROM6MAP b2). Otherwise it
  goes on as `PRINT`/`INPUT` (F097H/F091H) to the PC-1500 tables only. F097H/F091H are
  not on the LH5803's MODE-1 list. `#1`…`#9` are file numbers (native files).
- **The CE-1600P cassette driver picks the tape format from MODE alone** (`BMODE` F1BCH
  b6, `IS1500MODE` B5 `6668H`): MODE 1 = PC-1500 bit encoding, A0H sync, 32-byte header;
  MODE 0 = native. The `-1` in `CLOAD -1` / `CSAVE -1` is parsed and skipped
  (`ISMINUS1` `77F6H`). On the CE-150, `-1` selects the second recorder (REM 1).

## 2. MODE 0

| Command | No periphery | CE-1600P (+CE-1600F) | CE-150 | CE-158 |
|---|---|---|---|---|
| `SAVE` / `LOAD`, `BSAVE` / `BLOAD` | ✓ native: `S1:`/`S2:` RAM disk, `COM1:`/`COM2:` | ✓ as before, plus `CAS:` (cassette module FILE functions) and `X:`/`Y:` (floppy module) | ✓ as "no periphery" | ✓ as "no periphery" — the built-in COM ports, not the CE-158 |
| `CLOAD`, `CLOAD?`, `MERGE`, `CHAIN`, `CSAVE` | — no handler | ✓ native tape format | ✗ 110 (`X_CHKTOK`) | ✗ 110 |
| `CLOAD M` / `CSAVE M` | — | ✓ native tape format | ✗ 110 | ✗ 110 |
| `PRINT#` / `INPUT#` to tape | — | ✓ native (F2AEH/F2AFH) | routed to the CE-150, standard variables only (LH5803 `P_VARNAME` guard) ⚠ | routed to the CE-158 if CO/CI is declared ⚠ |
| `CSAVEa/r`, `CLOADa/r`, `MERGEa` | — | — | — | ✗ 110, assuming they are the `CSAVE`/`CLOAD`/`MERGE` tokens plus a suffix |

## 3. MODE 1

| Command | No periphery | CE-1600P (+CE-1600F) | CE-150 | CE-158 |
|---|---|---|---|---|
| `SAVE` / `LOAD`, `BSAVE` / `BLOAD` | ✓ native, no MODE check | ✓; `CAS:` untested ⚠ (the low-level tape routines switch format on MODE) | ✓ | ✓ |
| `CLOAD`, `CLOAD?`, `MERGE`, `CHAIN` | — | ✓ **PC-1500 tape format** (`K_CLOAD` B5 `6974H`, `CHAIN` `68FFH`, `MERGE` `6969H`) | ✓ CE-150 ROM on the LH-5803, PC-1500 format | ✓ `CLOAD`/`MERGE` over RS-232 once CI is declared ⚠ |
| `CSAVE` | — | ✗ 110 (`K_CSAVE` B5 `66A0H`) | ✓ | ✓ once CO is declared ⚠ |
| `CLOAD M` | — | ✓ PC-1500 ML tape | ✓ | ✓ over RS-232 once CI is declared: the CE-158's `CLOAD` entry parses the `r`, `M` and `a` suffixes (CE-158 ROM `90C8H`, `M` at `90D5H`) ⚠ |
| `CSAVE M` | — | ✗ 110 (inside `K_CSAVE`, after the MODE check) | ✓ | `CSAVE` (`90BBH`) shares the suffix parser, so `M` is accepted; the save path is not traced ⚠ |
| `PRINT#-1` (F2AEH) | — | ✗ 110 (B5 `6F35H`) | ✓ | CE-158 `PRINT#` once CO is declared |
| `INPUT#-1` (F2AFH) | — | ✓ per the ROM (B5 `6F31H`, PC-1500 header variant); the TRM says data can't be loaded in MODE 1 through the CE-1600P ⚠ | ✓ | CE-158 `INPUT#` once CI is declared |
| `CSAVEa/r`, `CLOADa/r`, `MERGEa` | — | — | — | ✓ once CO/CI is declared ⚠ |

✓ = handled; ✗ 110 = refused with error 110 (6EH); — = no handler for that
configuration; ⚠ = follows from the ROM routing but not run on a machine.

## 4. Where the result ends up

- **Native `LOAD`** (rom3b `K_LOAD` `6E22H`): the file's first byte decides the format —
  FFH + a header of type 21H is tokenized binary (`LOADFMT` `6F24H`), anything else is
  ASCII and is tokenized as PC-1600 BASIC. Target: the program area `TITLE` selects
  (S0/S1/S2, `PRGRANGE` `71B3H`); the end bookkeeping is `LOADEND` `70E1H`
  (`PC-1600-Work-Area-Map.md` §3.5). A CE-158 (27-byte) header doesn't start with FFH,
  so it is taken for text and fails. There is no PC-1500 path in `LOAD`.
- **`BLOAD`** (rom3b `7360H`): header FFH, type 10H; loads to the header's bank and
  address, or the `#bank,addr` given; auto-runs when the header has an exec address.
- **CE-1600P `CLOAD`/`CLOAD M`**: MODE 0 — the native tape header; MODE 1 — the address
  in the PC-1500 header (F239H, high byte first), unconverted, into the single program
  area MODE 1 leaves (`PC15MAP`, P0-B0 `1676H`). End bookkeeping `CASSETEND` (B5
  `74D3H`), then `PRGADR` and `BASPARES`.
- **CE-150 / CE-158 (MODE 1)**: the PC-1500 ROM code on the LH-5803 writes the pointers
  it shares with the Z-80 (LH5803 7865H = Z-80 F865H, …); `EXCOMM1500` then calls
  `PRGADR` (P1-B3 `5E49H`). F02CH is not written on this path; MODE 1's single ≤ 16 KB
  area doesn't cross a bank, so it needn't be.
- **PC-1500 machine code** (a MODE 1 `CLOAD M`) carries LH-5803 addresses; the Z-80 sees
  them at +8000H (`PC-1600-CPU-LH5803-Compat.md`).
- **No token conversion anywhere.** A PC-1500 program keeps its token values; the
  PC-1600 shows the same token under its own name (the TRM's "auto-rename" on cassette
  load: PC-1500 `CALL` token = PC-1600 `XCALL`). `LCURSOR` is the one name the TRM says
  must be changed by hand.

## 5. Consequences for a direct loader (an emulator that pokes a program in)

- **The periphery doesn't matter.** A peripheral is only the way in; memory ends up
  the same whichever way the program arrived. A loader that skips the transport has no
  reason to look at what is attached.
- **MODE matters** for two things:
  - **which file families are legitimate:** PC-1600 files load in both MODEs (`LOAD` has
    no MODE check); PC-1500 files (CE-158 header, PC-1500 tape image) reach a PC-1600
    only in MODE 1;
  - **where the program goes:** MODE 1 narrows the program area to one (`PC15MAP`).
    A loader that reads the live `ADTBL`/descriptors follows this by itself.
- **The header alone is not enough.** It says *what* the file is (family; kind: BASIC
  21H, ML 10H, RESERVE, data). *Whether* and *where* it can go comes from the live
  machine: MODE, `TITLE`, the slot descriptors, the `NEW` reserve. That is also how the
  ROM does it (`LOADFMT` for the type, `PRGRANGE` for the target). A `.bas` listing or a
  headerless `.bin` has no header at all.

## 6. Open questions

1. **Keyword names for a text listing in MODE 1.** The ROM's ASCII `LOAD` and keyboard
   entry use the PC-1600 names (you type `XCALL`; TRM "rename by hand"). The CE-158's
   `CLOADa` probably tokenizes on the LH-5803 with the PC-1500 names (`CALL`) — not
   verified.
2. **Are all shared tokens identical?** The ROM assumes so (no conversion on `CLOAD`);
   not checked token by token.
3. **`INPUT#-1` in MODE 1 through the CE-1600P:** allowed by the ROM, excluded by the
   TRM.
4. **`SAVE`/`LOAD "CAS:"` in MODE 1:** the FILE functions of the cassette module call
   tape routines that switch format on MODE; not traced.
5. **CE-158 CO/CI on the PC-1600:** whether the CE-158's own `SETDEV` (E886H) is
   reachable at all while the PC-1600 has a native `SETDEV`.
6. **CE-150 / CE-158 `PRINT#`/`INPUT#` in MODE 0:** routed to the peripheral, not
   refused by the LH5803; not run.
