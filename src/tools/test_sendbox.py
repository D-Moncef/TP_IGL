import os
from file_reader import read_file, read_dir
from file_writer import write_file
from pylint_inal import analyse_file
import subprocess

def run_pytest(target_dir: str):
    """
    Runs pytest safely on a sandbox directory.
    Returns structured results.
    """
    try:
        result = subprocess.run(
            ["pytest", target_dir],
            capture_output=True,
            text=True
        )

        return {
            "passed": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        return {
            "passed": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }
