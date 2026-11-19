# Skill evals

Questions a user might ask, with the document that must answer them. After a larger change, ask each question in a fresh
session with the skill installed and check that the agent reaches the document without reading anything big. `tools/check.py`
verifies that every path below exists.

| # | Question | Expected document |
|---|---|---|
| 1 | How does bank switching work on the PC-1600? | `Memory/PC-1600-Bank-Switching.md` |
| 2 | What does bit 6 of port 31H select? | `Memory/PC-1600-Bank-Switching.md` |
| 3 | Where does `NEW "S1:"` put a BASIC program? | `Memory/PC-1600-Program-Areas-and-NEW.md` |
| 4 | How much RAM does a PC-1500 with a CE-155 have, and what is the `NEW` offset? | `Memory/PC-1500-RAM-Sizing-and-NEW.md` |
| 5 | Why did the PC-1500A rewire the expansion connector? | `Expansion/PC-1500A-Rewiring.md` |
| 6 | How many wait states does the SC-7852 insert? | `CPU/PC-1600-SC7852-Z80.md` |
| 7 | Which LCD controllers does the PC-1600 use and at which ports? | `Display/PC-1600-Display-Hardware.md` |
| 8 | How does the PC-1500 ROM auto-repeat a key? | `Keyboard/PC-1500-Keyboard-Scan.md` |
| 9 | What are the bits of the PC-1600 interrupt cause register 32H? | `IO-Ports/PC-1600-IO-Ports.md` |
| 10 | How is baud rate set on the TC8576F? | `Serial-Parallel/PC-1600-CPC-TC8576.md` |
| 11 | What does the 16-byte file header of a PC-1600 file contain? | `Storage/PC-1600-Filesystem.md` |
| 12 | Which load commands work in MODE 1 with a CE-158? | `Storage/PC-1600-Load-Save-Matrix.md` |
| 13 | What is the header of a serial binary transfer from a PC-1500 with CE-158? | `Data-Formats/Binary-Exchange-Formats.md` |
| 14 | Pinout of the PC-1600 memory slot? | `Expansion/PC-1600-Connectors.md` |
| 15 | What is the CE-1601M and how does it bank? | `Expansion/PC-1600-Memory-Modules.md` |
| 16 | How does MODE 1 change `XPEEK`? | `Firmware/PC-1600-MODE0-MODE1.md` |
| 17 | Which ROM routine prints a character on the PC-1500 LCD? | `Firmware/PC-1500-ROM-Routines.md` |
| 18 | Write an LH5801 routine that copies 64 bytes. | `Programming/prompts/LH5801-Assembly-Prompt.md` |
| 19 | Write a PC-1500 BASIC program that prints prime factors. | `Programming/prompts/PC-1500-BASIC-Prompt.md` |
| 20 | Which ROM version is my PC-1600? | `Machines/PC-1600-ROM-Versions.md` |
