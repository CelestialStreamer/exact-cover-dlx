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
      {04}       {16}       {32}
    {03}   {09}   {15}   {23}   {31}   {39}
  {02}   {08}   {14}   {22}   {30}   {38}   {46}
{01}   {07}   {13}   {21}   {29}   {37}   {45}   {51}
  {06}   {12}   {20}   {28}   {36}   {44}   {50}
{05}   {11}   {19}   {27}   {35}   {43}   {49}   {55}
  {10}   {18}   {26}   {34}   {42}   {48}   {54}
    {17}   {25}   {33}   {41}   {47}   {53}
      {24}       {40}       {52}
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

    This example covers the diamond version.

    There are two kinds of constraints:

    1. Each shape must be used only once, and
    2. Each cell is covered once.

    The cells can be numbered as follows:

               4          16          32
            3     9    15    23    31    39
         2     8    14    22    30    38    46
      1     7    13    21    29    37    45    51
         6    12    20    28    36    44    50
      5    11    19    27    35    43    49    55
        10    18    26    34    42    48    54
           17    25    33    41    47    53
              24          40          52

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
        [0, 1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1, 1, 1, 1, 0],
    ]

    # Create a map for (x, y) to cell.
    # The first cell, 1, would be at (0, 0).
    # The next cell, 2, would be at (0, 1) and so on.
    cell = iter(range(1, 56))
    plane = {(x, y): next(cell) for y, column in enumerate(board) for x, c in enumerate(column) if c}

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
        # 2,116 candidates
        candidates=candidates(),
    )
    print("Diamond puzzle solutions:")
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
            "Generates solutions for the diamond variant of the IQ Puzzler Pro game.\nThere are 1,376,400 solutions."
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
