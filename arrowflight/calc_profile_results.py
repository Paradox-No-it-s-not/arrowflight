# parent.py
import argparse
import subprocess
import sys
import csv
import re
from pathlib import Path
import time


def main():
    parser = argparse.ArgumentParser(description="Calculate flights for a range of target-distances and -hights and write the output into a CSV file")
    parser.add_argument('profile_name', nargs='?', default='default', help='The name of the profile in the file arrows.json to be used for the calculations (default: default)')
    parser.add_argument('--x_values', nargs=3, type=float, default=[10.0, 2.0, 100.0], help='The start, step and end values for target distances in meters (default: 10 2 100)')
    parser.add_argument('--y_values', nargs=3, type=float, default=[-10,1,10], help='The start, step and end values for target heights in meters (default: -10 1 10)')
    

    args = parser.parse_args()
    profile_name = args.profile_name
    x_start, x_step, x_end = args.x_values
    y_start, y_step, y_end = args.y_values

    console_first = True           # steuert, ob --no-header an den Aufruf angehängt wird
    csv_header_written = False     # steuert, ob CSV-Header bereits in die Datei geschrieben wurde
    out_path = Path(profile_name + "_results.csv")

    def frange(start: float, stop: float, step: float):
        """Float-range generator (inclusive stop with small epsilon)."""
        x = float(start)
        eps = abs(step) * 1e-9
        if step == 0:
            raise ValueError("step must be non-zero")
        if step > 0:
            while x <= stop + eps:
                yield round(x, 10)
                x += step
        else:
            while x >= stop - eps:
                yield round(x, 10)
                x += step

    start = time.perf_counter()
    prev_len = 0

    with out_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        for x in frange(x_start, x_end + 1, x_step):
            for y in frange(y_start, y_end, y_step):
                # Erstelle die Befehlszeilenargumenteliste
                command = [
                    sys.executable,
                    "-m",
                    "arrowflight.flight",
                    str(x),
                    str(y),
                    profile_name,
                    "--no-plot",
                ]

                # nur ab dem zweiten Konsolenaufruf --no-header anhängen
                if not console_first:
                    command.append("--no-header")
                else:
                    console_first = False

                # write the running-command message in-place (same terminal line)
                msg = f"Running command: {' '.join(command)}"
                sys.stdout.write('\r' + msg + ' ' * max(0, prev_len - len(msg)))
                sys.stdout.flush()
                prev_len = len(msg)
                result = subprocess.run(command, capture_output=True, text=True)
                stdout = result.stdout or ""
                # diagnostic: if subprocess produced no stdout, log returncode and stderr
                if not stdout.strip():
                    # move to a fresh line for diagnostics
                    print()
                    print(f"Command produced no stdout (rc={result.returncode}). stderr:\n{result.stderr}")
                # ignore empty lines, split Tabellenfelder an 2+ spaces
                lines = [ln for ln in stdout.splitlines() if ln.strip()]
                for i, ln in enumerate(lines):
                    cols = re.split(r"\s{2,}", ln.strip())
                    # erste gefundene nicht-leere Zeile beim ersten Durchlauf ist der Header
                    if not csv_header_written:
                        writer.writerow(cols)
                        csv_header_written = True
                    else:
                        writer.writerow(cols)

    end=time.perf_counter()
    # ensure we end on a fresh line before printing summary
    print()
    print(f"Completed in {end - start:.2f} seconds.")

if __name__ == "__main__":
    main()
