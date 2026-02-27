"""MazeGenerator module for a_maze_ing"""

from typing import List, Tuple, Optional
import random


class MazeGenerator:
    """Class to generate mazes, compute solutions,
        and provide ASCII representations."""

    def __init__(self, width: int, height: int,
                 entry: Tuple[int, int], exit: Tuple[int, int],
                 perfect: bool, seed: Optional[int]) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed
        self.maze: List[List[dict]] = []
        self.solution = None

        if entry == exit:
            raise ValueError("Entry and exit points cannot be the same.")

        if entry[0] < 0 or entry[0] >= width or entry[1] < 0 or entry[1] >= height:
            raise ValueError("Entry point is out of maze bounds.")

        if exit[0] < 0 or exit[0] >= width or exit[1] < 0 or exit[1] >= height:
            raise ValueError("Exit point is out of maze bounds.")

        self.min_width = 7
        self.min_height = 5
        if self.width < self.min_width or self.height < self.min_height:
            raise ValueError("Maze must be at least 7x5 to draw '42'")

    def forty_two_cells(self) -> set[tuple[int, int]]:
        """Reserve cells needed to draw '42'"""

        # Cells needed to draw '42'
        FOUR = {(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4)}
        TWO = {(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2),
               (0, 3), (0, 4), (1, 4), (2, 4)}
        # calculate starting position to center '42' in the maze
        start_x = (self.width - self.min_width) // 2
        start_y = (self.height - self.min_height) // 2

        reserved = set()
        for x, y in FOUR:
            reserved.add((x + start_x, y + start_y))
        for x, y in TWO:
            reserved.add((x + start_x + 4, y + start_y))
        return reserved

    def create_grid(self) -> List[List[dict]]:
        """Initialize maze grid with all walls closed (True)."""
        maze = []

        x_index = 0
        while x_index < self.height:
            x = []
            y_index = 0
            while y_index < self.width:
                cell = {"up": True, "right": True, "down": True, "left": True}
                x.append(cell)
                y_index += 1
            maze.append(x)
            x_index += 1
        return maze

    def generate(self) -> None:
        """Generate the maze using recursive
            backtracking, skipping reserved cells
                and keeping track of solution path."""
        if self.seed is not None:
            random.seed(self.seed)  # Set seed for reproducibility
        self.maze = self.create_grid()
        self.reserved_cells = self.forty_two_cells()
        # Walls to remove in each direction
        directions = [
                    {"dx": 0, "dy": -1, "current": "up",  "opposite": "down"},
                    {"dx": 1, "dy": 0,  "current": "right", "opposite": "left"},
                    {"dx": 0, "dy": 1,  "current": "down",  "opposite": "up"},
                    {"dx": -1, "dy": 0, "current": "left",  "opposite": "right"},
                     ]
        visited = []
        # Mark all cells as unvisited
        for row in self.maze:
            visited.append([False] * len(row))
        # mark reserved cells as visited to prevent carving paths through them
        for x, y in self.reserved_cells:
            visited[y][x] = True

        def explore(x: int, y: int, path: list[str]) -> None:
            """Recursively explore and build paths from the current cell."""
            visited[y][x] = True
            # If we reach the exit, save the solution path
            if (x, y) == self.exit and self.solution is None:
                self.solution = path.copy()
            random.shuffle(directions)
            for direction in directions:
                neighbor_x = x + direction["dx"]
                neighbor_y = y + direction["dy"]
                if (neighbor_x < 0 or neighbor_x >= self.width or
                        neighbor_y < 0 or neighbor_y >= self.height):
                    continue
                if visited[neighbor_y][neighbor_x]:
                    continue
                # Remove walls between current and next cell
                self.maze[y][x][direction["current"]] = False
                self.maze[neighbor_y][neighbor_x][direction["opposite"]] = False
                # Add direction to path and explore next cell
                new_path = path + [direction["current"]]
                explore(neighbor_x, neighbor_y, new_path)
        # Start exploration from the entry point
        explore(self.entry[0], self.entry[1], [])
