import numpy as np
import matplotlib.pyplot as plt

# --- Parameter des Pfeils ---
m = 0.0152277        # Masse [kg]
d = 0.00542        # Durchmesser [m]
A = np.pi * (d/2)**2  # Stirnfläche [m²]
cw = 0.21        # Luftwiderstandsbeiwert
rho = 1.2        # Luftdichte [kg/m³]
g = 9.81         # Erdbeschleunigung [m/s²]
v0 = 70.0        # Anfangsgeschwindigkeit [m/s]
theta0 = np.radians(1.2)  # Abschusswinkel [rad]

# --- Startbedingungen ---
vx = v0 * np.cos(theta0)
vy = v0 * np.sin(theta0)
x, y = 0.0, 0.0

# --- Numerische Parameter ---
dt = 0.001  # Zeitschritt [s]
t = 0.0

# --- Speicher für Ergebnisse ---
xs, ys, vxs, vys, ts = [x], [y], [vx], [vy], [t]

# --- Simulation ---
# while y >= 0 and x <= 70:  # bis der Pfeil 70 m erreicht oder auf den Boden fällt
while x <= 70:  # bis der Pfeil 70 m erreicht oder auf den Boden fällt
    v = np.sqrt(vx**2 + vy**2)
    F_drag = 0.5 * rho * cw * A * v**2

    # Beschleunigungen
    ax = -F_drag * vx / (m * v)
    ay = -g - (F_drag * vy / (m * v))

    # Integration (Euler)
    vx += ax * dt
    vy += ay * dt
    x += vx * dt
    y += vy * dt
    t += dt

    # Speichern
    xs.append(x)
    ys.append(y)
    vxs.append(vx)
    vys.append(vy)
    ts.append(t)

# --- Auswertung ---
v_total = np.sqrt(np.array(vxs)**2 + np.array(vys)**2)

# --- Plot ---
plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
plt.plot(xs, v_total, color="tab:blue")
plt.ylabel("Geschwindigkeit [m/s]")
plt.title("Recurve-Pfeil mit Gravitation und Luftwiderstand")
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(xs, ys, color="tab:green")
plt.xlabel("Horizontale Entfernung [m]")
plt.ylabel("Höhe [m]")
plt.grid(True)

plt.tight_layout()
plt.show()

# --- Ergebnisse ---
print(f"Flugzeit: {t:.2f} s")
print(f"Endgeschwindigkeit: {v_total[-1]:.2f} m/s")
print(f"Einschlagwinkel: {np.degrees(np.arctan2(vys[-1], vxs[-1])):.2f}°")
