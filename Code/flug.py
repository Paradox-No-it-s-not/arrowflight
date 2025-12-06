# Version 3
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import sys

# --- Konstanten ---
# Umrechnung grain in kg
grainsTokg = 0.00006479891
# Umrechnung fps in m/s
fpsToms = 0.3048   
rho = 1.2
g = 9.81


# --- Parameter des Pfeils ---
mgrains = 235  # Masse in grain
d = 0.00542        # Durchmesser [m]
#Querschnittsfläche
A = np.pi * (d/2)**2
# 0.25 ist ein allgemein angenommener cw-Wert für Pfeile
cw = 0.25

m=mgrains * grainsTokg  # Masse in kg

## Startbedingungen
v0fps = 230  # Anfangsgeschwindigkeit in fps
v0 = 230 * fpsToms  # Anfangsgeschwindigkeit in m/s     

# --- Zielentfernung ---
try:
    target_x = float(sys.argv[1])  # in m
    target_y = float(sys.argv[2])  # in m
except (IndexError, ValueError):
    #print("Verwendung: flug-3.py <target_x[m]> <target_y[m]>")
    print("Verwendung: flug-3.py <target_x[m]> <target_y[m]> [NO_PLOT]")
    sys.exit(1)



# --- Numerische Parameter ---
dt = 0.001       # Zeitschritt [s]

def simulate_flight(theta):
    """Simuliert den Flug und gibt (Trefferweite, Flugzeit, Endgeschwindigkeit, Einschlagwinkel) zurück"""
    vx = v0 * np.cos(theta)
    vy = v0 * np.sin(theta)
    x, y, t = 0.0, 0.0, 0.0

    #while  x <= target_x * 1.5:  # Sicherheitspuffer
    while  x <= target_x:  # Sicherheitspuffer
        #print("Optimaler Abschusswinkel", np.degrees(theta), "x:", x, "y:", y)
        v = np.sqrt(vx**2 + vy**2)
        Fd = 0.5 * rho * cw * A * v**2
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


# --- Binäre Suche nach optimalem Winkel ---
low, high = np.radians(-45.0), np.radians(45.0)
best_theta, best_x_hit, best_y_hit  = None, None, None

for _ in range(25):  # 25 Iterationen ≈ sehr genau
    mid = 0.5 * (low + high)
    x_hit, y_hit, t, v_end, a_end = simulate_flight(mid)
    #print("low:", np.degrees(low), " high:", np.degrees(high), " mid:", np.degrees(mid))
    #print(f"low: {np.degrees(low):.2f}  high: {np.degrees(high):.2f}  mid: {np.degrees(mid):.2f} x_hit: {x_hit:.2f}  y_hit: {y_hit:.2f} " )

    if (x_hit < target_x) or (y_hit < target_y):
        low = mid  # zu kurz → Winkel erhöhen
    else:
        high = mid  # zu weit → Winkel verringern
    best_theta = mid
    best_x_hit, best_y_hit = x_hit, y_hit


# --- Finale Simulation mit optimalem Winkel ---
xs, ys, vxs, vys, ts = [], [], [], [], []
vx = v0 * np.cos(best_theta)
vy = v0 * np.sin(best_theta)
x, y, t = 0.0, 0.0, 0.0
#x, y, t = 0.0, target_y, 0.0

#while y >= target_y and x <= target_x:
while x <= target_x:
    v = np.sqrt(vx**2 + vy**2)
    Fd = 0.5 * rho * cw * A * v**2
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

v_total = np.sqrt(np.array(vxs)**2 + np.array(vys)**2)
zielhoehe_rel = (np.tan(best_theta) * target_x - target_y)

# --- Ergebnisse ---
headers = [
    "Zielentfernung",
    "Zielhöhe",
    "Optimales Hinhalten",
    "Optimaler Abschusswinkel",
    "best_x_hit",
    "best_y_hit",
    "Flugzeit",
    "Endgeschwindigkeit",
    "Einschlagwinkel"
]

values = [
    f"{target_x:.2f}m",
    f"{target_y:.2f}m",
    f"{zielhoehe_rel:.3f}",
    f"{np.degrees(best_theta):.3f}°",
    f"{best_x_hit:.2f}m",
    f"{best_y_hit:.2f}m",
    f"{t:.2f} s",
    f"{v_total[-1]:.2f} m/s",
    f"{np.degrees(np.arctan2(vys[-1], vxs[-1])):.2f}°"
]

# Berechne Spaltenbreiten (mindestens so breit wie Header oder Wert)
widths = [max(len(h), len(v)) for h, v in zip(headers, values)]

# Header zentriert, Werte rechtsbündig, Spalten mit 2 Leerzeichen getrennt
header_line = "  ".join(h.center(w) for h, w in zip(headers, widths))
value_line = "  ".join(v.rjust(w) for v, w in zip(values, widths))

print(header_line)
print(value_line)

if len(sys.argv) > 3 and sys.argv[3] == "NO_PLOT":
    sys.exit(0)
# --- Plot ---
plt.figure(figsize=(10,6))

plt.subplot(2,1,1)
plt.plot(xs, v_total, color="tab:blue")
plt.ylabel("Geschwindigkeit [m/s]")
plt.title("Recurve-Pfeil – Optimierter Flug (70 m Zielweite)")
plt.grid(True)

plt.subplot(2,1,2)
plt.plot(xs, ys, color="tab:green")
plt.xlabel("Horizontale Entfernung [m]")
plt.ylabel("Höhe [m]")
plt.grid(True)

# Additional plot: some circles around origin , soll ne Zielscheibe darstellen
plt.tight_layout()  # layout for first figure

# Erstelle zweite Figur mit den Kreisen und dem zusätzlichen Punkt bei (0, zielhoehe_rel)
fig2, ax2 = plt.subplots(figsize=(6,6))
circle_black = Circle((0, 0), 0.4, fill=False, edgecolor='black', linewidth=2)  # D=0.8 -> r=0.4
circle_blue = Circle((0, 0), 0.3, fill=False, edgecolor='tab:blue', linewidth=2) # D=0.6 -> r=0.3
circle_red = Circle((0, 0), 0.2, fill=False, edgecolor='red', linewidth=2)  # D=0.4 -> r=0.2
circcle_gold = Circle((0, 0), 0.1, fill=False, edgecolor='gold', linewidth=2) # D=0.2 -> r=0.1  
ax2.add_patch(circle_black)
ax2.add_patch(circle_blue)
ax2.add_patch(circle_red)
ax2.add_patch(circcle_gold)
ax2.plot(0, 0, 'ko', label='Nullpunkt')  # Nullpunkt markieren

# Zusätzlicher Punkt bei x=0, y=zielhoehe_rel
ax2.plot(0, zielhoehe_rel, marker='o', color='tab:green', markersize=8, label=f'zielhoehe_rel={zielhoehe_rel:.3f} m')

ax2.set_aspect('equal', 'box')
lim = max(0.4, abs(zielhoehe_rel) + 0.1)  # garantiert, dass der Punkt sichtbar ist
ax2.set_xlim(-lim, lim)
ax2.set_ylim(-lim, lim)
ax2.set_xlabel("X [m]")
ax2.set_ylabel("Y [m]")
ax2.set_title("Kreise um den Nullpunkt (D=0.8 m)")
ax2.grid(True)
ax2.legend()

plt.show()
