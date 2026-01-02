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
from .flight_profiles import Profile
from .flight_constants import Physics
from .flight_compute import simulate_flight, find_optimal_angle
from .flight_plot import plot_trajectory, plot_trajectories


# --- Numerical parameters ---
DT = 0.001       # default time step [s]


def main():
    parser = argparse.ArgumentParser(description="Compute optimal arrow launch angle using named profiles from a config file.")
    parser.add_argument('target_x', type=float, nargs='?', default=None, help='Target horizontal distance in meters')
    parser.add_argument('target_y', type=float, nargs='?', default=None, help='Target height in meters')
    parser.add_argument('profile', nargs='*', default=['default'], help='One or more named profiles from the config file (default: ["default"])')
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

    # allow multiple profiles
    profile_names = args.profile if isinstance(args.profile, list) else [args.profile]

    results = []
    trajectories = []

    phys = Physics()

    for pname in profile_names:
        if pname not in configs:
            print(f"Profile '{pname}' not found in config. Available profiles: {', '.join(sorted(configs.keys()))}")
            sys.exit(1)

        profile_obj = Profile.from_dict(pname, configs[pname])

        # find optimal angle
        best_theta, best_x_hit, best_y_hit = find_optimal_angle(profile_obj, target_x, target_y, dt=DT, phys=phys)

        # final simulation recording trajectory
        result = simulate_flight(best_theta, profile=profile_obj, target_x=target_x, dt=DT, phys=phys, record_trajectory=True)
        x_end, y_end, t, v_end, angle_end, xs, ys, vxs, vys, ts = result

        # total velocity
        v_total = np.sqrt(np.array(vxs)**2 + np.array(vys)**2)
        target_height_rel = (np.tan(best_theta) * target_x - target_y)

        impact_angle_deg = np.degrees(np.arctan2(vys[-1], vxs[-1]))

        results.append({
            'profile': pname,
            'target_x': f"{target_x:.2f}",
            'target_y': f"{target_y:.2f}",
            'holdover': f"{target_height_rel:.3f}",
            'launch_angle': f"{np.degrees(best_theta):.3f}",
            'best_x_hit': f"{best_x_hit:.2f}",
            'best_y_hit': f"{best_y_hit:.2f}",
            'flight_time': f"{t:.2f}",
            'final_speed': f"{v_total[-1]:.2f}",
            'impact_angle': f"{impact_angle_deg:.2f}"
        })

        # trajectories.append({'xs': xs, 'ys': ys, 'v_total': v_total, 'label': pname, 'target_height_rel': target_height_rel})
        trajectories.append({'xs': xs, 'ys': ys, 'v_total': v_total, 'label': pname, 'target_height_rel': target_height_rel, 'color': tuple(np.random.rand(3,))})
        

    # prepare and print table
    headers = [
        'Profile',
        "Target distance [m]",
        "Target height [m]",
        "Optimal holdover",
        "Optimal launch angle [°]",
        "best_x_hit [m]",
        "best_y_hit [m]",
        "Flight time [s]",
        "Final speed [m/s]",
        "Impact angle [°]"
    ]

    rows = []
    for r in results:
        rows.append([
            r['profile'], r['target_x'], r['target_y'], r['holdover'], r['launch_angle'], r['best_x_hit'], r['best_y_hit'], r['flight_time'], r['final_speed'], r['impact_angle']
        ])

    # compute column widths
    widths = []
    for ci, h in enumerate(headers):
        col_vals = [row[ci] for row in rows]
        widths.append(max(len(h), max(len(v) for v in col_vals)))

    header_line = "  ".join(h.center(w) for h, w in zip(headers, widths))
    if not args.no_header:
        print(header_line)

    for row in rows:
        print("  ".join(v.rjust(w) for v, w in zip(row, widths)))

    if args.no_plot:
        return

    plot_trajectories(trajectories, target_x)


if __name__ == "__main__":
    main()
