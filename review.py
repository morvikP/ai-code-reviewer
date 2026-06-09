#!/usr/bin/env python3
"""
AI Code Reviewer — CLI tool for code review via DeepSeek API.

Usage:
    python review.py path/to/file.py
    python review.py path/to/file.js --model deepseek-reasoner
    python review.py path/to/file.py --output review.md
    python review.py path/to/file.py --focus security
    python review.py path/to/folder --recursive
    python review.py old.py new.py --diff
"""

import sys
import os
import json
import http.client
import urllib.parse
from pathlib import Path


# ─── Configuration ───────────────────────────────────────────────────────────

DEEPSEEK_API_URL = "api.deepseek.com"
DEEPSEEK_API_ENDPOINT = "/v1/chat/completions"
DEFAULT_MODEL = "deepseek-chat"
SUPPORTED_EXTENSIONS = {".js", ".py", ".html", ".css", ".ts", ".jsx", ".tsx", ".json", ".md", ".txt", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"}

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


# ─── Error handling ──────────────────────────────────────────────────────────

class ReviewError(Exception):
    """Base exception for review tool."""
    pass


def die(message: str, exit_code: int = 1):
    """Print error message and exit."""
    print(f"{Colors.RED}Error:{Colors.END} {message}", file=sys.stderr)
    sys.exit(exit_code)


# ─── API key loading ─────────────────────────────────────────────────────────

def load_api_key() -> str:
    """Load DeepSeek API key from environment variable or .env file."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        return api_key

    # Try to load from .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("DEEPSEEK_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip("\"'")
                    return api_key

    die(
        "API key not found.\n\n"
        "Create a .env file in the project directory with:\n"
        "    DEEPSEEK_API_KEY=sk-your-key-here\n\n"
        "Or set the environment variable:\n"
        "    set DEEPSEEK_API_KEY=sk-your-key-here  (Windows)\n"
        "    export DEEPSEEK_API_KEY=sk-your-key-here  (Linux/Mac)"
    )


# ─── File reading ────────────────────────────────────────────────────────────

def read_file(file_path: str) -> str:
    """Read file contents. Raises ReviewError if file doesn't exist or is unsupported."""
    path = Path(file_path)

    if not path.exists():
        raise ReviewError(f"File not found: {file_path}")

    if not path.is_file():
        raise ReviewError(f"Not a file: {file_path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        print(f"{Colors.YELLOW}Warning:{Colors.END} Unsupported extension '{ext}'. Proceeding anyway...", file=sys.stderr)

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ReviewError(f"Cannot read file (not a text file): {file_path}")
    except PermissionError:
        raise ReviewError(f"Permission denied: {file_path}")
    except OSError as e:
        raise ReviewError(f"Error reading file: {e}")


# ─── Prompt building ─────────────────────────────────────────────────────────

def build_prompt(code: str, focus: str = None, diff_mode: bool = False) -> str:
    """Build the review prompt based on focus area and mode."""
    focus_instructions = {
        "security": "Focus specifically on security vulnerabilities: SQL injection, XSS, CSRF, insecure authentication, hardcoded secrets, unsafe deserialization, path traversal, etc.",
        "performance": "Focus specifically on performance issues: slow algorithms, unnecessary allocations, blocking I/O, memory leaks, N+1 queries, caching opportunities, etc.",
        "readability": "Focus specifically on code readability and maintainability: naming conventions, code organization, comments, complexity, adherence to language idioms, DRY violations, etc.",
        "bugs": "Focus specifically on finding potential bugs and logical errors: off-by-one errors, race conditions, null pointer dereferences, type errors, edge cases, etc.",
    }

    base_prompt = (
        "You are an expert code reviewer. Analyze the following code and provide a structured review.\n"
    )

    if diff_mode:
        base_prompt = (
            "You are an expert code reviewer. Below are two versions of code (OLD and NEW). "
            "Analyze the changes and evaluate them:\n"
            "- Are the changes correct and bug-free?\n"
            "- Do they follow best practices?\n"
            "- Are there any potential issues introduced?\n"
            "- Suggestions for improvement.\n\n"
        )

    if focus and focus in focus_instructions:
        base_prompt += focus_instructions[focus] + "\n\n"
    else:
        base_prompt += (
            "Cover the following aspects:\n"
            "1. Potential bugs and issues\n"
            "2. Code quality and readability\n"
            "3. Performance considerations\n"
            "4. Security concerns\n"
            "5. Suggestions for improvement\n\n"
        )

    base_prompt += "Here is the code to review:\n\n```\n" + code + "\n```\n"
    return base_prompt


# ─── API call ────────────────────────────────────────────────────────────────

def call_deepseek(prompt: str, model: str = DEFAULT_MODEL) -> dict:
    """Send request to DeepSeek API and return parsed JSON response."""
    api_key = load_api_key()

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
        "stream": False
    }

    body = json.dumps(payload)

    try:
        conn = http.client.HTTPSConnection(DEEPSEEK_API_URL, timeout=120)
        conn.request(
            "POST",
            DEEPSEEK_API_ENDPOINT,
            body=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        response = conn.getresponse()
        raw_data = response.read().decode("utf-8")
        conn.close()
    except http.client.HTTPException as e:
        raise ReviewError(f"HTTP error: {e}")
    except ConnectionRefusedError:
        raise ReviewError("Connection refused. Check your internet connection.")
    except TimeoutError:
        raise ReviewError("Request timed out. The API took too long to respond.")
    except OSError as e:
        raise ReviewError(f"Network error: {e}")

    if response.status != 200:
        try:
            error_data = json.loads(raw_data)
            error_msg = error_data.get("error", {}).get("message", raw_data)
        except (json.JSONDecodeError, AttributeError):
            error_msg = raw_data
        raise ReviewError(f"API returned HTTP {response.status}: {error_msg}")

    try:
        result = json.loads(raw_data)
    except json.JSONDecodeError:
        raise ReviewError(f"Failed to parse API response: {raw_data[:200]}")

    return result


def parse_review_response(response: dict) -> str:
    """Extract review text from DeepSeek API response."""
    try:
        content = response["choices"][0]["message"]["content"]
        return content.strip()
    except (KeyError, IndexError, TypeError) as e:
        raise ReviewError(f"Unexpected API response format: {e}")


# ─── Output formatting ───────────────────────────────────────────────────────

def print_review(review_text: str, file_path: str, model: str):
    """Print review with nice formatting."""
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}╔{'═' * 60}╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║  📋 Code Review Report{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.END}  File: {Colors.CYAN}{file_path}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║{Colors.END}  Model: {Colors.YELLOW}{model}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚{'═' * 60}╝{Colors.END}")
    print()
    print(review_text)
    print()
    print(f"{Colors.BOLD}{Colors.BLUE}╔{'═' * 60}╗{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}║  ✅ Review complete{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚{'═' * 60}╝{Colors.END}")
    print()


def save_review_md(review_text: str, file_path: str, model: str, output_path: str):
    """Save review to a Markdown file."""
    content = f"""# Code Review Report

- **File:** `{file_path}`
- **Model:** `{model}`
- **Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{review_text}

---

*Generated by AI Code Reviewer*
"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"{Colors.GREEN}Review saved to:{Colors.END} {output_path}")
    except OSError as e:
        raise ReviewError(f"Failed to save output file: {e}")


# ─── Diff mode ───────────────────────────────────────────────────────────────

def compute_diff(old_content: str, new_content: str) -> str:
    """Simple diff representation (unified-like)."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    import difflib
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile="old", tofile="new",
        n=3
    )
    return "".join(diff)


# ─── Recursive mode ──────────────────────────────────────────────────────────

def find_supported_files(directory: str) -> list:
    """Recursively find all supported files in a directory."""
    path = Path(directory)
    if not path.is_dir():
        return [str(path)] if path.suffix.lower() in SUPPORTED_EXTENSIONS else []

    files = []
    for p in path.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(str(p))
    return sorted(files)


# ─── CLI argument parsing ────────────────────────────────────────────────────

def parse_args() -> dict:
    """Parse command-line arguments manually (no argparse)."""
    args = sys.argv[1:]
    if not args:
        print(f"{Colors.BOLD}AI Code Reviewer{Colors.END}")
        print()
        print("Usage:")
        print("  python review.py <file>                         Review a single file")
        print("  python review.py <file> --model <model>         Choose model")
        print("  python review.py <file> --output <file.md>      Save review to file")
        print("  python review.py <file> --focus <topic>         Focus on topic")
        print("  python review.py <dir> --recursive              Review all files in dir")
        print("  python review.py <old> <new> --diff             Diff review mode")
        print()
        print("Models: deepseek-chat (default), deepseek-reasoner")
        print("Focus: security, performance, readability, bugs")
        sys.exit(0)

    result = {
        "files": [],
        "model": DEFAULT_MODEL,
        "output": None,
        "focus": None,
        "recursive": False,
        "diff": False,
    }

    i = 0
    positional = []
    while i < len(args):
        arg = args[i]
        if arg == "--model" and i + 1 < len(args):
            result["model"] = args[i + 1]
            i += 2
        elif arg == "--output" and i + 1 < len(args):
            result["output"] = args[i + 1]
            i += 2
        elif arg == "--focus" and i + 1 < len(args):
            result["focus"] = args[i + 1]
            i += 2
        elif arg == "--recursive":
            result["recursive"] = True
            i += 1
        elif arg == "--diff":
            result["diff"] = True
            i += 1
        elif arg.startswith("--"):
            die(f"Unknown option: {arg}")
        else:
            positional.append(arg)
            i += 1

    result["files"] = positional
    return result


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    try:
        opts = parse_args()

        # Diff mode: two files
        if opts["diff"]:
            if len(opts["files"]) != 2:
                die("Diff mode requires exactly two files: python review.py old.py new.py --diff")
            old_code = read_file(opts["files"][0])
            new_code = read_file(opts["files"][1])
            diff_text = compute_diff(old_code, new_code)
            if not diff_text.strip():
                die("Files are identical — nothing to review.")
            prompt = build_prompt(diff_text, focus=opts["focus"], diff_mode=True)
            file_label = f"{opts['files'][0]} → {opts['files'][1]}"
            response = call_deepseek(prompt, model=opts["model"])
            review = parse_review_response(response)
            print_review(review, file_label, opts["model"])
            if opts["output"]:
                save_review_md(review, file_label, opts["model"], opts["output"])
            return

        # Recursive mode
        if opts["recursive"]:
            if len(opts["files"]) != 1:
                die("Recursive mode requires exactly one directory: python review.py <dir> --recursive")
            dir_path = opts["files"][0]
            if not os.path.isdir(dir_path):
                die(f"Not a directory: {dir_path}")
            files = find_supported_files(dir_path)
            if not files:
                die(f"No supported files found in {dir_path}")
            print(f"{Colors.BOLD}Found {len(files)} file(s) to review.{Colors.END}")
            for f in files:
                print(f"\n{Colors.BOLD}{Colors.BLUE}{'─' * 60}{Colors.END}")
                print(f"{Colors.BOLD}Reviewing: {Colors.CYAN}{f}{Colors.END}")
                print(f"{Colors.BOLD}{Colors.BLUE}{'─' * 60}{Colors.END}")
                code = read_file(f)
                prompt = build_prompt(code, focus=opts["focus"])
                response = call_deepseek(prompt, model=opts["model"])
                review = parse_review_response(response)
                print_review(review, f, opts["model"])
            return

        # Single file mode
        if len(opts["files"]) != 1:
            die("Expected a single file path. Use --help for usage.")

        file_path = opts["files"][0]
        code = read_file(file_path)
        prompt = build_prompt(code, focus=opts["focus"])
        response = call_deepseek(prompt, model=opts["model"])
        review = parse_review_response(response)
        print_review(review, file_path, opts["model"])

        if opts["output"]:
            save_review_md(review, file_path, opts["model"], opts["output"])

    except ReviewError as e:
        die(str(e))
    except KeyboardInterrupt:
        die("Interrupted by user.", exit_code=130)


if __name__ == "__main__":
    main()
