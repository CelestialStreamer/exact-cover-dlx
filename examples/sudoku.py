import argparse
import itertools

from exact_cover import ExactCover


def main(N: int | None = 10, puzzle: list[int] | None = None):
    """
    From: https://en.wikipedia.org/wiki/Exact_cover#Sudoku

    The problem in Sudoku is to assign numbers (or digits, values, symbols) to
    cells (or squares) in a grid so as to satisfy certain constraints.

    In the standard 9x9 Sudoku variant, there are four kinds of constraints:
      * Row-Column: Each intersection of a row and column, i.e, each cell, must
        contain exactly one number.
      * Row-Number: Each row must contain each number exactly once
      * Column-Number: Each column must contain each number exactly once.
      * Box-Number: Each box must contain each number exactly once.

    While the first constraint might seem trivial, it is nevertheless needed to
    ensure there is only one number per cell. Naturally, placing a number into a
    cell prohibits placing any other number into the now occupied cell.

    Solving Sudoku is an exact cover problem. More precisely, solving Sudoku is
    an exact hitting set problem, which is equivalent to an exact cover problem,
    when viewed as a problem to select possibilities such that each constraint
    set contains (i.e., is hit by) exactly one selected possibility.

    Each possible assignment of a particular number to a particular cell is a
    possibility (or candidate). When Sudoku is played with pencil and paper,
    possibilities are often called pencil marks.

    In the standard 9x9 Sudoku variant, in which each of 9x9 cells is assigned
    one of 9 numbers, there are 9x9x9=729 possibilities. Using obvious notation
    for rows, columns and numbers, the possibilities can be labeled

        R1C1#1, R1C1#2, …, R9C9#9.

    The fact that each kind of constraint involves exactly one of something is
    what makes Sudoku an exact hitting set problem. The constraints can be
    represented by constraint sets. The problem is to select possibilities such
    that each constraint set contains (i.e., is hit by) exactly one selected
    possibility.

    In the standard 9x9 Sudoku variant, there are four kinds of constraints sets
    corresponding to the four kinds of constraints:

    * Row-Column: A row-column constraint set contains all the possibilities
        for the intersection of a particular row and column, i.e., for a cell.
        For example, the constraint set for row 1 and column 1, which can be
        labeled R1C1, contains the 9 possibilities for row 1 and column 1 but
        different numbers:

        R1C1 = { R1C1#1, R1C1#2, R1C1#3, R1C1#4, R1C1#5, R1C1#6, R1C1#7, R1C1#8, R1C1#9 }.

    * Row-Number: A row-number constraint set contains all the possibilities for
        a particular row and number. For example, the constraint set for row 1 and
        number 1, which can be labeled R1#1, contains the 9 possibilities for row 1
        and number 1 but different columns:

        R1#1 = { R1C1#1, R1C2#1, R1C3#1, R1C4#1, R1C5#1, R1C6#1, R1C7#1, R1C8#1, R1C9#1 }.

    * Column-Number: A column-number constraint set contains all the
        possibilities for a particular column and number. For example, the
        constraint set for column 1 and number 1, which can be labeled C1#1,
        contains the 9 possibilities for column 1 and number 1 but different rows:

        C1#1 = { R1C1#1, R2C1#1, R3C1#1, R4C1#1, R5C1#1, R6C1#1, R7C1#1, R8C1#1, R9C1#1 }.

    * Box-Number: A box-number constraint set contains all the possibilities for
        a particular box and number. For example, the constraint set for box 1
        (in the upper lefthand corner) and number 1, which can be labeled B1#1,
        contains the 9 possibilities for the cells in box 1 and number 1:

        B1#1 = { R1C1#1, R1C2#1, R1C3#1, R2C1#1, R2C2#1, R2C3#1, R3C1#1, R3C2#1, R3C3#1 }.

    Since there are 9 rows, 9 columns, 9 boxes and 9 numbers, there are
    9x9=81 row-column constraint sets, 9x9=81 row-number constraint sets,
    9x9=81 column-number constraint sets, and 9x9=81 box-number constraint sets:
    81+81+81+81=324 constraint sets in all.

    In brief, the standard 9x9 Sudoku variant is an exact hitting set problem
    with 729 possibilities and 324 constraint sets. Thus the problem can be
    represented by a 729x324 matrix.
    """
    sudoku_cover = ExactCover(
        constraints={
            # one answer per cell
            *(f"R{r}C{c}" for r in range(1, 9 + 1) for c in range(1, 9 + 1)),
            # number used once per row
            *(f"R{r}#{n}" for r in range(1, 9 + 1) for n in range(1, 9 + 1)),
            # number used once per column
            *(f"C{c}#{n}" for c in range(1, 9 + 1) for n in range(1, 9 + 1)),
            # number used once per nxn box
            *(f"B{b}#{n}" for b in range(1, 9 + 1) for n in range(1, 9 + 1)),
        },
        candidates={
            ((r, c), n): (
                f"R{r}C{c}",
                f"R{r}#{n}",
                f"C{c}#{n}",
                f"B{(3*((r-1)//3)+(c-1)//3)+1}#{n}",
            )
            for r in range(1, 9 + 1)
            for c in range(1, 9 + 1)
            for n in range(1, 9 + 1)
        },
    )

    if puzzle:
        # Convert puzzle, a list of numbers representing the initial starting point,
        # into the initial state for the search. The format should match however
        # the candidate keys are set up. In this case, ((row, column), value)
        # where row and column are the location of the cell, with the value.
        initial = [
            (
                (
                    cell // 9 + 1,  # Row
                    cell % 9 + 1,  # Column
                ),
                value,
            )
            for cell, value in enumerate(puzzle)
            if value  # Skip empty cells
        ]

    for n, solution in enumerate(itertools.islice(sudoku_cover.search(initial), N), start=1):
        print(f"Solution {n}:")
        solution = dict(solution)  # Create lookup table (row, column): value
        for r in range(1, 9 + 1):
            for c in range(1, 9 + 1):
                print(solution[(r, c)], end="")
            print()
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Finds solutions for the Sudoku Puzzle",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--puzzle",
        type=lambda s: list(map(int, s)),
        help=(
            "A string representing and unsolved Sudoku Puzzle.\n"
            "Example: 030050040008010500460000012070502080000603000040109030250000098001020600080060020"
        ),
    )
    parser.add_argument(
        "-N",
        default=10,
        type=int,
        help="Number of solutions to print. Default is 10. Pass -1 to print all solutions.",
    )
    args = parser.parse_args()
    if args.N == -1:
        args.N = None
    main(**vars(args))
