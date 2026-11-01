"""Verify saved before/after snapshots from an actual CubeMX regeneration."""
from pathlib import Path
import json

folder = Path(__file__).resolve().parent / 'regeneration-evidence'
before = (folder / 'main-before.c').read_text(encoding='utf-8')
after = (folder / 'main-after.c').read_text(encoding='utf-8')
checks = {
    'before_header_complete': before.startswith('/* USER CODE BEGIN Header */'),
    'after_header_complete': after.startswith('/* USER CODE BEGIN Header */'),
    'protected_declaration_before': 'volatile uint32_t lesson4_marker = 0U;' in before,
    'protected_declaration_after': 'volatile uint32_t lesson4_marker = 0U;' in after,
    'protected_assignment_before': 'lesson4_marker = 1U;' in before,
    'protected_assignment_after': 'lesson4_marker = 1U;' in after,
    'outside_comment_before': 'LESSON4_OUTSIDE_USER_CODE' in before,
    'outside_comment_removed': 'LESSON4_OUTSIDE_USER_CODE' not in after,
}
print(json.dumps(checks, indent=2))
if not all(checks.values()):
    raise SystemExit('Regeneration evidence verification failed.')
