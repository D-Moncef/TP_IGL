from pathlib import Path

def normalize_newlines(text: str) -> str:
    """
    Converts escaped sequences like '\\n' into real newlines.
    """
    return text.encode("utf-8").decode("unicode_escape")

def write_file(path_to_file: str, content: str, test: bool) -> bool:
    """
    Write a Python file inside the sandbox.

    Rules:
    - Path must contain 'sandbox'
    - File must have a .py extension
    - If test=False: file path must already exist
    - If test=True: file name must start with 'test_' or end with '_test.py'
    """

    path = Path(path_to_file)

    sandbox = Path("sandbox").resolve()
    full_path = path.resolve()

    if sandbox not in full_path.parents:
        raise Exception("File write outside sandbox is forbidden")

    if full_path.suffix != ".py":
        raise Exception(f"File {full_path.name} format is not valid (must be .py)")

    if not test:
        full_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        if not (full_path.name.startswith("test_") or full_path.name.endswith("_test.py")):
            raise Exception(f"Path {path_to_file} is not a valid test file path")

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    try:
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(normalize_newlines(content))
    except PermissionError as e:
        raise PermissionError(f"No permission to write file {full_path}: {e}")
    except Exception as e:
        raise Exception(f"Failed to write file {full_path}: {e}")

    return True

     
       
     
