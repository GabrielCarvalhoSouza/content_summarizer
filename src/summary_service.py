"""Generate a summary from a transcription file using a generative AI model.

This module provides a function to generate a summary from a transcription file using
a generative AI model.

Classes:
    SummaryError: Custom exception for errors during summary generation.

Functions:
    generate_summary: Generate a summary from a transcription file using a generative
        AI model.

"""

import logging
import textwrap
from pathlib import Path

from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types import GenerateContentResponse

logger = logging.getLogger(__name__)


class SummaryError(Exception):
    """Custom exception for errors during summary generation."""

    pass


def generate_summary(
    gemini_model: GenerativeModel,
    user_language: str,
    transcription_file_path: Path,
) -> str | None:
    """Generate a summary from a transcription file using a generative AI model.

    Args:
        gemini_model (GenerativeModel): The generative AI model to use for summary
            generation.
        user_language (str): The language in which the summary should be generated.
        transcription_file_path (Path): The path to the transcription file.
        resume_file_path (Path): The path where the generated summary will be saved.

    Raises:
        FileNotFoundError: If the transcription file does not exist.
        SummaryError: If an error occurs during the generation of the summary.

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
        string_res: str = str(res)
        logger.info("Summary generated successfully")
        return string_res
    except Exception as e:
        logger.exception("Failed to generate summary")
        raise SummaryError(f"Failed to generate summary: {e}") from e
