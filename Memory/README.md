# Memory

Physical and logical memory: address decoding, chip selects, bank switching, memory maps, program areas and `NEW`.

| Question | Start with |
|---|---|
| PC-1500: what is at which address, how much RAM, `NEW` offsets | `PC-1500-Address-Decoding.md`, `PC-1500-RAM-Sizing-and-NEW.md` |
| PC-1500: how 16 KB modules bank switch | `PC-1500-Bank-Switching.md` |
| PC-1600: memory map and how it differs from the PC-1500 | `PC-1600-Memory-Map.md` |
| PC-1600: ports 31H/28H/3DH, truth tables | `PC-1600-Bank-Switching.md` |
| PC-1600: where do BASIC and ML programs land, where does a module sit | `PC-1600-Program-Areas-and-NEW.md`, `PC-1600-Module-Window-Layout.md`, `PC-1600-BASIC-Program-Placement.md` |
| PC-1600: gate array, chip selects | `PC-1600-Gate-Array-and-Chip-Selects.md` |

**See also:** `../Expansion/` (modules and connectors), `../CPU/PC-1600-LH5803-Memory-View.md`, `../Firmware/PC-1600-Work-Area-Map.md` (RAM variables), `../Firmware/PC-1600-Transparent-Banking.md` (firmware calls).

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [PC-1500-Address-Decoding.md](PC-1500-Address-Decoding.md) | 1500 | cited | 24 | Address decoder, physical RAM chips, the machine-language area at &7C01, superseded hypotheses. |
| [PC-1500-Bank-Switching.md](PC-1500-Bank-Switching.md) | 1500+1600 | cited | 20 | Line-based and latch-based 16 KB module bank switching; CE-163 behaviour in PC-1600 slots. |
| [PC-1500-Chip-Select-Tables.md](PC-1500-Chip-Select-Tables.md) | 1500 | cited | 16 | Decoder notation and the PC-1500 and PC-1500A chip-select tables, reproduced from the TRM. |
| [PC-1500-RAM-Sizing-and-NEW.md](PC-1500-RAM-Sizing-and-NEW.md) | 1500 | cited | 10 | RAM size and NEW offset calculations for the empty machine, CE-155, 16K module, program modules; screen reverse. |
| [PC-1600-BASIC-Program-Placement.md](PC-1600-BASIC-Program-Placement.md) | 1600 | cited | 22 | Emulator spec: how LOAD scatters a tokenised BASIC program across S0's bank list via ADTBL; injection algorithm. |
| [PC-1600-Bank-Switching.md](PC-1600-Bank-Switching.md) | 1600 | cited | 25 | Port 31H bank register, truth tables, memory map by bank, auxiliary ports, the ~77 KB maximum. |
| [PC-1600-Gate-Array-and-Chip-Selects.md](PC-1600-Gate-Array-and-Chip-Selects.md) | 1600 | cited | 16 | Chip complement, LR38041 gate array, chip-select signals, slot connectors, signal summary, memory PWB wiring. |
| [PC-1600-Memory-Map.md](PC-1600-Memory-Map.md) | 1600 | cited | 28 | Z-80 view in four bank-switched pages, internal RAM layout, comparison with PC-1500(A), summary table. |
| [PC-1600-Module-Window-Layout.md](PC-1600-Module-Window-Layout.md) | 1600 | cited | 19 | Where a module sits in the 8000-BFFF window and how the BASIC/ML area slides; worked max-RAM example. |
| [PC-1600-Program-Areas-and-NEW.md](PC-1600-Program-Areas-and-NEW.md) | 1600 | cited | 15 | NEW across S0/S1/S2, where ML programs land, TITLE and program areas, program vs expansion memory. |
<!-- files:end -->
