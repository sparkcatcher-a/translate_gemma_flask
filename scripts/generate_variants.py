import re
import requests
import yaml

URL = "https://ollama.com/library/translategemma"
resp = requests.get(URL, timeout=15)
text = resp.text
# Find all table-like entries of the form | code | Language |
matches = re.findall(r"\|\s*([A-Za-z0-9_\-]+)\s*\|\s*([^\|\n]+)", text)
variants_map = {}
for code, name in matches:
    code = code.strip()
    name = name.strip()
    # filter out header/noise
    if not code or code.lower() in ("code", "------"):
        continue
    if name.lower().strip() in ("language", "----------"):
        continue
    # basic sanity: code must start with a letter
    if not re.match(r"^[A-Za-z]", code):
        continue
    base = code.split('-')[0]
    variants_map.setdefault(base, [])
    # avoid duplicates
    if not any(v['code'] == code for v in variants_map[base]):
        variants_map[base].append({'code': code, 'name': name})

# Sort variants for each base by code
for base in variants_map:
    variants_map[base] = sorted(variants_map[base], key=lambda v: v['code'])

out = {'language_variants': variants_map}
with open('variants.yaml', 'w', encoding='utf-8') as f:
    yaml.safe_dump(out, f, sort_keys=True, allow_unicode=True)

print('Wrote variants.yaml with', len(variants_map), 'bases')
