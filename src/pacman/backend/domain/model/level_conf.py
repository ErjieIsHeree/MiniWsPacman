from dataclasses import dataclass, field


@dataclass(frozen=True)
class LevelConf():
    width: int = field(default=15)
    height: int = field(default=15)
    pacgums: int = field(default=42)
    max_time: int = field(default=90)
