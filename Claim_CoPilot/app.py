"""
ClaimCopilot - Interactive CLI Demo

Usage:
    python app.py

Menu:
  1) Paste claim text
  2) Load claim from .txt file
  3) Exit

Notes:
  - When pasting text, finish by typing '///END' on a new line.
  - If no OPENAI_API_KEY is set, LLM-dependent parts will show '[LLM disabled]'.
"""

import os
import sys
from pathlib import Path
from typing import Optional

# --- Locate project root and src folder --------------------------------------

BASE = Path(__file__).resolve().parent
SRC = BASE / "src"

if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

# --- Import orchestrator and state -------------------------------------------

from orchestrator import Orchestrator  # type: ignore
from state import ClaimState  # type: ignore

END_MARKER = "///END"

# --- Pretty-print helpers ----------------------------------------------------

def print_section(title: str):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def print_dict(d: dict, indent: int = 2):
    if not d:
        print(" " * indent + "(none)")
        return
    for k, v in d.items():
        print(" " * indent + f"{k}: {v}")

def pause():
    """Simple pause so the user can read output before the menu reappears."""
    try:
        input("\n[Press Enter to return to the main menu]")
    except EOFError:
        # In some environments (e.g., non-interactive), just skip the pause.
        print()

def show_header():
    print("=" * 60)
    print("           ClaimCopilot - Agentic Claim Demo")
    print("=" * 60)
    print("This demo will run your multi-agent pipeline on claim text.")
    print("If no OPENAI_API_KEY is set, LLM parts will show '[LLM disabled]'.")
    print("-" * 60)
    print(f"When pasting text, finish by typing '{END_MARKER}' on a new line.")
    print("-" * 60)
    print()

# --- Core function to run pipeline on one claim text -------------------------

def run_claim(text: str, save_dir: Optional[Path] = None) -> ClaimState:
    """
    Run the full agentic workflow on a single claim text.
    Returns the final ClaimState.
    """
    orc = Orchestrator()
    state = orc.run(text)

    # Pretty print results
    print_section("RAW TEXT")
    print(text)

    print_section("EXTRACTED FIELDS")
    print_dict(state.extracted_fields)

    print_section("TRIAGE")
    print_dict(state.triage)

    print_section("ISSUES")
    if state.issues:
        for issue in state.issues:
            print("  -", issue)
    else:
        print("  (none)")

    print_section("SUMMARY")
    print(state.summary or "(no summary)")

    print_section("TRACE (Agents that ran)")
    for step in state.trace:
        print(f"  [{step['timestamp']}] {step['agent']} -> {step['action']}")

    # Optionally save JSON output
    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        fname = save_dir / "claim_result.json"
        fname.write_text(state.to_json(), encoding="utf-8")
        print_section("SAVED")
        print(f"Saved JSON result to: {fname}")

    return state

# --- Simple menu / CLI loop --------------------------------------------------

def read_text_from_file(path_str: str) -> str:
    path = Path(path_str)
    if not path.exists():
        print(f"[Error] File not found: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[Error] Could not read file: {e}")
        return ""

def read_multiline_input() -> str:
    """
    Read multiline claim text from stdin until the END_MARKER is entered.
    This avoids weird behavior with blank lines in some environments.
    """
    print("\nPaste your claim text below.")
    print(f"When you're done, type '{END_MARKER}' on a new line and press Enter.")
    print("-" * 60)

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            # End of input stream
            break
        if line.strip() == END_MARKER:
            break
        lines.append(line)

    return "\n".join(lines).strip()

def main():
    show_header()
    outputs_dir = BASE / "outputs"

    try:
        while True:
            print("\nMenu:")
            print("  1) Paste claim text")
            print("  2) Load claim from .txt file")
            print("  3) Exit")
            choice = input("Choose an option [1-3]: ").strip()

            if choice == "3":
                print("\nExiting. Goodbye!")
                break

            elif choice == "1":
                text = read_multiline_input()
                if not text:
                    print("[Warning] No text entered. Try again.")
                    continue

                run_claim(text, save_dir=outputs_dir)
                pause()

            elif choice == "2":
                path_str = input("Enter path to .txt file: ").strip()
                if not path_str:
                    print("[Warning] No path entered. Try again.")
                    continue

                text = read_text_from_file(path_str)
                if not text.strip():
                    print("[Warning] File is empty or could not be read.")
                    continue

                run_claim(text, save_dir=outputs_dir)
                pause()

            else:
                print("[Warning] Invalid choice. Please select 1, 2, or 3.")

    except KeyboardInterrupt:
        print("\n\n[Interrupted] Exiting ClaimCopilot. Goodbye!")

if __name__ == "__main__":
    main()
