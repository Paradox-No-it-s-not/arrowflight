# Version 4: Improved plot display and user-friendly exit
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.gridspec import GridSpec
import msvcrt
import sys

# --- Constants ---
# Conversion: grains to kg
grains_to_kg = 0.00006479891
# Conversion: fps to m/s
fps_to_ms = 0.3048   
rho = 1.2
g = 9.81



# --- Arrow parameters ---
mass_grains = 235  # mass in grains
diameter_m = 0.00542        # diameter [m]
# Cross-sectional area
a = np.pi * (diameter_m/2)**2
# 0.25 is a commonly assumed drag coefficient value for arrows
cw = 0.25

m = mass_grains * grains_to_kg  # mass in kg

## Initial conditions
v0_fps = 230  # initial speed in fps
v0_ms = v0_fps * fps_to_ms  # initial speed in m/s     

# --- Target distance ---
try:
    target_x = float(sys.argv[1])  # in m
    target_y = float(sys.argv[2])  # in m
except (IndexError, ValueError):
    print("Usage: flug.py <target_x[m]> <target_y[m]> [NO_PLOT] [NO_HEADER]")
    sys.exit(1)


# --- Numerical parameters ---
dt = 0.001       # time step [s]

def simulate_flight(theta):
    """Simulates the flight and returns (hit_distance, flight_time, end_speed, impact_angle)"""
    vx = v0_ms * np.cos(theta)
    vy = v0_ms * np.sin(theta)
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
vx = v0_ms * np.cos(best_theta)
vy = v0_ms * np.sin(best_theta)
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

if "NO_HEADER" not in sys.argv[3:]:
    print(header_line)
print(value_line)

if "NO_PLOT" in sys.argv[3:]:
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

# Wait for keypress and process GUI events in the meantime
while True:
    if msvcrt.kbhit():
        # read key and exit loop
        msvcrt.getch()
        break
    # short pause to process GUI events
    plt.pause(0.1)

plt.close('all')
