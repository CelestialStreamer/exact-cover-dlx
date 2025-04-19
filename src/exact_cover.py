from collections import deque
from typing import Generator, Iterable, Optional, Self

__all__ = ["ExactCover"]


class Data[Co, Ca]:
    """
    Elements of the cover matrix A are represented as a data object, with fields l, r, u, d.
    Rows of the matrix are doubly linked as circular lists via the l and r fields (left and right);
    columns are doubly linked as circular lists via the u and d fields (up and down).

    Columns track the column header, and rows track the row header.
    """

    def __init__(
        self,
        constraint: "Constraint[Co,Ca]",
        candidate: "Candidate[Co,Ca]",
        l: Optional[Self] = None,
        r: Optional[Self] = None,
        u: Optional[Self] = None,
        d: Optional[Self] = None,
    ):
        self.constraint = constraint
        self.candidate = candidate
        self.l = l or self
        self.r = r or self
        self.u = u or self
        self.d = d or self

    def right(self, skip_self=False):
        data = self
        if not skip_self:
            yield data
        while (data := data.r) is not self:
            yield data

    def left(self):
        data = self
        while (data := data.l) is not self:
            yield data

    def __repr__(self):
        return f"{self.__class__.__name__}(candidate={self.candidate.value!r}, constraint={self.constraint.value!r})"


class Constraint[Co, Ca](Data[Co, Ca]):
    """
    Column header, storing the value and the column size (number of data items in the column).

    The value can be anything meaningful to the user.
    """

    l: Self
    r: Self
    d: Data[Co, Ca]
    u: Data[Co, Ca]

    def __init__(self, value: Co, l: Self, r: Self):
        super().__init__(constraint=None, candidate=None, l=l, r=r)
        self.value = value
        self.size = int(0)

    def down(self):
        data = self
        while (data := data.d) is not self:
            yield data

    def up(self):
        data = self
        while (data := data.u) is not self:
            yield data

    def cover(self):
        # Remove column from matrix
        self.r.l = self.l
        self.l.r = self.r

        for i in self.down():
            # Remove row from matrix, but preserve this column's references
            for j in i.right(skip_self=True):
                j.d.u = j.u
                j.u.d = j.d
                j.constraint.size -= 1  # decrease counter for constraint

        return self

    def uncover(self):
        for i in self.up():
            for j in i.left():
                # Restore row to matrix
                j.constraint.size += 1  # increase counter for constraint
                j.d.u = j.u.d = j

        # Restore column to matrix
        self.r.l = self.l.r = self

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value!r}, size={self.size})"


class Candidate[Co, Ca](Data[Co, Ca]):
    u: Self
    d: Self
    r: Data[Co, Ca]
    l: Data[Co, Ca]

    def __init__(self, value: Ca, u: Self, d: Self):
        super().__init__(candidate=None, constraint=None, u=u, d=d)
        self.value = value

    def right(self):
        if self.r is not self:
            yield from self.r.right()

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value!r})"


class Root[Ca, Co](Data[Ca, Co]):
    u: Candidate[Ca, Co]
    d: Candidate[Ca, Co]
    l: Constraint[Ca, Co]
    r: Constraint[Ca, Co]

    def __init__(self):
        super().__init__(constraint=None, candidate=None)
        self.constraints = dict[Ca, Constraint[Ca, Co]]()
        self.candidates = dict[Co, Candidate[Ca, Co]]()

    def right(self):
        constraint = self
        while (constraint := constraint.r) is not self:
            yield constraint

    def down(self):
        candidate = self
        while (candidate := candidate.d) is not self:
            yield candidate

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class ExactCover[Co, Ca]:
    def __init__(
        self,
        constraints: Iterable[Co],
        candidates: Iterable[tuple[Ca, Iterable[Co]]],
        optional_constraints: Iterable[Co] = None,
    ):
        self.root = root = Root[Co, Ca]()

        con: Constraint[Co, Ca] = root
        for v in constraints:
            # Constraints are the column headers of our matrix.
            # Constraint is saved in root for convenience.
            # Append to row: col.r.l = col.r = Constraint(l=con, r=con.r)
            root.constraints[v] = con.r.l = con.r = con = Constraint[Co, Ca](value=v, l=con, r=con.r)

        if optional_constraints:
            for v in optional_constraints:
                # Optional constraints are similar to constraints, with the
                # exception that they are not linked to the other required headers.
                # Candidates may still cover these optional constraints, but
                # the search algorithm will skip these otherwise.
                root.constraints[v] = Constraint(value=v, l=None, r=None)

        can: Candidate[Co, Ca] = root
        for candidate, constraint_set in candidates:
            # Candidates are the row headers of our matrix.
            # Candidate is saved in root for use in searching when given initial values.
            # Append to column: can.d.u = can.d = Candidate(u=can, d=can.d)
            root.candidates[candidate] = can.d.u = can.d = can = Candidate(value=candidate, u=can, d=can.d)
            data: Data[Co, Ca] = can
            for v in constraint_set:
                # Lookup constraint by value
                try:
                    con = root.constraints[v]
                except KeyError as e:
                    message = (
                        f"Values for candidate {candidate!r} are not a subset of constraints."
                        f" {constraint_set} contains unknown constraint value: {v}"
                    )
                    raise TypeError(message) from e
                # Append to column: con.d.u = con.d = Data(u=con, d=con.d)
                # Append to row: data.r.l = data.r = Data(l=data, r=data.r)
                con.u.d = con.u = data.r.l = data.r = data = Data(
                    candidate=can, constraint=con, u=con.u, d=con, l=data, r=data.r
                )

                # Increase constraint candidate count
                con.size += 1

            # Remove candidate from data row. (Candidate still access data)
            can.l.r = can.r
            can.r.l = can.l

        # TODO: Remove constraint from data columns:
        # for con in root.right():
        #     con.d.u = con.u
        #     con.u.d = con.d

    def __search(self, O: deque[Ca]) -> Generator[set[Ca]]:
        if self.root.r == self.root:
            return (yield set(O))

        response = None
        # Cover constraint with fewest candidates to minimize branching
        constraint = min(self.root.right(), key=lambda e: e.size).cover()
        for row in constraint.down():
            for d in row.right(skip_self=True):
                d.constraint.cover()

            O.append(row.candidate.value)
            response = yield from self.__search(O)
            O.pop()

            for d in row.left():
                d.constraint.uncover()

            if response:
                break

        constraint.uncover()
        return response

    def search(self, initial: Iterable[Ca] = list[Ca]()):
        initial = deque(initial)
        covered = deque(
            data.constraint.cover() for candidate in initial for data in self.root.candidates[candidate].right()
        )

        try:
            g = self.__search(initial)
            for solution in g:
                yield solution
        finally:
            # Restore engine so it can be used for another search
            try:
                g.send("Stop")  # Uncover constraints if early exit
            except StopIteration:
                pass
            while covered:
                covered.pop().uncover()
