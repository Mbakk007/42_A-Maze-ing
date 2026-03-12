*This project has been created as part of the 42 curriculum by ael-bakk, jmoya-fe.*

# A-Maze-ing

A Python maze generator, solver, and renderer — featuring recursive backtracking, BFS pathfinding, ASCII/Unicode display, and a hidden **42** pattern embedded in every maze.

---

## Description

**A-Maze-ing** is a command-line tool that procedurally generates mazes of customizable size, solves them using BFS (Breadth-First Search), and renders them in the terminal using either ASCII characters or Unicode block characters.

### Goal

The goal of this project is to implement a fully functional maze generator from scratch, including:
- Procedural generation with configurable dimensions, entry/exit points, and optional seed for reproducibility.
- Automatic solving with the shortest path highlighted.
- A file output format encoding wall data in hexadecimal.
- A hidden **"42"** pattern drawn inside every maze large enough to contain it.

---

## Instructions

### Requirements

- Python 3.8 or higher
- No external dependencies required for core functionality

### Installation

```bash
# Clone the repository
git clone https://github.com/Mbakk007/42_A-Maze-ing.git
cd 42_A-Maze-ing

# (Optional) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development tools (linter + type checker)
make install
```

### Running the program

```bash
# Run with a configuration file
python3 a_maze_ing.py config.txt

# Or using the Makefile
make run
```

### Interactive Menu

Once the maze is generated and displayed, an interactive menu appears:

```
=== MAZE INTERACTIVE MENU ===
1. Toggle solution path
2. Change wall color
3. Change '42' pattern color
4. Change maze rendering style (ASCII/Unicode)
5. Generate new maze
6. Exit
```

### Linting & Type Checking

```bash
# Run flake8 + mypy
make lint

# Run in strict mode
make lint-strict
```

### Cleaning

```bash
# Remove cache files and generated output files
make clean
```

---

## Configuration File

The configuration file uses a simple `KEY=VALUE` format, one entry per line.  
Lines starting with `#` are treated as comments and ignored.

### Full structure

```ini
# ── Required fields ───────────────────────────────
WIDTH=X            # Maze width in cells (integer, min 1)
HEIGHT=X           # Maze height in cells (integer, min 1)
ENTRY=X,Y           # Entry point as x,y (must be within bounds)
EXIT=X,Y          # Exit point as x,y (must be within bounds, different from ENTRY)

# ── Optional fields ───────────────────────────────
OUTPUT_FILE=output_maze.txt  # Output file name (default: maze.txt)
PERFECT=TRUE/FALSE   # TRUE = perfect maze (no loops), FALSE = remove 10 extra walls
SEED=X               # Integer seed for reproducibility (omit for random)
```

### Rules

| Field | Required | Type | Notes |
|---|---|---|---|
| `WIDTH` | ✅ | Integer | Minimum 1; ≥ 8 to show "42" |
| `HEIGHT` | ✅ | Integer | Minimum 1; ≥ 6 to show "42" |
| `ENTRY` | ✅ | `x,y` | Must be within bounds |
| `EXIT` | ✅ | `x,y` | Must differ from `ENTRY` |
| `OUTPUT_FILE` | ❌ | String | Defaults to `maze.txt` |
| `PERFECT` | ❌ | `TRUE`/`FALSE` | Defaults to `None` (treated as perfect) |
| `SEED` | ❌ | Integer | Omit for a random maze each run |

### Output file format

The output file encodes the maze as follows:

- **One hexadecimal digit per cell**, encoding which walls are closed:

  | Bit | Direction |
  |---|---|
  | 0 (LSB) | North |
  | 1 | East |
  | 2 | South |
  | 3 | West |

  A closed wall sets the bit to `1`, an open wall to `0`.  
  Example: `3` (binary `0011`) = North and East walls closed.

- **One row per line**, left to right.
- **One empty line** after the grid.
- **Entry coordinates** (`x y`) on one line.
- **Exit coordinates** (`x y`) on one line.
- **Shortest path** as a string of `N`, `E`, `S`, `W` letters.

Example output for a 4×3 maze:
```
EFC6
9A5A
3F9C

0 0
3 2
EESSWEE
```

---

## How to use the MazeGenerator for a_maze_ing

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

---

## Maze Generation Algorithm

### Algorithm: Recursive Backtracking (DFS)

The maze is generated using **recursive backtracking**, also known as the **depth-first search (DFS)** algorithm.

#### How it works

1. Start at the **entry cell** and mark it as visited.
2. Randomly **shuffle the four possible directions** (N, E, S, W).
3. For each direction, check if the **neighbor is unvisited** and within bounds.
4. If so, **remove the wall** between the current cell and the neighbor, then **recurse** into the neighbor.
5. Repeat until all reachable cells are visited.
6. After generation, any **fully isolated cells** (all 4 walls closed) that were left unreachable are connected to an adjacent non-reserved cell.
7. If `PERFECT=FALSE`, **10 additional random walls** are removed to create loops and multiple paths.

#### Special handling: the "42" pattern

Before generation begins, cells that form the **"42" digit pattern** are marked as pre-visited. This prevents the algorithm from carving paths through them, leaving them as solid blocks that form the visible pattern in the rendered maze.

The pattern is centered in the maze and requires at least **8 columns × 6 rows**.

### Why this algorithm?

We chose recursive backtracking for several reasons:

- **Simple to implement** — the logic maps naturally to recursion.
- **Always produces a perfect maze** — exactly one path between any two cells (before optional wall removal).
- **Easy to seed** — using `random.seed()` makes mazes fully reproducible.
- **Compatible with reserved cells** — pre-marking "42" cells as visited integrates cleanly into the algorithm without extra logic.
- **Good visual quality** — produces long, winding corridors that look aesthetically interesting.

The main trade-off is stack depth for very large mazes. This is handled by dynamically increasing Python's recursion limit with `sys.setrecursionlimit()`.

---

## Reusable Code

The `mazegen.py` module is designed to be **fully reusable** as a standalone library.

### How to use it in your own project

```python
from mazegen import MazeGenerator

gen = MazeGenerator(
    width=15,
    height=15,
    entry=(0, 0),
    exit=(14, 14),
    perfect=True,
    seed=42,
    output="output_maze.txt"
)

gen.generate()   # Build the maze
gen.solve()      # Compute the shortest path

# Render to terminal
print(gen.render_ascii(show_solution=True))

# Save to file
gen.save_to_file("my_maze.txt")
```

### What is reusable

| Component | Description |
|---|---|
| `MazeGenerator` class | Full maze generation, solving and rendering |
| `generate()` | Produces the maze grid; works independently of solving |
| `solve()` | BFS solver; can be called separately after `generate()` |
| `render_ascii()` | ASCII/Unicode renderer with color support; fully parametric |
| `save_to_file()` | Writes the hex-encoded maze + solution to any file path |
| `maze` attribute | Raw 2D list of wall dictionaries; usable for custom renderers |
| `solution` attribute | List of `(x, y)` tuples; usable for custom path logic |

### Installation via flit

The module is packaged with **flit** and can be installed directly:

```bash
pip install flit
flit install
```

---

## Team & Project Management

### Team members

| Member | Role |
|---|---|
| **ael-bakk** | Maze generation algorithm, reserved cells logic, `mazegen.py` architecture |
| **jmoya-fe** | BFS solver, file output format, interactive menu, `a_maze_ing.py` |

Both members contributed to testing, debugging, ASCII rendering, and the `pyproject.toml` / `Makefile` setup.

### Planning

**Initial plan:**
- Design the data structures and implement the grid.
- Implement generation and solving.
- Implement rendering, file output, and the interactive menu.
- Testing, linting, documentation.

**How it evolved:**
- The "42" pattern requirement added complexity to the generation step and required careful handling of reserved cells before the algorithm runs.
- The file output hex format required more design time than expected to ensure correctness of the bit encoding.
- The interactive menu was added later and grew to include more options (Unicode mode, color changes) as we explored display possibilities.

### What worked well

- Splitting the project into two files (`mazegen.py` as a library, `a_maze_ing.py` as the entry point) made collaboration easier and kept responsibilities clear.
- Using a seed made debugging and testing consistent and reproducible.
- The BFS solver integrated cleanly with the existing maze structure.

### What could be improved

- The recursive backtracking approach can hit Python's recursion limit on very large mazes. An iterative DFS version would be more robust.
- The interactive menu could benefit from a cleaner UI library (e.g., `curses`).
- More generation algorithms (Prim's, Kruskal's, Wilson's) could be added as options in the config file.

### Tools used

| Tool | Purpose |
|---|---|
| **flake8** | PEP 8 style linting |
| **mypy** | Static type checking |
| **flit** | Python packaging |
| **make** | Task automation (`run`, `lint`, `clean`) |
| **GitHub** | Version control and collaboration |
| **GitHub Copilot** | Code suggestions, documentation, and debugging assistance |

---

## Resources

### Documentation & references

- [Python `random` module](https://docs.python.org/3/library/random.html) — used for shuffling directions and seeding.
- [Python `sys` module](https://docs.python.org/3/library/sys.html) — used for recursion limit and argument parsing.
- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — overview of recursive backtracking and alternatives.
- [Maze solving algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze-solving_algorithm) — background on BFS and DFS solving strategies.
- [Jamis Buck — Mazes for Programmers](https://pragprog.com/titles/jbmaze/mazes-for-programmers/) — comprehensive reference on maze generation and representation.
- [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code) — used for terminal colors in the renderer.
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/) — followed throughout the project.
- [mypy documentation](https://mypy.readthedocs.io/) — used for type annotation and static analysis.
- [flit documentation](https://flit.pypa.io/) — used for packaging `mazegen` as an installable module.

### AI usage

| **Debugging** | Identifying the `KeyError: 'WIDTH'` and `UnboundLocalError` bugs in `a_maze_ing.py` |
| **Documentation** | Generating and refining docstrings for `MazeGenerator` methods |
| **Type annotations** | Suggesting correct `typing` imports and annotations (`Dict`, `List`, `Tuple`, `Optional`, `Set`) |
| **README** | Drafting and structuring this README based on project requirements |
