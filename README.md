# cybersec-telegram-bot

Cybersecurity Telegram bot built to answer defensive security questions with context-aware responses from Ollama.

## Description

A local Telegram bot that provides cybersecurity guidance, including CVEs, Nmap, Splunk, Wireshark, hardening, and defensive best practices. The bot uses LangChain to structure prompts and Ollama as the language model backend.

## Tech Stack

- `python-telegram-bot` — Telegram bot API client.
- `langchain` — prompt and conversation workflow management.
- `langchain-ollama` — Ollama integration.
- `python-dotenv` — environment variable loading from `.env`.

## Installation

1. Create or activate a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## `.env` Configuration

Create a `.env` file in the project root with the following values:

```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL_NAME=llama3.1
```

- `TELEGRAM_TOKEN`: Telegram bot token from BotFather.
- `OLLAMA_BASE_URL`: Ollama server URL.
- `OLLAMA_MODEL_NAME`: Ollama model name.

## Start the Bot

Run the bot with:

```bash
python main.py
```

The bot will start polling Telegram updates and respond to incoming messages.

## Available Commands

- `/start` — sends a welcome message and short introduction.
- `/clear` — clears the current user's conversation history.

## Project Structure

```
.
├── bot.py          # Telegram bot handlers and main logic
├── chain.py        # Ollama prompt building and request handling
├── memory.py       # per-user chat memory manager
├── main.py         # application entry point
├── requirements.txt
├── pyproject.toml
└── README.md
```
