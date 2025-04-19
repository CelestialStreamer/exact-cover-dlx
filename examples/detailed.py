from exact_cover import ExactCover


def main():
    """
    From: https://en.wikipedia.org/wiki/Exact_cover#Detailed_example

    Le S = {A, B, C, D, E, F} be a collection of subsets of a set
    X = {1, 2, 3, 4, 5, 6, 7} such that:

    * A = {1, 4, 7},
    * B = {1, 4},
    * C = {4, 5, 7},
    * D = {3, 5, 6},
    * E = {2, 3, 6, 7}, and
    * F = {2, 7}.

    The subcollection S* = {B, D, F} is an exact cover, since each element is
    covered by (contained in) exactly one selected subset.
    """
    # Constraints to be satisfied
    X = {1, 2, 3, 4, 5, 6, 7}

    # Candidates which satisfy some of the constraints
    S = {
        "A": {1, 4, 7},
        "B": {1, 4},
        "C": {4, 5, 7},
        "D": {3, 5, 6},
        "E": {2, 3, 6, 7},
        "F": {2, 7},
    }

    # Set up exact cover problem
    engine = ExactCover(constraints=X, candidates=S)

    # Iterate through all solutions (in this case there will be just one)
    for solution in engine.search():
        print(solution)  # {"B", "D", "F"}


if __name__ == "__main__":
    main()
