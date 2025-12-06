import numpy as np
import matplotlib.pyplot as plt

# Gegebene Parameter
rho = 1.2         # Luftdichte [kg/m³]
cw = 0.21         # cw-Wert
d = 0.00542         # Durchmesser [m]
A = np.pi * (d/2)**2  # Stirnfläche [m²]
m = 0.0152277         # Masse [kg]
v0 = 70.104           # Anfangsgeschwindigkeit [m/s]
g = 9.81          # Erdbeschleunigung [m/s²]

# Horizontale Flugstrecke
x = np.linspace(0, 70, 10000)  # 0 bis 70 m

# Geschwindigkeit über die Strecke (nur Luftwiderstand, keine Gravitation)
v = v0 / (1 + (rho * cw * A * v0 * x) / (2 * m))

# Flugzeitintegration für jeden Abschnitt
dt = np.diff(x) / ((v[:-1] + v[1:]) / 2)
t = np.concatenate(([0], np.cumsum(dt)))

# Ballistische Kurve (mit Gravitation, ohne Windauftrieb)
# Annahme: idealer Startwinkel, der das Ziel bei 70 m trifft (~1.2°)
theta = np.radians(1.2)
vx = v * np.cos(theta)
vy0 = v0 * np.sin(theta)

# Zeitvektor für die gesamte Flugzeit
t_total = np.linspace(0, t[-1], len(x))

# Vertikale Position (mit Gravitation)
y = vy0 * t_total - 0.5 * g * t_total**2

# Plot
plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
plt.plot(x, v, color="tab:blue")
plt.title("Geschwindigkeitsverlauf und Flugbahn eines Recurve-Pfeils (70 m)")
plt.ylabel("Geschwindigkeit [m/s]")
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(x, y, color="tab:green")
plt.xlabel("Horizontale Entfernung [m]")
plt.ylabel("Höhe über Abschusspunkt [m]")
plt.grid(True)

plt.tight_layout()
plt.show()
