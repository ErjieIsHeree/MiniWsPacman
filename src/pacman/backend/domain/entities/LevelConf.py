from dataclasses import dataclass


@dataclass(frozen=True)
class LevelConf():
    width: int      # (a number from 1 to 5000, make tests)
    height: int     # (a number from 1 to 5000, make tests)
    pacgums: int    # (a number from 1 to 5000, make tests)
    max_time: int   # (a number from 1 to 5000, make tests)
