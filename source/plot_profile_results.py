# Read the file results.csv and plot 3D surface plot of specified surface data (e.g. aim_angle) vs target distance and target height. 
# use plotly.
import csv
import sys
import argparse
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from scipy.interpolate import griddata
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description="Plot 3D surface from results CSV")
    parser.add_argument('data_path', nargs='?', default='results.csv', help='Path to CSV file (default: results.csv)')
    # parameter values for plots as any of: aim, aim_angle, aim_0diff, aim_angle_0diff
    # to  plott multiple surfaces simultaneously
    parser.add_argument('--surfaces', '-s', nargs='+', choices=['aim', 'aim_angle', 'aim_0diff', 'aim_angle_0diff'],
                        default=['aim', 'aim_angle'],
                        help='Which surfaces to show. Possible values: aim, aim_angle, aim_0diff, aim_angle_0diff (default: aim, aim_angle)')
    args = parser.parse_args()

    data_path = Path(args.data_path)
    if not data_path.exists():
        print(f"File not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    pts = defaultdict(list)  # key=(x,y) -> list of z
    with data_path.open("r", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            try:
                x = float(row.get("Target distance [m]"))
                y = float(row.get("Target height [m]"))     # corresponds to theta_y
                y_aim = float(row.get("Optimal holdover"))  # corresponds to theta_aim. This is the vertical offset to apply at target distance
                # all angles in degrees
                theta = float(row.get("Optimal launch angle [°]"))  # the total launch angle
                theta_y = np.degrees(np.arctan2(y, x))  # The angle where the line of sight to the target is. Coresponds y 
                theta_aim = theta - theta_y  # The angle difference to the line of sight to the target. Corresponds to y_aim
            except (TypeError, ValueError):
                # skip malformed rows
                continue
            pts[(x, y)].append({'theta': theta, 'theta_y': theta_y, 'theta_aim': theta_aim, 'y_aim': y_aim})

    if not pts:
        print("No valid data rows found in CSV.", file=sys.stderr)
        sys.exit(1)

    xs, ys, thetays, thetas, theta_aims, y_aims = [], [], [], [], [], []
    theta_aim_0diffs, y_aim_0diffs =  [], []

    # build baseline mapping: for each x find the y_aim value at y==0 (if present)
    baseline_y_aim = {}
    baseline_theta_aim = {}
    for (xx, yy), recs in pts.items():
        if abs(yy) < 1e-12:  # treat as y == 0
            baseline_y_aim[xx] = recs[0].get('y_aim', 0.0)
            baseline_theta_aim[xx] = recs[0].get('theta_aim', 0.0)

    for (x, y), recs in pts.items():
        r = recs[0]                 # weil genau ein Satz pro (x,y) vorhanden ist
        theta_aim = r['theta_aim']
        thetay = r['theta_y']   
        theta = r['theta']      
        y_aim = r['y_aim']
        xs.append(x)
        ys.append(y)
        theta_aims.append(theta_aim)
        thetays.append(thetay)
        thetas.append(theta)
        y_aims.append(y_aim)
        # check difference compared to y=0 baseline
        y_aim_0diffs.append(y_aim - baseline_y_aim.get(x, 0.0))
        theta_aim_0diffs.append(theta_aim - baseline_theta_aim.get(x, 0.0))


    xs = np.array(xs)
    ys = np.array(ys)
    thetas = np.array(thetas)
    thetays = np.array(thetays)
    theta_aims = np.array(theta_aims)
    y_aims = np.array(y_aims)
    y_aim_0diffs = np.array(y_aim_0diffs)
    theta_aim_0diffs = np.array(theta_aim_0diffs)
    

    if xs.size == 0 or ys.size == 0:
        print("Not enough data for interpolation.", file=sys.stderr)
        sys.exit(1)

    xi = np.linspace(min(xs), max(xs), len(xs))
    yi = np.linspace(min(ys), max(ys), len(ys))
    xi, yi = np.meshgrid(xi, yi)

    # choose method based on available points
    method = 'cubic' if len(y_aims) >= 16 else ('linear' if len(y_aims) >= 3 else 'nearest')
    zi_y_aim = griddata((xs, ys), y_aims, (xi, yi), method=method)
    zi_theta_aim = griddata((xs, ys), theta_aims, (xi, yi), method=method)
    zi_y_aim_0diff = griddata((xs, ys), y_aim_0diffs, (xi, yi), method=method)
    zi_theta_aim_0diff = griddata((xs, ys), theta_aim_0diffs, (xi, yi), method=method)
    
 
    # plot selected surfaces
    fig = go.Figure()
    sel = set(args.surfaces)
    if 'aim' in sel:
        fig.add_trace(go.Surface(x=xi, y=yi, z=zi_y_aim, colorscale='RdBu', name='Optimal holdover', showlegend=True, showscale=True, opacity=1.0,
                                 colorbar=dict(title='m')))
    if 'aim_angle' in sel:
        fig.add_trace(go.Surface(x=xi, y=yi, z=zi_theta_aim, colorscale='Viridis', name='Aiming angle (°)', showlegend=True, showscale=True, opacity=0.8,
                                 colorbar=dict(title='°')))
    if 'aim_0diff' in sel:
        fig.add_trace(go.Surface(x=xi, y=yi, z=zi_y_aim_0diff, colorscale='Plasma', name='y_aim - y_aim(y=0)', showlegend=True, showscale=True, opacity=0.8,
                                 colorbar=dict(title='m')))
    if 'aim_angle_0diff' in sel:
        fig.add_trace(go.Surface(x=xi, y=yi, z=zi_theta_aim_0diff, colorscale='Cividis', name='θ_aim - θ_aim(y=0)', showlegend=True, showscale=True, opacity=0.8,
                                 colorbar=dict(title='°')))

    fig.update_layout(
        scene=dict(xaxis_title='Target distance [m]', yaxis_title='Target height [m]', zaxis_title='Values (see legend)'),
        title='3D Surface Plot of Optimal Holdover'
    )
    fig.show()

if __name__ == "__main__":
    main()


