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

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry point is out of maze bounds.")

        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            raise ValueError("Exit point is out of maze bounds.")

        self.min_width = 8
        self.min_height = 6
        if self.width < self.min_width or self.height < self.min_height:
            raise ValueError("Maze must be at least 8x6 to draw '42'"
                             "(and guarantee entry/exit paths).")

    def _forty_two_cells(self) -> set[tuple[int, int]]:
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
        if self.entry in reserved or self.exit in reserved:
            raise ValueError("Entry and exit points cannot be on '42' cells.")
        return reserved

    def _create_grid(self) -> List[List[dict]]:
        """Initialize maze grid with all walls closed (True)."""
        maze = []
        for _ in range(self.height):
            maze.append([{"up": True, "right": True, "down": True,
                          "left": True} for _ in range(self.width)])
        return maze

    def generate(self) -> None:
        """Generate the maze using recursive
            backtracking, skipping reserved cells."""
        if self.seed is not None:
            random.seed(self.seed)  # Set seed for reproducibility
        self.maze = self._create_grid()
        self.reserved_cells = self._forty_two_cells()
        # Walls to remove in each direction
        directions = [
                {"dx": 0, "dy": -1, "wall": "up",  "op_wall": "down"},
                {"dx": 1, "dy": 0,  "wall": "right", "op_wall": "left"},
                {"dx": 0, "dy": 1,  "wall": "down",  "op_wall": "up"},
                {"dx": -1, "dy": 0, "wall": "left",  "op_wall": "right"},
                     ]
        visited = []
        # Mark all cells as unvisited
        for row in self.maze:
            visited.append([False] * len(row))
        # mark reserved cells as visited to prevent carving paths through them
        for x, y in self.reserved_cells:
            visited[y][x] = True

        def explore(x: int, y: int) -> None:
            """Recursively explore and build paths from the current cell."""
            visited[y][x] = True
            random.shuffle(directions)
            for direction in directions:
                neighbor_x = x + direction["dx"]
                neighbor_y = y + direction["dy"]
                if not (0 <= neighbor_x < self.width and
                        0 <= neighbor_y < self.height):
                    continue
                if visited[neighbor_y][neighbor_x]:
                    continue
                # Remove walls between current and next cell
                self.maze[y][x][direction["wall"]] = False
                self.maze[neighbor_y][neighbor_x][direction["op_wall"]] = False
                explore(neighbor_x, neighbor_y)
        # Start exploration from the entry point
        explore(self.entry[0], self.entry[1])

    def solve(self) -> None:
        """Compute the solution path from entry to exit using BFS."""
        # Implement BFS to find the shortest path from entry to exit
        pass

    def render_ascii(self, show_solution: bool = False) -> str:
        """Return an ASCII representation of the maze."""
        # Implement ASCII rendering of the maze, optionally showing the solution path
        pass