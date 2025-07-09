"""Flask API to transcribe audio file using Whisper.

POST /transcribe with a file named "audio" to transcribe the audio file
and return the full transcription result as a JSON object.

"""

import logging
import os
import tempfile
from collections.abc import Iterable
from pathlib import Path

import dotenv
from faster_whisper import WhisperModel
from faster_whisper.transcribe import Segment
from flask import Flask, Response, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.datastructures import FileStorage

app: Flask = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://",
)


parent_path: Path = Path(__file__).parent
logfile_path: Path = parent_path / "app.log"
log_formatter: logging.Formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s"
)
file_handler: logging.FileHandler = logging.FileHandler(
    logfile_path, mode="a", encoding="utf-8"
)
file_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

logger.addHandler(file_handler)


dotenv.load_dotenv(parent_path / ".env")
api_secret_key: str | None = os.getenv("API_SECRET_KEY")

if api_secret_key is None:
    logger.error("API_SECRET_KEY environment variable not set")
    raise ValueError("API_SECRET_KEY environment variable not set")

whisper_model = WhisperModel("base", device="cpu", compute_type="int8")


@app.route("/transcribe", methods=["POST"])
@limiter.limit("2 per minute, 5 per day")
def transcribe() -> Response | tuple[Response, int]:
    """Handle POST requests to /transcribe.

    This function transcribes the uploaded audio file and returns the
    full transcription result as a JSON object.

    Returns:
        - 200 OK: transcription result as JSON
        - 400 Bad Request: no audio file was uploaded
        - 401 Unauthorized: invalid API key
        - 500 Internal Server Error: an error occurred during transcription

    """
    if request.headers.get("X-Api-Key") != api_secret_key:
        logger.warning("Unauthorized request from %s", request.remote_addr)
        return jsonify({"error": "Unauthorized"}), 401

    logger.info("Request received from %s", request.remote_addr)
    audio_file: FileStorage | None = request.files.get("audio")
    if not audio_file:
        logger.warning("No audio file uploaded")
        return jsonify({"error": "No audio file uploaded"}), 400

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "audio.mp3"

            audio_file.save(temp_path)

            logger.info("Initializing transcription")

            segments: Iterable[Segment]
            segments, _ = whisper_model.transcribe(str(temp_path), beam_size=5)
            transcription_text: str = "".join(segment.text for segment in segments)

            logger.info("Transcription completed")
            return jsonify({"transcription": transcription_text})

    except Exception:
        logger.exception("Error occurred during transcription")
        return jsonify(
            {"error": "An internal error occurred during transcription."}
        ), 500


if __name__ == "__main__":
    app.run(debug=True, port=8000)
