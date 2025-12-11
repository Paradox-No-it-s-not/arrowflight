# Arrowflight

Small simulator that computes an optimal launch angle for an arrow and visualizes the trajectory and related information.

## What it does
- Simulates arrow flight including aerodynamic drag
- Finds an optimal launch angle to hit a given horizontal distance and target height
- Prints results in a compact table
- Optionally shows plots: trajectory, speed profile, and a target-circle visualization

## Files
- `source/flight.py` — main script (Python)

## Requirements
- Python 3.8+ (or any modern Python 3)
- `numpy` and `matplotlib`

Install on Windows PowerShell:

```powershell
python -m pip install --upgrade pip
python -m pip install numpy matplotlib
```

## Usage
```
python .\source\flight.py <target_x[m]> <target_y[m]> [NO_PLOT] [NO_HEADER]
```
- `target_x` — horizontal target distance in meters (float)
- `target_y` — target height in meters (float)
- `NO_PLOT` — optional flag; if present, the script does not open matplotlib windows
- `NO_HEADER` — optional flag; if present, the script prints only the values line (no column header)

Notes:
- Distances are in meters; internal velocities are in m/s (script uses a default arrow speed in fps converted to m/s).
- When plots are enabled the program opens a non-blocking Matplotlib window and then waits for a keypress in the terminal before exiting.

## Examples (PowerShell)
- Run with a 50 m target at ground level (show plots and header):
```powershell
python .\source\flight.py 50 0
```

- Run for a 30 m target 1.5 m high, suppress plots but keep header:
```powershell
python .\source\flight.py 30 1.5 NO_PLOT
```

- Run and suppress the header line (useful for scripting/CSV-like output):
```powershell
python .\source\flight.py 25 0 NO_HEADER
```

- Run with both flags (no plot, no header — only values line printed):
```powershell
python .\source\flight.py 25 0 NO_PLOT NO_HEADER
```

## Output
By default the script prints a header row followed by a values row containing:
- Target distance, Target height, Optimal holdover, Optimal launch angle, best_x_hit, best_y_hit, Flight time, Final speed, Impact angle

If `NO_HEADER` is used, only the values row is printed. If `NO_PLOT` is used the script will exit after printing (no GUI windows are created).

## Notes & Next steps
