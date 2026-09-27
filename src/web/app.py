from flask import Flask, request, render_template, send_file
from src.templates_store.manager import TemplateManager
from src.templates_store.filler import fill_docx
from src.stt.gigaam_client import GigaAMTranscriber
from src.llm.llm_client import LLMStructurer
import os, re
from docx import Document

app = Flask(__name__)
tm = TemplateManager()
transcriber = GigaAMTranscriber()
llm = LLMStructurer()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def extract_fields(docx_path):
    doc = Document(docx_path)
    text = "\n".join(p.text for p in doc.paragraphs)
    return list(set(re.findall(r"{{(\w+)}}", text)))

@app.route("/")
def index():
    return render_template("index.html", templates=tm.list_templates())

@app.route("/upload_template", methods=["POST"])
def upload_template():
    file = request.files["docx"]
    description = request.form["description"]
    templates_dir = os.path.join(DATA_DIR, "templates")
    os.makedirs(templates_dir, exist_ok=True)
    path = os.path.join(templates_dir, file.filename)
    file.save(path)
    tm.add_template(path, description)
    return "OK", 200

@app.route("/process/<template_id>", methods=["POST"])
def process(template_id):
    tpl = tm.get_template(template_id)
    if not tpl:
        return "Шаблон не найден", 404

    text = ""
    if "audio" in request.files and request.files["audio"].filename:
        audio = request.files["audio"]
        audio_path = os.path.join(DATA_DIR, "tmp_audio.wav")
        audio.save(audio_path)
        text = transcriber.transcribe_file(audio_path)
        print(f"📝 Распознанный текст: {text}") 
    else:
        text = request.form.get("text", "").strip()
        print(f"📝 Распознанный текст: {text}") 

    if not text:
        return "Нет данных: ни аудио, ни текст", 400

    fields = extract_fields(tpl["path"])
    values = llm.fill_template_fields(text, tpl["description"], fields)

    output_path = os.path.join(DATA_DIR, f"output_{template_id}.docx")
    fill_docx(tpl["path"], output_path, values)
    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)