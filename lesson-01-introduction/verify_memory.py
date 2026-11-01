"""Reproduce lesson 1 memory arithmetic; no hardware access or external dependencies.

Run: python verify_memory.py
Reads device-facts.json beside this file and writes memory-results.json there.
Input capacities are manual transcriptions from ST DS9118 Rev 14, Table 2,
STM32F303xB. This script checks arithmetic, not the silicon capacity itself.
"""
import json
from pathlib import Path

base = Path(__file__).resolve().parent
facts = json.loads((base / 'device-facts.json').read_text(encoding='utf-8'))
assert facts['part'] == 'STM32F303CBT6'
assert (facts['flash_kib'], facts['main_sram_kib'], facts['ccm_kib']) == (128, 32, 8)
flash = facts['flash_kib'] * 1024
sram = facts['main_sram_kib'] * 1024
ccm = facts['ccm_kib'] * 1024
buffer_bytes = facts['buffer_elements'] * facts['buffer_element_bytes']
assert (flash, sram, ccm, buffer_bytes) == (131072, 32768, 8192, 4096)
assert buffer_bytes <= sram
result = {
    'part': facts['part'],
    'bytes_per_kib': 1024,
    'bits_per_byte': 8,
    'flash_bytes': flash,
    'main_sram_bytes': sram,
    'ccm_bytes': ccm,
    'total_volatile_ram_bytes': sram + ccm,
    'total_volatile_ram_kib': (sram + ccm) // 1024,
    'example_uint32_buffer_elements': facts['buffer_elements'],
    'example_buffer_bytes': buffer_bytes,
    'main_sram_after_buffer_only_bytes': sram - buffer_bytes,
    'note': 'Illustrative budget only; stack, globals, heap and alignment are not subtracted. Not measured free RAM.',
}
(base / 'memory-results.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
