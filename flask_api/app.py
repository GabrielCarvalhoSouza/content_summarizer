import os
import tempfile

import whisper
from flask import Flask, jsonify, request

app = Flask(__name__)
whisper_model = whisper.load_model("base")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "Nenhum arquivo de áudio enviado"}), 400

    temp_f = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp_filename = temp_f.name

    try:
        audio_file.save(temp_filename)
        temp_f.close()
        transcription = whisper_model.transcribe(temp_filename)
    finally:
        os.remove(temp_filename)

    return jsonify({"transcription": transcription})


if __name__ == "__main__":
    app.run(debug=True, port=8000)
