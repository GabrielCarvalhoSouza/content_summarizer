import tempfile
from typing import Any

import whisper
from flask import Flask, Response, jsonify, request
from werkzeug.datastructures import FileStorage
from whisper import Whisper

app: Flask = Flask(__name__)
whisper_model: Whisper = whisper.load_model("base")


@app.route("/transcribe", methods=["POST"])
def transcribe() -> Response | tuple[Response, int]:
    audio_file: FileStorage | None = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio file uploaded"}), 400

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3") as temp_f:
            temp_filename: str = temp_f.name
            audio_file.save(temp_filename)
            transcription: dict[str, Any] = whisper_model.transcribe(temp_filename)
            return jsonify({"transcription": transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)
