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
        raise Exception("Failed to execute pytest!")
