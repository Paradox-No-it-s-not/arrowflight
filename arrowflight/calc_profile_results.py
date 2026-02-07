# parent.py
import argparse
import subprocess
import sys
import csv
import re
from pathlib import Path
import time
import concurrent.futures
import threading
import itertools
import os


def main():
    parser = argparse.ArgumentParser(description="Calculate flights for a range of target-distances and -hights and write the output into a CSV file")
    parser.add_argument('profile_name', nargs='?', default='default', help='The name of the profile in the file arrows.json to be used for the calculations (default: default)')
    parser.add_argument('--x_values', nargs=3, type=float, default=[10.0, 2.0, 100.0], help='The start, step and end values for target distances in meters (default: 10 2 100)')
    parser.add_argument('--y_values', nargs=3, type=float, default=[-10,1,10], help='The start, step and end values for target heights in meters (default: -10 1 10)')
    

    args = parser.parse_args()
    profile_name = args.profile_name
    x_start, x_step, x_end = args.x_values
    y_start, y_step, y_end = args.y_values

    csv_header_written = [False]     # steuert, ob CSV-Header bereits in die Datei geschrieben wurde (mutable container)
    header_row = [None]              # store the header row to skip duplicates
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

    combos = list(itertools.product(list(frange(x_start, x_end + 1, x_step)), list(frange(y_start, y_end, y_step))))

    file_lock = threading.Lock()
    print_lock = threading.Lock()

    def run_and_write(x, y):
        command = [
            sys.executable,
            "-m",
            "arrowflight.flight",
            str(x),
            str(y),
            profile_name,
            "--no-plot",
        ]

        msg = f"Running command: {' '.join(command)}"
        with print_lock:
            sys.stdout.write('\r' + msg + ' ' * max(0, prev_len - len(msg)))
            sys.stdout.flush()

        result = subprocess.run(command, capture_output=True, text=True)
        stdout = result.stdout or ""
        if not stdout.strip():
            with print_lock:
                print()
                print(f"Command produced no stdout (rc={result.returncode}). stderr:\n{result.stderr}")

        lines = [ln for ln in stdout.splitlines() if ln.strip()]
        rows = [re.split(r"\s{2,}", ln.strip()) for ln in lines]

        with file_lock:
            with out_path.open("a", newline="", encoding="utf-8") as fout:
                writer = csv.writer(fout)
                for i, cols in enumerate(rows):
                    # write header once and remember it; skip any subsequent rows that match the header
                    if not csv_header_written[0]:
                        writer.writerow(cols)
                        csv_header_written[0] = True
                        header_row[0] = tuple(cols)
                    else:
                        if header_row[0] is not None and tuple(cols) == header_row[0]:
                            continue  # skip duplicate header row
                        writer.writerow(cols)

    # Ensure file is created/truncated before concurrent appends
    with out_path.open("w", newline="", encoding="utf-8") as fout:
        pass

    max_workers = min(32, (os.cpu_count() or 1) * 5, len(combos) or 1)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [ex.submit(run_and_write, x, y) for x, y in combos]
        # wait for all to complete, propagate exceptions
        for f in concurrent.futures.as_completed(futures):
            f.result()

    end=time.perf_counter()
    # ensure we end on a fresh line before printing summary
    print()
    print(f"Completed in {end - start:.2f} seconds.")

if __name__ == "__main__":
    main()
