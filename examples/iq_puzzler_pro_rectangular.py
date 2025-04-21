import argparse
import itertools
from datetime import datetime

from exact_cover import ExactCover

try:
    import numpy as np
except ImportError as e:
    print(f"{e.name} is required to run this script")
    exit(1)

PRINT_TEMPLATE = """
{01} {02} {03} {04} {05} {06} {07} {08} {09} {10} {11}
{12} {13} {14} {15} {16} {17} {18} {19} {20} {21} {22}
{23} {24} {25} {26} {27} {28} {29} {30} {31} {32} {33}
{34} {35} {36} {37} {38} {39} {40} {41} {42} {43} {44}
{45} {46} {47} {48} {49} {50} {51} {52} {53} {54} {55}
"""


def main(N: int, format: str):
    """
    The IQ Puzzle Pro game consists of 12 polyominos of different sizes.

    The 12 pieces are:

        111     1111    11     11
        1       1       1       11

        111     1       1      1
        1       11      111    11
        1        11      1     11

        11      1111    111    111
         111     1       1     1 1

    There are three variants of the game. A rectangular grid, another diamond-like
    shape, and the pyramid.

    This example covers the rectangular version. The rectangle is 5x11

    There are two kinds of constraints:

    1. Each shape must be used only once, and
    2. Each cell is covered once.

    The cells can be numbered as follows:

        1  2  3  4  5  6  7  8  9 10 11
       12 13 14 15 16 17 18 19 20 21 22
       23 24 25 26 27 28 29 30 31 32 33
       34 35 36 37 38 39 40 41 42 43 44
       45 46 47 48 49 50 51 52 53 54 55

    The strategy for computing candidates is to move, flip, and rotate each piece around.
    """

    # 1s represent where the shape is, zero padding where needed
    # Labels are arbitrary.
    shapes = {
        "A": [
            [1, 1, 1],
            [1],
        ],
        "B": [
            [1, 1, 1, 1],
            [1],
        ],
        "C": [
            [1, 1],
            [1],
        ],
        "D": [
            [1, 1, 1],
            [1],
            [1],
        ],
        "E": [
            [1, 1],
            [0, 1, 1],
        ],
        "F": [
            [1],
            [1, 1],
            [0, 1, 1],
        ],
        "G": [
            [1, 1],
            [0, 1, 1, 1],
        ],
        "H": [
            [1],
            [1, 1],
            [1],
            [1],
        ],
        "I": [
            [1],
            [1, 1],
            [1],
        ],
        "J": [
            [1],
            [1, 1, 1],
            [0, 1],
        ],
        "K": [
            [1, 1],
            [1],
            [1, 1],
        ],
        "L": [
            [1, 1, 1],
            [1, 1],
        ],
    }

    board = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
        [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33],
        [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44],
        [45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55],
    ]

    # Create a map for (x, y) to cell.
    # The first cell, 1, would be at (0, 0).
    # The next cell, 2, would be at (0, 1) and so on.
    plane = {(x, y): cell for y, column in enumerate(board) for x, cell in enumerate(column)}

    def candidates():
        for label, shape in shapes.items():
            # Compute the width/height of the shape. Shapes data isn't always
            # rectangular, so look through all rows for width.
            w, h = max(map(len, shape)), len(shape)

            # Convert shape data to homogeneous coordinate points
            shape = np.array(
                [
                    [x, y, 1]
                    for x, row in enumerate(shape)
                    for y, value in enumerate(row)
                    if value  # Skip leading 0 padding
                ]
            ).T

            # Generate unique orientations (some flip/rotation combos may be the same)
            orientations = {
                # Apply transformation to shape.
                # Convert to regular point list.
                # Store points in set as order doesn't matter.
                frozenset((x, y) for x, y, _ in (T @ shape).T.tolist())
                for T in [
                    # Rotations
                    np.array([[+1, +0, 1 - 1], [+0, +1, 1 - 1], [0, 0, 1]]),
                    np.array([[+0, -1, w - 1], [+1, +0, 1 - 1], [0, 0, 1]]),
                    np.array([[-1, +0, h - 1], [+0, -1, w - 1], [0, 0, 1]]),
                    np.array([[+0, +1, 1 - 1], [-1, +0, h - 1], [0, 0, 1]]),
                    # Rotations after flipping
                    np.array([[+0, +1, 1 - 1], [+1, +0, 1 - 1], [0, 0, 1]]),
                    np.array([[-1, +0, h - 1], [+0, +1, 1 - 1], [0, 0, 1]]),
                    np.array([[+0, -1, w - 1], [-1, +0, h - 1], [0, 0, 1]]),
                    np.array([[+1, +0, 1 - 1], [+0, -1, w - 1], [0, 0, 1]]),
                    # Each transformation keeps shape in 1st quadrant by translations as needed
                ]
            }

            for orientation in orientations:
                for dx, dy in itertools.product(
                    range(max(x for x, _ in plane.keys()) + 1),  # horizontal bounds
                    range(max(y for _, y in plane.keys()) + 1),  # vertical bounds
                ):
                    # Move shape in the plane
                    points = set((x + dx, y + dy) for x, y in orientation)
                    # Check entire shape is in bounds
                    if all(key in plane for key in points):
                        # Candidate found for shape. Return label and cells covered
                        cells = tuple(sorted(plane[point] for point in points))
                        yield (label, cells), (label, *cells)  # candidate, constraint

    start = datetime.now()

    engine = ExactCover(
        # 67 constraints
        constraints=[
            # Each shape used once
            *shapes.keys(),
            # Each cell covered once
            *range(1, 56),
        ],
        # 2,140 candidates
        candidates=candidates(),
    )
    print("Rectangular puzzle solutions:")
    breakpoint()

    if format == "dense":
        header = ",".join(label for label, shape in sorted(shapes.items()) for row in shape for column in row if column)
        print(f"{"Key":<21}", header)

    start = datetime.now()
    for n, solution in enumerate(itertools.islice(engine.search(), N), start=1):
        match format:
            case "pretty":
                print(f"{datetime.now() - start} {n:>6,}")
                print(
                    PRINT_TEMPLATE.format(
                        None,
                        *(label for _, label in sorted((cell, label) for label, cells in solution for cell in cells)),
                    )
                )

            case "simple":
                print(
                    f"{datetime.now() - start} {n:>6,}",
                    " ".join(f"{label}:{set(cells)}" for label, cells in sorted(solution)),
                )

            case "dense":
                print(
                    f"{datetime.now() - start} {n:>6,}",
                    ",".join(str(cell) for _, cells in sorted(solution) for cell in cells),
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Generates solutions for the rectangular variant of the IQ Puzzler Pro game.\n"
            "There are 4,331,140 solutions."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--format",
        choices=["pretty", "simple", "dense"],
        default="pretty",
        help=(
            "pretty: Shows solution in a rectangle.\n"
            "simple: Lists the cells each piece occupies\n"
            "dense: Lists the cells all pieces occupied in one list."
            " Header key is printed to show which item belongs to which piece."
        ),
    )
    parser.add_argument(
        "-N",
        default=10,
        type=int,
        help=(
            "Number of solutions to print. Default is 10. Pass -1 to print all solutions.\n"
            'Recommend using "--format dense" when printing all solutions.'
        ),
    )
    args = parser.parse_args()
    if args.N == -1:
        args.N = None
    main(**vars(args))
