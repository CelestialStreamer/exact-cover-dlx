import string
from datetime import datetime

import numpy as np

from exact_cover import ExactCover


def main():
    shapes = [
        [  # A
            [1, 1, 1],
            [1, 0, 0],
        ],
        [  # B
            [1, 1, 1, 1],
            [1, 0, 0, 0],
        ],
        [  # C
            [1, 1],
            [1, 0],
        ],
        [  # D
            [1, 1, 1],
            [1, 0, 0],
            [1, 0, 0],
        ],
        [  # E
            [1, 1, 0],
            [0, 1, 1],
        ],
        [  # F
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 1],
        ],
        [  # G
            [1, 1, 1, 0],
            [0, 0, 1, 1],
        ],
        [  # H
            [1, 1, 1, 1],
            [0, 0, 1, 0],
        ],
        [  # I
            [1, 1, 1],
            [0, 1, 0],
        ],
        [  # J
            [1, 0, 0],
            [1, 1, 1],
            [0, 1, 0],
        ],
        [  # K
            [1, 1, 1],
            [1, 0, 1],
        ],
        [  # L
            [1, 1, 1],
            [1, 1, 0],
        ],
    ]
    layers = [
        # Horizontal
        [
            [1, 2, 3, 4, 5],
            [6, 7, 8, 9, 10],
            [11, 12, 13, 14, 15],
            [16, 17, 18, 19, 20],
            [21, 22, 23, 24, 25],
        ],
        [
            [26, 27, 28, 29],
            [30, 31, 32, 33],
            [34, 35, 36, 37],
            [38, 39, 40, 41],
        ],
        [
            [42, 43, 44],
            [45, 46, 47],
            [48, 49, 50],
        ],
        [
            [51, 52],
            [53, 54],
        ],
        [
            [55],
        ],
        # / diagonal
        [
            [1],
        ],
        [
            [2, 26],
            [0, 6],
        ],
        [
            [3, 27, 42],
            [0, 7, 30],
            [0, 0, 11],
        ],
        [
            [4, 28, 43, 51],
            [0, 8, 31, 45],
            [0, 0, 12, 34],
            [0, 0, 0, 16],
        ],
        [
            [5, 29, 44, 52, 55],
            [0, 9, 32, 46, 53],
            [0, 0, 13, 35, 48],
            [0, 0, 0, 17, 38],
            [0, 0, 0, 0, 21],
        ],
        [
            [10, 33, 47, 54],
            [0, 14, 36, 49],
            [0, 0, 18, 39],
            [0, 0, 0, 22],
        ],
        [
            [15, 37, 50],
            [0, 19, 40],
            [0, 0, 23],
        ],
        [
            [20, 41],
            [0, 24],
        ],
        [
            [25],
        ],
        # \ diagonal
        [
            [5],
        ],
        [
            [4, 29],
            [0, 10],
        ],
        [
            [3, 28, 44],
            [0, 9, 33],
            [0, 0, 15],
        ],
        [
            [2, 27, 43, 52],
            [0, 8, 32, 47],
            [0, 0, 14, 37],
            [0, 0, 0, 20],
        ],
        [
            [1, 26, 42, 51, 55],
            [0, 7, 31, 46, 54],
            [0, 0, 13, 36, 50],
            [0, 0, 0, 19, 41],
            [0, 0, 0, 0, 25],
        ],
        [
            [6, 30, 45, 53],
            [0, 12, 35, 49],
            [0, 0, 18, 40],
        ],
        [
            [11, 34, 48],
            [0, 17, 39],
            [0, 0, 23],
        ],
        [
            [16, 38],
            [0, 22],
        ],
        [
            [21],
        ],
    ]
    point_layers = [
        {
            (x, y): value
            for x, column in enumerate(layer)
            for y, value in enumerate(column)
            if value
        }
        for layer in layers
    ]

    def generator():
        frozen = False
        for shape, name in zip(shapes, string.ascii_uppercase):
            w, h = len(shape[0]), len(shape)

            point_cloud = np.array(
                [
                    [x, y, 1]
                    for x, row in enumerate(shape)
                    for y, value in enumerate(row)
                    if value
                ]
            ).T
            aa = {
                frozenset(map(tuple, (rotation @ point_cloud)[0:2, :].T.tolist()))
                for rotation in [
                    np.array([[+1, +0, 1 - 1], [+0, +1, 1 - 1], [0, 0, 1]]),
                    np.array([[+0, -1, w - 1], [+1, +0, 1 - 1], [0, 0, 1]]),
                    np.array([[-1, +0, h - 1], [+0, -1, w - 1], [0, 0, 1]]),
                    np.array([[+0, +1, 1 - 1], [-1, +0, h - 1], [0, 0, 1]]),
                    np.array([[+0, +1, 1 - 1], [+1, +0, 1 - 1], [0, 0, 1]]),
                    np.array([[-1, +0, h - 1], [+0, +1, 1 - 1], [0, 0, 1]]),
                    np.array([[+0, -1, w - 1], [-1, +0, h - 1], [0, 0, 1]]),
                    np.array([[+1, +0, 1 - 1], [+0, -1, w - 1], [0, 0, 1]]),
                ]
            }

            for e in aa:
                shape = np.array([(x, y, 1) for x, y in e]).T

                for n, layer in enumerate(point_layers):
                    width = max(x for x, y in layer.keys()) + 1
                    height = max(y for x, y in layer.keys()) + 1
                    for x_offset in range(width):
                        for y_offset in range(height):
                            possible = (
                                np.array(
                                    [
                                        [1, 0, x_offset],
                                        [0, 1, y_offset],
                                        [0, 0, 1],
                                    ]
                                )
                                @ shape
                            )
                            thing = set((x, y) for x, y in possible[0:2, :].T.tolist())
                            if all(key in layer for key in thing):
                                blah = tuple(sorted(layer[foo] for foo in thing))
                                yield name, blah

    engine = ExactCover(
        constraints=[
            *string.ascii_uppercase[: len(shapes)],
            *range(
                1,
                max(cell for layer in layers for row in layer for cell in row) + 1,
            ),
        ],
        candidates={(name, indices): (name, *indices) for name, indices in generator()},
    )
    print("Built. Searching...")
    start = datetime.now()
    for n, solution in enumerate(engine.search(), start=1):
        print(f"{datetime.now() - start} {n:>4}", sorted(solution))


if __name__ == "__main__":
    main()
