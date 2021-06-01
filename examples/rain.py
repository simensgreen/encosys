from dataclasses import dataclass
from random import randint
from tkinter import *

from __init__ import World


# =================== Components begin ===================
@dataclass
class Transform:
    x: float
    y: float


class Gravity:
    VECTOR = Transform(0, 2)


class CanvasId(int):
    pass
# ==================== Components end ====================


class RainApp:
    FPS = 30
    DOT_SIZE = 2
    CANVAS_SIZE = 700
    GRAVITY_COLOR = {True: 'blue', False: 'red'}
    DOT_COUNT = 100

    def __init__(self):
        self.root = Tk()
        self.root.title(self.__class__.__name__)

        self.canvas = Canvas(width=self.CANVAS_SIZE, height=self.CANVAS_SIZE)
        self.canvas.pack()

        # =================== Important begin ===================
        self.world = World()
        self.world.system(self.gravity, family='phys', parallel=False)
        self.world.system(self.draw, family='draw')
        # ==================== Important end ====================

        for i in range(self.DOT_COUNT):
            self.draw_dot(randint(0, self.CANVAS_SIZE), randint(0, self.CANVAS_SIZE), gravity=i % 2 == 0)

    def draw_dot(self, x, y, gravity=True):
        transform = Transform(x, y)
        canvas_id = CanvasId(self.canvas.create_rectangle(self.transform_to_coords(transform),
                                                          fill=self.GRAVITY_COLOR[gravity], width=0))
        # =================== Important begin ===================
        if gravity:
            self.world.spawn(transform, canvas_id, Gravity())
        else:
            self.world.spawn(transform, canvas_id)
        # ==================== Important end ====================

    # ==================== Systems begin ====================
    @staticmethod
    def gravity(transforms: Transform, _grav: Gravity):
        """
        This system will receive tuple of entities components that have both Transform and Gravity
        It turns out that this system only manipulates entities subject to gravity.
        If you add `__` to the ending of the name`grav`, the system will receive only entities components without a
        Gravity component

        Args:
            transforms Tuple[Transform]: instances of Transform, associated with entity
            grav Tuple[Gravity]: instances of Gravity, associated with entity

        """
        for transform in iter(transforms):
            transform.x += Gravity.VECTOR.x
            transform.y += Gravity.VECTOR.y

    def draw(self, canvas_ids: CanvasId, transforms: Transform):
        """
        This system will receive tuple of entities components that have both Transform and CanvasId

        Args:
            canvas_ids Tuple[CanvasId]: instances of CanvasId, associated with entity:
            transforms Tuple[Transform]: instances of Transform, associated with entity

        """
        for canvas_id, transform in zip(canvas_ids, transforms):
            # for each entity (for each components set) update coords
            self.canvas.coords(canvas_id, self.transform_to_coords(transform))

    # ===================== Systems end =====================

    def transform_to_coords(self, transform):
        return (transform.x - self.DOT_SIZE, transform.y - self.DOT_SIZE,
                transform.x + self.DOT_SIZE, transform.y + self.DOT_SIZE)

    def process(self):
        # this is simplest way to loop
        self.root.after(round(1000 / self.FPS), self.process)

        # call systems associated with family name
        self.world.call_family('phys')
        self.world.call_family('draw')

    def run(self):
        self.process()
        self.root.mainloop()


if __name__ == '__main__':
    app = RainApp()
    app.run()
