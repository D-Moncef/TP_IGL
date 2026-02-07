import re

def extract_json(text: str) -> str:
    """
    Extract JSON content from a string that may be wrapped
    in ```json ... ``` or ``` ... ``` markers.
    """
    text = text.strip()

    # Match ```json ... ``` or ``` ... ```
    pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    match = re.match(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    # No markers → return as-is
    return text

def sanitize_llm_json(text: str) -> str:
    text = extract_json(text)  # from earlier
    # Remove triple-quoted docstrings
    text = re.sub(r'"""[\s\S]*?"""', '', text)
    return text.strip()