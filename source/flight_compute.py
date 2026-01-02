import numpy as np
from flight_profiles import Profile
from flight_constants import Physics


def simulate_flight(theta: float, profile: Profile, target_x: float, dt: float = 0.001,
                    phys: Physics = None, record_trajectory: bool = False):
    """Simulates flight using provided Profile and Physics; returns endpoint and optionally trajectory.

    See original implementation in `flight.py` for semantics.
    """
    # extract sim params from Profile
    v0 = profile.v0_ms()
    m = profile.mass_kg()
    a = profile.area()
    cw = profile.cw

    vx = v0 * np.cos(theta)
    vy = v0 * np.sin(theta)
    x, y, t = 0.0, 0.0, 0.0

    if record_trajectory:
        xs, ys, vxs, vys, ts = [], [], [], [], []

    rho = phys.rho if phys is not None else 1.2
    g = phys.g if phys is not None else 9.81

    while x <= target_x:
        v = np.sqrt(vx**2 + vy**2)
        if v == 0:
            Fd = 0.0
            ax = 0.0
            ay = -g
        else:
            Fd = 0.5 * rho * cw * a * v**2
            ax = -Fd * vx / (m * v)
            ay = -g - Fd * vy / (m * v)

        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt

        if record_trajectory:
            xs.append(x)
            ys.append(y)
            vxs.append(vx)
            vys.append(vy)
            ts.append(t)

    v_end = np.sqrt(vx**2 + vy**2)
    angle_end = np.degrees(np.arctan2(vy, vx))

    if record_trajectory:
        return x, y, t, v_end, angle_end, xs, ys, vxs, vys, ts
    return x, y, t, v_end, angle_end


def find_optimal_angle(profile: Profile, target_x: float, target_y: float, dt: float = 0.001,
                       phys: Physics = None, iterations: int = 25):
    """Binary search for optimal launch angle that reaches target_x/target_y.

    Returns (best_theta_rad, best_x_hit, best_y_hit)
    """
    low, high = np.radians(-45.0), np.radians(45.0)
    best_theta = None
    best_x_hit = best_y_hit = None

    for _ in range(iterations):
        mid = 0.5 * (low + high)
        x_hit, y_hit, t, v_end, a_end = simulate_flight(mid, profile=profile, target_x=target_x,
                                                       dt=dt, phys=phys)
        if (x_hit < target_x) or (y_hit < target_y):
            low = mid
        else:
            high = mid
        best_theta = mid
        best_x_hit, best_y_hit = x_hit, y_hit

    return best_theta, best_x_hit, best_y_hit
