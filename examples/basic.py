from exact_cover import ExactCover


def main():
    """
    From: https://en.wikipedia.org/wiki/Exact_cover#Basic_examples

    Let S = {N, O, P, E} be a collection of subsets of a set
    X = {1, 2, 3, 4} such that:

    * N = {},
    * O = {1, 3},
    * P = {1, 2, 3}, and
    * E = {2, 4}.

    The subcollection {O, E} is an exact cover of X, since the subsets O = {1, 3}
    and E = {2, 4} are disjoint and their union is X = {1, 2, 3, 4}.
    """
    # Constraints to be satisfied
    X = {1, 2, 3, 4}

    # Candidates which satisfy some of the constraints
    S = {
        "N": {},
        "O": {1, 3},
        "P": {1, 2, 3},
        "E": {2, 4},
    }

    # Set up exact cover problem
    engine = ExactCover(constraints=X, candidates=S)

    # Iterate through all solutions (in this case there will be just one)
    for solution in engine.search():
        print(solution)  # {"E", "O"}


if __name__ == "__main__":
    main()
