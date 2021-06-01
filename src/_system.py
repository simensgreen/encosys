from dataclasses import dataclass, field


@dataclass(frozen=True)
class System:
    func: callable
    query: tuple
    family: str
    parallel: bool = field(default=True)

    def __call__(self, *args, **kwargs):
        self.func(*args, **kwargs)
