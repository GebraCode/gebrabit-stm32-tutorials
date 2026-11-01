"""Reproduce a hypothetical buffer budget; not measured free MCU RAM."""
import json
samples=1024
bytes_per_sample=2
print(json.dumps({"scenario":"hypothetical buffer only", "samples":samples,"bytes_per_sample":bytes_per_sample,"buffer_bytes":samples*bytes_per_sample,"buffer_kib":samples*bytes_per_sample/1024},indent=2))
