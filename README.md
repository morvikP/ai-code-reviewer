# AI Code Reviewer

A minimal CLI tool for automated code review using the DeepSeek API. Built from scratch with Python — no frameworks, no API wrappers, just raw HTTP requests.

## Features

- ✅ Review single files (`.js`, `.py`, `.html`, `.css`, and more)
- ✅ Choose model: `deepseek-chat` (default) or `deepseek-reasoner`
- ✅ Focus areas: `security`, `performance`, `readability`, `bugs`
- ✅ Save review to Markdown file
- ✅ Recursive directory review
- ✅ Diff mode — compare two file versions
- ✅ Colorful terminal output
- ✅ Proper error handling (no Python tracebacks)

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-code-reviewer.git
cd ai-code-reviewer

# No dependencies needed — uses only Python standard library!
```

## Setup

1. Get a DeepSeek API key at [platform.deepseek.com](https://platform.deepseek.com/api_keys)
2. Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

3. Edit `.env` and add your key:

```
DEEPSEEK_API_KEY=sk-your-actual-key-here
```

Alternatively, set the environment variable:

```bash
# Windows
set DEEPSEEK_API_KEY=sk-your-actual-key-here

# Linux/Mac
export DEEPSEEK_API_KEY=sk-your-actual-key-here
```

## Usage

### Basic review

```bash
python review.py path/to/your/file.py
```

### Choose model

```bash
python review.py file.js --model deepseek-reasoner
```

### Focus on a specific topic

```bash
python review.py file.py --focus security
python review.py file.py --focus performance
python review.py file.py --focus readability
python review.py file.py --focus bugs
```

### Save review to file

```bash
python review.py file.html --output review.md
```

### Review all files in a directory

```bash
python review.py ./my-project --recursive
```

### Diff mode (compare two versions)

```bash
python review.py old.py new.py --diff
```

## Screenshot

![AI Code Reviewer in action](screenshot.png)

## How it works

1. Reads the source file
2. Builds a structured prompt for code review
3. Sends an HTTP POST request to `https://api.deepseek.com/v1/chat/completions`
4. Parses the JSON response
5. Displays the review with nice formatting

## Project structure

```
ai-code-reviewer/
├── review.py          # Main CLI program
├── .env.example       # Template for API key
├── .gitignore         # Prevents .env from being committed
└── README.md          # This file
```

## What I learned

- How to make raw HTTP requests to LLM APIs
- Why API keys must never be stored in code
- How tools like Cline, Aider, and OpenCode work under the hood
- JSON parsing and error handling in network applications

## License

MIT
