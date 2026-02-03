import os
import subprocess
from typing import Optional, Dict


def analyse_file(path_to_file: str) -> Optional[Dict[str, str]]:
    """Analyse a Python file using pylint and return the report and score."""

    if not os.path.exists(path_to_file):
        raise FileNotFoundError(f"path {path_to_file} does not exist")

    if not path_to_file.endswith(".py"):
        raise ValueError(f"file {path_to_file} format not valid")

    try:
        result = subprocess.run(
            ["pylint", path_to_file],
            capture_output=True,
            text=True
        )

        report = result.stdout + result.stderr

        score = None
        marker = "Your code has been rated at "
        if marker in report:
            score = report.split(marker)[1].split("/10")[0].strip()

        return {
            "score": score,
            "details": report
        }

    except Exception as e:
        raise RuntimeError(f"Failed to analyse file {path_to_file}") from e
