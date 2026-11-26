# Evidence

Tests, spikes and samples that were run to answer a question or to try something out. The **results** are in the reference
documents (`Memory/`, …); what is kept here is the *how*, so a result can be reproduced or doubted. Nothing here is
knowledge-base content and no document should cite it as a source of truth. Agents: skip this folder unless a document
sends you here.

| Folder | What | Result documented in |
|---|---|---|
| `program-area-tests/` | Four PC-1600 emulator presets, BASIC and ML payloads and a dump analyser for where programs land when modules are merged into S0 or used as program areas, and what `MEM`, `SAVE`, `NEW` do per `TITLE` area. | `Memory/PC-1600-Program-Areas-and-NEW.md`, `Memory/PC-1600-BASIC-Program-Placement.md` |
| `rom-defects/` | `rom-defects.bas` and three PC-1600 presets (CE-1601M RAM disk in slot 2) that show the INPUT# and PRINT# USING defects. | `Firmware/PC-1600-ROM-Defects.md` |
| `samples/basic/` | Two BASIC programs written with the BASIC prompt (calendar, Lissajous) with their companion guides: examples of the prompt's output. | `Programming/prompts/PC-1500-BASIC-Prompt.md` |
| `samples/asm/` | `memtest.asm`, a RAM test for the free region between BASIC program and variables, and `CE168FTest.bas`, a hand-written test of all 8 banks of a CE-163F module. | `Memory/PC-1500-Bank-Switching.md` |

The presets and the `.bas`/`.asm` files are Calc-U-1600 inputs (the product in the `calc-u` monorepo). Programs that are
meant to stay maintained live in `calc-u/products/calc-u-1600/examples/`; `samples/asm/memtest.asm` is to be compared with
the `memtest*` examples there and then dropped.
