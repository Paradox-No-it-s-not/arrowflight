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

# --- Constants ---
# Conversion: grains to kg
grains_to_kg = 0.00006479891
# Conversion: fps to m/s
fps_to_ms = 0.3048   
rho = 1.2
g = 9.81



# --- Arrow parameters will be loaded from a configuration file (JSON).
# CLI: flight.py <target_x> <target_y> [profile] [--config-file PATH] [--no-plot] [--no-header]
parser = argparse.ArgumentParser(description="Compute optimal arrow launch angle using named profiles from a config file.")
parser.add_argument('target_x', type=float, help='Target horizontal distance in meters')
parser.add_argument('target_y', type=float, help='Target height in meters')
parser.add_argument('profile', nargs='?', default='default', help='Named profile from the config file (default: "default")')
parser.add_argument('--config-file', '-c', default=str(Path(__file__).with_name('arrows.json')), help='Path to JSON config with named profiles')
parser.add_argument('--no-plot', action='store_true', help='Do not show plots')
parser.add_argument('--no-header', action='store_true', help='Do not print the header table')

args = parser.parse_args()

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

if args.profile not in configs:
    print(f"Profile '{args.profile}' not found in config. Available profiles: {', '.join(sorted(configs.keys()))}")
    sys.exit(1)

profile = configs[args.profile]

# Read profile parameters with sensible defaults
mass_grains = profile.get('mass_grains', 235)
diameter_m = profile.get('diameter_m', 0.00542)
cw = profile.get('cw', 0.25)
v0_fps = profile.get('v0_fps', 230)

# Cross-sectional area and conversions
a = np.pi * (diameter_m/2)**2
m = mass_grains * grains_to_kg
v0 = v0_fps * fps_to_ms


# --- Numerical parameters ---
dt = 0.001       # time step [s]

def simulate_flight(theta):
    """Simulates the flight and returns (hit_distance, flight_time, end_speed, impact_angle)"""
    vx = v0 * np.cos(theta)
    vy = v0 * np.sin(theta)
    x, y, t = 0.0, 0.0, 0.0

    #while  x <= target_x * 1.5:  # safety buffer
    while  x <= target_x:  # safety buffer
        #print("Optimal launch angle", np.degrees(theta), "x:", x, "y:", y)
        v = np.sqrt(vx**2 + vy**2)
        Fd = 0.5 * rho * cw * a * v**2
        ax = -Fd * vx / (m * v)
        ay = -g - Fd * vy / (m * v)

        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt

    v_end = np.sqrt(vx**2 + vy**2)
    angle_end = np.degrees(np.arctan2(vy, vx))
    return x, y, t, v_end, angle_end


# --- Binary search for optimal angle ---
low, high = np.radians(-45.0), np.radians(45.0)
best_theta, best_x_hit, best_y_hit  = None, None, None

for _ in range(25):  # 25 iterations ≈ very accurate
    mid = 0.5 * (low + high)
    x_hit, y_hit, t, v_end, a_end = simulate_flight(mid)
    #print("low:", np.degrees(low), " high:", np.degrees(high), " mid:", np.degrees(mid))
    #print(f"low: {np.degrees(low):.2f}  high: {np.degrees(high):.2f}  mid: {np.degrees(mid):.2f} x_hit: {x_hit:.2f}  y_hit: {y_hit:.2f} " )

    if (x_hit < target_x) or (y_hit < target_y):
        low = mid  # too short → increase angle
    else:
        high = mid  # too far → decrease angle
    best_theta = mid
    best_x_hit, best_y_hit = x_hit, y_hit


# --- Final simulation with optimal angle ---
xs, ys, vxs, vys, ts = [], [], [], [], []
vx = v0 * np.cos(best_theta)
vy = v0 * np.sin(best_theta)
x, y, t = 0.0, 0.0, 0.0
#x, y, t = 0.0, target_y, 0.0

#while y >= target_y and x <= target_x:
while x <= target_x:
    v = np.sqrt(vx**2 + vy**2)
    Fd = 0.5 * rho * cw * a * v**2
    ax = -Fd * vx / (m * v)
    ay = -g - Fd * vy / (m * v)

    vx += ax * dt
    vy += ay * dt
    x += vx * dt
    y += vy * dt
    t += dt

    xs.append(x)
    ys.append(y)
    vxs.append(vx)
    vys.append(vy)
    ts.append(t)

# total velocity
v_total = np.sqrt(np.array(vxs)**2 + np.array(vys)**2)
# relative target height
target_height_rel = (np.tan(best_theta) * target_x - target_y)

# --- Results ---
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

# Compute column widths (at least as wide as header or value)
widths = [max(len(h), len(v)) for h, v in zip(headers, values)]

# Header centered, values right-aligned, columns separated by 2 spaces
header_line = "  ".join(h.center(w) for h, w in zip(headers, widths))
value_line = "  ".join(v.rjust(w) for v, w in zip(values, widths))

if not args.no_header:
    print(header_line)
print(value_line)

if args.no_plot:
    sys.exit(0)
# --- Plot: both figures side-by-side using GridSpec ---
fig = plt.figure(figsize=(12,6))
gs = GridSpec(2, 3, figure=fig)

# Left: two stacked subplots (top: trajectory, bottom: speed)
ax1 = fig.add_subplot(gs[0, 0:2])
ax2 = fig.add_subplot(gs[1, 0:2])

# Right: a column spanning both rows (circles)
ax3 = fig.add_subplot(gs[0, 2])

# Top: trajectory
ax1.plot(xs, ys, color="tab:green")
ax1.set_xlabel("Horizontal distance [m]")
ax1.set_ylabel("Height [m]")
ax1.set_title(f"Arrow - Optimized flight ({target_x:.2f}m target)")
ax1.grid(True)

# Bottom: speed over time / distance
ax2.plot(xs, v_total, color="tab:blue")
ax2.set_ylabel("Speed [m/s]")
ax2.grid(True)

# Circles around the target
circle_black = Circle((0, 0), 0.4, fill=False, edgecolor='black', linewidth=2)  # D=0.8 -> r=0.4
circle_blue = Circle((0, 0), 0.3, fill=False, edgecolor='tab:blue', linewidth=2) # D=0.6 -> r=0.3
circle_red = Circle((0, 0), 0.2, fill=False, edgecolor='red', linewidth=2)  # D=0.4 -> r=0.2
circle_gold = Circle((0, 0), 0.1, fill=False, edgecolor='gold', linewidth=2) # D=0.2 -> r=0.1  
ax3.add_patch(circle_black)
ax3.add_patch(circle_blue)
ax3.add_patch(circle_red)
ax3.add_patch(circle_gold)
ax3.plot(0, 0, 'ko')  # mark origin (handle used later for ordering of the legends )

# Additional point at x=0, y=target_height_rel
ax3.plot(0, target_height_rel, marker='o', color='tab:green', markersize=8)

ax3.set_aspect('equal', 'box')
lim = max(0.4, abs(target_height_rel) + 0.1)  # ensures the point is visible
ax3.set_xlim(-lim, lim)
ax3.set_ylim(-lim, lim)
ax3.set_xlabel("X [m]")
ax3.set_ylabel("Y [m]")
ax3.set_title("Circles around target/origin (D=0.8 m)")
ax3.grid(True)

# Position the axis labels bottom-left in the plot
#ax3.xaxis.set_label_coords(0.01, -0.06)
#ax3.yaxis.set_label_coords(-0.08, 0.01)

# Label directly to the right of the green point (target height)
ax3.annotate(
    f"Target height: {target_height_rel:.3f} m",
    xy=(0, target_height_rel),
    xytext=(8, 0),
    textcoords='offset points',
    va='center',
    ha='left',
    fontsize=9,
    bbox=dict(boxstyle='round,pad=0.2', fc='white', alpha=0.7)
)

plt.tight_layout()

# Show the plots non-blocking and wait for a keypress in the terminal,
# so the program exits only after keypress (not by closing windows).
try:
    plt.show(block=False)
except TypeError:
    # Fallback: some older backends don't recognize the block keyword
    plt.show()

print("Press any key in the terminal to exit the program...")

# Use a background thread that blocks on `readchar.readkey()`; main thread keeps GUI alive
key_pressed = threading.Event()

def _wait_for_key():
    try:
        readchar.readkey()
    except Exception:
        # ignore any read errors
        pass
    key_pressed.set()

threading.Thread(target=_wait_for_key, daemon=True).start()

while not key_pressed.is_set():
    plt.pause(0.1)

plt.close('all')
