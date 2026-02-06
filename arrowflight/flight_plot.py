import numpy as np  # Third-party: numpy (BSD-3-Clause)
import matplotlib.pyplot as plt  # Third-party: matplotlib (PSF/BSD-like)
import readchar  # Third-party: readchar (MIT)
from matplotlib.patches import Circle
from matplotlib.gridspec import GridSpec
import threading
import random


def plot_trajectory(xs, ys, v_total, target_height_rel, target_x):
    fig = plt.figure(figsize=(12, 6))
    gs = GridSpec(2, 3, figure=fig)

    ax1 = fig.add_subplot(gs[0, 0:2])
    ax2 = fig.add_subplot(gs[1, 0:2])
    ax3 = fig.add_subplot(gs[0, 2])

    ax1.plot(xs, ys, color="tab:green")
    ax1.set_xlabel("Horizontal distance [m]")
    ax1.set_ylabel("Height [m]")
    ax1.set_title(f"Arrow - Optimized flight ({target_x:.2f}m target)")
    ax1.grid(True)

    ax2.plot(xs, v_total, color="tab:blue")
    ax2.set_ylabel("Speed [m/s]")
    ax2.grid(True)

    circle_black = Circle((0, 0), 0.4, fill=False, edgecolor='black', linewidth=2)
    circle_blue = Circle((0, 0), 0.3, fill=False, edgecolor='tab:blue', linewidth=2)
    circle_red = Circle((0, 0), 0.2, fill=False, edgecolor='red', linewidth=2)
    circle_gold = Circle((0, 0), 0.1, fill=False, edgecolor='gold', linewidth=2)
    ax3.add_patch(circle_black)
    ax3.add_patch(circle_blue)
    ax3.add_patch(circle_red)
    ax3.add_patch(circle_gold)
    ax3.plot(0, 0, 'ko')

    ax3.plot(0, target_height_rel, marker='o', color='tab:green', markersize=8)

    ax3.set_aspect('equal', 'box')
    lim = max(0.4, abs(target_height_rel) + 0.1)
    ax3.set_xlim(-lim, lim)
    ax3.set_ylim(-lim, lim)
    ax3.set_xlabel("X [m]")
    ax3.set_ylabel("Y [m]")
    ax3.set_title("Circles around target/origin (D=0.8 m)")
    ax3.grid(True)

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

    try:
        plt.show(block=False)
    except TypeError:
        plt.show()

    print("Press any key in the terminal to exit the program...")

    key_pressed = threading.Event()

    def _wait_for_key():
        try:
            readchar.readkey()
        except Exception:
            pass
        key_pressed.set()

    threading.Thread(target=_wait_for_key, daemon=True).start()
    while not key_pressed.is_set():
        plt.pause(0.1)
    plt.close('all')



def plot_trajectories(trajectories, target_x):
    """
    trajectories: list of dicts with keys: 'xs', 'ys', 'v_total', 'label', 'color' (color optional)
    """
    fig = plt.figure(figsize=(12, 6))
    gs = GridSpec(2, 3, figure=fig)

    ax1 = fig.add_subplot(gs[0, 0:2])
    ax2 = fig.add_subplot(gs[1, 0:2])
    ax3 = fig.add_subplot(gs[0, 2])

    for traj in trajectories:
        xs = traj['xs']
        ys = traj['ys']
        v_total = traj['v_total']
        label = traj.get('label')
        color = traj.get('color') or tuple(np.random.rand(3,))
        ax1.plot(xs, ys, color=color, label=label)
        ax2.plot(xs, v_total, color=color, label=label)

    ax1.set_xlabel("Horizontal distance [m]")
    ax1.set_ylabel("Height [m]")
    ax1.set_title(f"Arrow - Optimized flight ({target_x:.2f}m target)")
    ax1.grid(True)
    ax1.legend()

    ax2.set_ylabel("Speed [m/s]")
    ax2.grid(True)
    ax2.legend()

    # draw reference circles in ax3 (same as single-plot)
    circle_black = Circle((0, 0), 0.4, fill=False, edgecolor='black', linewidth=2)
    circle_blue = Circle((0, 0), 0.3, fill=False, edgecolor='tab:blue', linewidth=2)
    circle_red = Circle((0, 0), 0.2, fill=False, edgecolor='red', linewidth=2)
    circle_gold = Circle((0, 0), 0.1, fill=False, edgecolor='gold', linewidth=2)
    ax3.add_patch(circle_black)
    ax3.add_patch(circle_blue)
    ax3.add_patch(circle_red)
    ax3.add_patch(circle_gold)
    ax3.plot(0, 0, 'ko')

    # pick an average target height annotation if provided
    heights = [traj.get('target_height_rel', 0.0) for traj in trajectories]
    # avg_height = float(np.mean(heights)) if heights else 0.0
    # ax3.plot(0, avg_height, marker='o', color='tab:green', markersize=8)

    for traj in trajectories:
        aheight= traj.get('target_height_rel', 0.0)
        ax3.plot(0, aheight, marker='o', color= traj.get('color'), markersize=8, alpha=0.5)
        ax3.annotate(traj.get('label', ""), xy=(0.1, aheight-0.1))

    height_max = max(heights) if heights else 0.0
    ax3.set_aspect('equal', 'box')
    lim = max(0.4, abs(height_max) + 0.1)
    ax3.set_xlim(-lim, lim)
    ax3.set_ylim(-lim, lim)
    ax3.set_xlabel("X [m]")
    ax3.set_ylabel("Y [m]")
    ax3.set_title("Aiming rel. to target. (Reference circle D=0.8 m)")
    ax3.grid(True)


    plt.tight_layout()

    try:
        plt.show(block=False)
    except TypeError:
        plt.show()

    print("Press any key in the terminal to exit the program...")

    key_pressed = threading.Event()

    def _wait_for_key():
        try:
            readchar.readkey()
        except Exception:
            pass
        key_pressed.set()

    threading.Thread(target=_wait_for_key, daemon=True).start()
    while not key_pressed.is_set():
        plt.pause(0.1)
    plt.close('all')
