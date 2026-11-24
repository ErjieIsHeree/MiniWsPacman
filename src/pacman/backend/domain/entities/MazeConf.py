from dataclasses import dataclass

from entities import LevelConf


@dataclass(frozen=True)
class MazeConf():
    highscore_filename: str                 # (a file name with '.json' extension, cannot be empty and cannot be config.json)
    level_conf_defaults: LevelConf
    level_conf: dict[str, LevelConf]        # (the string are numbers from 1 to the last level, they cannot be repeated)
    levels: int                             # (a number from 1 to 100)
    lives: int                              # (a number from 1 to 100)
    points_per_pacgum: int                  # (a number from 1 to 5000)
    points_per_super_pacgum: int            # (a number from 1 to 5000)
    points_per_ghost: int                   # (a number from 1 to 5000)
    seed: int                               # (see MazeGenerator limits, try -inf and +inf)
