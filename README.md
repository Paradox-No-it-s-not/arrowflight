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
- `numpy`, `matplotlib`, and `readchar`

Install on Windows PowerShell:

```powershell
python -m pip install --upgrade pip
python -m pip install numpy matplotlib readchar
```

## Usage
```
python .\source\flight.py <target_x[m]> <target_y[m]> [profile] [--config-file PATH] [--no-plot] [--no-header]
```
- `target_x` — horizontal target distance in meters (float)
- `target_y` — target height in meters (float)
- `profile` — optional named arrow profile from the config (default: `default`)
- `--config-file PATH` — optional path to a JSON config file containing named profiles (default: `source/arrows.json`)
- `--no-plot` — optional flag; if present, the script does not open matplotlib windows
- `--no-header` — optional flag; if present, the script prints only the values line (no column header)

Notes:
- Distances are in meters; internal velocities are in m/s (script converts fps to m/s using the profile value).
- When plots are enabled the program opens a non-blocking Matplotlib window and waits for a keypress in the terminal before exiting.

## Configuration

The script reads named arrow profiles from a JSON file. A sample config is included at [source/arrows.json](source/arrows.json#L1).
Each profile is a JSON object with keys such as `mass_grains`, `diameter_m`, `cw`, and `v0_fps`.

Example `arrows.json` (excerpt):
```json
{
	"default": { "mass_grains": 235, "diameter_m": 0.00542, "cw": 0.25, "v0_fps": 230 },
	"light":   { "mass_grains": 180, "diameter_m": 0.00500, "cw": 0.24, "v0_fps": 245 }
}
```

Use the `profile` positional argument to select one of the named profiles. Override the config file location with `--config-file` if needed.

## Examples (PowerShell)
- Run for a 50 m target at ground level with the `default` profile (show plots and header):
```powershell
python .\source\flight.py 50 0 default
```

- Run for a 30 m target 1.5 m high using the `light` profile, suppress plots:
```powershell
python .\source\flight.py 30 1.5 light --no-plot
```

- Run with a custom config file and `heavy` profile:
```powershell
python .\source\flight.py 30 1.5 heavy --config-file C:\path\to\my_arrows.json
```

- Run without header (useful for scripting):
```powershell
python .\source\flight.py 25 0 default --no-header
```

## Output
By default the script prints a header row followed by a values row containing:
- Target distance, Target height, Optimal holdover, Optimal launch angle, best_x_hit, best_y_hit, Flight time, Final speed, Impact angle

If `NO_HEADER` is used, only the values row is printed. If `NO_PLOT` is used the script will exit after printing (no GUI windows are created).

## Notes

Internal comments and docstrings in `source/flight.py` have been translated from German to English.

Recent implementation details:

- The main script was renamed from `flug.py` to `flight.py`.
- Several variables were renamed to clear English snake_case names.
- The script now uses the cross-platform `readchar` library together with a small background thread to detect a terminal keypress without blocking the Matplotlib GUI. This works on Windows, macOS and Linux terminals.

Notes about keypress behavior:

- The POSIX implementation reads from `stdin` and therefore works when the script is run in a real terminal. Some IDE consoles or output capture environments may not behave the same way.
- The `readchar` approach reads one keypress in a blocking call inside a background thread; the main thread keeps the Matplotlib event loop alive with `plt.pause()` until a key is received.


