import tkinter as tk
from tkinter.constants import *
from dataclasses import dataclass, field
from typing import MutableSet, FrozenSet
import random
import time
import threading

CELL_DEFAULT_COLOUR = "white"
ANIMATE_DELAY = 0.01


@dataclass
@dataclass(unsafe_hash=True)
class Cell:
    x0: int
    y0: int
    x1: int
    y1: int
    colour: str = field(default=CELL_DEFAULT_COLOUR, compare=False)


def colour_cell(cell: Cell, canvas: tk.Canvas, colour: str):
    canvas.create_rectangle(
        cell.x0, cell.y0, cell.x1, cell.y1, fill=colour, outline="black"
    )


class WaveFunctionApp:
    def __init__(self, root: tk.Tk, height: int, width: int, step_count: int) -> None:
        self.root = root
        self.height = height
        self.width = width
        self.step_count = step_count

        self.canvas = tk.Canvas(root, width=self.width, height=self.height)
        self.canvas.pack()
        self._cells = None
        self._drawn = set()
        self.animate_stop = threading.Event()
        self.animate_running = threading.Event()

    def go(self):
        self._draw_grid()
        self._draw_buttons()

    @property
    def step_size(self) -> int:
        return int(self.width / self.step_count)

    @property
    def cells(self) -> FrozenSet[Cell]:
        if self._cells is None:
            self._cells = self._get_cells()
        return set(self._cells)

    @property
    def drawn(self) -> MutableSet[Cell]:
        return self._drawn

    @drawn.setter
    def drawn(self, drawn):
        self._drawn = drawn

    def _draw_grid(self):
        y_start = 0
        y_end = self.height

        for x in range(0, self.width, self.step_size):
            line = (x, y_start, x, y_end)
            self.canvas.create_line(line)

        x_start = 0
        x_end = self.width

        for y in range(0, self.height, self.step_size):
            line = (x_start, y, x_end, y)
            self.canvas.create_line(line)

    def _get_cells(self) -> FrozenSet[Cell]:
        cells = []
        for x in range(0, self.width, self.step_size):
            for y in range(0, self.height, self.step_size):
                cells.append(
                    Cell(x0=x, y0=y, x1=x + self.step_size, y1=y + self.step_size)
                )
        return cells

    def _draw_buttons(self) -> None:
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        next_cell = tk.Button(button_frame, text="next cell")
        fill_all = tk.Button(button_frame, text="fill all")
        reset = tk.Button(button_frame, text="reset")
        animate = tk.Button(button_frame, text="animate")

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        next_cell.grid(row=0, column=0, sticky=tk.W + tk.E)
        fill_all.grid(row=0, column=1, sticky=tk.W + tk.E)
        reset.grid(row=0, column=2, sticky=tk.W + tk.E)
        animate.grid(row=0, column=3, sticky=tk.W + tk.E)

        next_cell.bind("<Button-1>", self.go_click)
        fill_all.bind("<Button-1>", self.fill_all)
        reset.bind("<Button-1>", self.reset)
        animate.bind("<Button-1>", self.animate)

    def go_click(self, event: tk.Event) -> None:
        next = random.choice(list(self.cells))
        self.drawn.add(next)
        colour_cell(next, self.canvas, "blue")

    def fill_all(self, event: tk.Event) -> None:
        for cell in self.cells:
            cell.colour = "blue"
            self.drawn.add(cell)
            colour_cell(cell, self.canvas, cell.colour)

    def reset(self, event: tk.Event) -> None:
        self.animate_stop.set()
        for cell in self.drawn:
            cell.colour = CELL_DEFAULT_COLOUR
            colour_cell(cell, self.canvas, cell.colour)
        
        time.sleep(0.5)
        self.animate_stop.clear()
        
        self.drawn = set()

    def _animate(self) -> None:
        for cell in self.cells:
            if self.animate_stop.is_set():
                break

            if cell not in self.drawn:
                cell.colour = "blue"
                self.drawn.add(cell)
                colour_cell(cell, self.canvas, cell.colour)
                self.canvas.update()
                time.sleep(ANIMATE_DELAY)
        self.animate_running.clear()

    def animate(self, event: tk.Event) -> None:
        if not self.animate_running.is_set():
            self.animate_running.set()
            threading.Thread(target=self._animate).start()
            


if __name__ == "__main__":
    step_count = 100
    canvas_width, canvas_height = 1000, 1000

    root = tk.Tk()

    app = WaveFunctionApp(root, canvas_height, canvas_width, step_count)
    app.go()

    root.mainloop()
