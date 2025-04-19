import argparse
import itertools
from datetime import datetime

from exact_cover import ExactCover

try:
    import numpy as np
except ImportError as e:
    print(f"{e.name} is required to run this script")
    exit(1)


def main(N: int, format: str):
    """
    The game IQ Puzzle Pro game consists of 12 polyominos of different sizes.

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

    This example covers the pyramid.

    The pyramid has 5 layers: 5x5, 4x4, 3x3, 2x2, and 1x1. A puzzle piece can be
    placed horizontally (with all its ball shapes in the same pyramid level), or
    at a 45° angle (with its ball shapes spread over multiple layers).

    There are two kinds of constraints:

    1. Each shape must be used only once, and
    2. Each cell is covered once.

    The cells can be numbered as follows:

               55

             51  52
             53  54

           42  43  44
           45  46  47
           48  49  50

         26  27  28  29
         30  31  32  33
         34  35  36  37
         38  39  40  41

        1   2   3   4   5
        6   7   8   9  10
       11  12  13  14  15
       16  17  18  19  20
       21  22  23  24  25

    An example of the diagonal plane is:

       5 29 44 52 55
          9 32 46 53
            13 35 48
               17 38
                  21

    The strategy for computing candidates is to move and rotate each piece
    around each layer, the diagonal plane, and the reverse diagonal plane.
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

    # 5 horizontal slices: 5x5, 4x4, 3x3, 2x2, and 1x1
    cell = iter(itertools.count(1))  # Label cells a successive number from 1 to 55
    h = [[[next(cell) for _ in range(n)] for _ in range(n)] for n in range(5, 0, -1)]
    # 45 degree vertical slices from top left corner to bottom right corner
    v1 = [
        [
            [h[a - b][b + max(n - 5, 0)][(n - 1) - a - max(n - 5, 0)] for b in range(a + 1)]
            for a in range(5 - abs(n - 5))
        ]
        for n in range(1, 2 * 5)
    ]
    # -45 degree vertical slices from top right corner to bottom left corner
    v2 = [
        [[h[a - b][b + max(n - 5, 0)][b + max(5 - n, 0)] for b in range(a + 1)] for a in range(5 - abs(n - 5))]
        for n in range(1, 2 * 5)
    ]

    # Create a map for (x,y) to cell
    # The first cell, 1, would be at (0, 0).
    # The next cell, 2, would be at (0, 1) and so on.
    # Each layer's starting corner has (0, 0).
    # You can imagine each layer having a z-offset.
    planes = [
        {(x, y): cell for x, column in enumerate(plane) for y, cell in enumerate(column)}
        for plane in itertools.chain(h, v1, v2)
    ]

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

            for orientation, plane in itertools.product(orientations, planes):
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
        # 2,004 candidates
        candidates=candidates(),
    )
    print("3D puzzle solutions:")

    if format == "dense":
        header = ",".join(label for label, shape in sorted(shapes.items()) for row in shape for column in row if column)
        print(f"{"Key":<21}", header)

    start = datetime.now()
    for n, solution in enumerate(itertools.islice(engine.search(), N), start=1):
        if format == "pretty":
            print(f"{datetime.now() - start} {n:>6,}")

            # For each cell, get its label, reverse the order to draw aesthetically
            i = iter(
                label
                for _, label in sorted(
                    ((cell, label) for label, cells in solution for cell in cells),
                    reverse=True,
                )
            )

            for level in range(1, 6):
                for _ in range(level):
                    print(" " * (5 - level), end="")
                    for _ in range(level):
                        print(f" {next(i)}", end="")
                    print()
                print()
        elif format == "simple":
            print(
                f"{datetime.now() - start} {n:>6,}",
                " ".join(f"{label}:{set(cells)}" for label, cells in sorted(solution)),
            )
        elif format == "dense":
            formatted = ",".join(str(cell) for (_, cells) in sorted(solution) for cell in cells)
            print(f"{datetime.now() - start} {n:>6,}", formatted)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates solutions for the 3D variant of the IQ Puzzler Pro game.\nThere are 26,720 solutions.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--format",
        choices=["pretty", "simple", "dense"],
        default="pretty",
        help=(
            "pretty: Shows layers of the pyramid separately with the pieces drawn in place.\n"
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
    main(**vars(args))
