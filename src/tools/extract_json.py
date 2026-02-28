import re
import json
import os
from pathlib import Path

def strip_markdown_fences(output: str) -> str:
    """
    Removes Markdown code fences like ```json ... ```
    ONLY if they exist.
    Leaves text untouched otherwise.
    """
    text = output.strip()

    if text.startswith("```"):
        # Remove opening fence
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)

        # Remove closing fence
        text = re.sub(r"\n?```$", "", text)

    return text.strip()

def extract_json(output: str) -> str:
    """
    Extracts the first valid JSON object from a string.
    Ignores extra text before/after the JSON.

    Args:
        output (str): Raw LLM output.

    Returns:
        str: JSON string safe to parse with json.loads()

    Raises:
        ValueError: If no JSON object could be found.
    """
    # Match the first outermost {...} block
    stack = []
    start_idx = None
    for i, c in enumerate(output):
        if c == '{':
            if not stack:
                start_idx = i
            stack.append('{')
        elif c == '}':
            if stack:
                stack.pop()
                if not stack and start_idx is not None:
                    return output[start_idx:i + 1]

    raise ValueError("No JSON object found in LLM output")

def sanitize_llm_json(output: str) -> str:
    """
    Sanitizes a JSON string returned by an LLM:
    - fixes unescaped newlines inside string values
    - fixes unescaped quotes inside string values
    - re-dumps JSON to ensure it's valid

    Args:
        output (str): Raw JSON string from LLM

    Returns:
        str: Properly formatted JSON string
    """
    try:
        # Load JSON safely
        data = json.loads(output)
    except json.JSONDecodeError as e:
        # Sometimes LLM breaks quotes/newlines
        # Replace unescaped newlines inside strings
        output_fixed = re.sub(r'(?<!\\)\n', r'\\n', output)
        # Replace unescaped double quotes inside strings (naive fix)
        output_fixed = re.sub(r'(?<!\\)"', r'\"', output_fixed)
        data = json.loads(output_fixed)

    # Re-dump to ensure valid JSON
    return json.dumps(data, ensure_ascii=False)

def is_subpath(parent: Path, child: Path) -> bool:
    parent = parent.resolve()
    child = child.resolve()

    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False