import subprocess
import sys
from pathlib import Path


def main():
    base_dir = Path(__file__).resolve().parent
    for script in ["trends_save.py", "trends_plot.py"]:
        script_path = base_dir / script
        print(f"\n=== Running {script} ===")
        subprocess.run([sys.executable, str(script_path)], cwd=base_dir, check=True)


if __name__ == "__main__":
    main()
