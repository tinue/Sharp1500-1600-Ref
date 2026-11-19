# Programming

Writing programs for the machines. `prompts/` holds the paste-ready documents: attach one to any AI chat and describe the program you want.

| I want to | Use |
|---|---|
| write PC-1500 BASIC | `prompts/PC-1500-BASIC-Prompt.md` |
| write LH5801 assembly (PC-1500) | `prompts/LH5801-Assembly-Prompt.md` (generated, self-contained) |
| write Z-80 machine code for the PC-1600 | `PC-1600-Z80-Assembly-Guide.md` (first pass) |
| port PC-1500 BASIC to the PC-1600 | `PC-1600-BASIC-Porting.md` |

The LH5801 prompt is built from `LH5801-Assembly-Guide.md`, `../CPU/LH5801-Architecture.md`, `../CPU/LH5801-Instruction-Set.md`, `../Firmware/PC-1500-System-Variables.md` and `../Firmware/PC-1500-ROM-Routines.md` by `tools/build-prompts.py`. Edit the parts, not the generated file.

There is no PC-1600 BASIC authoring prompt yet.

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [LH5801-Assembly-Guide.md](LH5801-Assembly-Guide.md) | 1500 | cited | 31 | Quick reference card, sdas assembler syntax, idioms, TASM conversion, how to write a user guide. Part of the prompt. |
| [PC-1600-BASIC-Porting.md](PC-1600-BASIC-Porting.md) | 1600 | cited | 3 | Where PC-1600 BASIC is documented and the PC-1500 to PC-1600 porting gotchas. |
| [PC-1600-Z80-Assembly-Guide.md](PC-1600-Z80-Assembly-Guide.md) | 1600 | cited | 8 | Writing SC-7852 machine code: number encodings, calling BASIC math, conversions, bank-aware code (first pass). |
| [LH5801-Assembly-Prompt.md](prompts/LH5801-Assembly-Prompt.md) | 1500+1600 | generated | 127 | Paste-ready LH5801 assembly prompt, built from the parts by `tools/build-prompts.py`. |
| [PC-1500-BASIC-Prompt.md](prompts/PC-1500-BASIC-Prompt.md) | 1500 | cited | 32 | Paste-ready prompt: Sharp BASIC programmer role, device limits, coding style, keyword reference. |
<!-- files:end -->
