import subprocess
import os
from pathlib import Path

def run_pytest(target_dir: str):
    """
    Runs pytest safely on a sandbox directory.
    Ensures the project root is in PYTHONPATH to avoid import errors.
    Returns structured results.
    """
    try:
        target_path = Path(target_dir).resolve()  # .../sandbox/hidden_dataset
        env = os.environ.copy()
        env["PYTHONPATH"] = str(target_path.parent)  # .../sandbox
        result = subprocess.run(
            ["pytest", str(target_path)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(target_path)  # run inside hidden_dataset
        )

        return {
            "passed": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        raise Exception(f"Failed to execute pytest: {e}")