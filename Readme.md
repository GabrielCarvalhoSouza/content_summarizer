# Content Summarizer

## A tool to summarize YouTube videos using AI

Você já achou um vídeo do YouTube que você achou interessante o suficiente mas não tinha tempo para vê-lo? Com o Content Summarizer isso é possível! Obtenha resumos de alta qualidade de qualquer vídeo do Youtube completamente de graça através de um programa de linha de comando (CLI)!

## Features

- **Smart Caption/Transcription:** Automatically uses existing manual captions for speed, or falls back to highly accurate local transcription using Faster-Whisper.
- **Intelligent Summaries:** Leverages the Gemini API to generate clear, concise, and context-aware summaries.
- **Multi-language Support:** Delivers summaries in your system's native language.
- **Flexible Transcription:** Offers the choice between local processing (via Faster-Whisper) or a remote transcription API.
- **Performance Control:** Adjust the audio speed factor for faster transcriptions on local processing.
- **Simple & Powerful CLI:** A clean and intuitive command-line interface for easy use.

## Installation

### Prerequisites

You need to have Python 3.11+ and FFmpeg installed on your system.

### Recommended Installation

The best way to install is using `uv` to keep the environment isolated:

```bash
uv tool install content-summarizer
```

Or if you prefer to use `pipx`:

```bash
pipx install content-summarizer
```

You can also use the standard `pip`, but be aware that it will install the package in your global or current environment:

```bash
pip install content-summarizer
```

## Usage

### Basic Summarization

```bash
content-summarizer summarize "YOUR_YOUTUBE_URL_HERE"

# Example Usage
content-summarizer summarize "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Common Flags

```bash
# Reduce Verbosity
content-summarizer summarize "YOUR_YOUTUBE_URL_HERE" -q

# Change the audio speed factor for faster transcriptions (In this case the speed factor will be 3.0)
content-summarizer summarize "YOUR_YOUTUBE_URL_HERE" -s 3

# Change Whisper (Faster-Whisper) Model
content-summarizer summarize "YOUR_YOUTUBE_URL_HERE" -w large-v2

# Change Gemini Model
content-summarizer summarize "YOUR_YOUTUBE_URL_HERE" -g 2.5-pro
```

You can use multiple flags together, for a complete list of all flags use `content-summarizer -h` or `content-summarizer --help`
