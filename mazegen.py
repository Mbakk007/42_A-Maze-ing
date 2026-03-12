"""MazeGenerator module for a_maze_ing

This module provides the MazeGenerator class, which allows you to generate
mazes of customizable size, solve them, render them as ASCII, and save
them to a file.

Basic Usage Example::

    from MazeGenerator import MazeGenerator

    # Instantiate the generator with a 10x10 maze,
    gen = MazeGenerator(
        width=10,
        height=10,
        entry=(0, 0),
        exit=(9, 9),
        perfect=True,
        seed=42,
        output="maze.txt"
    )

    # Generate the maze
    gen.generate()

    # Solve the maze
    gen.solve()

    # Print the ASCII representation with the solution path
    print(gen.render_ascii(show_solution=True))

    # Save the maze and solution to a file
    gen.save_to_file("maze.txt")

Accessing the Maze Structure:

    After calling gen.generate(), the maze is stored in gen.maze, which is a
    2D list of dictionaries:

    gen.maze[y][x] -> {"up": bool, "right": bool, "down": bool, "left": bool}

    Each boolean indicates whether a wall is present in that direction.

Accessing the Solution:

    After calling gen.solve(), the solution is stored in gen.solution as a
    list of (x, y) tuples representing the path from entry to exit.

        gen.solution  ->  [(x0, y0), (x1, y1), ..., (xN, yN)]

    Example::

        gen.generate()
        gen.solve()

        if gen.solution:
            print("Solution path:", gen.solution)
        else:
            print("No solution found.")

Use save_to_file() to get the maze and solution in a text file.
"""

from typing import List, Tuple, Optional, Dict, Set, cast
import random
import sys

__version__ = "1.0.0"


class MazeGenerator:
    """Generate mazes, compute solutions, write to output files,
                                            and provide ASCII representations.

    The maze is built using a recursive backtracking algorithm starting from
    the entry point. Cells belonging to the '42' pattern (if the maze is large
    enough) are reserved and excluded from path carving."""

    def __init__(self, width: int, height: int,
                 entry: Tuple[int, int], exit: Tuple[int, int],
                 perfect: Optional[bool], seed: Optional[int],
                 output: Optional[str]) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit
        self.perfect: Optional[bool] = perfect
        self.seed: Optional[int] = seed
        self.maze: List[List[Dict[str, bool]]] = []
        self.output: Optional[str] = output
        self.solution: Optional[List[Tuple[int, int]]] = None
        self.reserved_cells: Set[Tuple[int, int]] = set()
        self.directions = [
                {"dx": 0, "dy": -1, "wall": "up",  "op_wall": "down"},
                {"dx": 1, "dy": 0,  "wall": "right", "op_wall": "left"},
                {"dx": 0, "dy": 1,  "wall": "down",  "op_wall": "up"},
                {"dx": -1, "dy": 0, "wall": "left",  "op_wall": "right"},
                     ]
        if entry == exit:
            raise ValueError("Entry and exit points cannot be the same.")

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry point is out of maze bounds.")

        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            raise ValueError("Exit point is out of maze bounds.")

    def _forty_two_cells(self) -> set[tuple[int, int]]:
        """Reserve cells needed to draw '42'"""

        if self.width < 8 or self.height < 6:
            print("Maze must be at least 8x6 to draw '42'")
            return set()

        # Cells needed to draw '42'
        FOUR = {(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4)}
        TWO = {(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2),
               (0, 3), (0, 4), (1, 4), (2, 4)}
        # calculate starting position to center '42' in the maze
        start_x = (self.width - 8) // 2
        start_y = (self.height - 6) // 2

        reserved = set()
        for x, y in FOUR:
            reserved.add((x + start_x, y + start_y))
        for x, y in TWO:
            reserved.add((x + start_x + 4, y + start_y))
        if self.entry in reserved or self.exit in reserved:
            raise ValueError("Entry and exit points cannot be on '42' cells.")
        return reserved

    def _create_grid(self) -> List[List[Dict[str, bool]]]:
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
            random.seed(self.seed)
        self.maze = self._create_grid()
        self.reserved_cells = self._forty_two_cells()
        visited = []
        # Mark all cells as unvisited
        for row in self.maze:
            visited.append([False] * len(row))
        # mark reserved cells as visited to prevent carving paths through them
        for x, y in self.reserved_cells:
            visited[y][x] = True
        # Recursion limit workaround
        required_limit = (self.width * self.height) + 1000
        try:
            if sys.getrecursionlimit() < required_limit:
                sys.setrecursionlimit(required_limit)
        except Exception as e:
            print(f"Warning: {e}")

        def explore(x: int, y: int) -> None:
            """Recursively explore and build paths from the current cell."""
            visited[y][x] = True
            random.shuffle(self.directions)
            for direction in self.directions:
                neighbor_x = x + cast(int, direction["dx"])
                neighbor_y = y + cast(int, direction["dy"])
                if not (0 <= neighbor_x < self.width and
                        0 <= neighbor_y < self.height):
                    continue
                if visited[neighbor_y][neighbor_x]:
                    continue
                # Remove walls between current and next cell
                self.maze[y][x][cast(str, direction["wall"])] = False
                self.maze[neighbor_y][neighbor_x][cast(
                    str, direction["op_wall"])] = False
                explore(neighbor_x, neighbor_y)
        # Start exploration from the entry point
        explore(self.entry[0], self.entry[1])
        # check if there is any remaining fully closed cell.
        for y in range(self.height):
            for x in range(self.width):
                if (self.maze[y][x]["up"] and self.maze[y][x]["right"]
                   and self.maze[y][x]["down"] and self.maze[y][x]["left"]):
                    if (x, y) not in self.reserved_cells:
                        if (x < self.width - 1 and
                           (x + 1, y) not in self.reserved_cells):
                            self.maze[y][x]["right"] = False
                            self.maze[y][x + 1]["left"] = False
                        elif (y < self.height - 1 and
                              (x, y + 1) not in self.reserved_cells):
                            self.maze[y][x]["down"] = False
                            self.maze[y + 1][x]["up"] = False
        # if perfect == False, remove 10 random walls
        if not self.perfect:
            removed = 0

            while removed < 10:
                x = random.randrange(self.width)
                y = random.randrange(self.height)

                direction = random.choice(self.directions)

                nx = x + cast(int, direction["dx"])
                ny = y + cast(int, direction["dy"])

                # check bounds
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue

                # skip reserved cells
                if ((x, y) in self.reserved_cells or
                   (nx, ny) in self.reserved_cells):
                    continue

                # remove wall if it exists
                if self.maze[y][x][cast(str, direction["wall"])]:
                    self.maze[y][x][cast(str, direction["wall"])] = False
                    self.maze[ny][nx][cast(str, direction["op_wall"])] = False
                    removed += 1

    def solve(self) -> None:
        """Compute the solution path from entry to exit using BFS."""

        # (current_x, current_y, path_so_far)
        queue = [(self.entry[0], self.entry[1], [self.entry])]

        # Keep track of visited cells
        visited = set()
        visited.add(self.entry)

        # keep track of index
        current_index = 0

        # while index in not at the end of the maze
        while current_index < len(queue):

            # Look at the current item based on our index
            current_x, current_y, path = queue[current_index]

            # increment index for the next iteration of the loop
            current_index += 1

            # if we reach the exit, save path
            if (current_x, current_y) == self.exit:
                self.solution = path
                return

            # Look at all 4 possible directions
            for direction in self.directions:
                wall_name = cast(str, direction["wall"])

                # If there is no wall in current direction, move forward
                if self.maze[current_y][current_x][wall_name] is False:
                    next_x = current_x + cast(int, direction["dx"])
                    next_y = current_y + cast(int, direction["dy"])

                    # mark as visited if not visited yet
                    if (next_x, next_y) not in visited:
                        visited.add((next_x, next_y))  # Mark as visited

                        # append path so far to new_path
                        new_path = path + [(next_x, next_y)]

                        # Add this to the end of the list to be checked later
                        queue.append((next_x, next_y, new_path))

        # If the loop finishes and we never found the exit
        self.solution = []

    def render_ascii(self, show_solution: bool = False,
                     wall_color: str = "\033[37m",
                     reserved_color: str = "\033[34m",
                     unicode: bool = False) -> str:
        """Return an ASCII representation of the maze.
            each cell is 3 by 1 characters.
            use unicode = True for unicode chars and false for simple ASCII."""
        if not unicode:
            edge = "+"
            horizontal = "-"
            vertical = "|"
        else:
            edge = "█"
            horizontal = "█"
            vertical = "█"

        maze = wall_color + edge + (horizontal * 4) * self.width + "\n"

        for y in range(self.height):
            middle_line = wall_color + vertical + "\033[0m"
            bottom_line = wall_color + edge + "\033[0m"

            for x in range(self.width):
                cell = "   "

                if (x, y) == self.entry:
                    cell = " S "
                elif (x, y) == self.exit:
                    cell = " E "
                elif (show_solution and self.solution
                      and (x, y) in self.solution):
                    cell = "\033[31m" + " ֎ " + "\033[0m"
                elif (x, y) in self.reserved_cells:
                    cell = reserved_color + "███" + "\033[0m"
                middle_line += cell

                # Right wall
                if self.maze[y][x]["right"]:
                    middle_line += wall_color + vertical + "\033[0m"
                else:
                    middle_line += " "

                # Bottom wall
                if self.maze[y][x]["down"]:
                    bottom_line += wall_color + (horizontal * 3) + "\033[0m"
                else:
                    bottom_line += "   "
                bottom_line += wall_color + edge + "\033[0m"
            maze += middle_line + "\n"
            maze += bottom_line + "\n"

        return maze

    def save_to_file(self, output: str) -> None:
        """Save the maze grid and solution to a text file.

        Writes the maze in an encoded format, followed by the entry
        and exit coordinates and the solution path."""
        def encode_cell(cell: Dict[str, bool]) -> str:
            value = 0
            if cell["up"]:
                value |= 1
            if cell["right"]:
                value |= 2
            if cell["down"]:
                value |= 4
            if cell["left"]:
                value |= 8
            return format(value, 'X')

        def path_to_directions(solution: List[Tuple[int, int]]) -> str:
            directions = []
            for i in range(len(solution) - 1):
                x1, y1 = solution[i]
                x2, y2 = solution[i + 1]
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0 and dy == -1:
                    directions.append("N")
                elif dx == 1 and dy == 0:
                    directions.append("E")
                elif dx == 0 and dy == 1:
                    directions.append("S")
                elif dx == -1 and dy == 0:
                    directions.append("W")
            return "".join(directions)
        with open(output, 'w') as f:
            for row in self.maze:
                line = "".join(encode_cell(cell) for cell in row)
                f.write(line + "\n")
            f.write("\n")

            f.write(f"{self.entry[0]} {self.entry[1]}\n")
            f.write(f"{self.exit[0]} {self.exit[1]}\n")

            if self.solution:
                f.write(path_to_directions(self.solution) + "\n")
            else:
                f.write("\n")
