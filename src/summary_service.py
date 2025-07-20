"""Provides a function to generate a summary from text using the Gemini API."""

import logging
import textwrap
from pathlib import Path

from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types import GenerateContentResponse

logger: logging.Logger = logging.getLogger(__name__)


class SummaryError(Exception):
    """Custom exception for errors during summary generation."""

    pass


def generate_summary(
    gemini_model: GenerativeModel,
    user_language: str,
    transcription_file_path: Path,
) -> str | None:
    """Read a transcription file and generates a summary using the Gemini model.

    This function validates the input file, constructs a prompt, calls the
    Gemini API, and returns the generated summary text in memory.

    Args:
        gemini_model (GenerativeModel): The initialized Gemini model instance.
        user_language (str): The target language for the summary.
        transcription_file_path (Path): The path to the text file containing the
                                        transcription or caption.

    Returns:
        str: The generated summary text.

    Raises:
        SummaryError: If the input file is not found or the API call fails.

    """
    if not transcription_file_path.exists():
        logger.error("Transcription file not found")
        raise FileNotFoundError("Transcription file not found")

    with transcription_file_path.open("r", encoding="utf-8") as f:
        transcription_content: str = f.read()
        prompt: str = textwrap.dedent(f"""
            You are an expert summarizer with a knack for clarity and a great sense of humor. Your mission is to distill the following video transcript into a summary that is natural, engaging, and easy to read, as if a friend were explaining the main points.

            Rules:

            Core Mission: Summarize all key points with clarity and objectivity. Capture the essence of the content.
            Formatting Freedom: Feel free to use bullet points, standard paragraphs, or a hybrid format—whichever presents the information most effectively and clearly.
            Word Count: Be as concise as possible, but you can go up to 2000 words if the content's complexity truly justifies it. No need to fill space unnecessarily.
            Match the Vibe: If the video is casual and humorous, reflect that with some clever wit, but keep the core information sharp. If the content is serious, dial back the jokes but maintain an engaging, non-robotic tone. A light, witty remark is fine even in serious topics.
            Be Seamless: Dive right into the summary. Do not use opening phrases like "This is a summary of..." or "The video discusses...".
            Output Language: The summary must be written in {user_language}. Always output in Markdown format.
            Content: {transcription_content}
            """)  # noqa: E501
    try:
        res: GenerateContentResponse = gemini_model.generate_content(prompt)
        logger.info("Summary generated successfully")
        return res.text
    except Exception as e:
        logger.exception("Failed to generate summary")
        raise SummaryError(f"Failed to generate summary: {e}") from e
