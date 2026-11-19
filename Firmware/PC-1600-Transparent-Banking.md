# PC-1600 Transparent Bank Switching (Firmware)

Summary: Firmware view of banking: system calls, RST shortcuts, ROM module headers, slot management, boot sequence.
Scope: PC-1600
Sources: - Service_Manual.pdf -- hardware architecture, schematics, gate array, slot pinouts - SHARP-PC1600-Systemhandbuch.pdf -- firmware, OS calls, module headers, software
Status: cited

> Split from `PC-1600-Memory-Bank-Switching.md` in the 2026-11 reorganisation. Section numbers are unchanged, so existing `§` references stay valid.
> Other parts: §8 → [PC-1600-LH5803-Memory-View.md](../CPU/PC-1600-LH5803-Memory-View.md); §2 → [PC-1600-Bank-Switching.md](../Memory/PC-1600-Bank-Switching.md); §1, §3, §4, §5, §11, §12 → [PC-1600-Gate-Array-and-Chip-Selects.md](../Memory/PC-1600-Gate-Array-and-Chip-Selects.md); §9 → [PC-1600-IO-Ports.md](../IO-Ports/PC-1600-IO-Ports.md); §7, §7a, §7b, §10 → [PC-1600-Memory-Modules.md](../Expansion/PC-1600-Memory-Modules.md).

## Part 6: Firmware -- Transparent Bank Switching

### How the OS Makes Bank Switching Transparent

The critical design principle: **Bank 0 (0000-3FFF) is NEVER switched out.** It contains all gateway routines. Any code in any bank can always call these routines to switch banks. The `BANKCALL` routine saves the current bank state and restores it on return, making cross-bank calls transparent.

### System Calls (all in Bank 0, always accessible)

| Address | Name | Description |
|---------|------|-------------|
| 0190H | **BANKSET** | Set bank. A=bank number, B=page number. |
| 0193H | **BANKREAD** | Read current bank of page in B. Returns in A. |
| 018DH | **MEMORYCHK** | Test if memory exists at bank. D=bank, E=high byte of address (40-B8). Returns: Carry+A=00 = no memory; NC+A=01 = RAM; NC+A=03 = ROM. |
| 019CH | **BANKJUMP** | Jump to different bank. A=bank, HL=address. WARNING: return address destroyed. |
| 019FH | **BANKCALL** | Call routine in different bank. A=bank, HL=address. Current bank saved and restored on return. |
| 0196H | **SLOT1MAP** | Remap Slot 1 addressing. A=00: Normal. A=01: Slot 1b also at 4000-7FFF of Bank 1. |
| 0199H | **SLOT2MAP** | Remap Slot 2 addressing. A=00: Normal. A=01: Slot 2a also at 0000-3FFF of Bank 1. A=02: Slot 2a at 4000-7FFF and Slot 2b at 0000-3FFF, both Bank 1. |
| 00E8H | **SLOTST** | Test slot header at high byte in D. Returns: A=00 error; F0="P" (program); F2="S" (system); FF="M" (RAM-Disk). |

### RST Shortcuts (single-byte opcodes, fastest cross-bank calls)

**RST 18H + 2-byte immediate (nn): BANKJP (Bank Jump)**

Address encoding implicitly selects bank:

| Address Range | Target Bank |
|---------------|-------------|
| 0000-3FFF | Bank 0 |
| 4000-7FFF | Bank 3 |
| 8000-BFFF | Bank 6 |
| C000-FFFF | Bank 0, mapped to 4000-7FFF |

**RST 20H + 3-byte immediate (b, nn): BANKCAL (Bank Call)**

- b = Bank number
- nn = Target address
- Example: `E7 05 08 40` = `CALL Bank 5, address 4008H`

### ROM Module Detection and Headers

At reset, the system scans for modules. Bitmaps at F0AEH and F0AFH encode which ROM modules are present:
- **F0AEH:** Modules with start address 4000 (bit-encoded)
- **F0AFH:** Modules with start address 6000 (bit-encoded)
- Bit mapping: b6=Bank 1, b5=Bank 2, ... b0=Bank 7

Each module begins with an **8-byte header** at 8000H, A000H, or B000H:

| Offset | Field |
|--------|-------|
| +0 | ID Code: 43H |
| +1 | ID Code: 16H |
| +2 | Reset jump / checksum |
| +3 | Start address / boot indicator |
| +4 | Module length / boot address |
| +5 | BASIC address |
| +6 | End address |
| +7 | Type byte: 80H/FFH = "M" (RAM-Disk), F0H = "P" (Program), F2H = "S" (System), 01H = Write-protected |
| +8 | RESERVE area (RAM-Disk formatting info) |

### Module Jump Table (at address 4000H for Page 1 modules)

```
4000 : 43       ID-Code
4001 : 16       ID-Code
4002 : JP XXXX  Reset jump
4005 : JP XXXX  Interrupt jump
4008 : JP XXXX  Jump to important routines
400B : (not used)
400E : JP XXXX  Jump for AUTORUN.BAS search
4011 : XX XX    Pointer to Device Name (e.g., "COM1:")
4013 : XX XX    Pointer to Token Table (+0036)
4015 : JP XXXX  Jump for File processing
```

### Working Memory Allocation for ROM Modules

ROM modules can allocate working memory via `CALL 02DFH`. Parameters: DE = size in bytes, C = module number (Creg).

| Creg | Purpose |
|------|---------|
| 00 | Standard system memory |
| 01-07 | ROM Bank 1-7, Start 4000 (EXROM1-EXROM7) |
| 08-0E | ROM Bank 1-7, Start 6000 (EXROM8-EXROME) |
| 0F | COM buffer |
| 10 | File buffer (DE = n * 313 bytes) |

### Slot Management System Addresses

| Address Range | Purpose |
|---------------|---------|
| F015-F01EH | Slot S1 descriptor |
| F01F-F028H | Slot S2 descriptor |
| F029-F02CH | Slot S0 descriptor |
| F050-F053H | S1: EPROM or write-protected |
| F054-F055H | S1: RAM only |
| F056-F059H | S2: EPROM or write-protected |
| F05A-F05BH | S2: RAM only |
| F07DH | Mirror of Port 3D state |
| F0AE-F0AFH | ROM module bitmaps |
| F0DC-F0DDH | Boot bank and address |
| F123-F126H | Coded module config (for reset) |

### Boot Sequence

1. Reset cause determined (stored at FA1BH; the source says F1ABH, but the ROM writes FA1BH at P0-B0 `0368H`, see `PC-1600-SubCpu-LU57813P.md` §4.1). Bits: b0=ALL RESET, b1=Internal RESET, b2=External RESET, b4=POWER ON, b5=External POWER ON, b6=WAKE$(0), b7=WAKE$(I)=CI
2. Peripheral reset and device identification via ROM-Bit scan
3. `CALL 4002` issued to all devices (A=07: device can deregister)
4. Memory module detection (changed config sets FA23H bit b7 = "NEW0?")
5. Power-on test (can program resume from `POWER AOFF`?)
6. Boot search priority:
   1. Peripheral device (Floppy) -- `CALL 4002, A=05`
   2. Found peripheral -- `CALL 4002, A=06`
   3. System software (EPROM)
   4. System software (RAM)
   5. Jump to bank (F0DCH), address (F0DDH)

---
