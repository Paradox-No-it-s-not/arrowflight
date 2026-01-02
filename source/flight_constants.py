from dataclasses import dataclass


@dataclass
class Physics:
    rho: float = 1.2
    g: float = 9.81

# Global conversion constants
GRAINS_TO_KG = 0.00006479891
FPS_TO_MS = 0.3048
