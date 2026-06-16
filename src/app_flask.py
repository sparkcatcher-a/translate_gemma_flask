import os
import yaml
from flask import Flask, render_template, request, jsonify
from gemma_client import translate

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

with open(os.path.join(BASE_DIR, "config.yaml"), "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)


@app.route("/")
def index():
    return render_template(
        "index.html",
        default_source=CFG.get("default_source", "en"),
        default_target=CFG.get("default_target", "de"),
        default_model=CFG.get("model"),
        default_text=CFG.get("default_text", ""),
        languages=CFG.get("languages", [
            {"code": "en", "name": "English"},
            {"code": "de", "name": "German"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "it", "name": "Italian"},
            {"code": "ja", "name": "Japanese"},
        ]),
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
