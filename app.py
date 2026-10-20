from pathlib import Path
from threading import Thread

import webview
from flask import Flask, render_template, request
from werkzeug.serving import make_server


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR),
    static_folder=str(FRONTEND_DIR),
    static_url_path="/static",
)


@app.route("/", methods=["GET", "POST"])
def index():
    input_text = request.form.get("input_text", "")
    result = None

    if request.method == "POST":
        xml_file = request.files.get("xml_file")
        has_xml_file = bool(xml_file and xml_file.filename)

        if not input_text.strip() and not has_xml_file:
            result = "Enter some text or upload an XML file."
        elif has_xml_file and not xml_file.filename.lower().endswith(".xml"):
            result = "Upload an XML file."
        elif has_xml_file:
            try:
                result = xml_file.read().decode("utf-8-sig")
                if not result:
                    result = "The uploaded XML file is empty."
            except UnicodeDecodeError:
                result = "The XML file must use UTF-8 encoding."
        else:
            result = f"working {input_text}"

    return render_template("index.html", input_text=input_text, result=result)


def run_desktop():
    server = make_server("127.0.0.1", 0, app)
    server_thread = Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    url = f"http://127.0.0.1:{server.server_port}"

    webview.create_window(
        "Book Analyzer",
        url,
        width=1100,
        height=850,
        min_size=(640, 600),
    )
    try:
        webview.start()
    finally:
        server.shutdown()
        server_thread.join(timeout=5)
        server.server_close()


if __name__ == "__main__":
    run_desktop()
