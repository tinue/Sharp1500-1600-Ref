# PC-1600 — MODE 0 vs MODE 1: what the ROM actually switches

Everything the `MODE 1` flag changes, located in the ROM, plus the partial MODE 1 that
`POKE &F1BC,PEEK(&F1BC) OR 64` produces. Derived from the "new" ROM disassembly
(`~/Development/sharp/pc1600/disasm/rom/pc1600/new/`, CE-1600P banks in
`disasm/rom/ce1600p/new/`). Bank names as there: P0-B0, P1-B0, P1-B3, rom3b = P1-B3B, P2-B6,
B4/B5 = the CE-1600P ROM's banks, LH5803 = the LH-5803's own ROM (LH-5803-view addresses,
`$xxxx`). Points marked ✔ were also run on the real ROMs in Calc-U-1600's headless
emulator. The user-level version of this material is the "MODE 0 and MODE 1 in detail"
section of `SharpBasicReference/PC-1600-BASIC-Reference.md`.

---

## 1. The model

- **The BASIC interpreter is on the Z-80 in both modes.** MODE 1 doesn't hand BASIC to
  the LH-5803.
- **MODE 1 is one flag:** `BMODE` (F1BCH) **b6**. The other `BMODE` bits are unrelated:
  - b7 = port 1FH bit 3, the single-byte (kanji) mode;
  - b1 = BREAK OFF;
  - b0 = error routine running.
- **The `MODE` command** (`K_MODE`, P1-B0 `5696H`) sets b6 and also does three more things:
  - It sets up the memory layout through `RAMODSET` (P0-B0 `163FH`) → `PC15MAP` (`1676H`).
  - It selects the PC-1500 character set (`CGMODE`).
  - In the `MODE 1` branch it sets `LWIDTHW` (FE18H) := 26, clears `DSPMODE` (FE42H) b1–2
    and calls `SETANK` and `SYMCLR2`.
- **If b6 already matches the requested mode**, `K_MODE` returns at once. `MODE 1` typed
  while b6 is set does nothing and gives no error ✔.
- **The LH-5803 runs one PC-1500 statement or function per `CALLH`** (P1-B3 `CALLH_B3`
  `5BF4H`) whenever a token has no Z-80 handler. This happens **in both modes**, through:
  - `EXCOMM1500` (P1-B3 `5E1DH`) → LH5803 `X_EXCOMM` `$E023` for statements;
  - `FUNC` → `X_FUNC` `$E02D` for functions.

  `CALLH` doesn't touch port 31H.

## 2. Token identity and handler routing

Decoded from the built-in token table `TOKTAB` (P2-B6 `B6DEH`). Bank byte `80H` means the
table has the name only and no handler.

| Token | PC-1600 name | PC-1500 name | Built-in handler |
|---|---|---|---|
| F18AH | `XCALL` | `CALL` | none → LH5803 `BCMD_CALL` `$CCF5` |
| F1A1H / F1A0H | `XPOKE` / `XPOKE#` | `POKE` / `POKE#` | none → LH5803 `BCMD_POKE` `$CCC1` / `$CCC2` |
| F16FH / F16EH | `XPEEK` / `XPEEK#` | `PEEK` / `PEEK#` | `0202H` (FUNC) → LH5803 `BCMD_PEEK_1600` `$DC9A` |
| F282H / F28CH / F26DH | `CALL` / `POKE` / `PEEK` | — | native Z-80 |
| E882H, E886H, E880H, E859H | `SETCOM`, `SETDEV`, `OUTSTAT`, `INSTAT` | CE-158, same tokens | native (rom3b `4063H`–`4072H`). Without a `"COM…:"` device, `GETCOMDEV` fails → `NOTHERE` (rom3b `7D02H`) → the ROM modules / PC-1500 tables. `INSTAT` also passes on if `F88CH` = 0 |
| F0B9H / F0B8H | `LPRINT` / `LLIST` | CE-150 | native `LPRINTB` / `LLISTB` (rom3b `7E52H`/`7E5EH`): the COM port if `OPN` redirected output there (`COMOUTACT`), else `PASSROM` → ROM modules (CE-1600P) → CE-150 |
| F099H | `LINE` (screen) | — | native rom3b `K_LINE`. A PC-1500 plotter line is F0B7H, which the PC-1600 calls `LLINE` |
| E680H–E686H, E7A9H, E883H–E885H, F089H, F08FH, F095H, F0A5H, F0B1H, F0B2H, F0B5H, F0B7H, F0BBH | `CSIZE` `GRAPH` `GLCURSOR` `SORGN` `ROTATE` `TEXT`, `RMT`, `TERMINAL` `DTE` `TRANSMIT`, `CLOAD` `MERGE` `CSAVE`, `LCURSOR`, `CONSOLE`, `CHAIN`, `COLOR`, `LLINE`, `TAB` | CE-150 / CE-158 | none → ROM modules first (CE-1600P B4/B5), then the CE-150/CE-158 ROM via the LH-5803 (`TOK1500` P1-B3 `5DF6H`) |

The lookup order (`COMMADR` P0-B0 `112FH`) is described in `PC-1600-Load-Save-Matrix.md`
§1. It doesn't depend on MODE.

## 3. LH-5803 side: three MODE tests

| Where | What MODE 1 changes |
|---|---|
| `P_MAPPRG` `$E63C` | **MODE 1 only:** `P_BANK` (port 31H, via ME1 `$A031`) := (first non-zero `ADTBL` entry AND 70H) OR 06H. This puts the program's bank into Z-80 page 2, which is the LH-5803's `0000H`–`3FFFH`. In MODE 0 nothing changes, and the window shows whatever page 2 holds. Called by `X_EXCOMM_GO` `$DC85` (every PC-1500 statement) and `BCMD_PEEK_1600` `$DC9A` (`XPEEK`). `P_BANK` is restored afterwards |
| `P_VARNAME` `$C34F` (patch in `GET_VAR_ADDR_1` `$D46A`) | **MODE 0:** a variable name whose second byte isn't 00H/20H (anything but `A`–`Z`, `A$`–`Z$`) → error 6EH. MODE 1: all names. `XPOKE &4100,A1` / `XCALL &4100,A1` give ERROR 110 in MODE 0 and work in MODE 1 ✔. `X=XPEEK A1` works in both, because the Z-80 evaluates the argument first ✔ |
| `X_CHKTOK` `$CDDD` | The tokens in `TAPETOK_TBL` `$CE3B` (`CSAVE`, `CLOAD`, `MERGE`, `CHAIN`, `LLIST`) → error 6EH in MODE 0. In MODE 1 the sub-CPU is asked first (`SUBCMD`, U = 5CH). If `TITLE` ≠ 0, the slot descriptor's page byte 07H must have b7 set, else error 18H |

Z-80 side of the same path: `EXCOMM1500` refuses E883H/E884H (`TERMINAL`, `DTE`) in MODE 0
with 6EH (P1-B3 `5E76H`).

**Memory picture** (✔ = observed in the emulator):

- **No module:** MODE 0 `XPEEK 0` = 255, with port 31H = 60H (page 2 = ROM bank 6) ✔.
- **CE-155 in slot 1:** the program was visible at its LH-5803 address in both modes ✔.
- **Always:** LH-5803 `4000H + n` = Z-80 `C000H + n` (`XPEEK &4100` = `PEEK &C100`) ✔.

## 4. Z-80 side: every `BMODE` b6 test

| ROM address | Routine | MODE 1 effect |
|---|---|---|
| P0-B0 `0C65H` | boot vector | b6 set → `RAMODSET(1)`. If that refuses, b6 is cleared and `PRGMODSEL` runs: MODE 1 survives power off/on only if the configuration still allows it |
| P0-B0 `1AD3H` | editor line overflow | MODE 1: scroll the line up |
| P0-B0 `1C7CH` | `RUNSET3` (`BASPARES`) | `F871H` (PRINT wait) := 0 in MODE 1 (wait for ENTER), 3 in MODE 0 (no pause). Matches the manual's `RUN` defaults. **Note:** `K_WAIT`'s comment (P1-B0 `6293H`) has 0 and 3 the wrong way round |
| P0-B0 `1E22H` | cursor to next line | MODE 1: erase line 3 and stay there |
| P0-B0 `269DH` | print at cursor | MODE 1: also update the PC-1500 LCD image (`CPY150LCD`) |
| P1-B0 `42F8H` | bottom display row | always 3 in MODE 1 |
| P1-B0 `55ADH` | `CURSOR` | MODE 1: x = column 0–25 of the one line (graphic column x·6) |
| P1-B0 `5671H` | `WIDTH` | MODE 1 → error 6FH |
| P1-B0 `5725H` | `CLS` | MODE 1: cursor row 3 |
| P1-B0 `587CH` | `GOTO` (direct) | MODE 1: scroll up first |
| P1-B0 `5EFAH`, `6046H` | `INPUT` row / prompt | MODE 1: no new line; prompt column = graphic column / 6 |
| P1-B0 `5FCBH` | `INPUT` value taken | MODE 1: `;` after the variable → syntax error (`INPUT A;` → ERROR 1 ✔); MODE 0 keeps the cursor ✔ |
| P1-B0 `633EH` | `PRINT` | MODE 1 → `PRINT1500` (`647DH`): PC-1500 line, `,` splits the line in halves, at most 2 items |
| P1-B0 `70E9H` | `CHKMSG` | a start-up check message clears b6 (back to MODE 0) |
| P1-B0 `7DFDH` | `TOKENIZE` | MODE 1: line numbers after jump tokens stay ASCII (no `1FH hi lo 00H` form). Software-Info 1600-014G: the CE-150 `LLIST` can't print the binary form |
| P1-B0 `7FE4H` | character matrix select | the kanji matrix clears b6 |
| P1-B3 `5E76H` | `EXCOMM1500` | MODE 0: `TERMINAL`/`DTE` → 6EH |
| P1-B3 `6A4CH` | `APOTST` | MODE 1: re-runs `RAMODSET(1)` after the slot map is rebuilt |
| rom3b `4124H` | `MODE1SCRL` | `CONT` (`4108H`/`411EH`): scroll up first |
| rom3b `4351H` | `NEW addr` | MODE 1 only; MODE 0 → error 19H (ERROR 25 ✔) |
| rom3b `6025H` | `GCURSOR` | MODE 1: one argument = dot column 0–155 of the next `GPRINT` |
| rom3b `609BH` | `GPRINT` | MODE 1: pattern into the line buffer, copied to the LCD (`CPY150LCD`), column kept in F874H/F875H |
| rom3b `62BAH` | `INIT "S1:"/"S2:"` | MODE 1 → error 6EH ✔ |
| rom3b `6AC8H` | `FILES` | MODE 1: one entry per screen instead of 3 |
| P2-B6 `AA8EH`, `AC13H`, `ACC4H` | `RXD$`, error 27H, string search | `AND 0C0H`: two-byte character handling off in MODE 1 or in single-byte mode |

**CE-1600P.**
- **B4 (plotter) never tests MODE.**
- **B5 (cassette) tests it through `IS1500MODE` (`6668H`), about 25 times:**
  - the tape format: PC-1500 bit encoding, A0H sync, 32-byte header;
  - `K_CSAVE` (`66A0H`) refuses `CSAVE`/`CSAVE M` in MODE 1;
  - `6F35H` refuses `PRINT#-1` in MODE 1;
  - the `CLOAD` target address is taken from the PC-1500 header (F239H) in MODE 1 (`6A1CH`).

  Details are in `PC-1600-Load-Save-Matrix.md` §2–3.

## 5. Entering and leaving MODE 1 (`RAMODSET` / `PC15MAP`)

- **When `MODE 1` is refused:** the gate is in `PC15MAP` and is described in
  `PC-1600-CPU-LH5803-Compat.md` §4 and `PC-1600-Memory-Architecture.md` §8. It refuses
  (6EH) only when S0 spans more than one module bank; no module is required.
- **Program area:** `PC15MAP` picks it itself and hides the other slots.
- **`ADTBL`** is cut to the chosen entry.
- **F860H–F863H** get the area in PC-1500 form. The cleared state (`PC15MAPCLR` `1662H`)
  is `FF FF FF` + the S0 base.
- **`RAMODSET(0)`** (back to MODE 0) runs `SSLOTMP`, `PC15MAPCLR` and `SELPRG 0`: the slot
  table is rebuilt and `TITLE` goes back to S0.

## 6. Forced MODE 1: `POKE &F1BC,PEEK(&F1BC) OR 64`

**The trick.** A tip from the time recommends this POKE for running PC-1500 programs larger
than 12 KB with a CE-1600M folded into S0. In that configuration `MODE 1` itself is refused
with ERROR 110. The POKE sets b6 without `RAMODSET`, `CGMODE` or the screen setup, so every
b6 test in §3–§4 fires while the memory layout stays the MODE 0 one.

**Emulator run.** CE-1600M in slot 1, `NEW0`, `INIT "S1:","F"`, `INIT "S1:","M"`:

- **`MODE 1` → ERROR 110.** The POKE is accepted; `MEM` stays 44602 ✔.
- **F860H–F863H stay in the cleared state** `FF FF FF 00` ✔.
- **A 230-line, ~17 KB program across both module banks runs to the end** and waits for
  ENTER after `PRINT` (the MODE 1 `F871H` default) ✔.
- **PC-1500 program pointers make no sense for it:** start F865H/F866H = `00C5H`, end
  F867H/F868H = `060FH` (high byte first, LH-5803 form, no bank) ✔.
- **`P_MAPPRG` maps the first bank only:** `XPEEK &C5` = `0 1 74` (line 1, length 74) ✔.
  The rest of the program is out of the LH-5803's reach.
- **The PC-1600 character set stays:** `CHR$ &5B;CHR$ &5D;CHR$ &27` prints `[]'`. A real
  MODE 1 prints `√`, `π` and the PC-1500 glyph ✔.
- **`INIT "S1:","F"` → ERROR 110** ✔. `MODE 1` again does nothing; `MODE 0` restores the
  normal state (b6 clear, `MEM` 44602) ✔.

**Predicted from the ROM, not run:**

- **Power off/on** goes through the boot vector (§4, `0C65H`). `RAMODSET(1)` refuses, b6 is
  cleared, and the machine comes back in MODE 0. `APOTST` calls `RAMODSET(1)` too.
- **LH-5803 code that walks the program** sees `00C5H`–`060FH` inside the first bank and
  will list or save the wrong program, or write over memory. This covers CE-150/CE-158
  `LLIST`, `CSAVE`, `CLOAD`, `MERGE`, `CHAIN`, and PC-1500 machine code that uses the
  program pointers.
- **The CE-1600P cassette `CLOAD`** is Z-80 code (B5). It loads into the bank list of the
  `TITLE` area (`CASAREA` `7415H`), which under the POKE still holds every S0 bank. That
  is why the tip lets a large PC-1500 tape load. Not run: the emulator has no tape input.
- **`P_VARNAME` accepts all variable names.** Whether the LH-5803 reaches variables that
  sit outside the first bank is open.

## 7. Open questions

1. What the sub-CPU command 5CH in `X_CHKTOK` asks for.
2. What exactly the LH-5803 sees at `0000H`–`3FFFH` in MODE 0 with banked modules, on real
   hardware. The emulator shows the current page-2 bank, or 255 when that is not module RAM.
3. A real-hardware check of the POKE-forced MODE 1 with a PC-1500 tape on the CE-1600P.
