# Expansion

Everything that plugs in: connector pinouts, the PC-1600 system bus, memory modules, and what a replacement module has to emulate.

**Out of scope:** modern hobbyist modules CE-1638, CE-163F and CE-163X (private material); superRAM is covered because the PC-1600 firmware must cope with it.

**Gaps:** `PC-1600-Expansion-Bus.md` is a stub (only peripheral ROM placement is written).

## Documents

<!-- files:begin -->
| File | Model | Status | KB | What it answers |
|---|---|---|---|---|
| [PC-1500-Connectors.md](PC-1500-Connectors.md) | 1500 | cited | 20 | PC-1500 40- and 60-pin connectors pin by pin, and the PC-1500A pin reassignment. |
| [PC-1500A-Rewiring.md](PC-1500A-Rewiring.md) | 1500 | cited | 7 | Why and how the PC-1500A rewired the expansion connector; the CE-155 worked example; why only 4 KB. |
| [PC-1600-Connectors.md](PC-1600-Connectors.md) | 1600 | cited | 12 | PC-1600 60-pin system bus and the two 40-pin memory-slot connectors; module hardware status. |
| [PC-1600-Expansion-Bus.md](PC-1600-Expansion-Bus.md) | 1600 | draft | 7 | Designing hardware for the 60-pin bus and memory slots (stub: only peripheral ROM placement written). |
| [PC-1600-Memory-Modules.md](PC-1600-Memory-Modules.md) | 1600 | cited | 24 | Module catalogue: CE-1600M, CE-1601M, superRAM, PC-1500 8x16K module in the PC-1600. |
| [Software-Defined-Memory-Extension.md](Software-Defined-Memory-Extension.md) | 1500+1600 | draft | 13 | What a microcontroller-based universal module must do on the wire to emulate each real memory module. |
<!-- files:end -->
