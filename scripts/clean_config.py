import yaml
import re

with open('config.yaml', 'r', encoding='utf-8') as f:
    cfg = yaml.safe_load(f)

with open('variants.yaml', 'r', encoding='utf-8') as f:
    variants = yaml.safe_load(f) or {}
language_variants = variants.get('language_variants', {})

# Build languages list with code and name. Prefer existing config name if present.
existing = {lang['code']: lang.get('name') for lang in cfg.get('languages', [])}
new_languages = []
for base in sorted(language_variants.keys()):
    name = existing.get(base)
    if not name:
        # derive name from first variant's name (strip parentheses)
        v = language_variants[base][0] if language_variants[base] else None
        if v:
            nm = v.get('name', base)
            # remove trailing parentheses content
            nm = re.sub(r"\s*\(.*\)", '', nm).strip()
            name = nm
        else:
            name = base
    new_languages.append({'code': base, 'name': name})

# Construct new config
new_cfg = {
    'model': cfg.get('model', 'translategemma:12b'),
    'api_base': None,
    'default_source': cfg.get('default_source', 'de'),
    'default_target': cfg.get('default_target', 'en'),
    'default_text': cfg.get('default_text', ''),
    'ollama_mode': cfg.get('ollama_mode', 'subprocess'),
    'timeout_seconds': cfg.get('timeout_seconds', 300),
    'favorite_languages': cfg.get('favorite_languages', ['en','de','fr']),
    'languages': new_languages,
}

with open('config.yaml', 'w', encoding='utf-8') as f:
    yaml.safe_dump(new_cfg, f, sort_keys=False, allow_unicode=True)

print('Wrote cleaned config.yaml with', len(new_languages), 'languages')
