from pathlib import Path


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

    if "sandbox" not in path.parts:
        raise Exception("Path to file is not inside the sandbox")

    if path.suffix != ".py":
        raise Exception(f"File {path.name} format is not valid (must be .py)")

    if not test:
        if not path.exists():
            raise Exception(f"Path {path_to_file} does not exist")

    else:
        if not (path.name.startswith("test_") or path.name.endswith("_test.py")):
            raise Exception(f"Path {path_to_file} is not a valid test file path")

        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
    except PermissionError as e:
        raise PermissionError(f"No permission to write file {path}: {e}")
    except Exception as e:
        raise Exception(f"Failed to write file {path}: {e}")

    return True

     
       
     
