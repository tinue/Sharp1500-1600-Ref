# PC-1600 Display IOCS

Summary: LCD IOCS routines (text, cursor, scroll, status line, graphics), LCD work area, 6x8 character generator.
Scope: PC-1600
Sources: PC-1600 Technical Reference Manual §7.3 (LCD hardware), read from the German Systemhandbuch scan. §3.1 (IOCS routines for LCD, work area, character font) and §10.1 (character-code table) pending. §3's port/command decode …
Status: cited

> Split from `PC-1600-Display-HD61202.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: Scope, §1, §2, §3, §4, §5, TODO → [PC-1600-Display-Hardware.md](PC-1600-Display-Hardware.md); §9 → [HD61102-HD61203-Datasheet-Facts.md](HD61102-HD61203-Datasheet-Facts.md).

## 6. LCD IOCS routines (TRM §3.1)

Call `CALL <entry>`. All addresses are in Bank 0. The character-mode routines operate on
**one text line at a time** — output never wraps to another line. Character mode is
26 columns wide (X 0–25) × 4 lines (Y 0–3); graphics mode uses dot coordinates
**0 ≤ X ≤ 155, 0 ≤ Y ≤ 31**. See `PC-1600-IOCS.md` §1 for the field conventions.

### 6.1 Character output & cursor

| Name | Entry | Function | Params | Return | Clobbers |
|---|---|---|---|---|---|
| **PRTANK** | 0100H | show one char at cursor, advance right | A = char code | CF=1 if it landed in the rightmost column (X=25) → cursor display turned off, cursor not advanced | AF, CRSRX, CRSRST |
| **PRTASTR** | 00EBH | show a string from memory at cursor until a terminator byte is met (terminator not shown) | DE = start addr; A = terminator code | DE = addr of last-shown byte + 1; CF=1 if a char landed in the rightmost column | AF, DE, CRSRX, CRSRST |
| **ERSSTR** | 013FH | show a run of blanks | (count) | — | — |
| **RVSCHR** | 011BH | flip the currently-shown characters to reverse video | — | — | — |
| **SETANK** | 0109H | switch the display to character mode | — | — | — |
| **CGMODE** | 0133H | switch the character-generator between PC-1500 and PC-1600 sets (also reachable via LCDWK1 b2) | — | — | — |
| **CRSRSET** | 0115H | set cursor position (char mode) | D = X, E = Y | CF=1 if outside the displayable area | AF, CRSRX (F060H), CRSRY (F05FH) |
| **CRSRPOS** | 0118H | read cursor position (char mode) | — | D = X, E = Y | DE |
| **CRSRSTAT** | 011EH | set cursor type | A = 00 off / 01 underline / 02 blinking block / 03 blinking blank | — | CRSRST (F067H) |

### 6.2 Line / scroll

| Name | Entry | Function | Params |
|---|---|---|---|
| **UPSCRL** | 012DH | scroll the display up one line; bottom line cleared; cursor display off | — |
| **DWNSCRL** | 0130H | scroll down one line; top line cleared; cursor display off | — |
| **INS1LN** | 0142H | insert a blank line at line A; that line and those below scroll down; cursor display off | A = line 0–3 · clobbers AF |
| **ERS1LN** | 0145H | clear an entire line (stays blank) | A = line position |

### 6.3 Status (symbol) line

| Name | Entry | Function | Params |
|---|---|---|---|
| **SMBLSET** | 013CH | set a symbol set into the state given by A | B = symbol-set number 0–2; A = 8-bit mask, 1 = ON (bit map below) |
| **SMBLREAD** | 0139H | read the status-line state | — |

**SMBLSET's bit map, confirmed 2026-08-30** from the TRM's own SMBLSET reference page
(§3.1 p28; primary source, a photo of the manual page supplied by the project owner) —
resolving the "not fully transcribed" gap this table previously carried. `A`'s 8 bits,
MSB → LSB, per `B`:

| B | b7 | b6 | b5 | b4 | b3 | b2 | b1 | b0 |
|---|---|---|---|---|---|---|---|---|
| 00H | DEF | I | II | III | SMALL | — | SHIFT | BUSY |
| 01H | — | RUN | PRO | RESERVE | — | RAD | G | DE |
| 02H | KBII | — | — | — | S | — | CTRL | Low battery |

(`—` = unused/undefined in the TRM's own table.) TRM's own note: *"Wenn entweder KBII
oder S auf 1 gesetzt ist, so wird das S Symbol angezeigt"* — "if either KBII or S is set
to 1, the S symbol is shown": on real hardware there is exactly one printed "S" position,
lit by either underlying cause; the "ローマ字→カナ" caption text this project's own
photo measurement (§1.1) found next to it is most likely a static, permanently-printed
explanation of what S means when lit, not a second independently-driven segment.

**Storage location, confirmed from ROM code (2026-09-26).** The symbol writer in
bank 6 (`8220H`, called with the page in A, e.g. `LD A,07H / CALL 8220H` at `82FCH`)
selects IC3 (C = 54H) and sets page **(A + DSPLPTR F05CH) & 7** (`81F0H`: `OR B8H`).
It sets column **3FH = 63** (`81FCH`: `OR 40H`) and writes the byte with `OUT (56H),A`,
waiting on both chips' busy bits (`817FH`) before each access. So the three sets live in
**IC3 column 63: B=00H → page 7, B=01H → page 6, B=02H → page 4**. Page 5 is unused.
The display start line rotates them along with the main screen. For page 4 the writer
folds KBII into S (`AND 77H`, then `OR 08H` if bit 3 or 7 was set) before the write.
The RAM shadows, read back by `8208H`, are **F64EH** (page 7), **F64FH** (page 6) and
**F3C6H** (page 4, pre-fold, so it still carries KBII in b7).

### 6.4 Graphics

| Name | Entry | Function | Params / notes |
|---|---|---|---|
| **DOTSET** | 0127H | plot one dot | dot at (X,Y); raster-op from **DOTSOP** (F096H): 00 = set, 01 = OR / clear, 02 = XOR / invert |
| **DOTREAD** | 012AH | read one dot's state | — |
| **LINE** | 0121H | draw a line between (X1,Y1) and (X2,Y2) with pattern LINPTN | params in the F08EH block (§6.5); on return X1POS←X2POS, Y1POS←Y2POS (endpoint becomes the next start) and LINPTN is rotated one dot right for a continuation; clobbers AF, BC, DE, HL, X1POS, Y1POS, LINPTN |
| **BOX** | 0124H | draw a rectangle with (X1,Y1)/(X2,Y2) as opposite corners | same F08EH param block · *(the TRM §3.1 worked example draws a line but ends `CALL &0124`; treat the `0121`/`0124` split as LINE/BOX per the routine table and verify against ROM)* |
| **GCRSRSET** | 014BH | set the graphics-cursor position | DE = X, BC = Y (2's-complement, −32768…32767) · clobbers GCRSRX, GCRSRY |
| **GCRSRPOS** | 0148H | read the graphics-cursor position | — |
| **PRTGCHR** | 014EH | show one char at the graphics-cursor position | 6×8 raster; DOTSOP framing (00 = draw new & clear old 6×8, 01 = OR with old) |
| **PRTGSTR** | 00EEH | show a string from memory at the graphics-cursor position | DE = start; A = terminator |
| **PRTGPTN** | 0154H | show a 1×8-dot pattern at the graphics-cursor position | DOTSOP framing (00 = new & clear old 1×8, 01 = OR) |
| **GPTNREAD** | 015AH | read a 1×8-dot pattern at the graphics-cursor position | — |

**Worked example (TRM §3.1):** `LINE(-5,-3)-(100,50),,&ADA9,BF` in BASIC ≡

```
POKE &F08E,&FB,&FF,&FD,&FF,&64,&00,&32,&00   ; X1=-5, Y1=-3, X2=100, Y2=50 (LE, 2's-comp)
POKE &F096,&00,&A9,&AD                       ; DOTSOP=0 ; LINPTN = &ADA9
CALL &0124
```

### 6.5 Whole-screen / raw

| Name | Entry | Function |
|---|---|---|
| **CLS** | 0112H | clear the whole display (no params, no return) |
| **BSPCTR** | 00E5H | enable / disable the LCD |
| **SAVELCD** | 015DH | save one line's 156×8-dot bitmap to RAM |
| **LOADLCD** | 0160H | load one line's 156×8-dot bitmap from RAM |
| **CPY1500LCD** | 0157H | copy the 4th display line (156-byte bitmap) into the PC-1500-mode LCD RAM at 7600H–764FH or 7700H–774FH — the compatibility bridge for `PC-1600-LH5803-Memory-View.md` §5 |

## 7. LCD work area (TRM §3.1.2)

SC-7852-view addresses; 2-byte fields are little-endian (L then H) unless noted.

| Name | Addr | Bytes | Meaning |
|---|---|---|---|
| LCDWK1 | F05DH | 1 | b0: LCD mode (0); **b2**: character set (0 = PC-1600, 1 = PC-1500); **b3**: codes 00H–1FH (0 → shown as blanks, 1FH as the "insert" symbol; 1 → shown from the user CG table at CTRCGA/CTRCGB); **b4**: cursor-blink frequency (0 = normal, 1 = double) |
| LCDWK2 | F05EH | 1 | b0: cursor-blink work; b1: LCD interrupt-request mask |
| CRSRX | F060H | 1 | cursor X (0–25) |
| CRSRY | F05FH | 1 | cursor Y (0–3) |
| CRSRT | F067H | 1 | cursor type (00 off / 01 underline / 02 blink block / 03 blink blank) |
| CTRCGA | F061/F062H | 2 | start address of the CG table for codes **00H–1FH** (must be > 8000H) |
| CTRCGB | F063H | 1 | bank (0–7) of that table |
| UPAGGA | F064/F065H | 2 | start address of the CG table for codes **80H–FFH** (must be > 8000H) |
| UPAGGB | F066H | 1 | bank (0–7) of that table |
| X1POS | F08E/F08FH | 2 | LINE/BOX corner 1 X (2's-complement) |
| Y1POS | F090/F091H | 2 | LINE/BOX corner 1 Y |
| X2POS | F092/F093H | 2 | LINE/BOX corner 2 X |
| Y2POS | F094/F095H | 2 | LINE/BOX corner 2 Y |
| DOTSOP | F096H | 1 | dot / pattern raster-op (see §6.4) |
| LINPTN | F097/F098H | 2 | line pattern (same encoding as the BASIC `LINE` pattern argument) |
| GCRSRX | F099/F09AH | 2 | graphics-cursor X |
| GCRSRY | F09B/F09CH | 2 | graphics-cursor Y |

(These overlap the `PC-1600-Work-Area-Map.md` §3.2 LCD entries; the addresses here from
§3.1.2 are the authoritative set for the graphics params, which §6.3 of that doc did not
list.)

## 8. Character generator (TRM §3.1.3)

- A PC-1600 character cell is **6 × 8 dots**. In the CG table each of the 6 columns is one
  byte (an 8-dot vertical slice), stored **left column first**; within a byte **LSB = top
  dot, MSB = bottom dot**. Example — "G" = `3E 41 41 49 39 00`.
- Three CG tables:
  1. **codes 20H–7FH** — in ROM, fixed.
  2. **codes 80H–FFH** — in ROM; the user can point at an alternate RAM table via
     **UPAGGA/UPAGGB**. The whole table is swapped, so all codes must be defined.
  3. **codes 00H–1FH** — no ROM table. To use them the user builds a RAM table, sets
     **CTRCGA/CTRCGB**, and sets **LCDWK1 bit 3 = 1**.
