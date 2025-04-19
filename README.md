## Installation

Use poetry to install the package in your environment
```
poetry install
```

## Usage

Create an engine by passing in constraints, candidate, and any optional constraints.

```python
from exact_cover import ExactCover

engine = ExactCover(
    constraints={1, 2, 3, 4},
    candidates={
        "N": {},
        "O": {1, 3},
        "P": {1, 2, 3},
        "E": {2, 4},
    },
)
```

Iterate through any solutions it finds:

```
>>> for solution in engine.search():
>>>   print(solution)
{"E", "O"}
```

This finds a solution {E,O} where E={2, 4} and O={1, 3} are disjoint and cover X={1,2,3,4}.

Candidates may be specified as an iterable of label and constraints:

```python
engine = ExactCover(
    constraints={1, 2, 3, 4},
    candidates=(
        ("N", ()),
        ("O", (1, 3)),
        ("P", (1, 2, 3)),
        ("E", (2, 4)),
    ),
)
```

This is useful if there are many candidates and generating many would require.

Labels may be whatever you find convenient.

The Sudoku example uses the row, column, and value as the key:
```python
ExactCover(
    constraints={
        *(f"R{r}C{c}" for r in range(1, 9 + 1) for c in range(1, 9 + 1)),
        *(f"R{r}#{n}" for r in range(1, 9 + 1) for n in range(1, 9 + 1)),
        *(f"C{c}#{n}" for c in range(1, 9 + 1) for n in range(1, 9 + 1)),
        *(f"B{b}#{n}" for b in range(1, 9 + 1) for n in range(1, 9 + 1)),
    },
    candidates={
        # label is ((row, column), value)
        ((r, c), n): (f"R{r}C{c}", f"R{r}#{n}", f"C{c}#{n}", f"B{(3*((r-1)//3)+(c-1)//3)+1}#{n}")
        for r in range(1, 9 + 1)
        for c in range(1, 9 + 1)
        for n in range(1, 9 + 1)
    },
)
```

Partial solutions may be passed in during search:

```python
# Start search with 3 filled in at row 1, column 2, and 6 filled in at row 4, column 5.
sudoku_engine.search([((1, 2), 3), ((4, 5), 6)])
```


Optional constraints may be specified. These are constraints which are not required to be covered by candidate, though they may if needed. These allow "at most one" constraints without requiring creating dummy candidates. The n queens problem uses optional constraints:

```python
ExactCover(
    constraints={
        *(f"R{rank}" for rank in ranks),
        *(f"F{file}" for file in files),
    },
    optional_constraints={
        *(f"D1{rank+file-1}" for rank in ranks for file in files),
        *(f"D2{rank-file+n}" for rank in ranks for file in files),
    },
    candidates={
        # label is the tuple (rank, file)
        (rank, file): (f"R{rank}", f"F{file}", f"D1{rank+file-1}", f"D2{rank-file+n}")
        for rank in ranks
        for file in files
    },
)
```
