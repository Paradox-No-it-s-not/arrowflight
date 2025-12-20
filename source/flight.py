# Version 4: Improved plot display and user-friendly exit
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.gridspec import GridSpec
import threading
import readchar
import sys
import argparse
import json
from pathlib import Path
from profiles import Profile
from constants import Physics
from compute import simulate_flight, find_optimal_angle
from plot import plot_trajectory


# --- Numerical parameters ---
DT = 0.001       # default time step [s]


def main():
    parser = argparse.ArgumentParser(description="Compute optimal arrow launch angle using named profiles from a config file.")
    parser.add_argument('target_x', type=float, nargs='?', default=None, help='Target horizontal distance in meters')
    parser.add_argument('target_y', type=float, nargs='?', default=None, help='Target height in meters')
    parser.add_argument('profile', nargs='?', default='default', help='Named profile from the config file (default: "default")')
    parser.add_argument('--list-profiles', action='store_true', help='List available profiles from the config file and exit')
    parser.add_argument('--config-file', '-c', default=str(Path(__file__).with_name('arrows.json')), help='Path to JSON config with named profiles')
    parser.add_argument('--no-plot', action='store_true', help='Do not show plots')
    parser.add_argument('--no-header', action='store_true', help='Do not print the header table')

    args = parser.parse_args()

    # If not listing profiles, require target_x and target_y
    if not args.list_profiles and (args.target_x is None or args.target_y is None):
        parser.error('target_x and target_y are required unless --list-profiles is used')

    target_x = args.target_x
    target_y = args.target_y

    config_path = Path(args.config_file)
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
    except Exception as e:
        print(f"Failed to read config file: {e}")
        sys.exit(1)

    if args.list_profiles:
        for name in sorted(configs.keys()):
            print(name)
        return

    if args.profile not in configs:
        print(f"Profile '{args.profile}' not found in config. Available profiles: {', '.join(sorted(configs.keys()))}")
        sys.exit(1)

    profile_obj = Profile.from_dict(args.profile, configs[args.profile])

    phys = Physics()

    # find optimal angle
    best_theta, best_x_hit, best_y_hit = find_optimal_angle(profile_obj, target_x, target_y, dt=DT, phys=phys)

    # final simulation recording trajectory
    result = simulate_flight(best_theta, profile=profile_obj, target_x=target_x, dt=DT, phys=phys, record_trajectory=True)
    x_end, y_end, t, v_end, angle_end, xs, ys, vxs, vys, ts = result

    # total velocity
    v_total = np.sqrt(np.array(vxs)**2 + np.array(vys)**2)
    target_height_rel = (np.tan(best_theta) * target_x - target_y)

    headers = [
        "Target distance",
        "Target height",
        "Optimal holdover",
        "Optimal launch angle",
        "best_x_hit",
        "best_y_hit",
        "Flight time",
        "Final speed",
        "Impact angle"
    ]

    values = [
        f"{target_x:.2f}m",
        f"{target_y:.2f}m",
        f"{target_height_rel:.3f}",
        f"{np.degrees(best_theta):.3f}°",
        f"{best_x_hit:.2f}m",
        f"{best_y_hit:.2f}m",
        f"{t:.2f} s",
        f"{v_total[-1]:.2f} m/s",
        f"{np.degrees(np.arctan2(vys[-1], vxs[-1])):.2f}°"
    ]

    widths = [max(len(h), len(v)) for h, v in zip(headers, values)]
    header_line = "  ".join(h.center(w) for h, w in zip(headers, widths))
    value_line = "  ".join(v.rjust(w) for v, w in zip(values, widths))

    if not args.no_header:
        print(header_line)
    print(value_line)

    if args.no_plot:
        return

    plot_trajectory(xs, ys, v_total, target_height_rel, target_x)


if __name__ == "__main__":
    main()
