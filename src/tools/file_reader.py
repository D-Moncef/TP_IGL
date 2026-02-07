import os 
from pathlib import Path

def read_file(path_to_file: str):
    """
    Read a Python file located inside the sandbox directory.
    """
    path = Path(path_to_file).resolve()

    # Enforce sandbox restriction
    sandbox_root = Path("sandbox").resolve()
    if sandbox_root not in path.parents:
        raise PermissionError("File is not inside sandbox")

    # Enforce Python files only
    if path.suffix != ".py":
        raise ValueError(f"File {path.name} is not a Python file")

    if not path.is_file():
        raise FileNotFoundError(f"{path} does not exist")

    return path.read_text(encoding="utf-8")

def read_dir(path_to_dir: str):
    """
    Read all Python files inside a directory (recursively).
    """
    path = Path(path_to_dir).resolve()

    if not path.is_dir():
        raise FileNotFoundError(f"{path_to_dir} is not a valid directory")

    content = {}

    for file_path in path.rglob("*.py"):
        content[str(file_path)] = read_file(str(file_path))

    return content

def read_dir_separate(path_to_dir: str):
    content = {"source_files": {}, "test_files": {}}
    path = Path(path_to_dir).resolve()

    if not path.is_dir():
        raise FileNotFoundError(f"{path_to_dir} is not a valid directory")

    for file_path in path.rglob("*.py"):
        try:
            file_content = read_file(path_to_dir)  # your existing read_file function
            
            # Decide if it is a test file
            if "test" in file_path.stem.lower() or "tests" in file_path.parts:
                content["test_files"][str(file_path)] = file_content
            else:
                content["source_files"][str(file_path)] = file_content

        except FileNotFoundError as e:
            raise e
        except PermissionError as e:
            raise e

    return content
