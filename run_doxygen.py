
#!/usr/bin/env python3
"""Run Doxygen using the Doxyfile next to this script."""

import shutil
import subprocess
import sys
from pathlib import Path


def run():
    script_dir = Path(__file__).resolve().parent
    config = script_dir / "Doxyfile"

    if not config.is_file():
        print(f"ERROR: Doxyfile not found: {config}", file=sys.stderr)
        return 1

    executable = shutil.which("doxygen")
    if executable is None:
        print("ERROR: doxygen was not found in PATH.", file=sys.stderr)
        return 1

    print(f"Using configuration: {config}")
    result = subprocess.run(
        [executable, str(config)],
        cwd=script_dir,
        check=False,
    )

    if result.returncode != 0:
        print(
            f"Doxygen failed with exit code {result.returncode}.",
            file=sys.stderr,
        )
        return result.returncode

    html_index = script_dir / "docs" / "html" / "index.html"
    print("Doxygen finished successfully.")

    if html_index.is_file():
        print(f"Documentation: {html_index}")

    return 0


if __name__ == "__main__":
    run()
