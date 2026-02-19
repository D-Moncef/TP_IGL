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
        # Compute the project root (assumes target_dir is inside the project)
        target_path = Path(target_dir).resolve()
        project_root = target_path.parent

        # Prepare environment with PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)

        result = subprocess.run(
            ["pytest", str(target_path)],
            capture_output=True,
            text=True,
            env=env  # pass the updated environment
        )

        return {
            "passed": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        raise Exception(f"Failed to execute pytest: {e}")