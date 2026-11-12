from dataclasses import dataclass, field

from .level_conf import LevelConf


@dataclass(frozen=True)
class GameConf():
    highscore_filename: str = field(default="asd")
    level_conf_defaults: LevelConf = field(default=LevelConf())
    level_conf: dict[str, LevelConf] = field(default={
        "5": LevelConf(height=16, width=16, pacgums=50, max_time=120),
        "10": LevelConf(height=17, width=17, pacgums=70, max_time=150),
        "15": LevelConf(height=18, width=18, pacgums=80, max_time=180),
        "20": LevelConf(height=19, width=19, pacgums=100, max_time=210)
    })
    levels: int = field(default=25)
    lives: int = field(default=5)
    points_per_pacgum: int = field(default=10)
    points_per_super_pacgum: int = field(default=50)
    points_per_ghost: int = field(default=200)
    seed: int = field(default=42)
