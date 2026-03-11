import sys
from typing import Dict, Tuple
from mazegen import MazeGenerator
import random

# ANSI color codes
COLORS = [
    "\033[31m",  # red
    "\033[32m",  # green
    "\033[33m",  # yellow
    "\033[34m",  # blue
    "\033[35m",  # magenta
    "\033[36m",  # cyan
    "\033[37m",  # white
]
RESET = "\033[0m"


def parser(filename: str) -> Dict[str, str]:
    """Parse configuration file into a dictionary."""
    config = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                key, value = line.split('=', 1)
                config[key] = value
    except FileNotFoundError:
        print(f"Error: Configuration file {filename} not found!")
        sys.exit(1)
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)
    return config


def parse_tuple(value: str) -> Tuple[int, int]:
    """Convert 'x,y' → (x,y)."""
    x, y = value.split(",")
    return int(x), int(y)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    config_file = sys.argv[1]
    config = parser(config_file)

    try:
        width = int(config['WIDTH'])
        height = int(config['HEIGHT'])
        entry = parse_tuple(config['ENTRY'])
        exit = parse_tuple(config['EXIT'])
        output_file = config.get('OUTPUT_FILE', 'maze.txt')
        perfect = (config['PERFECT'].strip().upper() == "TRUE" if
                   config.get('PERFECT') else None)
        seed = int(config['SEED']) if config.get('SEED') else None
        maze = MazeGenerator(width, height, entry, exit, perfect,
                             seed, output_file)
    except Exception as error:
        print(f"Invalid configuration values: {error}")
        print("Switching to default values... (10x10)")
        maze = MazeGenerator(10, 10, (0, 0), (9, 9), None, None, output_file)

    maze.generate()
    maze.solve()
    show_solution = False
    wall_color = "\033[37m"
    reserved_color = "\033[34m"
    print(maze.render_ascii(show_solution, wall_color, reserved_color))
    maze.save_to_file(output_file)

    while True:
        print("\n=== MAZE INTERACTIVE MENU ===")
        print("1. Toggle solution path")
        print("2. Change wall color")
        print("3. Change '42' pattern color")
        print("4. Generate new maze")
        print("5. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            show_solution = not show_solution
            print(maze.render_ascii(show_solution, wall_color, reserved_color))
        elif choice == '2':
            wall_color = random.choice(COLORS)
            print(maze.render_ascii(show_solution, wall_color, reserved_color))
        elif choice == '3':
            reserved_color = random.choice(COLORS)
            print(maze.render_ascii(show_solution, wall_color, reserved_color))
        elif choice == '4':
            seed = random.seed()
            maze.generate()  # Regenerate maze with different seed
            maze.solve()
            print(maze.render_ascii(show_solution, wall_color, reserved_color))
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
