import locale
import os
import textwrap

import google.generativeai as genai
from dotenv import load_dotenv

from path_manager import path_manager

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)  # type: ignore[reportPrivateImportUsage]
gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")  # type: ignore[reportPrivateImportUsage]


class ResumeError(Exception):
    pass


def resume():
    if not path_manager.transcription_file_path.exists():
        raise FileNotFoundError("Transcription file not found")

    user_language, _ = locale.getdefaultlocale()
    with open(path_manager.transcription_file_path, "r", encoding="utf-8") as f:
        transcription_content = f.read()
        prompt = textwrap.dedent(f"""
            You are an expert summarizer with a knack for clarity and a great sense of humor. Your mission is to distill the following video transcript into a summary that is natural, engaging, and easy to read, as if a friend were explaining the main points.

            Rules:

            Core Mission: Summarize all key points with clarity and objectivity. Capture the essence of the content.
            Formatting Freedom: Feel free to use bullet points, standard paragraphs, or a hybrid format—whichever presents the information most effectively and clearly.
            Word Count: Be as concise as possible, but you can go up to 2000 words if the content's complexity truly justifies it. No need to fill space unnecessarily.
            Match the Vibe: If the video is casual and humorous, reflect that with some clever wit, but keep the core information sharp. If the content is serious, dial back the jokes but maintain an engaging, non-robotic tone. A light, witty remark is fine even in serious topics.
            Be Seamless: Dive right into the summary. Do not use opening phrases like "This is a summary of..." or "The video discusses...".
            Output Language: The summary must be written in {user_language}. Always output in Markdown format.
            Content: {transcription_content}
            """)
    try:
        res = gemini_model.generate_content(prompt)
        with open(path_manager.resume_file_path, "w", encoding="utf-8") as f:
            f.write(res.text)
    except Exception as e:
        raise ResumeError(f"Failed to generate resume: {e}") from e
