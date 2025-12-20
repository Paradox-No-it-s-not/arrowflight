from dataclasses import dataclass
from typing import Dict
import math
from constants import GRAINS_TO_KG, FPS_TO_MS


@dataclass
class Profile:
    name: str
    mass_grains: float = 235.0
    diameter_m: float = 0.00542
    cw: float = 0.25
    v0_fps: float = 230.0
    

    def mass_kg(self) -> float:
        return self.mass_grains * GRAINS_TO_KG

    def area(self) -> float:
        return math.pi * (self.diameter_m / 2.0) ** 2

    def v0_ms(self) -> float:
        return self.v0_fps * FPS_TO_MS

    def to_sim_params(self) -> Dict[str, float]:
        return {
            'v0': self.v0_ms(),
            'm': self.mass_kg(),
            'a': self.area(),
            'cw': self.cw
        }

    @classmethod
    def from_dict(cls, name: str, d: Dict) -> 'Profile':
        return cls(
            name=name,
            mass_grains=d.get('mass_grains', 235.0),
            diameter_m=d.get('diameter_m', 0.00542),
            cw=d.get('cw', 0.25),
            v0_fps=d.get('v0_fps', 230.0)
        )
