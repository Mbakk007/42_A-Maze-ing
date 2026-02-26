import sys
from typing import Dict, Tuple
from mazegen import MazeGenerator


def parser(filename: str) -> Dict[str, str]:
    """Parse configuration file into a dictionary."""
    config = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('#') or not line:
                    continue
                key, value = line.split('=')
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
        # output_file = config['OUTPUT_FILE']
        perfect = config['PERFECT'] == 'True'
        seed = int(config['SEED']) if config['SEED'] else None
    except Exception as error:
        print(f"Invalid configuration values: {error}")
        sys.exit(1)

    maze = MazeGenerator(width, height, entry, exit, perfect, seed)
    maze.generate()
    # mazegenerator.solution
    # mazegenerator.write to output file

    while True:
        print("\n=== MAZE INTERACTIVE MENU ===")
        print("1. Display maze (ASCII)")
        print("2. Toggle solution path")
        print("3. Change wall color")
        print("4. Generate new maze")
        print("5. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            # placeholder for displaying maze in ASCII
            pass
        elif choice == '2':
            # placeholder for toggling solution path
            pass
        elif choice == '3':
            # placeholder for changing wall color
            pass
        elif choice == '4':
            maze.generate()  # Regenerate maze with same parameters
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
