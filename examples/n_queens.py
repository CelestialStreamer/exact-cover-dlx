import argparse
import itertools

from exact_cover import ExactCover


def main(n: int, N: int):
    """
    From: https://en.wikipedia.org/wiki/Exact_cover#N_queens_problem

    The N queens problem is the problem of placing n chess queens on an nxn
    chessboard so that no two queens threaten each other. A solution requires
    that no two queens share the same row, column, or diagonal. It is an example
    of a generalized exact cover problem.

    The problem involves four kinds of constraints:
        * Rank: For each of the N ranks, there must be exactly one queen.
        * File: For each of the N files, there must be exactly one queen.
        * Diagonals: For each of the 2N - 1 diagonals, there must be at most one queen.
        * Reverse diagonals: For each of the 2N - 1 reverse diagonals, there must be
        at most one queen.

    A solution to eight queens puzzle:

          a b c d e f g h
        8           X     8
        7       X         7
        6             X   6
        5 X               5
        4               X 4
        3   X             3
        2         X       2
        1     X           1
          a b c d e f g h
    """

    # This example shows how to use optional constraints.
    # While each of the first and last diagonals and reverse diagonals may be
    # skipped because they involved only one square, this code shows the
    # complete solution as it's easier to understand.
    ranks = range(1, n + 1)
    files = range(1, n + 1)
    n_queens = ExactCover(
        constraints={
            # Each rank must be covered by only one queen
            *(f"R{rank}" for rank in ranks),
            # Each file must be covered by only one queen
            *(f"F{file}" for file in files),
        },
        optional_constraints={
            # Each diagonal may be covered by at most one queen
            *(f"D1{rank+file-1}" for rank in ranks for file in files),
            # Each reverse diagonal may be covered by at most one queen
            *(f"D2{rank-file+n}" for rank in ranks for file in files),
        },
        candidates={
            # The key here can be anything, but the only reasonable
            # choice is the queen's location on the board.
            (rank, file): (
                # Queen occupies one rank and one file
                f"R{rank}",
                f"F{file}",
                # Queen occupies two diagonals
                f"D1{rank+file-1}",
                f"D2{rank-file+n}",
            )
            for rank in ranks
            for file in files
        },
    )

    print(f"N queens problem with {n=}")
    for n, solution in enumerate(itertools.islice(n_queens.search(), N), start=1):
        print(f"Solution {n}:")
        for rank in ranks:
            for file in files:
                if (rank, file) in solution:
                    print("X", end="")
                else:
                    print(".", end="")
            print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Finds solutions to for the N queens problem",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "n",
        nargs="?",
        default=8,
        type=int,
        help="How many queens to place on an nxn chessboard.\nDefault is 8.",
    )
    parser.add_argument(
        "-N",
        default=100,
        type=int,
        help="Number of solutions to print. Default is 100. Pass -1 to print all solutions.",
    )
    args = parser.parse_args()
    if args.N == -1:
        args.N = None
    main(**vars(args))
