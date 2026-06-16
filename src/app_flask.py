import os
import yaml
from flask import Flask, render_template, request, jsonify
import logging
from gemma_client import translate

logging.basicConfig(level=logging.DEBUG)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)




def load_offline_variants():
    """Load variants.yaml from disk if present. Returns mapping or None."""
    variants_path = os.path.join(BASE_DIR, "variants.yaml")
    if not os.path.exists(variants_path):
        return None
    try:
        with open(variants_path, "r", encoding="utf-8") as vf:
            data = yaml.safe_load(vf) or {}
            return data.get("language_variants", {})
    except Exception:
        return None


def save_variants_to_disk(variants_map):
    variants_path = os.path.join(BASE_DIR, "variants.yaml")
    try:
        with open(variants_path, "w", encoding="utf-8") as vf:
            yaml.safe_dump({"language_variants": variants_map}, vf, sort_keys=True, allow_unicode=True)
    except Exception:
        pass

# For offline-only mode we keep only load_offline_variants() and no online fetching.


@app.route("/")
def index():
    # Build base language list from config + variants.yaml (offline-only)
    configured_languages = CFG.get("languages") or []
    favorite_codes = CFG.get("favorite_languages", ["en", "de", "fr"])[:]
    favorite_set = set(favorite_codes)

    # Load variants from disk (variants.yaml) or fall back to config-defined variants
    language_variants = load_offline_variants()
    if language_variants is None:
        language_variants = {lang["code"]: lang.get("variants", []) for lang in configured_languages}

    # Build a base code -> display name map using configured languages first
    code_map = {lang["code"]: lang.get("name") for lang in configured_languages}

    base_codes = sorted(language_variants.keys(), key=lambda c: code_map.get(c, c))
    if not base_codes:
        base_codes = [lang["code"] for lang in configured_languages]

    languages = []
    for code in base_codes:
        languages.append({"code": code, "name": code_map.get(code, code)})

    # Ensure favorites appear first and are valid
    favorite_languages = [lang for code in favorite_codes for lang in languages if lang["code"] == code]
    other_languages = [lang for lang in languages if lang["code"] not in favorite_set]
    other_languages = sorted(other_languages, key=lambda lang: lang["name"])
    languages_sorted = favorite_languages + other_languages

    def get_variant_list(base_code):
        return language_variants.get(base_code, [])

    source_variants = get_variant_list(CFG.get("default_source", "de"))
    target_variants = get_variant_list(CFG.get("default_target", "en"))
    default_source_variant = source_variants[0]["code"] if source_variants else CFG.get("default_source")
    default_target_variant = target_variants[0]["code"] if target_variants else CFG.get("default_target")
    return render_template(
        "index.html",
        default_source=CFG.get("default_source", "de"),
        default_target=CFG.get("default_target", "en"),
        default_source_variant=default_source_variant,
        default_target_variant=default_target_variant,
        default_model=CFG.get("model"),
        default_text=CFG.get("default_text", ""),
        languages=languages_sorted,
        source_variants=source_variants,
        target_variants=target_variants,
        language_variants=language_variants,
    )


@app.route("/translate", methods=["POST"])
def do_translate():
    data = request.get_json() or {}
    source_code = data.get("source_code")
    target_code = data.get("target_code")
    source_name = data.get("source_name", source_code)
    target_name = data.get("target_name", target_code)
    text = data.get("text", "")
    model = data.get("model") or CFG.get("model")
    if not text.strip():
        return jsonify({"status": "error", "error": "Empty input"}), 400
    try:
        out = translate(
            source_name=source_name,
            source_code=source_code,
            target_name=target_name,
            target_code=target_code,
            text=text,
            model=model,
        )
        return jsonify({"status": "ok", "translation": out})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
