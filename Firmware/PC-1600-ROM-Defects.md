# PC-1600 ROM defects

Summary: Defects in the PC-1600 ROM that a BASIC user can run into, each found in the disassembly and confirmed in Calc-U.
Scope: PC-1600, both ROM revisions (NEW `PEEK #(0,&7FFF)` = 5, OLD = 130)
Sources: ROM:PC-1600-ROM/disasm/new/PC1600-P1-B3B.asm, EMU:sources/evidence/rom-defects
Status: emulator-verified

The defects that Sharp's own Software-Info bulletins describe (ON ADIN, LLIST on the CE-150, LINE, TAB on COM1:) are not
repeated here. Each entry gives the cause in the ROM, what the user sees, a way to avoid it and the test. The tests are
the presets in [`../sources/evidence/rom-defects/`](../sources/evidence/rom-defects/), which run
`rom-defects.bas` on a PC-1600 with a CE-1601M RAM disk in slot 2. For the OLD revision, set `model: PC-1600:old`.
Calc-U runs the original ROM, so a result there is the ROM's behaviour. None of it has been checked on a real machine.

## 1. INPUT# evaluates a numeric field as an expression

**Cause.** INPUT# (bank 3b, 68EBH) reads each field as text into F400H. For a numeric variable it ends the text with CR
and hands it to the expression evaluator `EXPRESS` (6955H), in the context of the running program. Only a failed
evaluation gives 0 (695CH). The type test after it (6961H, `cp 0D3H` / `jr c`) keeps every result below D3H, and that
includes the string type D0H. [ROM:PC-1600-ROM/disasm/new/PC1600-P1-B3B.asm@6955]
[ROM:PC-1600-ROM/disasm/old/PC1600-P1-B3B.asm@6846]

**What the user sees.** A file written with `PRINT#1,"2*3":PRINT#1,"B$":PRINT#1,"HELLO"`, read back with
`INPUT#1,A,C,D` while `B$="XY"` and `HE=7`:

| Field | Read into | Result |
|---|---|---|
| `2*3` | `A` | 6: the text is computed |
| `HELLO` | `D` | 7: the value of the variable `HE` |
| `B$` | `C` | the string goes into the numeric variable: `PRINT C` shows `/Y`, `PRINT C+1` gives ERROR 17 |

So a text field read into a numeric variable can silently give the value of some variable, or leave a numeric
variable that every later calculation refuses. The manual only says that the order and type of the variables must
match the file. [EMU:input.pc1600]

**To avoid it.** Read a field whose content is not certain into a string variable and convert it with `VAL`.

## 2. PRINT# USING: an error leaves the USING state wrong

**Cause.** PRINT# (bank 3b, 6777H) saves the USING state (USINGFF, F896H..F898H) and clears it before each item, so a
`USING` in PRINT# applies only to its own item. Its normal end (681AH) and its error exits (6834H..683FH) restore the
saved state, but an error in the format (67D3H) or in the expression (67DDH) returns with `ret c` directly, past the
restore. [ROM:PC-1600-ROM/disasm/new/PC1600-P1-B3B.asm@67DD] [ROM:PC-1600-ROM/disasm/old/PC1600-P1-B3B.asm@66B8]

**What the user sees.** Only with `ON ERROR GOTO`, because without it the program stops. Two forms:

| Program | Expected | Observed |
|---|---|---|
| `PRINT#1,USING "##.##";1/0`, handler `PRINT ERN;ERL` | `38 130` | ERROR 36 IN (handler line): the item's `##.##` is still on, and 130 does not fit it [EMU:print-using-leak.pc1600] |
| `USING "###.#"`, then `PRINT#1,1/0`, handler `PRINT 3.14159` | `3.1` | `3.14159`: the program's own USING is gone [EMU:print-using-lost.pc1600] |

The wrong state also outlives the program: after the first form, `PRINT 3.14159` in direct mode still shows `3.14`.

**To avoid it.** Start the error handler with a `USING` statement that sets the format it wants (`USING` alone for
none).
