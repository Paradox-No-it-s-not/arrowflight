# Arrowflight

Small simulator that computes an optimal launch angle for an arrow and visualizes the trajectory and related information.

## What it does
- Simulates arrow flight including aerodynamic drag
- Finds an optimal launch angle to hit a given horizontal distance and target height
- Prints results in a compact table
- Optionally shows plots: trajectory, speed profile, and a target-circle visualization

## First steps
- Execute the steps listed in [Installation](##Installation)
- Execute in a commandline:
```powershell
arrowflight 50 0 default
```
This should print the calculated data in the console and show up a window with some plots of the arrow's flight to the target.


## Installation

### Steps to install
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```
### Requirements
- Python 3.8+
- `numpy`, `matplotlib`, `plotly`, `scipy`, `readchar`

Installing editable (`-e`) registers console scripts named `arrowflight`, `calc_profile_results` and `plot_profile_results` which are thin wrappers around the package modules.



## Usage
As a first step open the file arrows.json and insert a new named setup for your bow/arrow, or place your data into the existing default setup.
Test the main simulator (prints table, optionally plots):

```powershell
arrowflight <target_x[m]> <target_y[m]> [profile] [--config-file PATH] [--no-plot] [--no-header]
```

Or run the module directly:

```powershell
python -m arrowflight.flight <target_x[m]> <target_y[m]> [profile] [--config-file PATH] [--no-plot] [--no-header]
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

## Files
- [arrowflight/flight.py](arrowflight/flight.py) — **Main CLI**: entry point; parses arguments, loads a named profile from the JSON config, runs the simulation/optimizer and optionally plots results.
- [arrowflight/flight_compute.py](arrowflight/flight_compute.py) — **Computation**: physics and numerical routines (flight simulator and angle optimizer).
- [arrowflight/flight_plot.py](arrowflight/flight_plot.py) — **Plot helpers**: functions for drawing single or multiple trajectories and related charts using Matplotlib.
- [arrowflight/flight_profiles.py](arrowflight/flight_profiles.py) — **Profile dataclass**: profile factory and conversion helpers (mass, area, velocity conversions).
- [arrowflight/flight_constants.py](arrowflight/flight_constants.py) — **Constants**: physical constants and unit conversion factors used across modules.
- [arrowflight/arrows.json](arrowflight/arrows.json) — **Config**: sample JSON with multiple named arrow profiles (mass, diameter, drag coeff, initial speed).
- [arrowflight/calc_profile_results.py](arrowflight/calc_profile_results.py) — **Batch runner**: convenience script to call the package entrypoint over ranges of `x`/`y` and write CSV results.
- [arrowflight/plot_profile_results.py](arrowflight/plot_profile_results.py) — **3D plotting / analysis**: read CSV output and create interactive plots or summaries.

Run the tools via the package entrypoints or installed console scripts (see Installation).


## Configuration

Named profiles are stored in the JSON file at [arrowflight/arrows.json](arrowflight/arrows.json#L1) by default. Each profile is a JSON object with keys such as `mass_grains`, `diameter_m`, `cw`, and `v0_fps`.

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
arrowflight 50 0 default
```

- Run for a 30 m target 1.5 m high using the `light` profile, suppress plots:
```powershell
arrowflight 30 1.5 light --no-plot
```
- Run for a 30 m target -2m height using the `heavy` and `default` profiles in order to compare the flights
```powershell
arrowflight 30 -2.0 heavy default 
```
- Run the batch CSV generator (example range):
```powershell
calc_profile_results default --x_values 10 10 30 --y_values -1 1 1
```

- Plot results from a CSV file (interactive Plotly surface):
```powershell
plot_profile_results source/results.csv -s aim aim_angle_0diff
```

## Output
By default the script prints a header row followed by a values row containing:
- Target distance, Target height, Optimal holdover, Optimal launch angle, best_x_hit, best_y_hit, Flight time, Final speed, Impact angle

If `NO_HEADER` is used, only the values row is printed. If `NO_PLOT` is used the script will exit after printing (no GUI windows are created).

## Notes

Key implementation notes:

- The code is packaged as `arrowflight` and provides three entry points: `arrowflight`, `calc_profile_results`, and `plot_profile_results`.
- Plotting uses Matplotlib and Plotly. Plotly surfaces open in a browser or inline depending on your environment.
- The `readchar` keypress helper works in real terminals; some IDE consoles and remote environments may not support the same interactive behavior.

## macOS notes

The package and console scripts work on macOS when installed into a Python environment (virtualenv or system). Recommended steps:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

After installation the commands `arrowflight`, `calc_profile_results` and  `plot_profile_results` will be available in the active environment's `bin/` directory. Verify i.e. with:

```bash
which arrowflight
```

You can also run the module without installing, i.e.. :

```bash
python3 -m arrowflight.flight 60 5 default --no-plot
```

Notes about plotting and interactivity on macOS:
- Use `--no-plot` in headless or CI environments to avoid GUI issues.
- Matplotlib backends and Plotly may open GUI windows or browser tabs depending on your environment; Terminal and iTerm2 work well for the `readchar` keypress helper.



